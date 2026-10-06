"""Combo snapshots and the cast spell's physical hand-center condition."""
import unittest
from expanded import Game,Action,random_deck
from engine.game import Card
from engine.cards import UnsupportedCard

class CastConditionsTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.health=30;p.mana=p.max_mana=10;p.cards_played=0
        return g
    def run_cast(self,g,op,owner=0,**extra):
        g._start_play_effects([op],dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False,**extra))
    def bribe(self,g,owner=0,**extra):
        g._summon(1-owner,'AT_037t')
        self.run_cast(g,('cast_fixed_spell','CATA_EVENT_402','random'),owner,**extra)
    def test_combo_requires_previous_completed_card(self):
        for count in (0,1):
            with self.subTest(count=count):
                g=self.game();g.players[0].cards_played=count;self.bribe(g)
                self.assertEqual(len(g.players[0].hand),count)
                self.assertEqual([c.card_id for c in g.players[1].hand],['TOKEN_COIN'])
                self.assertEqual(g.players[0].cards_played,count)
    def test_explicit_false_snapshot_survives_root_card_count(self):
        g=self.game();g.players[0].cards_played=1;self.bribe(g,combo=False)
        self.assertFalse(g.players[0].hand)
    def test_explicit_true_snapshot_remains_active(self):
        g=self.game();self.bribe(g,combo=True);self.assertEqual(g.players[0].hand[0].card_id,'TOKEN_COIN')
    def test_offturn_old_counter_cannot_activate_combo(self):
        g=self.game();g.players[1].cards_played=4;self.bribe(g,1)
        self.assertFalse(g.players[1].hand);self.assertEqual(g.players[0].hand[0].card_id,'TOKEN_COIN')
    def test_internal_cast_does_not_enable_combo_for_next_cast(self):
        g=self.game();self.bribe(g);self.bribe(g)
        self.assertFalse(g.players[0].hand);self.assertEqual(len(g.players[1].hand),2)
    def test_generated_shot_does_not_inherit_caster_hand_center(self):
        g=self.game();self.run_cast(g,('cast_fixed_spell','TIME_600','enemies'),hand_center=True)
        self.assertEqual(g.players[1].health,27)
    def test_hand_center_uses_actual_spell_before_consumption(self):
        for size,index,damage in [(1,0,5),(3,1,5),(3,0,3),(3,2,3),(2,0,3),(2,1,3)]:
            with self.subTest(size=size,index=index):
                g=self.game();hand=[g._add(0,'TOKEN_COIN') for _ in range(size)]
                hand[index].card_id='TIME_600';c=hand[index]
                self.run_cast(g,('cast_zone_spell','hand',c.uid,'enemies'))
                self.assertEqual(g.players[1].health,30-damage);self.assertNotIn(c,g.players[0].hand)
    def test_deck_spell_does_not_use_deck_center(self):
        g=self.game();c=Card(g._new_id(),'TIME_600');g.players[0].deck=[c]
        self.run_cast(g,('cast_zone_spell','deck',c.uid,'enemies'));self.assertEqual(g.players[1].health,27)
    def test_detached_card_has_no_inferred_hand_position(self):
        g=self.game();c=Card(g._new_id(),'TIME_600')
        self.run_cast(g,('cast_physical_spell',c,'enemies'),hand_center=True)
        self.assertEqual(g.players[1].health,27)
    def test_untransformed_shadow_is_still_rejected(self):
        g=self.game()
        with self.assertRaises(UnsupportedCard):self.run_cast(g,('cast_fixed_spell','CORE_RLK_567','random'))
    def test_generated_self_damage_spells_hit_cast_owner(self):
        for cid,amount in [('JAIL_443t',2),('TIME_025t',3)]:
            with self.subTest(cid=cid):
                g=self.game();self.run_cast(g,('cast_fixed_spell',cid,'random'),owner=1)
                self.assertEqual(g.players[1].health,30-amount);self.assertEqual(g.players[0].health,30)
    def test_quest_reward_spell_applies_persistent_murloc_bonus(self):
        g=self.game();self.run_cast(g,('cast_fixed_spell','TLC_426t','random'))
        self.assertEqual(g.players[0].murloc_summon_bonus,1)
    def test_permanent_reward_obeys_board_capacity(self):
        for full in (False,True):
            with self.subTest(full=full):
                g=self.game()
                if full:
                    for _ in range(7):g._summon(0,'AT_037t')
                self.run_cast(g,('cast_fixed_spell','TLC_446t','random'))
                self.assertEqual(len(g.players[0].permanents),0 if full else 1)
    def test_relation_health_spell_uses_actual_target_owner(self):
        for owner,bonus in [(0,2),(1,-2)]:
            with self.subTest(owner=owner):
                g=self.game();m=g._summon(owner,'CS3_020');before=m.health
                self.run_cast(g,('cast_fixed_spell','TLC_813','random'))
                self.assertEqual(m.health,before+bonus)
