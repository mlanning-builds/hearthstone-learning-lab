"""Candidate shared Colossal entry machinery; no collectible admission.

Layouts use the frozen source inventory's explicit limb identities and left
markers. Position/notification ordering still needs independent client traces.
Magmaw uses a finite, per-entity replenishment queue. Army scaling lives in the staged Herald
module; no layout grants complete card support.
"""
from engine.cards import UnsupportedCard

# Ordered (card identity, side). Never infer playable dependencies from prefixes.
LAYOUTS = {
    'CATA_139': tuple((cid, 'right') for cid in ('CATA_139t','CATA_139t2','CATA_139t3','CATA_139t4')),
    'CATA_150': (('CATA_150t','left'), ('CATA_150t1','right')),
    'CATA_151': (('CATA_151t','right'), ('CATA_151t1','right')),
    'CATA_153': (('CATA_153t','right'), ('CATA_153t1','right')),
    'CATA_154': (('CATA_154t','right'), ('CATA_154t1','right')),
    'CATA_155': (('CATA_155t','right'), ('CATA_155t1','right')),
    'CATA_300': tuple((cid,'right') for cid in ('CATA_300t1','CATA_300t2','CATA_300t3')),
    'CATA_432': tuple((cid,'right') for cid in ('CATA_432t1','CATA_432t2','CATA_432t3','CATA_432t4')),
    'CATA_488': (('CATA_488t','right'), ('CATA_488t2','right')),
    'CATA_550': tuple((('CATA_550t' if i%6==0 else 'CATA_550t'+str(i%6+1)), 'right') for i in range(99)),
    'CATA_726': (('CATA_726t','right'), ('CATA_726t1','right')),
}

class ColossalEntries:
    def _colossal_preflight(self, cid, *, owner=None, copy_from=None, dormant_turns=None):
        record = self.cards.get(cid, {})
        if cid not in LAYOUTS:
            if cid == 'CATA_550' or 'COLOSSAL' in record.get('mechanics', ()):
                raise UnsupportedCard('Colossal entry needs an explicit layout/replenishment rule: '+cid)
            return
        if dormant_turns or (copy_from is not None and (copy_from.dormant or copy_from.silenced)):
            raise UnsupportedCard('Colossal dormant/silenced-copy entry requires reviewed semantics')
        # Validate every dependency before creating the body, even on a full board.
        for limb, side in LAYOUTS[cid]:
            if owner is not None:self._herald_entry_preflight(owner,limb)
            if side not in ('left','right'):
                raise UnsupportedCard('Unknown Colossal appendage position')
            if limb in LAYOUTS or limb == cid:
                raise UnsupportedCard('Recursive Colossal appendage layout')
            if self.cards.get(limb, {}).get('type') != 'MINION':
                raise UnsupportedCard('Missing Colossal appendage: '+limb)
            if 'COLOSSAL' in self.cards[limb].get('mechanics', ()):
                raise UnsupportedCard('Recursive Colossal appendage dependency')

    def _colossal_enter(self, body):
        if body is None or body.card_id not in LAYOUTS:
            return
        board = self.players[body.owner].board
        # Never inherit links from a copied parent. Each entry owns fresh limbs.
        body.rule_state['colossal_appendages'] = []
        if body.card_id=='CATA_550':
            body.rule_state['colossal_remaining']=99
            self._colossal_refill(body)
            return
        right_anchor = body
        for cid, side in LAYOUTS[body.card_id]:
            if len(board) >= 7 or body not in board:
                break
            position = board.index(body) if side == 'left' else board.index(right_anchor) + 1
            limb = self._summon(body.owner, cid, position, entry_origin='colossal',
                                entry_site='colossals.entry', entry_source=body)
            if limb is not None:
                limb.rule_state['colossal_parent'] = body.uid
                body.rule_state['colossal_appendages'].append(limb.uid)
                if side == 'right':
                    right_anchor = limb

    def _colossal_refill(self,body):
        board=self.players[body.owner].board
        if body not in self.players[body.owner].minions or body.health<=0 or body.silenced:return False
        changed=False
        while len(board)<7 and body.rule_state.get('colossal_remaining',0)>0:
            remaining=body.rule_state['colossal_remaining']
            cid,side=LAYOUTS['CATA_550'][99-remaining]
            # Consume before callbacks; nested entry cannot duplicate a slot.
            body.rule_state['colossal_remaining']=remaining-1
            own=[m for m in board if getattr(m,'rule_state',{}).get('colossal_parent')==body.uid]
            anchor=own[-1] if own else body
            limb=self._summon(body.owner,cid,board.index(anchor)+1,entry_origin='colossal',
                              entry_site='colossals.refill',entry_source=body)
            if limb is None:
                body.rule_state['colossal_remaining']=remaining
                break
            limb.rule_state['colossal_parent']=body.uid
            body.rule_state['colossal_appendages'].append(limb.uid)
            changed=True
        return changed

    def _colossal_space_checkpoint(self):
        changed=False
        for body in sorted([m for p in self.players for m in p.minions
                            if m.card_id=='CATA_550'],key=lambda m:m.uid):
            changed=self._colossal_refill(body) or changed
        return changed
