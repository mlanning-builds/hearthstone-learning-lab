"""Returned tokens retain physical payloads and reject known incomplete pools."""
import unittest
from copy import deepcopy
from expanded import Game,Action,random_deck
from expanded.cards import registry,COLLECTIBLE_IDS
from expanded.permanents import PERMANENT_IDS
from engine.cards import UnsupportedCard

class ReturnedTokenTests(unittest.TestCase):
    def test_registered_minions_can_return_to_hand_and_be_replayed(self):
        # Zero-Health templates require construction-specific fixtures.
        # Raw MINION records also encode untouchable board objects, which cannot
        # enter a hand or be played as minions; their lifecycle is tested separately.
        ids=sorted(cid for cid,c in registry().items() if c['type']=='MINION'
                   and not c.get('collectible') and c.get('health',0)>0
                   and cid not in COLLECTIBLE_IDS and cid not in PERMANENT_IDS and cid!='GDB_100t1')
        self.assertGreater(len(ids),20)
        prototype=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        prototype.step(Action('mulligan'));prototype.step(Action('mulligan'))
        for cid in ids:
            with self.subTest(card=cid):
                g=deepcopy(prototype)
                p=g.players[0];p.hand=[];p.mana=p.max_mana=10
                payload=None
                if cid in ('CATA_470t1','ICC_828t'):
                    from expanded.minion_forge import ForgePart
                    part=ForgePart('CS2_182',source='returned-token fixture')
                    g._forge_choice(dict(kind='forge_part',forge_kind='dragon' if cid=='CATA_470t1' else 'zombeast',owner=0,discount=0,first=part,parts=[part]),dict(card_id=part.card_id))
                    payload=p.hand.pop()
                elif cid.startswith('BAR_079_m'):
                    from expanded.historical_golem_crafting import BODIES,resolve_choice
                    tier=next(tier for tier,body in BODIES.items() if body==cid)
                    resolve_choice(g,dict(kind='historical_golem_power',owner=0,tier=tier,keyword='BAR_079t5'),dict(power='wildvine'))
                    payload=p.hand.pop()
                elif cid=='DAL_431t':
                    from expanded.historical_horror_crafting import resolve_choice
                    spell='CORE_CS2_053'
                    self.assertTrue(g._supports_internal_spell(spell))
                    resolve_choice(g,dict(kind='historical_horror_teach',owner=0,first=spell,modes={spell:'none'}),dict(card_id=spell))
                    payload=p.hand.pop()
                m=g._summon(0,cid,entry_source=payload,entry_stats=getattr(payload,'base_stat_override',None));self.assertIsNotNone(m)
                if cid in ('MEND_046t','TIME_704t','TOY_504t','TSC_052t'):m._learned_spell='CORE_CS2_029'
                if m.dormant:
                    g._bounce(m)
                    self.assertEqual(p.hand,[])
                    self.assertIn(m,p.board)
                    g._awaken(m)
                g._bounce(m);card=p.hand[0]
                # Exercise play dispatch independent of unusually expensive tokens.
                card.cost_delta=-g.cards[cid]['cost']
                action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid)
                g.step(action);g.assert_invariants()
                if cid in ('MEND_046t','TIME_704t','TOY_504t','TSC_052t'):
                    self.assertEqual(getattr(card,'_learned_spell',None),'CORE_CS2_029')
                if cid=='TIME_875t':
                    self.assertFalse(any(x.card_id==cid for x in p.all_minions))
                    self.assertTrue(any(g._card_data(x)['id']==cid for x in p.deck))
                else:self.assertTrue(any(x.card_id==cid for x in p.all_minions))
                if m.card_id in ('EDR_416t','EDR_840t','EDR_840t1','EDR_840t2'):
                    self.assertTrue(next(x for x in p.all_minions if x.card_id==cid).dormant)
                self.assertFalse(any(c.uid==card.uid for c in p.hand))
