"""Shared follow-up continuations and explicit state/hand conditions."""
import unittest
from unittest.mock import patch
from expanded import Game,Action,random_deck
from expanded.cards import RULES
from expanded.game import Card

class InternalFollowupTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('MAGE',31),random_deck('ROGUE',53)],seed=71,record=True)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*30;p.health=30;p.mana=p.max_mana=10
        return g
    def enemy(self,g,health):
        m=g._summon(1,'CS3_020');m.health=health;m.max_health=max(health,m.max_health);return m
    def cast(self,g,cid,policy='enemies'):
        g._start_play_effects([('cast_fixed_spell',cid,policy)],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def interrupt_damage(self,g):
        original=g._deal_effect
        def deal(target,amount,ctx):
            value=original(target,amount,ctx)
            g._effect(('choose_fixed_summon',('AT_037t',)),dict(owner=0,source=None))
            return value
        return patch.object(g,'_deal_effect',side_effect=deal)
    def test_mortal_coil_kill_draw_waits_for_choice(self):
        g=self.game();self.enemy(g,1)
        with self.interrupt_damage(g):self.cast(g,'CORE_EX1_302')
        self.assertIsNotNone(g.pending_choice);self.assertEqual(g.players[0].hand,[])
        g.step(g.legal_actions()[0]);self.assertEqual(len(g.players[0].hand),1)
        self.assertFalse(g.players[1].minions)
    def test_mortal_coil_shield_does_not_draw(self):
        g=self.game();m=self.enemy(g,1);m.keywords.add('DIVINE_SHIELD');self.cast(g,'CORE_EX1_302')
        self.assertEqual(g.players[0].hand,[]);self.assertEqual(m.health,1)
    def test_slam_survival_draw_waits_for_choice(self):
        g=self.game();m=self.enemy(g,8)
        with self.interrupt_damage(g):self.cast(g,'CORE_EX1_391')
        self.assertEqual(g.players[0].hand,[]);self.assertEqual(m.health,6)
        g.step(g.legal_actions()[0]);self.assertEqual(len(g.players[0].hand),1)
    def test_slam_kill_does_not_draw(self):
        g=self.game();self.enemy(g,2);self.cast(g,'CORE_EX1_391')
        self.assertEqual(g.players[0].hand,[])
    def test_nascent_bolt_draws_two_after_survival(self):
        g=self.game();m=self.enemy(g,8);self.cast(g,'TIME_216')
        self.assertEqual(m.health,3);self.assertEqual(len(g.players[0].hand),2)
    def test_initiation_copy_waits_for_choice(self):
        g=self.game();self.enemy(g,4)
        with self.interrupt_damage(g):self.cast(g,'CORE_SCH_512')
        self.assertEqual(g.players[0].minions,[])
        g.step(g.legal_actions()[0])
        self.assertEqual([m.card_id for m in g.players[0].minions],['AT_037t','CS3_020'])
        copy=g.players[0].minions[1];self.assertEqual(copy.health,g.cards['CS3_020']['health'])
    def test_initiation_on_survivor_does_not_copy(self):
        g=self.game();self.enemy(g,8);self.cast(g,'CORE_SCH_512')
        self.assertEqual(g.players[0].minions,[])
    def test_kill_buff_occurs_after_child_choice(self):
        g=self.game();self.enemy(g,3)
        with patch.object(g.rng,'choice',side_effect=lambda xs:next((x for x in xs if isinstance(x,int) and x>0),xs[0])),self.interrupt_damage(g):
            self.cast(g,'END_014')
        self.assertEqual(g.players[0].minions,[]);g.step(g.legal_actions()[0])
        m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(4,4))
    def test_kill_heal_occurs_after_child_choice(self):
        g=self.game();self.enemy(g,5);g.players[1].health=10
        with self.interrupt_damage(g):self.cast(g,'CATA_303')
        self.assertEqual(g.players[1].health,10);g.step(g.legal_actions()[0])
        self.assertEqual(g.players[1].health,15)
    def test_normal_hand_play_uses_same_followup_boundary(self):
        g=self.game();self.enemy(g,1);c=g._add(0,'CORE_EX1_302')
        action=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid)
        with self.interrupt_damage(g):g.step(action)
        self.assertEqual(g.players[0].hand,[]);g.step(g.legal_actions()[0])
        self.assertEqual(len(g.players[0].hand),1);self.assertEqual(g.players[0].cards_played,1)
    def test_quick_shot_sees_empty_hand_after_consumption(self):
        g=self.game();c=g._add(0,'CORE_BRM_013')
        g._start_play_effects([('cast_zone_spell','hand',c.uid,'enemies')],dict(owner=0,source=None))
        self.assertEqual(len(g.players[0].hand),1);self.assertEqual(g.players[1].health,27)
    def test_held_condition_selects_correct_branch(self):
        for held,damage in ((False,4),(True,8)):
            with self.subTest(held=held):
                g=self.game();m=self.enemy(g,20)
                if held:g._add(0,'CORE_EX1_312')
                self.cast(g,'FIR_923');self.assertEqual(m.health,20-damage)
    def test_hand_condition_rejects_unsupported_alternative(self):
        g=self.game()
        with patch.dict(RULES,{'FIR_923':('none',[('if_holding',(('cost','ge',8),),('damage_random_enemy_minion',8),('unknown_effect',))])}):
            self.assertFalse(g._supports_internal_spell('FIR_923'))
    def test_state_condition_uses_prior_turn(self):
        for prior,draws,armor in ((False,2,6),(True,1,3)):
            with self.subTest(prior=prior):
                g=self.game();g.players[0].minion_played_last_turn=prior;self.cast(g,'MEND_043')
                self.assertEqual(len(g.players[0].hand),draws);self.assertEqual(g.players[0].armor,armor)
    def test_weapon_required_spell_fizzles_without_weapon(self):
        g=self.game();self.cast(g,'CORE_CS2_074')
        self.assertTrue(any(e['event']=='spell_fizzle' for e in g.events))
    def test_weapon_required_spell_buffs_present_weapon(self):
        g=self.game();g._equip(0,'CS2_082');before=g.players[0].weapon['attack'];self.cast(g,'CORE_CS2_074')
        self.assertEqual(g.players[0].weapon['attack'],before+2)
    def test_friendly_character_spell_does_not_heal_enemy(self):
        g=self.game();g.players[0].health=10;g.players[1].health=10
        self.cast(g,'CORE_CFM_604','random')
        self.assertEqual(g.players[0].health,22);self.assertEqual(g.players[1].health,10)
    def test_far_sight_keeps_drawn_physical_card_and_discount(self):
        g=self.game();c=Card(g._new_id(),'CORE_CS2_029');g.players[0].deck=[c]
        self.cast(g,'CORE_CS2_053');self.assertIs(g.players[0].hand[0],c);self.assertEqual(g._cost(c,0),1)
    def test_hex_transforms_without_deathrattle(self):
        g=self.game();m=g._summon(1,'CORE_EX1_110');self.cast(g,'CORE_EX1_246')
        self.assertNotEqual(g.players[1].minions[0].card_id,'CORE_EX1_110')
        self.assertEqual(g.players[1].death_history,[])
    def test_generated_fixed_insertion_retains_full_count(self):
        g=self.game();self.cast(g,'TLC_826')
        self.assertEqual(sum(g._card_data(c)['id']=='UNG_920t2' for c in g.players[0].deck),10)
