"""Live Shatter transitions and all seven collectible family members."""
import unittest
import test_expanded_generation as fixtures
from engine.game import Card
from expanded import Action,Game,random_deck
from expanded.shatter import HALVES,PARENTS,TOKEN_IDS,RULES
from expanded.cards import COLLECTIBLE_IDS

class ShatterTests(unittest.TestCase):
    def setUp(self):self.h=fixtures.GenerationTests();self.g=self.h.game()
    def add(self,cid,settle=True):
        c=Card(self.g._new_id(),cid);self.g._enter_hand(0,c)
        if settle:self.g._settle(allow_event_choices=True)
        return c
    def hand(self):return [c.card_id for c in self.g.players[0].hand]
    def play(self,cid,target=0):
        c=next(c for c in self.g.players[0].hand if c.card_id==cid)
        a=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target)
        self.g.step(a)
    def combined(self,cid):
        c=self.add(cid,False);self.g._b60_state(c)['shatter_combined']=True;return c
    def test_all_collectibles_and_dependencies_registered(self):
        self.assertTrue(set(HALVES)|{'CATA_202','TIME_101'}<=COLLECTIBLE_IDS)
        self.assertTrue(TOKEN_IDS<=self.g.cards.keys());self.assertFalse(TOKEN_IDS&COLLECTIBLE_IDS)
    def test_splits_to_opposite_hand_ends(self):
        self.add('TOKEN_COIN');self.add('CATA_489')
        self.assertEqual(self.hand(),['CATA_489t','TOKEN_COIN','CATA_489t2'])
    def test_empty_hand_splits_and_immediately_combines(self):
        self.add('CATA_489');self.assertEqual(self.hand(),['CATA_489'])
        self.assertTrue(self.g.players[0].hand[0].rule_state['shatter_combined'])
    def test_one_slot_only_left_half(self):
        for _ in range(9):self.add('TOKEN_COIN')
        self.add('CATA_489');self.assertEqual(self.hand(),['CATA_489t']+['TOKEN_COIN']*9)
    def test_full_hand_no_split_event(self):
        for _ in range(10):self.add('TOKEN_COIN')
        before=len([e for e in self.g.events if e['event']=='shatter'])
        self.add('CATA_489');self.assertEqual(len(self.hand()),10)
        self.assertEqual(len([e for e in self.g.events if e['event']=='shatter']),before)
    def test_playing_middle_card_combines(self):
        self.add('TOKEN_COIN');self.add('CATA_489');self.play('TOKEN_COIN')
        self.assertEqual(self.hand(),['CATA_489'])
    def test_discarding_middle_card_combines(self):
        middle=self.add('TOKEN_COIN');self.add('CATA_820');self.g._discard_card(0,middle);self.g._settle()
        self.assertEqual(self.hand(),['CATA_820'])
    def test_matching_halves_from_different_parents_combine(self):
        self.add('CATA_489t');self.add('CATA_489t2')
        self.assertEqual(self.hand(),['CATA_489'])
    def test_identical_halves_do_not_combine(self):
        self.add('CATA_489t');self.add('CATA_489t');self.assertEqual(len(self.hand()),2)
    def test_different_families_do_not_combine(self):
        self.add('CATA_489t');self.add('CATA_820t2');self.assertEqual(len(self.hand()),2)
    def test_nested_pairs_remain_separated_by_combined_card(self):
        for cid in ['CATA_489t','CATA_820t','CATA_820t2','CATA_489t2']:self.add(cid,False)
        self.g._settle();self.assertEqual(self.hand(),['CATA_489t','CATA_820','CATA_489t2'])
    def test_merge_adds_cost_discounts_and_spell_damage(self):
        a=self.add('CATA_489t',False);b=self.add('CATA_489t2',False)
        a.cost_delta=-1;b.cost_delta=-2;a.spell_damage_bonus=1;b.spell_damage_bonus=2
        self.g._settle();c=self.g.players[0].hand[0]
        self.assertEqual((c.cost_delta,c.spell_damage_bonus),(-3,3))
    def test_draw_discount_before_split_inherited_twice(self):
        self.add('TOKEN_COIN');self.g.players[0].deck=['CATA_489']
        self.h.run_ops(self.g,[('filtered_draw',(('type','eq','SPELL'),),1,-1)])
        self.assertEqual([getattr(c,'cost_delta',0) for c in self.g.players[0].hand],[-1,0,-1])
        self.play('TOKEN_COIN');self.assertEqual(self.g.players[0].hand[0].cost_delta,-2)
    def test_temporary_survives_split_and_merge(self):
        self.add('TOKEN_COIN');c=self.add('CATA_489',False);self.g._make_temporary(c);self.g._settle()
        self.assertTrue(self.g._is_temporary(self.g.players[0].hand[0]));self.assertTrue(self.g._is_temporary(self.g.players[0].hand[-1]))
        self.play('TOKEN_COIN');self.assertTrue(self.g._is_temporary(self.g.players[0].hand[0]))
    def test_combined_copy_does_not_split(self):
        self.add('CATA_489');c=self.g._copy_card(self.g.players[0].hand[0]);self.g._enter_hand(0,c);self.g._settle()
        self.assertEqual(self.hand(),['CATA_489','CATA_489'])
    def test_combined_shuffle_and_redraw_does_not_split(self):
        self.add('CATA_489');c=self.g.players[0].hand[0];self.g.players[0].deck=[]
        self.g._shuffle_hand_card(0,c);self.g._draw(0);self.g._settle()
        self.assertEqual(self.hand(),['CATA_489']);self.assertTrue(self.g.players[0].hand[0].rule_state['shatter_combined'])
    def test_split_identities_hidden_from_opponent_events(self):
        self.add('TOKEN_COIN');self.add('CATA_820')
        events=[e for e in self.g.observe(1)['events'] if e['event'].startswith('shatter')]
        self.assertTrue(events);self.assertTrue(all('card' not in e for e in events))
    def test_no_rng_used_by_split_or_merge(self):
        before=self.g.rng.getstate();self.add('CATA_489');self.assertEqual(self.g.rng.getstate(),before)
    def test_original_does_not_split_during_mulligan(self):
        self.g.phase='mulligan';self.add('CATA_489');self.assertEqual(self.hand(),['CATA_489'])
        self.assertFalse(getattr(self.g.players[0].hand[0],'rule_state',{}).get('shatter_combined',False))
    def test_pyromancer_triggers_once_on_split_not_combine(self):
        self.g._summon(0,'TIME_101');enemy=self.g._summon(1,'EX1_tk34')
        self.add('TOKEN_COIN');self.add('CATA_489');self.assertEqual(enemy.health,4)
        self.play('TOKEN_COIN');self.assertEqual(enemy.health,4)
    def test_enemy_pyromancer_does_not_trigger(self):
        self.g._summon(1,'TIME_101');self.add('CATA_489');self.assertEqual(self.g.players[0].health,30)
        self.assertEqual(self.g.players[1].minions[0].health,3)
    def test_silenced_pyromancer_does_not_trigger(self):
        m=self.g._summon(0,'TIME_101');self.g._silence(m);enemy=self.g._summon(1,'EX1_tk34')
        self.add('CATA_489');self.assertEqual(enemy.health,6)
    def test_stolen_power_generates_already_combined_other_class(self):
        self.add('CATA_202');self.play('CATA_202')
        c=self.g.players[0].hand[0];self.assertIn(c.card_id,HALVES);self.assertNotEqual(self.g.cards[c.card_id]['cardClass'],'MAGE')
        self.assertTrue(c.rule_state['shatter_combined'])
    def test_combined_wildwood_treants_have_deathrattle(self):
        self.combined('CATA_134');self.play('CATA_134');before=list(self.g.players[0].minions)
        self.assertEqual(len(before),2);self.assertTrue(all(m.attached_death_effects for m in before))
        before[0].health=0;self.g._settle();self.assertEqual(len(self.g.players[0].minions),2)
    def test_combined_schism_copies_after_buff_and_elusive(self):
        target=self.g._summon(0,'EDR_851t');self.combined('CATA_306');self.play('CATA_306',target.uid)
        self.assertEqual([(m.attack,m.health) for m in self.g.players[0].minions],[(3,4),(3,4)])
        self.assertTrue(all('ELUSIVE' in self.g._effective_keywords(m) for m in self.g.players[0].minions))
    def test_combined_flight_summons_then_buffs(self):
        self.combined('CATA_479');self.play('CATA_479')
        self.assertEqual([(m.attack,m.health) for m in self.g.players[0].minions],[(5,2),(5,2)])
        self.assertTrue(all('DIVINE_SHIELD' in m.keywords for m in self.g.players[0].minions))
    def test_combined_arcane_flow_damages_target_then_all_enemies(self):
        target=self.g._summon(1,'EX1_tk34');self.combined('CATA_489');self.play('CATA_489',target.uid)
        self.assertFalse(self.g.players[1].minions);self.assertEqual(self.g.players[1].health,28)
    def test_combined_supply_draws_minions_then_buffs_hand(self):
        self.g.players[0].deck=['CORE_CS2_029']+['EDR_851t']*3
        self.combined('CATA_820');self.play('CATA_820')
        self.assertEqual(self.hand(),['EDR_851t']*3)
        self.assertEqual([(c.attack_bonus,c.health_bonus) for c in self.g.players[0].hand],[(2,2)]*3)
        self.assertEqual(self.g.players[0].deck,['CORE_CS2_029'])
    def test_each_half_is_legally_playable_without_other_effect(self):
        for cid in PARENTS:
            with self.subTest(cid=cid):
                self.setUp();target=self.g._summon(0,'EDR_851t');self.add(cid)
                mode=RULES[cid][0];self.play(cid,target.uid if mode!='none' else 0)
                self.g.assert_invariants()
