# After playing a Battlecry minion

Gallagio Goon (JAIL_802) uses a shared minion-mechanic play matcher and a buff operation targeting the event's played entity. It does not trigger from direct summons or opponent plays. The current after-play phase follows the resolved Battlecry and any pending choice. Missing/dead source entities are not recreated by the buff.

Pinned JAIL_802 metadata supplies the Battlecry selector and +1/+1 effect. Tests cover Battlecry resolution, summon exclusion, wrong owner/type, multiple listeners, Silence and absent source. This is not independent validation of all transformation/control-change and simultaneous trigger cases.
