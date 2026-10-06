"""Replacement identity, costs, usage, reversible state, and summon refresh."""
import copy
import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.features import SCHEMA,encode_decision
from expanded.selectors import has_tribe

class ReplacementPowersTests(unittest.TestCase):
    def game(self,hero='MAGE'):
        g=Game([random_deck(hero,1),random_deck('HUNTER',2)],seed=83)
        g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.health=30;p.armor=0;p.power_used=False
        return g
    def play(self,g,cid):
        c=g._enter_hand(0,Card(g._new_id(),cid))
        g.players[0].mana=10
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def use(self,g):g.step(Action('power'))
    def star(self,g):self.play(g,'JAIL_EVENT_101')
    def demon(self,g,owner=0):return g._summon(owner,'EX1_tk34')
    def test_jaraxxus_preserves_health_and_adds_armor(self):
        g=self.game();g.players[0].health=11;g.players[0].max_health=40;g.players[0].armor=7
        self.play(g,'CORE_EX1_323');p=g.players[0]
        self.assertEqual((p.health,p.max_health,p.armor),(11,40,12));self.assertEqual(p.hero_class,'WARLOCK')
    def test_jaraxxus_equips_blood_fury(self):
        g=self.game();self.play(g,'CORE_EX1_323');w=g.players[0].weapon
        self.assertEqual((w['card_id'],w['attack'],w['durability']),('EX1_323w',3,8))
    def test_jaraxxus_is_not_cast_as_spell(self):
        g=self.game();self.play(g,'CORE_EX1_323');self.assertEqual(g.players[0].spells_turn,[])
        self.assertEqual(g.players[0].played_history[-1]['card_id'],'CORE_EX1_323')
    def test_inferno_summons_reviewed_six_six(self):
        g=self.game();self.play(g,'CORE_EX1_323');self.use(g)
        m=g.players[0].minions[0];self.assertEqual((m.card_id,m.attack,m.health),('EX1_tk34',6,6))
        self.assertEqual(g.players[0].health,30);self.assertFalse(g.players[0].hand)
    def test_inferno_full_board_unavailable(self):
        g=self.game();self.play(g,'CORE_EX1_323')
        for _ in range(7):g._summon(0,'EDR_851t')
        self.assertFalse(any(a.kind=='power' for a in g.legal_actions()))
    def test_replacement_not_targeted_like_old_mage_power(self):
        g=self.game();self.star(g)
        self.assertEqual([a for a in g.legal_actions() if a.kind=='power'],[Action('power')])
    def test_star_cost_and_damage(self):
        g=self.game();self.star(g);mana=g.players[0].mana;self.use(g)
        self.assertEqual(g.players[0].mana,mana-1);self.assertEqual(g.players[1].health,28)
    def test_star_upgrade_does_not_refresh_used_power(self):
        g=self.game();self.star(g);self.use(g);self.star(g)
        self.assertEqual(g.players[0].primary_power['damage'],3);self.assertTrue(g.players[0].power_used)
    def test_star_upgrade_increases_next_damage(self):
        g=self.game();self.star(g);self.star(g);self.use(g)
        self.assertEqual(g.players[1].health,27)
    def test_new_power_refreshes_previous_used_power(self):
        g=self.game('WARRIOR');g.step(Action('power'));self.star(g)
        self.assertIn(Action('power'),g.legal_actions())
    def test_power_once_per_turn_until_refreshed(self):
        g=self.game();self.star(g);self.use(g)
        self.assertNotIn(Action('power'),g.legal_actions());self.demon(g);self.assertIn(Action('power'),g.legal_actions())
    def test_enemy_demon_does_not_refresh(self):
        g=self.game();self.star(g);self.use(g);self.demon(g,1);self.assertTrue(g.players[0].power_used)
    def test_non_demon_does_not_refresh(self):
        g=self.game();self.star(g);self.use(g);g._summon(0,'EDR_851t');self.assertTrue(g.players[0].power_used)
    def test_failed_full_board_summon_does_not_refresh(self):
        g=self.game();self.star(g)
        for _ in range(7):g._summon(0,'EDR_851t')
        self.use(g);self.assertIsNone(self.demon(g));self.assertTrue(g.players[0].power_used)
    def test_played_demon_refreshes_after_play(self):
        g=self.game();self.star(g);self.use(g);self.play(g,'EX1_tk34')
        self.assertFalse(g.players[0].power_used)
    def test_summon_notification_does_not_refresh_replaced_power(self):
        g=self.game();self.star(g);m=g._summon(0,'EX1_tk34',entry_origin='play')
        self.play(g,'TLC_632');self.use(g);g._publish_pending_summon(m)
        self.assertTrue(g.players[0].power_used)
    def test_same_name_new_instance_does_not_receive_old_refresh(self):
        g=self.game();self.star(g);m=g._summon(0,'EX1_tk34',entry_origin='play')
        g._replace_primary_power(0,dict(card_id='JAIL_EVENT_101hp',damage=2));self.use(g)
        g._publish_pending_summon(m);self.assertTrue(g.players[0].power_used)
    def test_sulfuras_eight_damage_and_use_count(self):
        g=self.game('WARRIOR');self.play(g,'TLC_632');self.use(g)
        self.assertEqual(g.players[1].health,22);self.assertEqual(g.players[0].primary_power['remaining'],1)
        self.assertEqual(g.players[0].primary_power['card_id'],'TLC_632t2')
    def test_sulfuras_restores_base_power_after_second_use(self):
        g=self.game('WARRIOR');self.play(g,'TLC_632');self.use(g);g.players[0].power_used=False;self.use(g)
        self.assertIsNone(g.players[0].primary_power);self.assertEqual(g.players[1].health,14)
        g.players[0].mana=2;self.use(g);self.assertEqual(g.players[0].armor,2)
    def test_sulfuras_restores_upgraded_star(self):
        g=self.game();self.star(g);self.star(g);self.play(g,'TLC_632');self.use(g)
        g.players[0].power_used=False;self.use(g)
        self.assertEqual(g.players[0].primary_power['card_id'],'JAIL_EVENT_101hp');self.assertEqual(g.players[0].primary_power['damage'],3)
    def test_nested_sulfuras_preserves_previous_remaining_use(self):
        g=self.game();self.play(g,'TLC_632');self.use(g);self.play(g,'TLC_632');self.use(g)
        g.players[0].power_used=False;self.use(g)
        self.assertEqual(g.players[0].primary_power['remaining'],1)
        g.players[0].mana=2;self.use(g);self.assertIsNone(g.players[0].primary_power)
    def test_replacement_cancels_old_sulfuras_restore(self):
        g=self.game();self.play(g,'TLC_632');self.use(g);self.star(g);self.use(g)
        self.assertEqual(g.players[0].primary_power['card_id'],'JAIL_EVENT_101hp')
    def test_spell_damage_does_not_modify_power_damage(self):
        g=self.game();g._summon(0,'CORE_EX1_012');self.play(g,'TLC_632');self.use(g)
        self.assertEqual(g.players[1].health,22)
    def test_next_power_discount_consumed_on_replacement_power(self):
        g=self.game();self.star(g);g.players[0].next_power_cost_effects=[dict(kind='set',amount=0)];before=g.players[0].mana
        self.use(g);self.assertEqual(g.players[0].mana,before);self.assertFalse(g.players[0].next_power_cost_effects)
    def test_normal_after_use_triggers_fire(self):
        g=self.game();self.star(g);m=g._summon(0,'EDR_470');before=m.health;self.use(g)
        self.assertEqual(m.health,before+2);self.assertEqual(g.players[0].hero_power_uses,1)
    def test_countered_sulfuras_does_not_replace_power(self):
        g=self.game();g.players[1].secrets=[Card(g._new_id(),'CORE_EX1_287')];self.play(g,'TLC_632')
        self.assertIsNone(g.players[0].primary_power)
    def test_counterspell_does_not_counter_hero_card(self):
        g=self.game();g.players[1].secrets=[Card(g._new_id(),'CORE_EX1_287')];self.play(g,'CORE_EX1_323')
        self.assertEqual(g.players[0].primary_power['card_id'],'EX1_tk33');self.assertEqual(len(g.players[1].secrets),1)
    def test_turn_refresh_does_not_reset_star_damage(self):
        g=self.game();self.star(g);self.star(g);self.use(g);g.step(Action('end'));g.step(Action('end'))
        self.assertFalse(g.players[0].power_used);self.assertEqual(g.players[0].primary_power['damage'],3)
    def test_power_state_public_and_feature_encodable(self):
        g=self.game();self.star(g);self.play(g,'TLC_632');view=g.observe(0,include_events=False)
        self.assertEqual(view['players'][0]['primary_power']['restore']['card_id'],'JAIL_EVENT_101hp')
        self.assertEqual(g.observe(1)['players'][0]['primary_power']['remaining'],2)
        rows=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']))
        self.assertTrue(rows);self.assertEqual(SCHEMA,'visible-action-features-v58')
    def test_observation_cannot_mutate_stored_restore(self):
        g=self.game();self.star(g);self.play(g,'TLC_632');v=g.observe(0)
        v['players'][0]['primary_power']['restore']['damage']=100
        self.assertEqual(g.players[0].primary_power['restore']['damage'],2)
    def test_dormant_demon_play_refreshes_star(self):
        g=self.game();self.star(g);self.use(g);self.play(g,'CORE_BT_156')
        self.assertFalse(g.players[0].power_used)
        self.assertTrue(next(m for m in g.players[0].all_minions if m.card_id=='CORE_BT_156').dormant)
    def test_awaking_demon_is_not_another_summon(self):
        g=self.game();self.star(g);m=g._summon(0,'CORE_BT_156');self.use(g);g._awaken(m)
        self.assertTrue(g.players[0].power_used)
    def test_hero_card_playable_on_full_board(self):
        g=self.game()
        for _ in range(7):g._summon(0,'EDR_851t')
        self.play(g,'CORE_EX1_323');self.assertEqual(len(g.players[0].board),7)
        self.assertEqual(g.players[0].hero_card_id,'CORE_EX1_323')
    def test_countered_star_upgrade_preserves_existing_power(self):
        g=self.game();self.star(g);g.players[1].secrets=[Card(g._new_id(),'CORE_EX1_287')]
        self.star(g);self.assertEqual(g.players[0].primary_power['damage'],2)
    def test_restored_inferno_retains_summon_power(self):
        g=self.game();self.play(g,'CORE_EX1_323');self.play(g,'TLC_632');self.use(g)
        g.players[0].power_used=False;self.use(g);g.players[0].mana=2;self.use(g)
        self.assertEqual(g.players[0].minions[0].card_id,'EX1_tk34')
    def test_hero_power_can_finish_game(self):
        g=self.game();self.star(g);g.players[1].health=2;self.use(g)
        self.assertTrue(g.terminal);self.assertEqual(g.players[0].hero_power_uses,1)
    def second(self,g,target):g.step(Action('power',target=target,choices=(1,)))
    def test_second_power_spends_corpses_not_mana(self):
        g=self.game();self.play(g,'JAIL_446');m=g.players[0].minions[0];before=m.attack
        g.players[0].mana=0;g.players[0].corpses=3;self.second(g,m.uid)
        self.assertEqual((g.players[0].corpses,g.players[0].mana,m.attack),(0,0,before+3))
        self.assertFalse(g.players[0].power_used);self.assertTrue(g.players[0].secondary_power['used'])
    def test_second_power_requires_corpses_even_with_mana(self):
        g=self.game();self.play(g,'JAIL_446');g.players[0].corpses=2
        self.assertFalse(any(a.kind=='power' and a.choices==(1,) for a in g.legal_actions()))
    def test_power_slots_have_independent_use_limits(self):
        g=self.game();self.play(g,'JAIL_446');g.players[0].corpses=6;m=g.players[0].minions[0]
        g.step(Action('power',target=g.hero_id(1)));self.second(g,m.uid)
        self.assertEqual(g.players[0].hero_power_uses,2)
        self.assertFalse(any(a.kind=='power' for a in g.legal_actions()))
    def test_second_power_can_buff_enemy_minion(self):
        g=self.game();self.play(g,'JAIL_446');g.players[0].corpses=3;m=g._summon(1,'EDR_851t');self.second(g,m.uid)
        self.assertEqual(m.attack,4)
    def test_second_power_cannot_target_hero_or_enemy_stealth(self):
        g=self.game();self.play(g,'JAIL_446');g.players[0].corpses=3;m=g._summon(1,'EDR_851t');m.keywords.add('STEALTH')
        targets=[a.target for a in g.legal_actions() if a.kind=='power' and a.choices==(1,)]
        self.assertTrue(all(t>0 for t in targets));self.assertNotIn(m.uid,targets)
    def test_secondary_power_refreshes_next_turn(self):
        g=self.game();self.play(g,'JAIL_446');g.players[0].corpses=6;self.second(g,g.players[0].minions[0].uid)
        g.step(Action('end'));g.step(Action('end'));self.assertFalse(g.players[0].secondary_power['used'])
    def test_second_power_consumes_next_power_cost_effect(self):
        g=self.game();self.play(g,'JAIL_446');g.players[0].corpses=0;g.players[0].next_power_cost_effects=[dict(kind='set',amount=0)]
        self.second(g,g.players[0].minions[0].uid)
        self.assertFalse(g.players[0].next_power_cost_effects);self.assertEqual(g.players[0].corpses,0)
    def test_generic_refresh_refreshes_both_slots(self):
        g=self.game();self.play(g,'JAIL_446');g.players[0].power_used=True;g.players[0].secondary_power['used']=True
        g._effect(('refresh_power',),dict(owner=0,source=None));self.assertFalse(g.players[0].power_used);self.assertFalse(g.players[0].secondary_power['used'])
    def test_star_refresh_does_not_refresh_secondary(self):
        g=self.game();self.play(g,'JAIL_446');self.star(g);g.players[0].corpses=3;self.second(g,g.players[0].minions[0].uid)
        self.use(g);self.demon(g);self.assertFalse(g.players[0].power_used);self.assertTrue(g.players[0].secondary_power['used'])
    def test_second_power_fires_after_use_triggers(self):
        g=self.game();self.play(g,'JAIL_446');g.players[0].corpses=3;m=g._summon(0,'EDR_470');before=m.health
        self.second(g,m.uid);self.assertEqual(m.health,before+2)
    def test_secondary_slot_visible_and_encodable(self):
        g=self.game();self.play(g,'JAIL_446');g.players[0].corpses=3;v=g.observe(0,include_events=False)
        self.assertEqual(v['players'][0]['secondary_power']['cost'],3)
        self.assertTrue(any(a['kind']=='power' and a['choices']==(1,) for a in v['legal_actions']))
        self.assertTrue(encode_decision(dict(actor=0,observation=v,actions=v['legal_actions'])))
    def test_regrant_replaces_secondary_instead_of_adding_third_slot(self):
        g=self.game();self.play(g,'JAIL_446');g.players[0].corpses=6;self.second(g,g.players[0].minions[0].uid);self.play(g,'JAIL_446')
        self.assertFalse(g.players[0].secondary_power['used'])
        self.assertEqual({a.choices for a in g.legal_actions() if a.kind=='power'},{(),(1,)})
    def test_failed_secondary_effect_rolls_back_payment_and_usage(self):
        from unittest.mock import patch
        g=self.game();self.play(g,'JAIL_446');g.players[0].corpses=3;target=g.players[0].minions[0].uid
        with patch.object(g,'_buff',side_effect=RuntimeError('fixture failure')):
            with self.assertRaises(RuntimeError):self.second(g,target)
        self.assertEqual(g.players[0].corpses,3);self.assertFalse(g.players[0].secondary_power['used'])
        self.assertEqual(g.players[0].hero_power_uses,0)
    def test_corpse_payment_does_not_progress_mana_spent_cards(self):
        g=self.game();self.play(g,'JAIL_446');c=g._enter_hand(0,Card(g._new_id(),'CATA_131'));g.players[0].corpses=3
        self.second(g,g.players[0].minions[0].uid)
        self.assertEqual(getattr(c,'rule_state',{}).get('held_mana_spent',0),0)
