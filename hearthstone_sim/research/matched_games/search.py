"""Bounded learned-value combat planning from public observations ONLY.

No Game instance, private deck, hidden hand or real engine RNG is accepted.
This deliberately limited transition model searches plain minion attacks in
positions without ongoing card triggers. Unmodeled positions use the base
policy and expose the reason/coverage. Unknown secret activation is not modeled;
this is a limited combat-planning contender, not exact full-information MCTS.
"""

from copy import deepcopy
import torch

KEYWORDS = {"TAUNT", "DIVINE_SHIELD", "RUSH", "CHARGE", "WINDFURY", "ELUSIVE", "STEALTH"}


def supported(view, cards):
    if view.get("phase") != "play":
        return False, "non_play_phase"
    from expanded.cards import TRIGGERS, DEATH_EFFECTS, AURAS, CONDITIONAL_ATTACK, NO_CORPSE

    for p in view["players"]:
        if p.get("weapon"):
            return False, "weapon"
        for m in p["board"]:
            if m.get("type") != "MINION" or m.get("dormant") or m["health"] <= 0:
                return False, "non_plain_board_object"
            cid = m["card_id"]
            data = cards.get(cid, {})
            if (
                cid in TRIGGERS
                or cid in DEATH_EFFECTS
                or cid in AURAS
                or cid in CONDITIONAL_ATTACK
                or cid in NO_CORPSE
            ):
                return False, "card_trigger_or_aura"
            if set(m.get("keywords", [])) - KEYWORDS:
                return False, "unmodeled_keyword"
            if (
                m.get("rule_state")
                or m.get("attached_death_effects")
                or m.get("aura_attack")
                or m.get("aura_health")
            ):
                return False, "attached_or_aura_effect"
            # Only plain printed stats/keywords; Battlecry/other rules can install
            # persistent effects not represented by the basic public fields.
            if set(data.get("mechanics", [])) - KEYWORDS:
                return False, "unmodeled_printed_mechanic"
    return True, None


def attacks(view):
    owner = view["viewer"]
    enemy = 1 - owner
    turn = view["turn"]
    p = view["players"][owner]
    q = view["players"][enemy]
    taunts = [m for m in q["board"] if "TAUNT" in m["keywords"] and "STEALTH" not in m["keywords"]]
    targets = taunts or [m for m in q["board"] if "STEALTH" not in m["keywords"]]
    result = []
    for m in p["board"]:
        keys = set(m["keywords"])
        fresh = m["summoned_turn"] == turn
        if (
            m["attack"] <= 0
            or m.get("frozen_until", -1) >= turn
            or m["attacks"] >= (2 if "WINDFURY" in keys else 1)
        ):
            continue
        if fresh and not keys & {"RUSH", "CHARGE"}:
            continue
        for target in targets:
            result.append(
                dict(kind="attack", source=m["uid"], target=target["uid"], position=-1, choices=())
            )
        if not taunts and (not fresh or "CHARGE" in keys):
            result.append(
                dict(kind="attack", source=m["uid"], target=-1 - enemy, position=-1, choices=())
            )
    return result


def transition(view, action):
    nxt = deepcopy(view)
    owner = nxt["viewer"]
    p = nxt["players"][owner]
    q = nxt["players"][1 - owner]
    attacker = next(m for m in p["board"] if m["uid"] == action["source"])
    attacker["attacks"] += 1
    if "STEALTH" in attacker["keywords"]:
        attacker["keywords"].remove("STEALTH")
    events = nxt.setdefault("events", [])
    events.append(
        dict(
            turn=nxt["turn"],
            event="attack",
            player=owner,
            source=attacker["uid"],
            target=action["target"],
        )
    )

    def damage(m, amount):
        if amount <= 0:
            return
        if "DIVINE_SHIELD" in m["keywords"]:
            m["keywords"].remove("DIVINE_SHIELD")
        else:
            m["health"] -= amount

    if action["target"] < 0:
        amount = attacker["attack"]
        absorbed = min(q["armor"], amount)
        q["armor"] -= absorbed
        q["health"] -= amount - absorbed
    else:
        defender = next(m for m in q["board"] if m["uid"] == action["target"])
        a, d = attacker["attack"], defender["attack"]
        damage(defender, a)
        damage(attacker, d)
    for side in nxt["players"]:
        dead = [m for m in side["board"] if m["health"] <= 0]
        side["corpses"] += len(dead)
        side["board"] = [m for m in side["board"] if m["health"] > 0]
    return nxt


def choose(decision, model, encoder, base_index, cfg):
    view = decision["observation"]
    okay, reason = supported(view, encoder.cards)
    stats = dict(searched=False, reason=reason, nodes=0)
    if not okay:
        return base_index, stats
    legal = decision["actions"]
    if legal[base_index]["kind"] != "attack" or legal[base_index]["source"] <= 0:
        return base_index, dict(stats, reason="base_policy_non_minion_attack")
    with torch.no_grad():
        logits, _ = model([encoder.encode(decision)])
    indices = [i for i, a in enumerate(legal) if a["kind"] == "attack" and a["source"] > 0]
    indices = sorted(indices, key=lambda i: float(logits[0][i]), reverse=True)[: cfg["width"]]
    if base_index not in indices:
        indices[-1] = base_index

    def value(v):
        enemy = 1 - v["viewer"]
        if v["players"][enemy]["health"] <= 0:
            return 1.0
        if v["players"][v["viewer"]]["health"] <= 0:
            return -1.0
        fake = deepcopy(decision)
        fake["observation"] = v
        # Value encoding is independent of action head outputs. Retain a
        # nonempty public candidate only to satisfy the encoder contract.
        fake["actions"] = [dict(kind="end", source=0, target=0, position=-1, choices=())]
        v["legal_actions"] = fake["actions"]
        with torch.no_grad():
            return float(model([encoder.encode(fake)])[1][0])

    def descend(v, depth):
        score = value(v)
        if depth == 0 or stats["nodes"] >= cfg["max_nodes"] or abs(score) == 1:
            return score
        for action in attacks(v)[: cfg["width"]]:
            if stats["nodes"] >= cfg["max_nodes"]:
                break
            stats["nodes"] += 1
            score = max(score, descend(transition(v, action), depth - 1))
        return score

    best = base_index
    best_score = float("-inf")
    for i in indices:
        if stats["nodes"] >= cfg["max_nodes"]:
            break
        stats["nodes"] += 1
        score = descend(transition(view, legal[i]), cfg["depth"] - 1)
        if score > best_score:
            best, best_score = i, score
    return best, dict(stats, searched=True, reason=None)
