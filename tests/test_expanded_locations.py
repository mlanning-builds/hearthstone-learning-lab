"""User-run checks for mixed boards and four explicitly implemented Locations."""
import copy
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.locations import Location
from expanded.cards import COLLECTIBLE_IDS
from engine.cards import UnsupportedCard


class LocationTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('WARRIOR',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        self.p.hand=[];self.q.hand=[];self.p.mana=self.p.max_mana=10
        self.p.deck=['CORE_CS2_029']*10;self.q.deck=['CORE_CS2_029']*10

    def give(self,cid):
        card=Card(self.g._new_id(),cid);self.p.hand.append(card);return card

    def play(self,cid,target=0,position=None):
        card=self.give(cid)
        if position is None:
            position=len(self.p.board) if self.g.cards[cid]['type'] in ('MINION','LOCATION') else -1
        self.g.step(Action('play',card.uid,target,position))
        return card

    def place(self,cid='CORE_REV_990',owner=0,position=-1):
        return self.g._place_location(owner,cid,position)

    def use(self,location,target=0):
        self.g.step(Action('activate',location.uid,target))

    def test_play_costs_mana_but_activation_does_not(self):
        target=self.g._summon(0,'Core_CS2_200')
        self.play('CORE_REV_990');location=self.p.locations[0]
        self.assertEqual(self.p.mana,9)
        self.assertEqual(self.p.cards_played,1)
        self.use(location,target.uid)
        self.assertEqual(self.p.mana,9);self.assertEqual(self.p.cards_played,1)
        self.assertEqual((target.attack,target.health),(8,6))
        self.assertEqual(location.durability,2)

    def test_cooldown_skips_next_owner_turn(self):
        location=self.place('CATA_584');self.use(location)
        self.assertFalse(any(a.kind=='activate' for a in self.g.legal_actions()))
        for _ in range(2):self.g.step(Action('end'))
        self.assertFalse(any(a.kind=='activate' for a in self.g.legal_actions()))
        for _ in range(2):self.g.step(Action('end'))
        self.assertIn(Action('activate',location.uid),self.g.legal_actions())

    def test_seven_shared_slots_block_play_summon_and_summoning_power(self):
        self.p.hero_class='PALADIN';self.place()
        for _ in range(6):self.g._summon(0,'Core_CS2_200')
        a=self.give('CORE_REV_990');b=self.give('CORE_CS2_189')
        actions=self.g.legal_actions()
        self.assertFalse(any(x.kind=='play' and x.source in (a.uid,b.uid) for x in actions))
        self.assertNotIn(Action('power'),actions)
        self.assertIsNone(self.g._summon(0,'Core_CS2_200'))
        self.assertEqual(len(self.p.board),7)

    def test_location_is_not_an_attack_or_spell_target(self):
        location=self.place(owner=1)
        m=self.g._summon(0,'Core_CS2_200');m.summoned_turn=-1
        spell=self.give('CORE_CS2_029')
        self.assertFalse(any(a.target==location.uid for a in self.g.legal_actions()))
        self.assertNotIn(location.uid,self.g._characters())
        with self.assertRaises(ValueError):self.g._damage(location.uid,1)

    def test_area_damage_destroy_and_buffs_ignore_locations(self):
        location=self.place();self.g._summon(0,'Core_CS2_200')
        ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)
        self.g._effect(('board_buff',2,2),ctx)
        self.g._effect(('area_damage','all_characters',1),ctx)
        self.g._effect(('destroy_all_minions',),ctx);self.g._settle()
        self.assertEqual(self.p.board,[location]);self.assertEqual(location.durability,3)
        self.assertEqual(self.p.corpses,1)

    def test_location_separates_adjacent_aura(self):
        wolf=self.g._summon(0,'CORE_EX1_162')
        target=self.g._summon(0,'Core_CS2_200')
        self.assertEqual(target.attack,7)
        self.place(position=1)
        self.assertEqual(target.attack,6)
        self.assertEqual(self.p.board[0],wolf)

    def test_chamber_buffs_only_chosen_hand_minion_privately(self):
        location=self.place('CATA_477');a=self.give('Core_CS2_200');b=self.give('CORE_CS2_189')
        spell=self.give('CORE_CS2_029')
        self.assertNotIn(Action('activate',location.uid,spell.uid),self.g.legal_actions())
        self.use(location,a.uid)
        self.assertEqual((a.attack_bonus,a.health_bonus),(2,2))
        self.assertEqual((b.attack_bonus,b.health_bonus),(0,0))
        other=self.g.observe(1)
        self.assertNotIn('hand',other['players'][0]);self.assertEqual(other['legal_actions'],[])
        event=next(e for e in other['events'] if e['event']=='location_activated')
        self.assertEqual(event['target'],'PRIVATE_HAND_CARD')

    def test_chamber_has_no_action_without_hand_minions(self):
        self.place('CATA_477');self.give('CORE_CS2_029')
        self.assertFalse(any(a.kind=='activate' for a in self.g.legal_actions()))

    def test_volcano_damage_ignores_spell_damage(self):
        self.g._summon(0,'CORE_EX1_012')
        location=self.place('CATA_584');self.use(location)
        self.assertEqual(self.q.health,27)

    def test_fire_spell_enables_volcano_bonus_then_resets_next_turn(self):
        location=self.place('CATA_584')
        self.play('CORE_CS2_029',-2)
        self.use(location)
        self.assertEqual(self.q.health,18)
        self.assertTrue(self.p.fire_spell_played)
        for _ in range(2):self.g.step(Action('end'))
        self.assertFalse(self.p.fire_spell_played)

    def test_countered_fire_spell_does_not_enable_bonus_or_card_count(self):
        location=self.place('CATA_584')
        self.q.secrets.append(Card(self.g._new_id(),'CORE_EX1_287'))
        self.play('CORE_CS2_029',-2)
        self.assertFalse(self.p.fire_spell_played);self.assertEqual(self.p.cards_played,0)
        self.use(location);self.assertEqual(self.q.health,27)

    def test_underbelly_token_draws_on_death(self):
        location=self.place('JAIL_877');self.use(location)
        rat=self.p.minions[0]
        self.assertEqual((rat.card_id,rat.attack,rat.health),('JAIL_877t',2,1))
        rat.health=0;self.g._settle()
        self.assertEqual(len(self.p.hand),1)
        self.assertIn(location,self.p.board)

    def test_final_charge_frees_full_board_slot_before_summon(self):
        location=self.place('JAIL_877');location.durability=1
        for _ in range(6):self.g._summon(0,'Core_CS2_200')
        self.use(location)
        self.assertEqual(len(self.p.board),7)
        self.assertFalse(self.p.locations)
        self.assertEqual(self.p.board[0].card_id,'JAIL_877t')
        self.assertEqual(self.p.corpses,0)

    def test_spent_location_leaves_no_corpse_or_attack_entity(self):
        location=self.place('CATA_584');location.durability=1
        self.use(location)
        self.assertEqual(self.p.board,[]);self.assertEqual(self.p.corpses,0)
        self.assertFalse(any(a.source==location.uid for a in self.g.legal_actions()))

    def test_location_play_does_not_trigger_spell_cast(self):
        self.g._summon(0,'CORE_EX1_559')
        self.play('CATA_584');self.use(self.p.locations[0])
        self.assertEqual(self.p.hand,[])

    def test_invalid_activation_preserves_state_and_rng(self):
        location=self.place('CORE_REV_990')
        before=self.g.observe(0);rng=self.g.rng.getstate()
        with self.assertRaises(ValueError):self.use(location,-2)
        self.assertEqual(self.g.observe(0),before);self.assertEqual(self.g.rng.getstate(),rng)

    def test_failed_activation_rolls_back_durability_removal_and_rng(self):
        location=self.place('JAIL_877');location.durability=1
        before=self.g.observe(0);rng=self.g.rng.getstate()
        with patch.object(Game,'_summon',side_effect=RuntimeError('fixture')):
            with self.assertRaisesRegex(RuntimeError,'fixture'):self.use(location)
        self.assertEqual(self.g.observe(0),before);self.assertEqual(self.g.rng.getstate(),rng)

    def test_observation_identifies_public_location_and_board_order(self):
        self.g._summon(0,'Core_CS2_200');location=self.place()
        self.g._summon(0,'Core_CS2_200')
        for viewer in (0,1):
            board=self.g.observe(viewer)['players'][0]['board']
            self.assertEqual([x['type'] for x in board],['MINION','LOCATION','MINION'])
            self.assertEqual(board[1]['durability'],3);self.assertTrue(board[1]['ready'])
            self.assertNotIn('health',board[1])

    def test_unknown_locations_stay_unsupported(self):
        self.assertNotIn('EDR_520',COLLECTIBLE_IDS)
        with self.assertRaises(UnsupportedCard):self.place('EDR_520')

    def test_location_between_minions_survives_enemy_bounce_and_turn_changes(self):
        location=self.place(owner=1)
        self.g._summon(1,'Core_CS2_200')
        self.g._effect(('bounce_all_enemies',),dict(owner=0,source=None,target=0))
        self.g._settle()
        self.assertEqual(self.q.board,[location])
        for _ in range(2):self.g.step(Action('end'))
        self.assertEqual(self.q.board,[location])
