"""Constructed-only Dark Gift eligibility, physical state and live consumers."""
import unittest
import test_expanded_generation as fixtures
from engine.game import Card
from expanded import Action
from expanded.dark_gifts import GIFTS,RULES
from expanded.cards import COLLECTIBLE_IDS

class DarkGiftTests(unittest.TestCase):
    def setUp(self):self.h=fixtures.GenerationTests();self.g=self.h.game()
    def add(self,cid,owner=0):
        c=Card(self.g._new_id(),cid);self.g._enter_hand(owner,c);return c
    def play(self,card,target=0):
        self.g.players[0].mana=10
        self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid and a.target==target))
    def gift(self,card,gift):return self.g._dark_attach(0,card,gift)
    def test_closed_consumers_registered(self):self.assertTrue(set(RULES)<=COLLECTIBLE_IDS)
    def test_ten_constructed_gifts_exclude_archive_and_battlegrounds(self):
        self.assertEqual(len(GIFTS),10);self.assertNotIn('EDR_100t10',GIFTS);self.assertNotIn('EDR_100t4',GIFTS)
    def test_existing_keywords_exclude_partly_redundant_gifts(self):
        c=self.add('EDR_851t');self.g._b60_state(c)['dark_gifts']=['EDR_100t13']
        self.assertNotIn('EDR_100t13',self.g._dark_eligible(c))
    def test_zero_attack_cannot_get_charge_or_short_claws(self):
        c=self.add('EDR_851t');c.attack_bonus=-1
        self.assertNotIn('EDR_100t6',self.g._dark_eligible(c));self.assertNotIn('EDR_100t2',self.g._dark_eligible(c))
    def test_double_battlecry_requires_battlecry(self):
        self.assertNotIn('EDR_100t7',self.g._dark_eligible(self.add('EDR_851t')))
        self.assertIn('EDR_100t7',self.g._dark_eligible(self.add('CORE_CS2_189')))
    def test_three_offers_have_distinct_eligible_gifts(self):
        cards=[self.add(cid) for cid in ['EDR_851t','CORE_CS2_189','EX1_tk34']]
        gifts=self.g._dark_assign(cards);self.assertEqual(len(set(gifts)),3)
        for c,gift in zip(cards,gifts):self.assertIn(gift,self.g._dark_eligible(c))
    def test_attack_health_and_keyword_survive_play(self):
        c=self.add('EDR_851t');self.gift(c,'EDR_100t');self.play(c)
        m=self.g.players[0].minions[0];self.assertEqual((m.attack,m.health),(4,1));self.assertIn('LIFESTEAL',m.keywords)
    def test_short_claws_changes_attack_and_cost(self):
        c=self.add('EX1_tk34');self.gift(c,'EDR_100t2')
        self.assertEqual((c.attack_bonus,c.cost_delta),(-2,-2));self.play(c)
        self.assertEqual(self.g.players[0].minions[0].attack,4)
    def test_double_battlecry_runs_twice_without_duplicate_play(self):
        c=self.add('CORE_CS2_189');self.gift(c,'EDR_100t7');self.play(c,self.g.hero_id(1))
        self.assertEqual(self.g.players[1].health,28);self.assertEqual(self.g.players[0].cards_played,1)
    def test_living_nightmare_summons_two_two_copy(self):
        c=self.add('EX1_tk34');self.gift(c,'EDR_100t5');self.play(c)
        self.assertEqual([(m.attack,m.health) for m in self.g.players[0].minions],[(6,6),(2,2)])
    def test_living_nightmare_copy_does_not_repeat_battlecry(self):
        c=self.add('CORE_CS2_189');self.gift(c,'EDR_100t5');self.play(c,self.g.hero_id(1))
        self.assertEqual(self.g.players[1].health,29);self.assertEqual(len(self.g.players[0].minions),2)
    def test_reborn_restores_full_health_and_enchantments_once(self):
        c=self.add('EDR_851t');self.gift(c,'EDR_100t9');self.gift(c,'EDR_100t1');self.play(c)
        m=self.g.players[0].minions[0];self.g._buff(m,2,3);m.health=0;self.g._settle()
        reborn=self.g.players[0].minions[0];self.assertEqual((reborn.attack,reborn.health),(5,6))
        self.assertIn('ELUSIVE',reborn.keywords);self.assertNotIn('REBORN',reborn.keywords)
        reborn.health=0;self.g._settle();self.assertFalse(self.g.players[0].minions)
    def test_silence_removes_gifts_and_reborn(self):
        c=self.add('EDR_851t');self.gift(c,'EDR_100t9');self.play(c);m=self.g.players[0].minions[0]
        self.g._silence(m);m.health=0;self.g._settle();self.assertFalse(self.g.players[0].minions)
    def test_sweet_dreams_places_card_at_top_with_stats(self):
        self.g.players[0].deck=['TOKEN_COIN'];c=self.add('EDR_851t');self.gift(c,'EDR_100t8')
        self.assertFalse(self.g.players[0].hand);drawn=self.g._draw(0)
        self.assertEqual((drawn.card_id,drawn.attack_bonus,drawn.health_bonus),('EDR_851t',4,5))
    def test_wallow_copies_given_gift_in_hand_and_deck(self):
        a=self.add('EDR_487');self.g.players[0].deck=['EDR_487'];c=self.add('EDR_851t');self.gift(c,'EDR_100t')
        for wallow in [a,self.g.players[0].deck[0]]:
            self.assertEqual(wallow.attack_bonus,3);self.assertEqual(self.g._dark_list(wallow),['EDR_100t'])
    def test_wallow_does_not_copy_itself_or_recurse(self):
        c=self.add('EDR_487');self.gift(c,'EDR_100t')
        self.assertEqual(c.attack_bonus,3);self.assertEqual(len(self.g._dark_list(c)),1)
    def test_wallow_sweet_dreams_keeps_gifts_but_clears_other_buffs(self):
        c=self.add('EDR_487');self.gift(c,'EDR_100t');c.attack_bonus+=7
        self.gift(c,'EDR_100t8');c=self.g.players[0].deck[-1]
        self.assertEqual((c.attack_bonus,c.health_bonus),(7,5));self.assertEqual(len(self.g._dark_list(c)),2)
    def test_deck_wallow_moves_to_top_on_sweet_dreams_copy(self):
        self.g.players[0].deck=['EDR_487','TOKEN_COIN'];c=self.add('EDR_851t');self.gift(c,'EDR_100t8')
        self.assertEqual(self.g.players[0].deck[-1].card_id,'EDR_487')
    def test_overgrown_horror_discounts_only_gifted_minions(self):
        a=self.add('EDR_851t');b=self.add('EDR_851t');self.gift(a,'EDR_100t')
        self.play(self.add('EDR_654'));self.assertEqual(a.cost_delta,-2);self.assertEqual(getattr(b,'cost_delta',0),0)
    def test_matriarch_summons_both_taunt_dragons(self):
        self.gift(self.add('EDR_851t'),'EDR_100t');self.play(self.add('FIR_901'))
        brood=[m for m in self.g.players[0].minions if m.card_id=='FIR_901t']
        self.assertEqual(len(brood),2);self.assertTrue(all((m.attack,m.health)==(4,4) and 'TAUNT' in m.keywords for m in brood))
    def test_payoffs_do_nothing_without_gift(self):
        self.play(self.add('FIR_956'));self.assertEqual(self.g.players[0].armor,0);self.assertEqual(self.g.players[0].temporary_attack,0)
    def test_dragon_turtle_grants_attack_and_armor(self):
        self.gift(self.add('EDR_851t'),'EDR_100t');self.play(self.add('FIR_956'))
        self.assertEqual((self.g.players[0].temporary_attack,self.g.players[0].armor),(3,6))
    def test_cindersword_gets_weapon_attack(self):
        self.gift(self.add('EDR_851t'),'EDR_100t');self.play(self.add('FIR_922'))
        self.assertEqual(self.g.players[0].weapon['attack'],self.g.cards['FIR_922']['attack']+3)
    def test_xavius_discovers_actual_deck_card_without_draw_event(self):
        self.g.players[0].deck=['EDR_851t'];self.play(self.add('EDR_856'))
        self.assertEqual(self.g.pending_choice['kind'],'dark_deck');self.g.step(Action('choose',choices=(0,)))
        cards=self.g.players[0].hand+self.g.players[0].deck
        selected=next(c for c in cards if getattr(c,'card_id',None)=='EDR_851t')
        self.assertEqual(len(self.g._dark_list(selected)),1);self.assertEqual(self.g.players[0].discoveries_total,1)
    def test_nightmare_fuel_copies_enemy_without_removing(self):
        self.g.players[1].deck=['EDR_851t'];self.g.players[0].cards_played=0;self.play(self.add('EDR_528'))
        self.assertIsNone(self.g.pending_choice['options'][0]['dark_gift']);self.g.step(Action('choose',choices=(0,)))
        self.assertEqual(self.g.players[1].deck,['EDR_851t']);self.assertEqual(self.g.players[0].hand[0].card_id,'EDR_851t')
    def test_nightmare_fuel_combo_displays_gift_only_to_owner(self):
        self.g.players[1].deck=['EDR_851t'];self.g.players[0].cards_played=1;self.play(self.add('EDR_528'))
        self.assertIn(self.g.pending_choice['options'][0]['dark_gift'],GIFTS)
        self.assertEqual(self.g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
    def test_no_deck_minions_no_choice(self):
        self.g.players[0].deck=['TOKEN_COIN'];self.play(self.add('EDR_856'));self.assertIsNone(self.g.pending_choice)
