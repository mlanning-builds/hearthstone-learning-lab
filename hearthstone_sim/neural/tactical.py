"""Owner-started supervised lessons from scripted, public engine positions.

No work at import. Construction makes bounded fixtures, never complete games.
The owner explicitly starts the warm-up; only its public observation is encoded.
"""

import torch

VERSION = "basic-tactics-v2-threat-survival"
REFRESH_EVERY_ITERATIONS = 16
REFRESH_STEPS = 16
NEUTRALS = (
    "CORE_CS2_179",
    "CORE_DRG_079",
    "CORE_EX1_010",
    "CORE_EX1_028",
    "CORE_GIL_558",
    "CORE_GVG_085",
    "CORE_LOOT_137",
    "CORE_NEW1_023",
    "CS3_038",
    "Core_CS2_200",
    "EDR_486",
    "EDR_598",
    "TIME_053",
    "TIME_056",
    "TLC_248",
)


def _legacy_lessons():
    """Scripted legal decisions with explicit acceptable actions; no teacher rollout."""
    from expanded import Game, Action, Deck
    from dataclasses import asdict

    lessons = []
    for variant in range(4):
        for kind in (
            "attack_lethal",
            "spell_lethal",
            "safe_trade",
            "develop",
            "remove_threat",
            "buff_friend",
        ):
            deck = tuple(cid for cid in NEUTRALS for _ in range(2))
            g = Game([Deck("MAGE", deck), Deck("WARRIOR", deck)], seed=97 + variant)
            g.step(Action("mulligan"))
            g.step(Action("mulligan"))
            g.current = 0
            g.turn = 5
            g.phase = "play"
            for p in g.players:
                p.hand = []
                p.board = []
                p.mana = p.max_mana = 10
                p.health = 30
                p.armor = 0
            wanted = None
            if kind in ("attack_lethal", "safe_trade"):
                m = g._summon(0, "CORE_CS2_179")
                m.summoned_turn = -1
                m.attack = 3 + variant
                m.health = m.max_health = 8
                if kind == "attack_lethal":
                    g.players[1].health = m.attack
                    target = -2
                else:
                    enemy = g._summon(1, "CORE_CS2_179")
                    enemy.attack = 5
                    enemy.health = 2
                    target = enemy.uid

                def wanted(a):
                    return a.kind == "attack" and a.source == m.uid and a.target == target
            elif kind in ("spell_lethal", "remove_threat"):
                c = g._add(0, "CORE_CS2_029")
                g.players[0].mana = 4
                if kind == "spell_lethal":
                    g.players[1].health = 3 + variant
                    target = -2
                else:
                    enemy = g._summon(1, "CORE_CS2_179")
                    enemy.attack = 8
                    enemy.health = 6
                    target = enemy.uid

                def wanted(a):
                    return a.kind == "play" and a.source == c.uid and a.target == target
            elif kind == "develop":
                c = g._add(0, "CORE_CS2_179")
                g.players[0].mana = 4

                def wanted(a):
                    return a.kind == "play" and a.source == c.uid
            else:
                own = g._summon(0, "CORE_CS2_179")
                own.summoned_turn = -1
                g._summon(1, "CORE_CS2_179")
                c = g._add(0, "CS2_092")
                g.players[0].mana = 4

                def wanted(a):
                    return a.kind == "play" and a.source == c.uid and a.target == own.uid

            actions = g.legal_actions()
            view = g.observe(0)
            view["legal_actions"] = [asdict(a) for a in actions]
            answers = [i for i, a in enumerate(actions) if wanted(a)]
            if not answers:
                raise ValueError("Lesson has no legal answer: " + kind)
            lessons.append(
                dict(
                    name=f"{kind}-{variant}",
                    kind=kind,
                    version=VERSION,
                    decision=dict(actor=0, observation=view, actions=view["legal_actions"]),
                    answers=answers,
                )
            )
    return lessons


def threat_position(variant, split="assessment"):
    """A removal prevents lethal; every other immediate move leaves lethal available.

    These are bounded scripted positions, not a rollout teacher or a game policy.
    Training and assessment use different hero-health / attack combinations.
    """
    if split not in ("training", "assessment") or variant not in range(4):
        raise ValueError("Unknown threat lesson split or variant")
    from expanded import Game, Action, Deck

    deck = tuple(cid for cid in NEUTRALS for _ in range(2))
    g = Game(
        [Deck("MAGE", deck), Deck("WARRIOR", deck)],
        seed=197 + variant + (100 if split == "assessment" else 0),
    )
    g.step(Action("mulligan"))
    g.step(Action("mulligan"))
    g.current = 0
    g.turn = 5
    g.phase = "play"
    for p in g.players:
        p.hand = []
        p.board = []
        p.mana = p.max_mana = 10
        p.health = 30
        p.armor = 0
    g.players[0].health = 1 + variant + (4 if split == "assessment" else 0)
    g.players[0].mana = 4
    # A harmless decoy varies target position without introducing another lethal.
    if variant % 2:
        decoy = g._summon(1, "CORE_CS2_179")
        g._set_entity_stats(decoy, 0, 1)
        decoy.summoned_turn = -1
    enemy = g._summon(1, "CORE_CS2_179")
    g._set_entity_stats(
        enemy,
        6 + variant + (4 if split == "assessment" else 0),
        (3 + variant) if split == "training" else (6 - variant),
    )
    enemy.summoned_turn = -1
    card = g._add(0, "CORE_CS2_029")
    g._refresh_auras()
    if not (enemy.health == enemy.max_health and enemy.attack >= g.players[0].health):
        raise ValueError("Inconsistent threat fixture")
    return g, card.uid, enemy.uid


