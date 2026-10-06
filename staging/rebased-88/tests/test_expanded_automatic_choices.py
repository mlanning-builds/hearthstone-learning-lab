"""Scheduler regressions; substituted operations do not claim new card support."""
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.cards import RULES
from engine.cards import UnsupportedCard

class AutomaticChoiceTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('ROGUE',31),random_deck('MAGE',53)],seed=71,record=True)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*30;p.mana=p.max_mana=10
        return g
    def cast(self,g,ops):
        with patch.dict(RULES,{'EX1_129':('none',ops)}):
            g._start_play_effects([('cast_fixed_spell','EX1_129','random'),('armor',3)],
                                 dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
    def test_spell_choice_resolves_then_parent_continues(self):
        g=self.game();self.cast(g,[('choose_fixed_summon',('EDR_851t',)),('draw',1)])
        self.assertIsNone(g.pending_choice);self.assertIsNone(g.pending_frame)
        self.assertEqual(len(g.players[0].minions),1);self.assertEqual(len(g.players[0].hand),1)
        self.assertEqual(g.players[0].armor,3)
    def test_consecutive_choices_resolve_once_each(self):
        g=self.game();self.cast(g,[('choose_fixed_summon',('EDR_851t',))]*2)
        self.assertEqual(len(g.players[0].minions),2)
        self.assertEqual(sum(e['event']=='automatic_choice' for e in g.events),2)
    def test_single_option_does_not_consume_rng(self):
        g=self.game();state=g.rng.getstate();self.cast(g,[('choose_fixed_summon',('EDR_851t',))])
        self.assertEqual(g.rng.getstate(),state)
    def test_multiple_options_use_seeded_rng(self):
        g=self.game()
        with patch.object(g.rng,'randrange',return_value=1) as choose:
            self.cast(g,[('choose_fixed_summon',('EDR_851t','CS3_020'))])
        choose.assert_called_once_with(2)
        self.assertEqual(g.players[0].minions[0].card_id,'CS3_020')
    def test_manual_play_still_waits(self):
        g=self.game();g._start_play_effects([('choose_fixed_summon',('EDR_851t',)),('armor',3)],
            dict(owner=0,source=None,target=0,bonus=0,lifesteal=False))
        self.assertIsNotNone(g.pending_choice);self.assertFalse(g.pending_choice['_automatic'])
        self.assertEqual(g.players[0].armor,0)
    def test_inner_trigger_choice_overrides_automatic_parent(self):
        g=self.game();original=g._deal_effect
        def damage(target,amount,ctx):
            result=original(target,amount,ctx)
            g._effect(('choose_fixed_summon',('EDR_851t',)),dict(owner=1,source=None,target=0,bonus=0,lifesteal=False))
            return result
        g._summon(1,'CS3_020')
        with patch.object(g,'_deal_effect',side_effect=damage):
            self.cast(g,[('area_damage','enemy_minions',1),('draw',1)])
        self.assertEqual(g.pending_choice['owner'],1);self.assertFalse(g.pending_choice['_automatic'])
        self.assertEqual(len(g.players[0].hand),0);self.assertEqual(g.players[0].armor,0)
        g.step(g.legal_actions()[0])
        self.assertEqual(len(g.players[0].hand),1);self.assertEqual(g.players[0].armor,3)
    def test_replay_wrapper_preserves_child_automatic_ownership(self):
        g=self.game();ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False,automatic_choices=True)
        g._effect_checkpoint(('replay_one',('choose_fixed_summon',('EDR_851t',)),ctx),dict(owner=0,source=None))
        self.assertIsNone(g.pending_choice);self.assertEqual(len(g.players[0].minions),1)
    def test_nested_selected_option_inherits_automatic_policy(self):
        g=self.game();m=g._summon(0,'EDR_851t')
        g._effect_checkpoint(('choose_self_effect',(('summon',('choose_fixed_summon',('EDR_851t',))),)),
            dict(owner=0,source=m,target=0,bonus=0,lifesteal=False,automatic_choices=True))
        self.assertIsNone(g.pending_choice);self.assertEqual(len(g.players[0].minions),2)
    def test_discover_uses_physical_card_and_records_once(self):
        g=self.game();c=g._add(0,'CORE_CS2_029');g.players[0].hand.remove(c);g.players[0].deck=[c]
        before=g.players[0].discoveries_this_turn
        self.cast(g,[('discover_deck',)])
        self.assertIs(g.players[0].hand[0],c);self.assertEqual(g.players[0].deck,[])
        self.assertEqual(g.players[0].discoveries_this_turn,before+1)
    def test_death_frame_cast_resolves_automatic_choice(self):
        g=self.game();m=g._summon(0,'TLC_522');m.health=0
        with patch.dict(RULES,{'EX1_129':('none',[('choose_fixed_summon',('EDR_851t',))])}):g._settle()
        self.assertIsNone(g.pending_choice);self.assertIsNone(g._death_frame)
        self.assertEqual([m.card_id for m in g.players[0].minions],['EDR_851t'])
    def test_empty_automatic_choice_fails_explicitly(self):
        g=self.game();g.pending_choice=dict(owner=0,kind='fixed_summon',options=[],_automatic=True)
        with self.assertRaises(UnsupportedCard):g._resolve_automatic_choices()
    def test_unmarked_existing_choice_is_not_taken_over(self):
        g=self.game();choice=dict(owner=1,kind='fixed_summon',options=[dict(card_id='EDR_851t')])
        g.pending_choice=choice
        g._effect_checkpoint(('armor',1),dict(owner=0,automatic_choices=True))
        self.assertIs(g.pending_choice,choice);self.assertNotIn('_automatic',choice)
