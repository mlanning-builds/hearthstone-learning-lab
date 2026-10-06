"""Closed forced-combat outcomes use the ordinary attack/death pipeline."""
import unittest
import test_expanded_forced_combat as fixtures
from expanded import Action

class CombatSequenceTests(unittest.TestCase):
    def setUp(self):self.h=fixtures.ForcedCombatTests();self.g=self.h.game()
    def play(self,cid,target=0):self.h.play(self.g,cid,target)
    def test_duel_repeats_until_target_dies(self):
        enemy=self.g._summon(1,'CORE_CS2_189');enemy.attack=1;enemy.health=enemy.max_health=3
        self.play('CORE_BT_120',enemy.uid)
        m=self.g.players[0].minions[0]
        self.assertEqual(m.health,7);self.assertEqual(m.attacks,0)
        self.assertFalse(self.g.players[1].minions)
    def test_duel_stops_when_challenger_dies(self):
        enemy=self.g._summon(1,'EX1_tk34');enemy.attack=10
        self.play('CORE_BT_120',enemy.uid)
        self.assertFalse(self.g.players[0].minions);self.assertEqual(enemy.health,5)
    def test_duel_shield_blocks_only_first_strike(self):
        enemy=self.g._summon(1,'EDR_851t');enemy.keywords.add('DIVINE_SHIELD')
        self.play('CORE_BT_120',enemy.uid)
        self.assertEqual(self.g.players[0].minions[0].health,8)
        self.assertFalse(self.g.players[1].minions)
    def test_duel_never_switches_to_reborn_copy(self):
        enemy=self.g._summon(1,'EDR_851t');enemy.keywords.add('REBORN')
        self.play('CORE_BT_120',enemy.uid)
        self.assertEqual(len(self.g.players[1].minions),1)
        self.assertNotEqual(enemy.uid,self.g.players[1].minions[0].uid)
        self.assertEqual(self.g.players[0].minions[0].health,9)
    def test_duel_bound_for_immortal_opponents(self):
        enemy=self.g._summon(1,'EX1_tk34');enemy.keywords.add('IMMUNE');enemy.attack=0
        challenger=self.g._summon(0,'CORE_BT_120')
        self.h.effect(self.g,('force_duel',),source=challenger,target=enemy.uid)
        self.assertEqual(self.g.players[0].friendly_attacks,30)
        self.assertEqual(enemy.health,6)
    def test_drake_spills_attack_above_minion_health(self):
        self.g._summon(0,'EDR_453');enemy=self.g._summon(1,'EX1_tk34')
        self.g.step(Action('end'))
        self.assertFalse(self.g.players[1].minions);self.assertEqual(self.g.players[1].health,24)
    def test_drake_spills_even_through_divine_shield(self):
        self.g._summon(0,'EDR_453');enemy=self.g._summon(1,'EDR_851t');enemy.keywords.add('DIVINE_SHIELD')
        self.g.step(Action('end'))
        self.assertEqual(enemy.health,1);self.assertNotIn('DIVINE_SHIELD',enemy.keywords)
        self.assertEqual(self.g.players[1].health,19)
    def test_drake_manual_attack_does_not_spill(self):
        m=self.g._summon(0,'EDR_453');m.summoned_turn=-1;enemy=self.g._summon(1,'EDR_851t')
        self.g.step(Action('attack',m.uid,enemy.uid));self.assertEqual(self.g.players[1].health,30)
    def test_drake_does_not_attack_hero_when_board_empty(self):
        self.g._summon(0,'EDR_453');self.g.step(Action('end'));self.assertEqual(self.g.players[1].health,30)
    def test_silenced_drake_has_no_end_trigger(self):
        m=self.g._summon(0,'EDR_453');self.g._silence(m);enemy=self.g._summon(1,'EDR_851t')
        self.g.step(Action('end'));self.assertEqual(enemy.health,1);self.assertEqual(self.g.players[1].health,30)
    def test_drake_lifesteal_includes_spill(self):
        m=self.g._summon(0,'EDR_453');m.keywords.add('LIFESTEAL');self.g.players[0].health=10
        self.g._summon(1,'EDR_851t');self.g.step(Action('end'));self.assertEqual(self.g.players[0].health,22)
    def test_ursoc_attacks_both_sides_and_remembers_kills(self):
        self.g._summon(0,'EDR_851t');self.g._summon(1,'EDR_851t');self.play('EDR_819')
        m=self.g.players[0].minions[0]
        self.assertEqual(m.card_id,'EDR_819');self.assertFalse(self.g.players[1].minions)
        self.assertEqual(m.rule_state['combat_kills'],['EDR_851t','EDR_851t'])
        m.health=0;self.g._settle()
        self.assertEqual([x.card_id for x in self.g.players[0].minions],['EDR_851t','EDR_851t'])
    def test_ursoc_simultaneous_death_remembers_victim(self):
        enemy=self.g._summon(1,'EDR_851t');enemy.attack=50;self.play('EDR_819')
        self.assertEqual([m.card_id for m in self.g.players[0].minions],['EDR_851t'])
    def test_ursoc_retaliation_kills_are_not_recorded(self):
        m=self.g._summon(0,'EDR_819');enemy=self.g._summon(1,'EDR_851t')
        self.g._force_attack(enemy.uid,m.uid);m.health=0;self.g._settle()
        self.assertFalse(self.g.players[0].minions)
    def test_ursoc_normal_attacks_record_kills(self):
        m=self.g._summon(0,'EDR_819');m.summoned_turn=-1;enemy=self.g._summon(1,'EDR_851t')
        self.g.step(Action('attack',m.uid,enemy.uid));m.health=0;self.g._settle()
        self.assertEqual([x.card_id for x in self.g.players[0].minions],['EDR_851t'])
    def test_ursoc_silence_erases_remembered_kills(self):
        m=self.g._summon(0,'EDR_819');enemy=self.g._summon(1,'EDR_851t')
        self.g._force_attack(m.uid,enemy.uid);self.g._silence(m);m.health=0;self.g._settle()
        self.assertFalse(self.g.players[0].minions)
    def test_ursoc_resurrection_uses_base_stats(self):
        enemy=self.g._summon(1,'EDR_851t');self.g._buff(enemy,2,2);self.play('EDR_819')
        m=self.g.players[0].minions[0];m.health=0;self.g._settle()
        self.assertEqual((self.g.players[0].minions[0].attack,self.g.players[0].minions[0].health),(1,1))
    def heal_enemy(self,target,amount=2):
        self.h.effect(self.g,('heal',amount),target=target)
    def test_shadow_attacks_before_healing_enemy_hero(self):
        self.g._summon(0,'TLC_821');self.g.players[1].health=10
        self.heal_enemy(self.g.hero_id(1));self.assertEqual(self.g.players[1].health,6)
    def test_shadow_full_health_target_does_not_gain_healing_after_attack(self):
        self.g._summon(0,'TLC_821');self.heal_enemy(self.g.hero_id(1))
        self.assertEqual(self.g.players[1].health,24)
    def test_shadow_cannot_save_lethally_attacked_target(self):
        self.g._summon(0,'TLC_821');self.g.players[1].health=5
        self.heal_enemy(self.g.hero_id(1),20);self.assertTrue(self.g.terminal)
        self.assertLessEqual(self.g.players[1].health,0)
    def test_shadow_lifesteal_heals_controller(self):
        self.g._summon(0,'TLC_821');self.g.players[0].health=10
        self.heal_enemy(self.g.hero_id(1));self.assertEqual(self.g.players[0].health,16)
    def test_shadow_does_not_trigger_on_friendly_healing(self):
        self.g._summon(0,'TLC_821');self.g.players[0].health=10
        self.heal_enemy(self.g.hero_id(0));self.assertEqual(self.g.players[0].health,12)
        self.assertEqual(self.g.players[1].health,30)
    def test_shadow_silence_disables_trigger(self):
        m=self.g._summon(0,'TLC_821');self.g._silence(m);self.g.players[1].health=10
        self.heal_enemy(self.g.hero_id(1));self.assertEqual(self.g.players[1].health,12)
    def test_shadow_minion_killed_does_not_return_from_healing(self):
        self.g._summon(0,'TLC_821');m=self.g._summon(1,'EDR_851t')
        self.heal_enemy(m.uid,20);self.assertFalse(self.g.players[1].minions)
    def test_multiple_shadows_attack_before_single_capped_heal(self):
        self.g._summon(0,'TLC_821');self.g._summon(0,'TLC_821');self.g.players[1].health=29
        self.heal_enemy(self.g.hero_id(1),4);self.assertEqual(self.g.players[1].health,18)
    def test_shadow_healing_bonus_not_applied_twice(self):
        self.g._summon(0,'TLC_821');self.g.players[1].health=20;self.g.players[0].permanent_healing_bonus=2
        self.heal_enemy(self.g.hero_id(1),2);self.assertEqual(self.g.players[1].health,18)
