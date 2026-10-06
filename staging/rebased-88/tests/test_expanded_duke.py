import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class DukeTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARLOCK',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        for p in self.g.players:p.hand=[];p.deck=[];p.mana=p.max_mana=10
    def discard(self,owner=0):
        c=Card(self.g._new_id(),'CORE_CS2_029');self.g.players[owner].hand.append(c)
        self.g._discard_card(owner,c)
    def test_past_and_future_discards_scale_without_healing_damage(self):
        self.discard();m=self.g._summon(0,'CATA_493')
        self.assertEqual((m.attack,m.health),(4,4))
        self.g._damage(m.uid,1);self.discard()
        self.assertEqual((m.attack,m.health,m.max_health),(6,5,6))
        self.g._refresh_auras();self.assertEqual(m.health,5)
    def test_silence_removes_scaling_and_rush(self):
        self.discard();m=self.g._summon(0,'CATA_493');self.g._silence(m);self.discard()
        self.assertEqual((m.attack,m.health,m.max_health),(2,2,2));self.assertNotIn('RUSH',m.keywords)
    def test_other_owner_discard_does_not_buff(self):
        m=self.g._summon(0,'CATA_493');self.discard(1)
        self.assertEqual((m.attack,m.health),(2,2))
    def test_copy_does_not_double_dynamic_bonus(self):
        self.discard();m=self.g._summon(0,'CATA_493');self.g._buff(m,1,1)
        copy=self.g._summon(0,'CATA_493',copy_from=m)
        self.assertEqual((copy.attack,copy.health),(5,5))
        self.discard();self.assertEqual((m.attack,copy.attack),(7,7))
    def test_hand_view_and_filter_include_dynamic_stats(self):
        self.discard();c=Card(self.g._new_id(),'CATA_493');self.p.hand.append(c)
        view=self.g.observe(0)['players'][0]['hand'][0]
        self.assertEqual((view['attack'],view['health']),(4,4))
        self.assertTrue(self.g._matches_filter(c,(('attack','ge',4),),hand_owner=0))
    def test_deck_stat_filter_uses_owner_history(self):
        self.discard();self.p.deck=['CATA_493']
        drawn=self.g._draw_filtered(0,(('attack','ge',4),))
        self.assertEqual(drawn.card_id,'CATA_493')
    def test_stat_setting_retains_continuous_bonus(self):
        self.discard();m=self.g._summon(0,'CATA_493')
        self.g._effect(('set_target_stats',3,3),dict(owner=0,source=None,target=m.uid,bonus=0,lifesteal=False))
        self.g._refresh_auras();self.assertEqual((m.attack,m.health),(5,5))
