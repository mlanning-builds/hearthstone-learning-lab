# Resumable minion post-play checkpoints

The candidate now finishes three explicit stages in order: summon reactions; minion-play reactions; after-card Secret checks. Each stage settles its queued work before the next one begins. A choice pauses the sequence; its cursor resumes once. The private frame is covered by the existing full-state rollback and terminal cleanup.

Previously `_after_play` queued summon and played notifications, then immediately invoked after-card Secrets before settling those queues. Rat Trap could therefore create a target before a previously queued summon-damage reaction selected its target. This update removes that internal queue overtaking according to the candidate's explicit phase contract. It does not certify every Hearthstone cross-trigger timing rule.

Eleven checks are prepared for stage order, Secrets observing completed reactions, single/multiple choices, terminal outcomes, Rat Trap firing once, rollback/retry, history accounting, spell-counter isolation and private frame state. Synthetic listeners deliberately isolate scheduling; they do not add collectible cards or claim legal deck combinations. Run notebook 13 locally. No simulator checks were executed by the assistant.

Card inventory remains 506 written / 679 missing. The previous passing receipt with 1,136 checks is historical after this edit.

## Remaining scope

Individual summons inside an effect's Python loop still queue at that operation's checkpoint; this update does not insert unverified death processing after every summon. General nested card-effect frames, recursive summon compensation, timestamp ordering across Secret/listener types, self-transformation and independent pinned-build traces remain outstanding. The new fidelity gap `minion_postplay_phase_contract` records this limitation. This is one working part of the event-system milestone, not completion of that milestone.

Primary historical evidence: Blizzard's Update 11.2 describes changes to when summon/play trigger eligibility is evaluated: https://news.blizzard.com/en-us/article/21802981/update-11-2-june-5 . It distinguishes eligibility from later execution, but does not alone establish all build-251952 Secret/multi-summon ordering. No broader conformance claim is derived from it. The earlier pinned Fireplace source review provides an architectural comparison, not a current game oracle.
