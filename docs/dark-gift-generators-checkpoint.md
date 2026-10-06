# All-card queue and remaining Dark Gift generators — October 5, 2026

The all-card queue replaces the fixed 60-card delivery constraint. It covers all 317 pending collectibles and retains unresolved selectors, token identities and dependency cycles. Priority scores estimate reuse relative to implementation effort; they are not time estimates. Regenerate with `tools/build_completion_queue.py --engine-root staging/rebased-88` from the project directory. Nine queue checks cover selector rejection, graph cycles, complete accounting and deterministic output.

## Executable staging

`expanded/dark_gift_generators.py` contains the shared runtime and declarations for all 12 pending Dark Gift generators: Treacherous Tormentor, Creature of Madness, Darkrider, Avant-Gardening, Rite of Atrocity, Jumpscare!, Brutish Endmaw, Wings of Eternity, Cremate, Smoke Bomb, Shadowflame Stalker and Shadowflame Suffusion.

Shared behavior includes distinct eligible gifts, chooser-visible offers, source exclusion, conditional Dragon requirements, Corpse payment, cost modification, copies and shuffling unchosen offers. Complete pool contracts are checked before payment or card removal. Historical discovery requires an explicit historical contract and rejects Standard collectibles and noncollectible tokens. Missing outcomes fail closed.

These declarations are **not live registrations**. Coverage remains 868 live and 317 pending. Thirty-five controlled-pool tests validate the runtime, not production outcome membership. Complete pools and generated dependencies remain blockers. Historical membership review may introduce additional non-Standard outcomes beyond the 317 pending Standard collectibles.

## Live fixes

Dark Gift options now expose their gift to the choosing player, while opponents retain the waiting view. Schema v34 marks this observation change. Aviana's permanent cost setting now explicitly survives play, rather than being consumed like a one-use discount; the entity-effect suite has 46 passing checks including consecutive paid plays.

## Evidence limits and admission gates

The frozen catalog supplies printed card text. Existing Constructed gift definitions follow [Blizzard's 32.2 patch notes](https://news.blizzard.com/en-gb/article/24198086/32-2-patch-notes). Discover source exclusion is documented by the [Discover reference](https://hearthstone.wiki.gg/wiki/Discover).

Jumpscare gift retention and shuffle ordering have community reports, including [gift-retention discussion](https://us.forums.blizzard.com/en/hearthstone/t/jumpscare-doesnt-give-a-minion-and-drawn-minnions-bug/143761) and [later ordering discussion](https://www.reddit.com/r/hearthstone/comments/1rxdqcr/dark_gift_top_of_deck_didnt_work/). These are limited evidence, not independent client traces. Stalker's Sweet Dreams copy zone behavior and related Wallow interactions also remain conformance-review items.

Admission requires complete reviewed membership, all outcomes executable, integration hooks, behavioral regression and review of these timing/zone questions. Passing synthetic tests alone never enables a card or permits a truncated outcome pool. Learning and deck search remain separate later gates.

## Consolidated validation

2,953 full-suite checks passed with zero failures/errors/skips and unchanged fingerprint `a5567c8f8cf8b837fc5307f54da66b040ffcb64320dd08102c81048710965934`. All 22 smoke games finished without errors/caps and checked 2,508 feature decisions using the same source. Receipts and detailed log are linked from the [candidate status](../staging/rebased-88/STATUS.md).
