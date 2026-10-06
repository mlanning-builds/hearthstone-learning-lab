"""Physical origin and hand transitions, tested through shared paths and card plays."""
import unittest
from copy import deepcopy
from expanded import Game, Action, random_deck
from expanded.game import Card

class ProvenanceTests(unittest.TestCase):
    def game(self, fresh=False):
        g=Game([random_deck('PALADIN',31),random_deck('MAGE',53)],seed=71)
        if fresh:return g
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=[];p.health=30;p.mana=p.max_mana=10;p.armor=0
        return g
    def card(self,g,cid='CORE_CS2_029',original=None,copied=None):
        c=Card(g._new_id(),cid)
        if original is not None:
            c._starting_owner=original;d=g.cards[cid];c._starting_identity=d.get('countAsCopyOfDbfId',d.get('dbfId',cid))
        if copied is not None:c._copied_from_owner=copied
        return c
    def play(self,g,cid=None,card=None,target=None):
        c=g._enter_hand(g.current,self.card(g,cid)) if card is None else card
        g.players[g.current].mana=10
        actions=[a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and (target is None or a.target==target)]
        self.assertTrue(actions,(c.card_id,target));g.step(max(actions,key=lambda a:a.position))
        return next((m for m in reversed(g.players[g.current].minions) if m.card_id==c.card_id),None)
    def effect(self,g,op,owner=0,**kwargs):
        g._effect(op,dict(owner=owner,source=None,target=0,bonus=0,**kwargs))
    def test_initial_cards_are_physical_originals(self):
        g=self.game(True)
        for owner,p in enumerate(g.players):
            self.assertEqual(len(p.deck)+len(p.hand),30)
            self.assertTrue(all(g._started_in_deck(c,owner) for c in p.deck+p.hand))
    def test_mulligan_preserves_originals_coin_is_generated(self):
        g=self.game(True);ids=[c.uid for c in g.players[0].hand]
        g.step(Action('mulligan',choices=tuple(ids)));g.step(Action('mulligan'))
        for owner,p in enumerate(g.players):
            cards=p.deck+p.hand
            self.assertEqual(sum(g._started_in_deck(c,owner) for c in cards),30)
        coin=next(c for c in g.players[1].hand if c.card_id=='TOKEN_COIN')
        self.assertFalse(g._started_in_deck(coin,1))
    def test_generated_same_identity_is_not_original(self):
        g=self.game();a=self.card(g,original=0);b=g._copy_card(a)
        self.assertTrue(g._started_in_deck(a,0));self.assertFalse(g._started_in_deck(b,0));self.assertNotEqual(a.uid,b.uid)
    def test_draw_retains_origin_and_stamps_entry(self):
        g=self.game();c=self.card(g,original=0);g.players[0].deck=[c]
        self.assertIs(g._draw(0),c);self.assertTrue(g._started_in_deck(c,0));self.assertEqual(c._hand_entry_turn,g.turn)
    def test_full_hand_draw_burn_does_not_enter(self):
        g=self.game();g.players[0].hand=[self.card(g) for _ in range(10)];c=self.card(g,original=0);g.players[0].deck=[c]
        self.assertIsNone(g._draw(0));self.assertFalse(hasattr(c,'_hand_entry_turn'));self.assertFalse(g.players[0].deck)
    def test_transfer_preserves_owner_but_is_not_copy(self):
        g=self.game();c=self.card(g,original=1);g._enter_hand(0,c)
        self.assertFalse(g._started_in_deck(c,0));self.assertTrue(g._started_in_deck(c,1));self.assertFalse(g._copied_from_opponent(c,0))
    def test_copy_ancestry_and_inherited_copy(self):
        g=self.game();c=self.card(g,original=1);a=g._clone_hand_card(0,c,source_owner=1);b=g._clone_hand_card(0,a)
        for x in (a,b):self.assertTrue(g._copied_from_opponent(x,0));self.assertFalse(g._started_in_deck(x,1))
    def test_plain_own_copy_is_not_opponent_copy(self):
        g=self.game();c=g._clone_hand_card(0,self.card(g,original=0));self.assertFalse(g._copied_from_opponent(c,0))
    def test_play_bounce_preserves_starting_lineage(self):
        g=self.game();c=g._enter_hand(0,self.card(g,'EDR_851t',original=0));m=self.play(g,card=c);g._bounce(m)
        self.assertTrue(g._started_in_deck(g.players[0].hand[-1],0))
    def test_recruit_bounce_preserves_lineage(self):
        g=self.game();c=self.card(g,'EDR_851t',original=0)
        m=g._summon(0,c.card_id,entry_origin='recruit',entry_source=c);g._bounce(m)
        self.assertTrue(g._started_in_deck(g.players[0].hand[-1],0))
    def test_board_copy_bounce_does_not_gain_original(self):
        g=self.game();c=self.card(g,'EDR_851t',original=1);m=g._summon(1,c.card_id,entry_origin='recruit',entry_source=c)
        clone=g._summon(0,m.card_id,copy_from=m);g._bounce(clone);held=g.players[0].hand[-1]
        self.assertFalse(g._started_in_deck(held,1));self.assertTrue(g._copied_from_opponent(held,0))
    def test_hand_transform_keeps_entry_time(self):
        g=self.game();c=g._enter_hand(0,self.card(g,'EDR_851t',original=0));turn=c._hand_entry_turn;g.turn+=1
        g._b60_transform_card(c,'CS2_033');self.assertEqual(c._hand_entry_turn,turn);self.assertFalse(g._started_in_deck(c,0))
    def test_steamcleaner_removes_generated_same_identity_both_decks(self):
        g=self.game();originals=[]
        for i,p in enumerate(g.players):
            c=self.card(g,original=i);originals.append(c);p.deck=[c,g._copy_card(c),self.card(g,original=1-i)]
        self.play(g,'CORE_REV_946')
        for i,p in enumerate(g.players):self.assertEqual(p.deck,[originals[i]]);self.assertEqual(p.fatigue,0)
    def test_steamcleaner_empty_decks(self):
        g=self.game();self.play(g,'CORE_REV_946');self.assertEqual([p.fatigue for p in g.players],[0,0])
    def test_techysaurus_counts_plays_not_draws(self):
        g=self.game();c=self.card(g,'DINO_409');g._add(0,'TOKEN_COIN');self.assertEqual(g._cost(c,0),7)
        coin=g.players[0].hand[-1];self.play(g,card=coin);self.assertEqual(g._cost(c,0),6)
    def test_original_play_does_not_discount_techysaurus(self):
        g=self.game();c=g._enter_hand(0,self.card(g,'EDR_851t',original=0));self.play(g,card=c)
        self.assertEqual(g._cost(self.card(g,'DINO_409'),0),7)
    def test_techysaurus_floor(self):
        g=self.game();g.players[0]._nonstarting_plays=20;self.assertEqual(g._cost(self.card(g,'DINO_409'),0),0)
    def test_armaments_draws_one_of_each_origin_spell(self):
        g=self.game();a=self.card(g,original=0);b=self.card(g);m=self.card(g,'EDR_851t');g.players[0].deck=[a,b,m]
        self.play(g,'EDR_251');self.assertEqual({c.uid for c in g.players[0].hand},{a.uid,b.uid});self.assertEqual(g.players[0].deck,[m])
    def test_armaments_no_match_does_not_fatigue(self):
        g=self.game();self.play(g,'EDR_251');self.assertEqual(g.players[0].fatigue,0)
    def test_dreamwarden_draw_and_buff(self):
        g=self.game();c=self.card(g);g.players[0].deck=[c];m=self.play(g,'EDR_256')
        self.assertEqual((m.attack,m.health),(5,6));self.assertIn(c,g.players[0].hand)
    def test_dreamwarden_original_only_no_buff(self):
        g=self.game();g.players[0].deck=[self.card(g,original=0)];m=self.play(g,'EDR_256');self.assertEqual((m.attack,m.health),(3,4))
    def test_shovel_death_draws_only_nonstarting_spell(self):
        g=self.game();a=self.card(g,original=0);b=self.card(g);g.players[0].deck=[a,b];g._equip(0,'JAIL_380');g._break_weapon(0)
        self.assertEqual(g.players[0].hand,[b]);self.assertEqual(g.players[0].deck,[a])
    def test_soul_requires_play_while_held(self):
        g=self.game();s=g._enter_hand(0,self.card(g,'JAIL_433'));copy=g._enter_hand(0,self.card(g,'TOKEN_COIN',copied=1))
        self.assertEqual(g._cost(s,0),5);self.play(g,card=copy);self.assertEqual(g._cost(s,0),1)
    def test_soul_new_copy_not_retroactive(self):
        g=self.game();copy=g._enter_hand(0,self.card(g,'TOKEN_COIN',copied=1));self.play(g,card=copy)
        s=g._enter_hand(0,self.card(g,'JAIL_433'));self.assertEqual(g._cost(s,0),5)
    def test_stolen_original_does_not_activate_soul(self):
        g=self.game();s=g._enter_hand(0,self.card(g,'JAIL_433'));c=g._enter_hand(0,self.card(g,'TOKEN_COIN',original=1));self.play(g,card=c)
        self.assertEqual(g._cost(s,0),5)
    def test_sweeper_activated_damages_enemy_only(self):
        g=self.game();s=g._enter_hand(0,self.card(g,'JAIL_432'));c=g._enter_hand(0,self.card(g,'TOKEN_COIN',copied=1));self.play(g,card=c)
        a=g._summon(0,'CS2_033');b=g._summon(1,'CS2_033');before=b.health;self.play(g,card=s)
        self.assertEqual(b.health,before-2);self.assertEqual(a.health,before)
    def test_sweeper_inactive_no_damage(self):
        g=self.game();b=g._summon(1,'CS2_033');before=b.health;self.play(g,'JAIL_432');self.assertEqual(b.health,before)
    def test_shade_only_discounts_copies(self):
        g=self.game();a=g._enter_hand(0,self.card(g,copied=1));b=g._enter_hand(0,self.card(g,original=1));c=g._enter_hand(0,self.card(g))
        m=g._summon(0,'JAIL_434');m.health=0;g._settle()
        self.assertEqual([getattr(x,'cost_delta',0) for x in (a,b,c)],[-1,0,0])
    def test_waygate_discounts_generated_same_id_not_original(self):
        g=self.game();a=g._enter_hand(0,self.card(g,original=0));b=g._enter_hand(0,self.card(g));self.play(g,'TLC_364')
        self.assertEqual((getattr(a,'cost_delta',0),getattr(b,'cost_delta',0)),(0,-1))
    def test_burglar_only_new_opponent_hand_cards(self):
        g=self.game();old=g._enter_hand(1,self.card(g));old._hand_entry_turn=g.turn-1;new=g._enter_hand(1,self.card(g));self.play(g,'JAIL_205');g.step(Action('end'))
        self.assertIn(new,g.players[0].hand);self.assertNotIn(new,g.players[1].hand);self.assertIn(old,g.players[1].hand)
        self.assertFalse(g._copied_from_opponent(new,0))
    def test_burglar_full_hand_removes_and_burns(self):
        g=self.game();new=g._enter_hand(1,self.card(g));g.players[0].hand=[self.card(g) for _ in range(10)]
        self.effect(g,('origin_steal_new_hand',));self.assertEqual(len(g.players[0].hand),10);self.assertNotIn(new,g.players[1].hand)
    def test_reentry_updates_entry_turn(self):
        g=self.game();c=g._enter_hand(1,self.card(g));g.players[1].hand.remove(c);g.turn+=1;g._enter_hand(1,c)
        self.assertEqual(c._hand_entry_turn,g.turn)
    def test_private_lineage_not_serialized(self):
        g=self.game();g._enter_hand(1,self.card(g,original=1,copied=0));view=g.observe(0)
        self.assertNotIn('_starting_owner',str(view));self.assertNotIn('_copied_from_owner',str(view));self.assertNotIn('_hand_entry_turn',str(view))
    def test_invalid_action_rolls_back_origins(self):
        g=self.game();c=g._enter_hand(0,self.card(g,original=0));before=deepcopy(g.__dict__)
        with self.assertRaises(Exception):g.step(Action('play',source=c.uid,target=999999))
        self.assertEqual(g.players[0].hand[0].__dict__,before['players'][0].hand[0].__dict__);self.assertEqual(g.rng.getstate(),before['rng'].getstate())
    def test_shuffle_preserves_origin_and_resets_held_progress(self):
        g=self.game();c=g._enter_hand(0,self.card(g,'JAIL_433',original=0));g._b60_state(c)['opponent_copy_played']=True
        clean=g._shuffle_hand_card(0,c);self.assertTrue(g._started_in_deck(clean,0));self.assertFalse(getattr(clean,'rule_state',{}))
        g.turn+=1;g._draw(0);self.assertEqual(clean._hand_entry_turn,g.turn)
    def test_deck_spell_copies_are_nonstarting(self):
        g=self.game();c=self.card(g,original=0);g.players[0].deck=[c];self.effect(g,('copy_deck_spells',))
        self.assertEqual(len(g.players[0].deck),2);self.assertEqual(sum(g._started_in_deck(x,0) for x in g.players[0].deck),1)
    def test_opponent_draw_snapshot_copy_has_ancestry(self):
        g=self.game();c=self.card(g,original=1);g._effect(('copy_drawn_set_cost',1),dict(owner=0,event=dict(card=c)))
        copy=g.players[0].hand[-1];self.assertTrue(g._copied_from_opponent(copy,0));self.assertEqual(g._cost(copy,0),1)
    def test_opponent_deck_copy_has_ancestry(self):
        g=self.game();g.players[1].deck=[self.card(g,original=1)];self.effect(g,('copy_enemy_deck',))
        self.assertTrue(g._copied_from_opponent(g.players[0].hand[-1],0))
    def test_opponent_hand_copy_has_ancestry(self):
        g=self.game();g._enter_hand(1,self.card(g));self.effect(g,('copy_lowest_enemy_hand',))
        self.assertTrue(g._copied_from_opponent(g.players[0].hand[-1],0))
    def test_burglar_silenced_does_not_steal(self):
        g=self.game();m=self.play(g,'JAIL_205');g._silence(m);c=g._enter_hand(1,self.card(g));g.step(Action('end'))
        self.assertIn(c,g.players[1].hand);self.assertNotIn(c,g.players[0].hand)
    def test_two_burglars_do_not_duplicate_cards(self):
        g=self.game();self.play(g,'JAIL_205');self.play(g,'JAIL_205');c=g._enter_hand(1,self.card(g));g.step(Action('end'))
        self.assertEqual(sum(x.uid==c.uid for x in g.players[0].hand),1)
    def test_armaments_full_hand_second_draw_burns(self):
        g=self.game();g.players[0].hand=[self.card(g) for _ in range(9)]
        g.players[0].deck=[self.card(g,original=0),self.card(g)];self.play(g,'EDR_251')
        self.assertEqual(len(g.players[0].hand),10);self.assertFalse(g.players[0].deck);self.assertEqual(g.players[0].fatigue,0)
    def test_soul_activated_play_destroys_target(self):
        g=self.game();s=g._enter_hand(0,self.card(g,'JAIL_433'));copy=g._enter_hand(0,self.card(g,'TOKEN_COIN',copied=1));self.play(g,card=copy)
        m=g._summon(1,'CS2_033');self.play(g,card=s,target=m.uid);self.assertNotIn(m,g.players[1].board);self.assertEqual(g.players[0].mana,9)
    def test_feature_view_contains_own_origin_predicates(self):
        from expanded.features import encode_decision, SCHEMA
        g=self.game();g._enter_hand(0,self.card(g,original=0));view=g.observe(0)
        self.assertTrue(view['players'][0]['hand'][0]['started_in_deck']);self.assertNotIn('hand',view['players'][1])
        encoded=encode_decision(dict(actor=0,observation=view,actions=view['legal_actions']))
        self.assertTrue(encoded);self.assertIn('started_in_deck',str(encoded));self.assertEqual('visible-action-features-v58',SCHEMA)
