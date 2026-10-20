"""Structured, policy-visible entity tokens; no private Game access.

Every field of the current observation is represented except bookkeeping and
constant fidelity prose. Public events use an explicit recent-history window;
its omitted count is encoded. No state entities or legal actions are truncated.
Hashed field/value embeddings have collisions: this is a versioned baseline,
not a claim of a lossless sufficient statistic.
"""

from dataclasses import dataclass
import hashlib
import json
import math

SCHEMA = "visible-entity-transformer-v1"


@dataclass(frozen=True)
class EncoderConfig:
    buckets: int = 32768
    history_events: int = 64
    max_state_tokens: int = 768
    max_fields_per_token: int = 8192

    def __post_init__(self):
        if (
            self.buckets < 256
            or min(self.history_events, self.max_state_tokens, self.max_fields_per_token) < 1
        ):
            raise ValueError("Invalid encoder limits")


def stable_bucket(value, buckets):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return 1 + int.from_bytes(hashlib.blake2b(raw.encode(), digest_size=8).digest(), "little") % (
        buckets - 1
    )


class VisibleEncoder:
    def __init__(self, config=EncoderConfig(), card_definitions=None):
        self.config = config
        # Only looked up for identities already present in the viewer's data.
        self.cards = card_definitions or {}

    def encode(self, decision):
        view = decision["observation"]
        viewer = view["viewer"]
        if viewer not in (0, 1) or decision["actor"] != viewer:
            raise ValueError("Wrong observation viewer")
        if decision["actions"] != view["legal_actions"] or not decision["actions"]:
            raise ValueError("Expected matching nonempty legal candidates")
        refs = {-1 - viewer: "self/hero", -1 - (1 - viewer): "opponent/hero"}
        for owner, player in enumerate(view["players"]):
            for zone in ("hand", "board"):
                for slot, entity in enumerate(player.get(zone, ())):
                    if isinstance(entity, dict) and "uid" in entity:
                        refs[entity["uid"]] = (
                            f"{'self' if owner == viewer else 'opponent'}/{zone}/{slot}"
                        )

        def clean(value, key=""):
            if isinstance(value, dict):
                result = {}
                for k, v in sorted(value.items()):
                    if k in ("uid", "colossal_parent", "imprisoned_entity") or k.endswith("_uid"):
                        result[k] = refs.get(v, "unresolved") if isinstance(v, int) else clean(v)
                    elif (
                        k in ("owner", "player", "controller", "current_player") and type(v) is int
                    ):
                        result[k] = "self" if v == viewer else "opponent" if v == 1 - viewer else v
                    elif k in ("source", "target") and type(v) is int:
                        result[k] = refs.get(v, "none" if v == 0 else "unresolved")
                    else:
                        result[k] = clean(v, k)
                # Include frozen printed rules/attributes for visible identities.
                cid = value.get("card_id")
                if cid in self.cards:
                    data = self.cards[cid]
                    result["printed"] = {
                        k: data[k]
                        for k in (
                            "name",
                            "type",
                            "cost",
                            "attack",
                            "health",
                            "durability",
                            "mechanics",
                            "text",
                            "races",
                            "spellSchool",
                            "cardClass",
                        )
                        if k in data
                    }
                return result
            if isinstance(value, (list, tuple)):
                return [clean(v, key) for v in value]
            return value

        def row(kind, value):
            fields = [(stable_bucket(["kind", kind], self.config.buckets), 1.0)]

            def visit(obj, path):
                if isinstance(obj, dict):
                    if not obj:
                        fields.append((stable_bucket([path, "empty"], self.config.buckets), 1.0))
                    for k, v in sorted(obj.items()):
                        visit(v, path + [k])
                elif isinstance(obj, (tuple, list)):
                    fields.append(
                        (stable_bucket([path, "length"], self.config.buckets), math.log1p(len(obj)))
                    )
                    for i, v in enumerate(obj):
                        visit(v, path + [i])
                elif type(obj) in (int, float):
                    if not math.isfinite(obj):
                        raise ValueError("Nonfinite observation")
                    fields.append(
                        (
                            stable_bucket([path, "number"], self.config.buckets),
                            math.copysign(math.log1p(abs(obj)), obj),
                        )
                    )
                elif isinstance(obj, (str, bool)) or obj is None:
                    fields.append((stable_bucket([path, obj], self.config.buckets), 1.0))
                else:
                    raise ValueError("Observation is not plain JSON: " + str(type(obj)))
                if len(fields) > self.config.max_fields_per_token:
                    raise ValueError("Entity token overflow; raise max_fields_per_token explicitly")

            visit(clean(value), [kind])
            return fields

        states = [
            row(
                "summary",
                {
                    k: v
                    for k, v in view.items()
                    if k
                    not in (
                        "players",
                        "events",
                        "legal_actions",
                        "viewer",
                        "winner",
                        "terminal",
                        "approximation_profile",
                        "additional_approximations",
                        "version",
                    )
                },
            )
        ]
        for owner in (viewer, 1 - viewer):
            side = "self" if owner == viewer else "opponent"
            player = view["players"][owner]
            for key, value in sorted(player.items()):
                if key in ("hand", "board"):
                    states.append(row(side + "/" + key + "/count", len(value)))
                    for i, entity in enumerate(value):
                        states.append(row(side + "/" + key + "/" + str(i), entity))
                else:
                    states.append(row(side + "/" + key, value))
        events = view.get("events", [])
        window = self.config.history_events
        states.append(row("history_omitted", max(0, len(events) - window)))
        for i, event in enumerate(events[-window:]):
            states.append(row("recent_event/" + str(i), event))
        if len(states) > self.config.max_state_tokens:
            raise ValueError("State token overflow; raise max_state_tokens explicitly")
        actions = []
        entities = {
            e["uid"]: e
            for p in view["players"]
            for z in ("board", "hand")
            for e in p.get(z, ())
            if isinstance(e, dict) and "uid" in e
        }
        for action in decision["actions"]:
            resolved = dict(action)
            for role in ("source", "target"):
                uid = action.get(role)
                if uid in entities:
                    resolved[role + "_entity"] = entities[uid]
            if action["kind"] == "mulligan":
                resolved["choices"] = [
                    refs.get(uid, "unresolved") for uid in action.get("choices", ())
                ]
            elif action["kind"] == "choose":
                options = (view.get("pending_choice") or {}).get("options", [])
                resolved["selected_options"] = [options[i] for i in action.get("choices", ())]
            actions.append(row("action", resolved))
        return {"state": states, "actions": actions}
