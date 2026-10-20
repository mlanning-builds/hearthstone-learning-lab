# Spirit of the Mountain assignment review

The staged implementation greedily chooses one unused type when each minion is played. It forgets the other types on a dual-type minion, so a later single-type minion can leave progress below the feasible number of unique types. It also unnecessarily consumes random state for a bookkeeping assignment.

The repair snapshots every typed minion play and computes a maximum matching between plays and printed minion types. A minion counts at most once; each type counts at most once. Prior dual-type or ALL minions can move to another type to accommodate a later play. Progress is capped at the quest target so a full-hand deferred reward cannot be stranded by additional typed plays. This is deterministic bookkeeping, not a random outcome pool.

A [July 6 player report](https://us.forums.blizzard.com/en/hearthstone/t/spirit-of-the-mountain-quest-is-bugged/148461) directly describes the confusing multi-type progression. The explanation in its replies describes maximum reassignment. These observations motivate the repair; they are not developer confirmation or a frozen-client trace. The pure matching helper was checked against an independent exhaustive assignment oracle for 3,615 short sequences over four types.

The reward remains a separate behavior review. The [official Adapt designer explanation](https://news.blizzard.com/en-us/article/20659256/hearthside-chat-adapt-in-un-goro-with-dean-ayala) establishes three choices from ten possible enhancements. Local tests must cover all ten applications, persistent grant stacking, source removal, Silence, timed Stealth, repeated choices and played-versus-summoned minions. No random collectible pool is required. Independent event timing and copied/repeated reward behavior remain fidelity questions.

The staged grant hook now explicitly rejects Dormant played-minion timing instead of silently dropping grants. This unresolved interaction is an admission gate, not an invented approximation.
