"""Normal-registry entry, death, opening-deck and paid-action scenarios."""
import unittest
import test_expanded_generation as fixtures
from expanded import Game, Action, cards
from expanded.decks import Deck, eligible, validate
from expanded.fabled_decks import BUNDLES

class FixedStandardAdmissionTests(unittest.TestCase):
    def game(self):
        return fixtures.GenerationTests().game()

    def play(self,g,cid,target=0):
        g.players[0].mana=g.players[0].max_mana=10
        card=g._add(0,cid)
        cost=g._cost(card,0)
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid and a.target==target))
        self.assertEqual(g.players[0].mana,10-cost)
        g.assert_invariants()
        return next(m for m in g.players[0].minions if m.card_id==cid)

    def deck(self,hero,root=None,kind=None):
        records=cards.registry()
        candidates=[cid for cid in sorted(cards.COLLECTIBLE_IDS)
                    if cid!=root and cid not in ('CS3_035','JAIL_800','JAIL_397','JAIL_430','REV_018','TIME_005')
                    and eligible(records[cid],hero,(0,0,0))
                    and (kind is None or records[cid]['type']==kind)
                    and 'QUEST' not in records[cid].get('mechanics',())
                    and cid not in BUNDLES]
        ids=[] if root is None else [root]
        for cid in candidates:
            limit=1 if records[cid].get('rarity')=='LEGENDARY' else 2
            ids.extend([cid]*min(limit,30-len(ids)))
            if len(ids)==30:break
        ids=tuple(ids)
        deck=Deck(hero,ids)
        self.assertEqual(validate(deck),[])
        return deck

    def test_all_seven_colossals_have_real_paid_entry_and_literal_limbs(self):
        expected={'CATA_139':['CATA_139t','CATA_139t2','CATA_139t3','CATA_139t4'],
                  'CATA_150':['CATA_150t','CATA_150t1'],
                  'CATA_151':['CATA_151t','CATA_151t1'],
                  'CATA_300':['CATA_300t1','CATA_300t2','CATA_300t3'],
                  'CATA_432':['CATA_432t1','CATA_432t2','CATA_432t3','CATA_432t4'],
                  'CATA_550':['CATA_550t','CATA_550t2','CATA_550t3','CATA_550t4','CATA_550t5','CATA_550t6'],
                  'CATA_726':['CATA_726t','CATA_726t1']}
        for cid,limbs in expected.items():
            with self.subTest(cid=cid):
                g=self.game();body=self.play(g,cid)
                children=[m for m in g.players[0].minions if m is not body]
                self.assertEqual([m.card_id for m in children],limbs)
                self.assertEqual(len({m.uid for m in [body]+children}),1+len(limbs))
                for m in children:
                    self.assertIn(m.card_id,cards.TOKEN_IDS)
                    self.assertNotIn(m.card_id,cards.COLLECTIBLE_IDS)

    def test_ragnaros_registered_end_triggers_appendage_deathrattles(self):
        g=self.game();self.play(g,'CATA_150');g.step(Action('end'))
        self.assertEqual(g.players[1].health,26)
        self.assertEqual(len(g.players[0].minions),3)

    def test_wickerfang_registered_end_gains_leg_stats(self):
        g=self.game();body=self.play(g,'CATA_139');before=body.attack,body.max_health
        g.step(Action('end'));self.assertEqual((body.attack,body.max_health),(before[0]+4,before[1]+4))

    def test_chromatus_registered_head_death_removes_matching_keyword(self):
        g=self.game();body=self.play(g,'CATA_432');head=next(m for m in g.players[0].minions if m.card_id=='CATA_432t4')
        self.assertIn('DIVINE_SHIELD',g._effective_keywords(body));head.health=0;g._settle()
        self.assertNotIn('DIVINE_SHIELD',g._effective_keywords(body));self.assertIn('TAUNT',g._effective_keywords(body))

    def test_magmaw_registered_death_replenishes_without_reusing_uid(self):
        g=self.game();body=self.play(g,'CATA_550');first=g.players[0].minions[1];old={m.uid for m in g.players[0].minions}
        first.health=0;g._settle();self.assertEqual(len(g.players[0].board),7)
        self.assertEqual(body.rule_state['colossal_remaining'],92);self.assertTrue({m.uid for m in g.players[0].minions}-old)

    def test_nozdormu_real_starting_decks_install_and_enforce_clock(self):
        deck=self.deck('WARRIOR','CS3_035');g=Game([deck,deck],seed=51)
        g.step(Action('mulligan'));g.step(Action('mulligan'));owner=g.current
        self.assertEqual(g.turn_time_limit,15);self.assertFalse(g.elapse_decision_time(14.9))
        self.assertTrue(g.elapse_decision_time(.1));self.assertEqual(g.current,1-owner)

    def test_single_nozdormu_does_not_enable_clock(self):
        g=Game([self.deck('WARRIOR','CS3_035'),self.deck('WARRIOR')],seed=52)
        self.assertIsNone(g.turn_time_limit)

    def test_mugzee_real_spell_deck_gets_only_mugs_passive(self):
        g=Game([self.deck('SHAMAN','JAIL_800','SPELL'),self.deck('WARRIOR')],seed=53)
        self.assertEqual(g.players[0].primary_power['card_id'],'JAIL_800hp1');self.assertIsNone(g.players[0].secondary_power)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        self.assertFalse(any(a.kind=='power' for a in g.legal_actions()))

    def test_mugzee_real_minion_deck_gets_only_zees_passive(self):
        g=Game([self.deck('SHAMAN','JAIL_800','MINION'),self.deck('WARRIOR')],seed=54)
        self.assertEqual(g.players[0].primary_power['card_id'],'JAIL_800hp2')
        self.assertIsNone(g.players[0].secondary_power)

if __name__=='__main__':unittest.main()
