# Repeated minion plays

Twisted Webweaver (EDR_540) listens for another friendly minion being played whose canonical identity already appears in that player's play history. The minion-play event records a repetition Boolean after the current play has entered history; a count above one means there was a previous play. Identity follows the pinned `countAsCopyOfDbfId` field when present, falling back to dbfId or a local token ID. Summons do not enter play history.

Eight fixtures cover first/second/third plays, history predating the listener, summons, exclusion of the newly played Webweaver itself, Silence, opposing history, multiple listeners and a synthetic equivalent-ID record. The synthetic ID is test-only and is never registered in the catalog.

The existing event pipeline resolves these listeners after the played card's effects. General before/after-play phase fidelity and nested automatic play ordering remain unverified against the reference client. The pinned local record supplies the rule text; fixture passes are not full conformance evidence.
