"""Automatic draw activation versus burn, play, cast, and recruitment."""
import unittest
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.on_draw_cards import IMP,SHRED,CAST_EFFECTS,SUMMON_DRAW

class OnDrawTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('WARLOCK',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g
    def play(self,g,cid):
        c=g._enter_hand(0,Card(g._new_id(),cid));g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    def draw(self,g,cid,owner=0):
        g.players[owner].deck.append(cid);g._draw(owner);g._settle(allow_event_choices=True)
    def test_gear_armor_and_replacement(self):
        g=self.game();self.draw(g,'JAIL_386t');self.assertEqual(g.players[0].armor,2);self.assertEqual([c.card_id for c in g.players[0].hand],['CORE_CS2_029'])
    def test_acorn_summons_squirrel(self):
        g=self.game();self.draw(g,'SW_439t');self.assertEqual([m.card_id for m in g.players[0].minions],['SW_439t2']);self.assertEqual(len(g.players[0].hand),1)
    def test_shred_deals_three_not_lifesteal(self):
        g=self.game();self.draw(g,SHRED);self.assertEqual(g.players[0].health,27)
    def test_blight_deals_two(self):
        g=self.game();self.draw(g,'JAIL_443t');self.assertEqual(g.players[0].health,28)
    def test_immune_to_spellpower_shred(self):
        g=self.game();g._summon(0,'CATA_EVENT_401');self.draw(g,SHRED);self.assertEqual(g.players[0].health,27)
    def test_cast_chain_draws_one_ordinary_card(self):
        g=self.game();g.players[0].deck=['CORE_CS2_029','JAIL_386t',SHRED,'JAIL_386t'];g._draw(0);g._settle()
        self.assertEqual((g.players[0].armor,g.players[0].health,len(g.players[0].hand),len(g.players[0].deck)),(2,29,1,0))
    def test_empty_replacement_fatigues(self):
        g=self.game();g.players[0].deck=[SHRED];g._draw(0);g._settle();self.assertEqual(g.players[0].health,26);self.assertEqual(g.players[0].fatigue,1)
    def test_lethal_shred_stops_replacement(self):
        g=self.game();g.players[0].health=3;self.draw(g,SHRED);self.assertTrue(g.terminal);self.assertFalse(g.players[0].hand);self.assertEqual(len(g.players[0].deck),20)
    def test_all_auto_cards_burn_without_activating(self):
        for cid in CAST_EFFECTS.keys()|SUMMON_DRAW.keys():
            with self.subTest(cid=cid):
                g=self.game()
                for _ in range(10):g._add(0,'TOKEN_COIN')
                self.draw(g,cid);self.assertEqual(len(g.players[0].deck),20);self.assertFalse(g.players[0].board);self.assertFalse(g.players[1].board);self.assertEqual(g.players[0].health,30);self.assertEqual(g.players[0].armor,0)
    def test_summon_draw_greenwing_token_taunt(self):
        g=self.game();self.draw(g,'EDR_260t');m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(4,5));self.assertIn('TAUNT',m.keywords)
    def test_summon_draw_ninja_stealth(self):
        g=self.game();self.draw(g,'TLC_513t2');m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(3,3));self.assertIn('STEALTH',m.keywords)
    def test_imp_goes_to_opponent(self):
        g=self.game();self.draw(g,IMP);self.assertFalse(g.players[0].board);m=g.players[1].minions[0];self.assertEqual((m.attack,m.health),(3,3));self.assertIn('LIFESTEAL',m.keywords)
    def test_full_board_summon_fails_but_draw_replaces(self):
        g=self.game()
        for _ in range(7):g._summon(0,'EDR_851t')
        self.draw(g,'EDR_260t');self.assertEqual(len(g.players[0].board),7);self.assertEqual(len(g.players[0].hand),1)
    def test_auto_spell_does_not_trigger_player_cast_listener(self):
        g=self.game();g._summon(0,'JAIL_718');self.draw(g,'JAIL_386t');self.assertEqual(len(g.players[0].hand),1)
    def test_held_shred_manual_play_no_replacement(self):
        g=self.game();self.play(g,SHRED);self.assertEqual(len(g.players[0].deck),20);self.assertEqual(g.players[0].health,27)
    def test_shuffle_sources_counts(self):
        for cid,token,count in [('JAIL_386','JAIL_386t',5),('TIME_025',SHRED,2),('TIME_026',SHRED,2),('TIME_027',SHRED,2),('JAIL_881','JAIL_881t',2),('TLC_518','TLC_513t2',3)]:
            with self.subTest(cid=cid):
                g=self.game();self.play(g,cid);self.assertEqual(sum(g._card_data(c)['id']==token for c in g.players[0].deck),count)
                self.assertEqual(g.players[0].shuffle_history[-1]['count'],count)
    def test_death_shuffle_sources(self):
        for cid,token,count,owner in [('CAP_400',IMP,2,1),('CORE_SW_439','SW_439t',4,0),('EDR_260','EDR_260t',2,0)]:
            with self.subTest(cid=cid):
                g=self.game();m=g._summon(0,cid);m.health=0;g._settle();self.assertEqual(sum(g._card_data(c)['id']==token for c in g.players[owner].deck),count)
    def test_fatebreaker_casts_without_drawing_and_buffs(self):
        g=self.game();g.players[0].deck=[SHRED];self.play(g,'TIME_028');m=g.players[0].minions[0]
        self.assertEqual((m.attack,m.health),(7,7));self.assertEqual(g.players[0].health,27);self.assertEqual(g.players[0].fatigue,0)
    def test_fatebreaker_without_shred_no_buff(self):
        g=self.game();self.play(g,'TIME_028');m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(4,4));self.assertEqual(g.players[0].health,30)
    def test_velocidrake_copies_after_damage(self):
        g=self.game();g.players[0].deck=[SHRED];self.play(g,'TIME_029');self.assertEqual(len(g.players[0].minions),2);self.assertEqual(g.players[0].health,27)
    def test_lethal_shred_cancels_reward(self):
        g=self.game();g.players[0].health=3;g.players[0].deck=[SHRED];self.play(g,'TIME_029');self.assertTrue(g.terminal);self.assertEqual(len(g.players[0].minions),1)
    def test_constable_moves_physical_imp_and_buffs(self):
        g=self.game();c=Card(g._new_id(),IMP);g.players[1].deck.insert(0,c);self.play(g,'CAP_401');self.assertIs(g.players[1].deck[-1],c);g._draw(1);g._settle();m=g.players[0].minions[0]
        imp=next(m for m in g.players[0].minions if m.card_id==IMP);self.assertEqual((imp.attack,imp.health),(5,5))
    def test_mastermind_applies_to_all_summon_routes(self):
        g=self.game();self.play(g,'CAP_406');m=g._summon(0,IMP);self.assertEqual((m.attack,m.health),(5,5));self.assertEqual(g.observe(1)['players'][0]['imp_upgrades'],1)
    def test_mastermind_stacks(self):
        g=self.game();g.players[0].imp_upgrades=2;self.draw(g,IMP,1);m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(7,7))
    def test_harsh_sentence_enemy_shuffle_and_cost(self):
        g=self.game();self.play(g,'CAP_404');self.assertEqual(sum(g._card_data(c)['id']==IMP for c in g.players[1].deck),2);g.step(Action('end'));c=g._enter_hand(1,Card(g._new_id(),'EDR_851t'));self.assertEqual(g._cost(c,1),2)
    def test_tripwire_missile_total(self):
        g=self.game();self.draw(g,'JAIL_881t');self.assertEqual(g.players[1].health,26)
    def test_follow_evidence_inserts_imp_and_attaches_to_playable_card(self):
        g=self.game();g._add(0,'TOKEN_COIN');self.play(g,'CAP_402');c=g.players[0].hand[0]
        self.assertEqual(c._follow_effects[0]['card_id'],'CAP_402');self.assertEqual(sum(g._card_data(v)['id']==IMP for v in g.players[1].deck),1)
    def test_follow_evidence_carrier_inserts_another_imp(self):
        g=self.game();g._add(0,'TOKEN_COIN');self.play(g,'CAP_402');c=g.players[0].hand[0];g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
        self.assertEqual(sum(g._card_data(v)['id']==IMP for v in g.players[1].deck),2)
    def test_follow_evidence_drawn_imp_summons_for_follow_caster(self):
        g=self.game();self.play(g,'CAP_402');imp=next(c for c in g.players[1].deck if g._card_data(c)['id']==IMP);g.players[1].deck.remove(imp);g.players[1].deck.append(imp);g._draw(1);g._settle()
        self.assertEqual([m.card_id for m in g.players[0].minions],[IMP])
