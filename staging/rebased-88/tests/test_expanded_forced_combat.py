"""Controller-correct forced attacks and bounded summon/attack groups."""
import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class ForcedCombatTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('WARRIOR',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g
    def play(self,g,cid,target=0,cost=None):
        c=g._enter_hand(0,Card(g._new_id(),cid))
        if cost is not None:c.set_cost=cost
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
    def effect(self,g,op,source=None,target=0):
        g._start_play_effects([op],dict(owner=0,source=source,target=target,bonus=0,lifesteal=False));g._settle()
    def test_forced_attack_does_not_consume_normal_attack(self):
        g=self.game();m=g._summon(0,'CS3_020');m.summoned_turn=-1;g._force_attack(m.uid,g.hero_id(1));self.assertEqual(m.attacks,0);self.assertEqual(g.players[1].health,22)
        self.assertTrue(any(a.kind=='attack' and a.source==m.uid for a in g.legal_actions()))
    def test_frozen_sleeping_cant_attack_can_be_forced(self):
        g=self.game();m=g._summon(0,'CS3_020');m.frozen_until=99;m.keywords.add('CANT_ATTACK');g._force_attack(m.uid,g.hero_id(1));self.assertEqual(g.players[1].health,22)
    def test_enemy_forced_attack_keeps_turn_controller(self):
        g=self.game();a=g._summon(1,'CS3_020');b=g._summon(0,'CORE_TTN_866');health=b.health;g._force_attack(a.uid,b.uid)
        self.assertEqual(g.current,0);self.assertEqual(b.health,health-a.attack);self.assertEqual(a.attacks,0)
    def test_forced_attack_does_not_retarget_dead_subject(self):
        g=self.game();a=g._summon(0,'CS3_020');b=g._summon(1,'EDR_851t');b.health=0;g._force_attack(a.uid,b.uid);self.assertEqual(a.attacks,0);self.assertEqual(g.players[1].health,30)
    def test_divine_shield_and_poisonous_use_shared_combat(self):
        g=self.game();a=g._summon(0,'EDR_851t');a.keywords.add('POISONOUS');b=g._summon(1,'CS3_020');b.keywords.add('DIVINE_SHIELD');g._force_attack(a.uid,b.uid)
        self.assertNotIn('DIVINE_SHIELD',b.keywords);self.assertGreater(b.health,0)
    def test_same_side_lifesteal_heals_controller(self):
        g=self.game();a=g._summon(0,'CS3_020');b=g._summon(0,'CORE_TTN_866');g.players[0].health=10;g._force_attack(a.uid,b.uid)
        self.assertGreater(g.players[0].health,10);self.assertEqual(g.players[1].health,30)
    def test_inquisitor_follows_hero_attack(self):
        g=self.game();g._summon(0,'CS3_020');g.players[0].temporary_attack=1;g.step(Action('attack',g.hero_id(0),g.hero_id(1)));self.assertEqual(g.players[1].health,21)
    def test_muncher_attacks_lowest_health_enemy_hero(self):
        g=self.game();m=g._summon(0,'RLK_720');g.players[1].health=5;g._summon(1,'CS3_020');g.step(Action('end'));self.assertEqual(g.players[1].health,5-m.attack)
    def test_muncher_attacks_lowest_health_minion(self):
        g=self.game();g._summon(0,'RLK_720');m=g._summon(1,'EDR_851t');g.step(Action('end'));self.assertNotIn(m,g.players[1].board);self.assertEqual(g.players[1].health,30)
    def test_hound_forces_all_initial_enemies_to_attack(self):
        g=self.game();a=g._summon(1,'EDR_851t');b=g._summon(1,'EDR_851t');self.play(g,'JAIL_435');self.assertFalse(g.players[1].minions)
    def test_hound_is_preparable(self):
        g=self.game();c=g._enter_hand(0,Card(g._new_id(),'JAIL_435'));self.assertIn(Action('prepare',source=c.uid),g.legal_actions())
    def test_terror_end_forces_attacks_and_lifesteals(self):
        g=self.game();g._summon(0,'CORE_TTN_866');g.players[0].health=10;g._summon(1,'EDR_851t');g.step(Action('end'));self.assertGreater(g.players[0].health,10);self.assertFalse(g.players[1].board)
    def test_mask_enemy_attacks_chosen_friendly(self):
        g=self.game();m=g._summon(0,'EDR_851t');e=g._summon(1,'EDR_851t');g.players[0].health=10;self.play(g,'DINO_428',m.uid)
        self.assertEqual(m.attack,8);self.assertEqual(m.max_health,10);self.assertNotIn(e,g.players[1].minions);self.assertGreater(g.players[0].health,10)
    def test_mask_can_target_enemy_and_forces_opposite_side(self):
        g=self.game();a=g._summon(0,'EDR_851t');b=g._summon(1,'EDR_851t');self.play(g,'DINO_428',b.uid);self.assertNotIn(a,g.players[0].board);self.assertEqual(b.attack,8)
    def test_dreamsaber_discounted_attacks_two_distinct(self):
        g=self.game();g._summon(1,'EDR_851t');g._summon(1,'EDR_851t');self.play(g,'EDR_014',cost=3);self.assertFalse(g.players[1].minions)
    def test_dreamsaber_full_price_does_not_attack(self):
        g=self.game();g._summon(1,'EDR_851t');self.play(g,'EDR_014');self.assertEqual(len(g.players[1].minions),1)
    def test_surgery_summons_four_even_if_target_dies_early(self):
        g=self.game();m=g._summon(1,'EDR_851t');self.play(g,'JAIL_454',m.uid);self.assertEqual(len(g.players[0].minions),3);self.assertFalse(g.players[1].board)
    def test_trees_can_attack_friendly_target(self):
        g=self.game();m=g._summon(0,'CS3_020');self.play(g,'TLC_230',m.uid);self.assertNotIn(m,g.players[0].board)
    def test_traveler_shadow_attacks_enemy(self):
        g=self.game();m=g._summon(0,'TIME_434');e=g._summon(1,'EDR_851t');m.health=0;g._settle();self.assertNotIn(e,g.players[1].board)
    def test_hounds_attack_when_no_minions_in_deck(self):
        g=self.game();self.play(g,'TIME_443');self.assertEqual(g.players[1].health,24);self.assertEqual(len(g.players[0].minions),2)
    def test_hounds_do_not_attack_with_deck_minion(self):
        g=self.game();g.players[0].deck.append('EDR_851t');self.play(g,'TIME_443');self.assertEqual(g.players[1].health,30)
    def test_stormbrewer_pre_damage_kills_before_retaliation(self):
        g=self.game();a=g._summon(0,'TLC_107');e=g._summon(1,'EDR_851t');before=a.health;g._force_attack(a.uid,e.uid);self.assertEqual(a.health,before);self.assertNotIn(e,g.players[1].board)
    def test_stormbrewer_kindred_rush(self):
        g=self.game();g.players[0].previous_tribes={'ELEMENTAL'};self.play(g,'TLC_107');self.assertIn('RUSH',g.players[0].minions[0].keywords)
    def test_spire_stats_equal_remaining_hand_size(self):
        g=self.game();self.play(g,'JAIL_511');g._add(0,'TOKEN_COIN');g._add(0,'TOKEN_COIN');loc=g.players[0].locations[0];g.step(Action('activate',loc.uid));m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(2,2))
    def test_spire_zero_hand_demon_dies_before_attack(self):
        g=self.game();self.play(g,'JAIL_511');loc=g.players[0].locations[0];g.step(Action('activate',loc.uid));self.assertFalse(g.players[0].minions)
    def test_nested_forced_attack_pre_damage_precedes_combat(self):
        g=self.game();a=g._summon(0,'TLC_107');b=g._summon(1,'EDR_851t');before=a.health
        context=dict(owner=0,source=a,target=0,bonus=0,lifesteal=False)
        g._rule_events.append(('captured_effects',dict(operations=(('force_group_one',a.uid,'random'),),context=context),[]));g._settle()
        self.assertEqual(a.health,before);self.assertNotIn(b,g.players[1].board)
    def test_forced_pre_attack_fires_before_retaliation_on_opponent_turn(self):
        g=self.game();a=g._summon(1,'TLC_107');b=g._summon(0,'EDR_851t');before=a.health
        self.effect(g,('force_pair',a.uid,b.uid));self.assertEqual(a.health,before);self.assertNotIn(b,g.players[0].board)
