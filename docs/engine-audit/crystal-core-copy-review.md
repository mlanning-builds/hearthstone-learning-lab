# Crystal Core physical copy repair

Six new ordinary-registry checks cover copies leaving a player with Crystal
Core. The complete 116-check Crystal Core, provenance, Dark Gift and Latorvius
focused group passes. A fresh full regression is required for the changed source.

Newly inserted deck minions can receive their owner's effective 5/5 base through
the stat accessor before the physical card stores an override. Copying these
cards to an opponent previously restored printed stats. Three new cases
reproduced the defect: a Latorvius reward inserted after Crystal Core, a raw deck
identity, and a physical card carrying separate bonuses and a cost discount.

The copy path now snapshots the known source owner's effective 5/5 base for
minions. It preserves separate attack/health bonuses, cost changes and copy
ancestry, creates a new physical identity, and leaves the source untouched.
Spells and copies from an owner without Crystal Core retain their existing bases.

This closes the tested physical-copy path; it does not settle every stat and
control transition. Dormant entry, explicit-stat copies, Reborn, scaling bodies,
stat swaps and damage-preservation ordering remain tracked fidelity gates.
