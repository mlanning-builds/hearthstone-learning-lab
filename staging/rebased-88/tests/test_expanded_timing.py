"""User-run damage/checkpoint regressions; synthetic hooks are labeled below."""
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.cards import TRIGGERS


class TimingTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        self.p.hand=[];self.q.hand=[]
        self.p.mana=self.p.max_mana=10
        self.p.deck=['CORE_CS2_029']*5
        self.q.deck=['CORE_CS2_029']*5
        self.ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)

    def test_nested_trigger_checkpoint_keeps_lethal_damage_listener(self):
        self.g._summon(0,'CORE_EX1_604')
        acolyte=self.g._summon(0,'CORE_EX1_007')
        # Synthetic trigger invokes a helper with an internal settle checkpoint.
        hook=('damaged_minion',[('missiles','enemies',1)])
        start=len(self.g.events)
        with patch.dict(TRIGGERS,{'CORE_EX1_604':hook}):
            self.g._damage(acolyte.uid,99)
            self.g._settle()
        self.assertEqual(len(self.p.hand),1)
        self.assertNotIn(acolyte,self.p.board)
        self.assertEqual(self.q.health,29)
        self.assertFalse(self.g._rule_events)
        events=[e['event'] for e in self.g.events[start:]]
        self.assertLess(events.index('draw'),events.index('death'))

    def test_nested_batches_defer_deaths_until_outer_checkpoint(self):
        m=self.g._summon(0,'CORE_EX1_096')
        with self.g._damage_batch():
            with self.g._damage_batch():
                self.g._damage(m.uid,99);self.g._settle()
                self.assertIn(m,self.p.board)
            self.g._settle()
            self.assertIn(m,self.p.board)
            self.assertEqual(self.p.hand,[])
        self.g._settle()
        self.assertNotIn(m,self.p.board)
        self.assertEqual(len(self.p.hand),1)
        self.assertEqual(self.g._damage_batch_depth,0)

    def test_batch_depth_restores_on_exception(self):
        with self.assertRaisesRegex(RuntimeError,'fixture'):
            with self.g._damage_batch():
                with self.g._damage_batch():raise RuntimeError('fixture')
        self.assertEqual(self.g._damage_batch_depth,0)
        m=self.g._summon(0,'CORE_EX1_096');m.health=0
        self.g._settle()
        self.assertNotIn(m,self.p.board)

    def test_simultaneous_hero_lethal_is_draw(self):
        with self.g._damage_batch():
            self.g._damage(-1,30);self.g._settle()
            self.assertFalse(self.g.terminal)
            self.g._damage(-2,30)
        self.g._settle()
        self.assertTrue(self.g.terminal)
        self.assertIsNone(self.g.winner)

    def test_combat_deals_both_hits_before_deathrattle_draws(self):
        a=self.g._summon(0,'CORE_EX1_096');b=self.g._summon(1,'CORE_EX1_096')
        a.summoned_turn=-1
        start=len(self.g.events)
        self.g.step(Action('attack',a.uid,b.uid))
        events=self.g.events[start:]
        hits=[i for i,e in enumerate(events) if e['event']=='damage']
        deaths=[i for i,e in enumerate(events) if e['event']=='death']
        self.assertEqual(len(hits),2);self.assertEqual(len(deaths),2)
        self.assertLess(max(hits),min(deaths))
        self.assertEqual((len(self.p.hand),len(self.q.hand)),(1,1))

    def test_area_damage_finishes_hits_before_removals(self):
        a=self.g._summon(0,'CORE_EX1_096');b=self.g._summon(1,'CORE_EX1_096')
        start=len(self.g.events)
        self.g._effect(('area_damage','all_minions',2),self.ctx)
        self.g._settle()
        events=self.g.events[start:]
        hits=[i for i,e in enumerate(events) if e['event']=='damage']
        deaths=[i for i,e in enumerate(events) if e['event']=='death']
        self.assertEqual(len(hits),2);self.assertEqual(len(deaths),2)
        self.assertLess(max(hits),min(deaths))
        self.assertEqual((len(self.p.hand),len(self.q.hand)),(1,1))

    def test_missiles_resolve_deathrattle_between_shots(self):
        cairne=self.g._summon(1,'CORE_EX1_110');cairne.health=1
        self.g._effect(('missiles','enemy_minions',2),self.ctx)
        self.g._settle()
        self.assertEqual(len(self.q.board),1)
        baine=self.q.board[0]
        self.assertEqual(baine.card_id,'TOKEN_BAINE')
        self.assertEqual(baine.health,self.g.cards['TOKEN_BAINE']['health']-1)

    def test_deathrattle_uses_last_slot_before_reborn(self):
        m=self.g._summon(0,'CORE_AV_337')
        m.keywords.add('REBORN')
        for _ in range(6):self.g._summon(0,'Core_CS2_200')
        m.health=0
        self.g._settle()
        self.assertEqual(len(self.p.board),7)
        self.assertFalse(any(x.card_id==m.card_id for x in self.p.board))
        self.assertEqual(sum(x.card_id=='AV_337t' for x in self.p.board),1)
