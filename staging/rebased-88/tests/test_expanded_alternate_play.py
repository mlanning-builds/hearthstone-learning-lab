"""Either-side controller effects and non-mana payment boundaries."""
import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card
from expanded.alternate_play import EITHER_SIDE

class AlternatePlayTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('WARLOCK',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g
    def put(self,g,cid):return g._enter_hand(0,Card(g._new_id(),cid))
    def play(self,g,c,enemy=False,position=0):
        g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.choices==((1,) if enemy else ()) and (a.position==position or a.position==-1)))
    def test_each_disguised_card_can_play_on_either_side(self):
        for cid in sorted(EITHER_SIDE):
            for enemy in [False,True]:
                with self.subTest(cid=cid,enemy=enemy):
                    g=self.game();c=self.put(g,cid);before=g.players[0].mana;self.play(g,c,enemy);p=g.players[int(enemy)]
                    self.assertTrue(any(m.card_id==cid for m in p.minions));self.assertEqual(g.players[0].mana,before-g.cards[cid]['cost']);self.assertEqual(g.players[0].cards_played,1);self.assertEqual(g.players[1].cards_played,0)
    def test_full_friendly_board_allows_enemy_side(self):
        g=self.game()
        for _ in range(7):g._summon(0,'EDR_851t')
        c=self.put(g,'CAP_004');actions=[a for a in g.legal_actions() if a.source==c.uid];self.assertTrue(actions);self.assertTrue(all(a.choices==(1,) for a in actions));self.play(g,c,True)
    def test_full_enemy_board_blocks_enemy_side(self):
        g=self.game()
        for _ in range(7):g._summon(1,'EDR_851t')
        c=self.put(g,'CAP_004');self.assertFalse(any(a.source==c.uid and a.choices==(1,) for a in g.legal_actions()))
    def test_operator_enemy_controller_death_draws_for_actor(self):
        g=self.game();self.play(g,self.put(g,'CAP_004'),True);m=g.players[1].minions[0];m.health=0;g._settle();self.assertEqual(len(g.players[0].hand),2);self.assertFalse(g.players[1].hand)
    def test_doctor_enemy_controller_shuffles_own_deck(self):
        g=self.game();self.play(g,self.put(g,'JAIL_442'),True);g.players[1].minions[0].health=0;g._settle();self.assertEqual(sum(g._card_data(c)['id']=='JAIL_443t' for c in g.players[1].deck),4)
    def test_detective_overloads_recipient_only(self):
        g=self.game();self.play(g,self.put(g,'JAIL_452'),True);self.assertEqual((g.players[0].overload_next,g.players[1].overload_next),(0,2))
    def test_watchman_damages_recipients_other_minions(self):
        g=self.game();a=g._summon(0,'CS3_020');b=g._summon(1,'CS3_020');before=b.health;self.play(g,self.put(g,'JAIL_455'),True);self.assertEqual(b.health,before-2);self.assertEqual(a.health,before)
    def test_executioner_uses_enemy_side_position(self):
        g=self.game();a=g._summon(1,'EDR_851t');b=g._summon(1,'CS3_020');self.play(g,self.put(g,'JAIL_461'),True,0);self.assertNotIn(a,g.players[1].board);self.assertIn(b,g.players[1].board)
    def test_corpse_card_requires_corpses_not_mana(self):
        g=self.game();c=self.put(g,'TLC_436');self.assertFalse(any(a.source==c.uid for a in g.legal_actions()));g.players[0].corpses=5;g.players[0].mana=0;self.play(g,c);self.assertEqual((g.players[0].corpses,g.players[0].mana),(0,0))
    def test_corpse_payment_discounted_cost(self):
        g=self.game();c=self.put(g,'TLC_436');c.cost_delta=-3;g.players[0].corpses=2;self.play(g,c);self.assertEqual(g.players[0].corpses,0);self.assertEqual(g.players[0].mana,10)
    def test_knight_requires_actual_hero_healing(self):
        g=self.game();c=self.put(g,'CORE_ETC_523');g._heal(g.hero_id(0),3,healer=0);self.assertEqual(g._payment_kind(c,0),'mana');g.players[0].health=20;g._heal(g.hero_id(0),3,healer=1);self.assertEqual(g._payment_kind(c,0),'health')
    def test_minion_healing_does_not_unlock_knight(self):
        g=self.game();m=g._summon(0,'CS3_020');m.health=1;g._heal(m.uid,3,healer=0);c=self.put(g,'CORE_ETC_523');self.assertEqual(g._payment_kind(c,0),'mana')
    def test_own_health_payment_cannot_be_lethal(self):
        g=self.game();p=g.players[0];p.hero_healed_turn=True;p.health=3;c=self.put(g,'CORE_ETC_523');self.assertFalse(any(a.source==c.uid for a in g.legal_actions()))
    def test_health_payment_ignores_armor_immune_shield_and_damage_triggers(self):
        g=self.game();p=g.players[0];p.hero_healed_turn=True;p.health=20;p.armor=5;p.divine_shield=True;p.hero_immune_expiry_players=[0];p.mana=0;c=self.put(g,'CORE_ETC_523');self.play(g,c)
        self.assertEqual((p.health,p.armor,p.mana,p.hero_damage_events_turn),(17,5,0,0));self.assertTrue(p.divine_shield)
    def test_health_healing_condition_resets_next_turn(self):
        g=self.game();g.players[0].hero_healed_turn=True;g.step(Action('end'));self.assertFalse(g.players[0].hero_healed_turn)
    def test_warloc_only_eligible_murloc_consumes_effect(self):
        g=self.game();self.play(g,self.put(g,'CATA_180'));self.play(g,self.put(g,'EDR_851t'));self.assertTrue(g.players[0].payment_effects)
        c=self.put(g,'CORE_EX1_509');before=g.players[0].health;cost=g._cost(c,0);self.play(g,c);self.assertEqual(g.players[0].health,before-cost);self.assertFalse(g.players[0].payment_effects)
    def test_warloc_cost_above_three_ineligible(self):
        g=self.game();g.players[0].payment_effects=['murloc_health'];c=self.put(g,'CORE_EX1_509');c.set_cost=4;self.assertEqual(g._payment_kind(c,0),'mana')
    def test_agamaggan_rejects_above_ten(self):
        g=self.game();g.players[0].payment_effects=['enemy_health'];c=self.put(g,'CORE_CS2_029');c.set_cost=11;self.assertFalse(any(a.source==c.uid for a in g.legal_actions()))
    def test_agamaggan_enemy_payment_can_be_lethal(self):
        g=self.game();g.players[0].payment_effects=['enemy_health'];g.players[0].mana=0;g.players[1].health=2;g.players[1].armor=10;self.play(g,self.put(g,'JAIL_718'));self.assertTrue(g.terminal);self.assertEqual(g.winner,0);self.assertEqual(g.players[1].armor,10)
    def test_agamaggan_sets_next_payment(self):
        g=self.game();self.play(g,self.put(g,'EDR_489'));self.assertEqual(g.players[0].payment_effects,['enemy_health'])
    def test_non_mana_payment_does_not_count_as_mana_spent(self):
        g=self.game();m=g._summon(0,'CATA_130');before=m.attack;g.players[0].corpses=5;self.play(g,self.put(g,'TLC_436'));self.assertEqual(m.attack,before)