def build_lessons(split="assessment"):
    from dataclasses import asdict

    lessons = [item for item in _legacy_lessons() if item["kind"] != "remove_threat"]
    for item in lessons:
        item["version"] = VERSION
    for variant in range(4):
        g, source, target = threat_position(variant, split)
        actions = g.legal_actions()
        view = g.observe(0)
        view["legal_actions"] = [asdict(action) for action in actions]
        answers = [
            i
            for i, a in enumerate(actions)
            if a.kind == "play" and a.source == source and a.target == target
        ]
        if len(answers) != 1:
            raise ValueError("Threat fixture must have one removal answer")
        lessons.append(
            dict(
                name=f"remove_threat-{split}-{variant}",
                kind="remove_threat",
                version=VERSION,
                split=split,
                decision=dict(actor=0, observation=view, actions=view["legal_actions"]),
                answers=answers,
            )
        )
    return lessons


def lesson_indices(step, lessons):
    # Half the examples rehearse threat removal; half retain the other skills.
    threat = [i for i, lesson in enumerate(lessons) if lesson["kind"] == "remove_threat"]
    other = [i for i, lesson in enumerate(lessons) if lesson["kind"] != "remove_threat"]
    if not threat or not other:
        raise ValueError("Expected threat and non-threat lessons")
    return [threat[(step * 2 + i) % len(threat)] for i in range(2)] + [
        other[(step * 2 + i) % len(other)] for i in range(2)
    ]


def resume_state(previous):
    """Version only the lesson counter, retaining the original lesson receipts."""
    from copy import deepcopy

    state = deepcopy(previous)
    if state.get("version") != VERSION:
        old = deepcopy(state)
        history = old.pop("previous_versions", [])
        state.update(
            version=VERSION,
            completed=0,
            refresh_count=0,
            last_refresh_iteration=None,
            previous_versions=history + ([old] if old.get("completed", 0) else []),
        )
    return state


def refresh_if_due(
    model,
    optimizer,
    encoder,
    state,
    *,
    iteration,
    enabled,
    allow_training=False,
    emit=lambda **k: None,
):
    """Bounded rehearsal once per 16 completed PPO batches; counters resume safely."""
    if (
        not enabled
        or iteration % REFRESH_EVERY_ITERATIONS
        or state.get("last_refresh_iteration") == iteration
    ):
        return False
    if not allow_training:
        raise ValueError("Tactical refresh requires owner activation")
    if state.get("version") != VERSION:
        raise ValueError("Normalize tactical version before refresh")
    report = warmup(
        model, optimizer, encoder, steps=REFRESH_STEPS, completed=0, allow_training=True, emit=emit
    )
    state.update(
        last_refresh_iteration=iteration,
        refresh_count=state.get("refresh_count", 0) + 1,
        last_refresher=report,
    )
    return True


def warmup(
    model, optimizer, encoder, *, steps, completed=0, allow_training=False, emit=lambda **k: None
):
    """Supervised warm-up only when explicitly owner-started. Preserves Adam state."""
    if not allow_training:
        raise ValueError("Tactical learning requires owner activation")
    if type(steps) is not int or not 0 <= completed <= steps:
        raise ValueError("Invalid tactical step budget")
    lessons = build_lessons("training")
    encoded = [encoder.encode(x["decision"]) for x in lessons]
    before = assess(model, encoder)
    model.eval()
    for step in range(completed, steps):
        indices = lesson_indices(step, lessons)
        logits, _ = model([encoded[i] for i in indices])
        loss = torch.stack(
            [
                -torch.logsumexp(p.log_softmax(-1)[lessons[i]["answers"]], dim=0)
                for p, i in zip(logits, indices)
            ]
        ).mean()
        if not torch.isfinite(loss):
            raise FloatingPointError("Nonfinite tactical loss")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5, error_if_nonfinite=True)
        optimizer.step()
        emit(event="tactical_progress", done=step + 1, total=steps, loss=float(loss.detach()))
    return dict(
        version=VERSION,
        completed=steps,
        lessons=len(lessons),
        assessment_before=before,
        assessment_after=assess(model, encoder),
    )


def assess(model, encoder, *, lessons=None):
    """Static lesson accuracy, not a strength benchmark; never updates weights."""
    lessons = build_lessons() if lessons is None else lessons
    hits = 0
    mass = 0.0
    by_kind = {}
    model.eval()
    with torch.no_grad():
        for lesson in lessons:
            logits, _ = model([encoder.encode(lesson["decision"])])
            p = logits[0].softmax(-1)
            correct = int(int(p.argmax()) in lesson["answers"])
            hits += correct
            mass += float(p[lesson["answers"]].sum())
            row = by_kind.setdefault(lesson["kind"], dict(correct=0, total=0))
            row["correct"] += correct
            row["total"] += 1
    return dict(
        version=VERSION,
        split="assessment",
        correct=hits,
        total=len(lessons),
        accuracy=hits / len(lessons),
        mean_answer_probability=mass / len(lessons),
        by_kind=by_kind,
    )
