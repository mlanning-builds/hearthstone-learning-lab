# Nested, opponent-side and aura bindings

Thirteen additional historical collectible bodies are written, bringing the total to 412. Standard remains 896/1,185. Fixed generated records do not approve any historical generation pool.

Splitting Spacerock, Splitting Festeroot and Lingering Zombie have explicit intermediate and final child bodies. Their recursive Deathrattles resolve through ordinary effect frames and stop at printed terminal bodies. Board limits apply at each generation. The Beast and Saronite Taskmaster use the existing opponent-summon operation, preserving the recipient controller and appending at that controller's battlefield end. The dependency scanner now recognizes this operation's literal child reference.

Six stat aura providers, Robes of Protection and Houndmaster Shaw bind frozen text to shared continuous rules. Shaw required an explicit `others` scope for keyword auras: it excludes each provider from its own grant, while two active providers grant Rush to each other. Derived keywords remain outside stored enchantments and copied intrinsic state. Silence, Dormant sources, controller changes and disappearance use active provider checks. Mal'Ganis uses the existing hero immunity rule and other-Demon stat aura.

Ninety-eight focused checks passed after application, including the surrounding shared-system and dependency checks. Initial validation included a misspelled test-module name; the corrected complete group passed. Full changed-source regression is still required. The preceding 4,664-check receipt applies to the 399-body fingerprint. No training or notebook cells were executed.

The 4,685-check full run found four assertions in an older generic fixture that incorrectly assumed intermediate generated bodies had no Deathrattles. The fixture now checks the exact child identities for those four intermediates. That failed receipt is retained; a new full run is required for the corrected source.
