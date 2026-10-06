# Hero maximum Health

Candidate players now store maximum Health (default 30). Healing and random healing respect this value. Story of Amara sets current and maximum Health to 40, preserves Armor, and does not count as healing. Repeated casts reset the value.

Reference: https://hearthstone.wiki.gg/wiki/Story_of_Amara and the matching set-Health mechanic documented at https://hearthstone.wiki.gg/wiki/Amara%2C_Warden_of_Hope . Applying the same mechanic to Story is an inference; no independent client trace has certified it. Layered maximum-Health enchantments and hero replacement remain unverified.

Visible feature schema v6 includes public maximum Health and personal turn counts, plus target hero maximum Health. Old checkpoints intentionally reject the changed schema. This does not establish full Standard readiness or optimal play.
