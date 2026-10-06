"""Prepare action boundaries, physical-card state, and connected effects."""
import unittest
from copy import deepcopy
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.game import Card
from expanded.features import encode_decision

class PrepareTests(unittest.TestCase):
    def game(self):
        g=Game([random_deck('ROGUE',31),random_deck('MAGE',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        for p in g.players:
            p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*20;p.mana=p.max_mana=10;p.health=30;p.armor=0
        return g
    def put(self,g,cid,owner=0):return g._enter_hand(owner,Card(g._new_id(),cid))
    def play(self,g,c,target=0):
        a=next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target)
        g.step(a)
    def prepare(self,g,c):g.step(Action('prepare',source=c.uid))
    def test_preparing_spends_only_needed_mana(self):
        g=self.game();c=self.put(g,'JAIL_913');cost=g._cost(c,0);self.prepare(g,c)
        self.assertEqual(g.players[0].mana,10-(cost-1));self.assertEqual(g._cost(c,0),0)
    def test_remaining_mana_plus_one_discount(self):
        g=self.game();c=self.put(g,'JAIL_913');cost=g._cost(c,0);g.players[0].mana=1;self.prepare(g,c)
        self.assertEqual(g._cost(c,0),cost-2);self.assertEqual(g.players[0].mana,0)
    def test_one_cost_requires_one_mana(self):
        g=self.game();c=self.put(g,'JAIL_913');c.set_cost=1;self.prepare(g,c)
        self.assertEqual(g.players[0].mana,9);self.assertEqual(g._cost(c,0),0)
    def test_zero_mana_cannot_prepare(self):
        g=self.game();c=self.put(g,'JAIL_913');g.players[0].mana=0
        self.assertNotIn(Action('prepare',source=c.uid),g.legal_actions())
    def test_zero_cost_cannot_prepare(self):
        g=self.game();c=self.put(g,'JAIL_913');c.set_cost=0
        self.assertNotIn(Action('prepare',source=c.uid),g.legal_actions())
    def test_nonprepare_and_jailbird_cannot_prepare(self):
        g=self.game()
        for cid in ['TOKEN_COIN','JAIL_453']:
            c=self.put(g,cid);self.assertNotIn(Action('prepare',source=c.uid),g.legal_actions())
    def test_lock_blocks_play_until_next_own_turn(self):
        g=self.game();c=self.put(g,'JAIL_457');self.prepare(g,c)
        self.assertFalse(any(a.source==c.uid for a in g.legal_actions()))
        g.step(Action('end'));g.step(Action('end'))
        self.assertTrue(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()))
        self.assertNotIn(Action('prepare',source=c.uid),g.legal_actions())
    def test_no_play_or_shuffle_event(self):
        g=self.game();c=self.put(g,'JAIL_457');p=g.players[0];before=(p.cards_played,len(p.played_history),len(p.shuffle_history),list(p.deck))
        self.prepare(g,c);self.assertEqual(before,(p.cards_played,len(p.played_history),len(p.shuffle_history),list(p.deck)))
        self.assertFalse(p.board)
    def test_preserves_hand_slot(self):
        g=self.game();self.put(g,'TOKEN_COIN');c=self.put(g,'JAIL_457');self.put(g,'TOKEN_COIN');ids=[x.uid for x in g.players[0].hand];self.prepare(g,c)
        self.assertEqual(ids,[x.uid for x in g.players[0].hand])
    def test_full_board_can_prepare(self):
        g=self.game();c=self.put(g,'JAIL_457')
        for _ in range(7):g._summon(0,'EDR_851t')
        self.assertIn(Action('prepare',source=c.uid),g.legal_actions());self.prepare(g,c)
    def test_spell_without_target_can_prepare(self):
        g=self.game();c=self.put(g,'JAIL_913');self.prepare(g,c)
    def test_existing_lock_blocks_prepare(self):
        g=self.game();c=self.put(g,'JAIL_913');c.play_lock=dict(owner=0,until=g.players[0].turns_taken+1)
        self.assertNotIn(Action('prepare',source=c.uid),g.legal_actions())
    def test_copy_retains_discount_and_lock(self):
        g=self.game();c=self.put(g,'JAIL_457');self.prepare(g,c);copy=g._clone_hand_card(0,c)
        self.assertEqual(g._cost(copy,0),0);self.assertTrue(copy.rule_state['prepared'])
        self.assertFalse(any(a.source==copy.uid for a in g.legal_actions()))
    def test_shuffle_resets_prepare(self):
        g=self.game();c=self.put(g,'JAIL_457');self.prepare(g,c);clean=g._shuffle_hand_card(0,c)
        self.assertFalse(getattr(clean,'rule_state',{}).get('prepared'));self.assertEqual(g._cost(clean,0),g.cards[c.card_id]['cost'])
    def test_jailbirds_discount_by_reduction(self):
        g=self.game();birds=[self.put(g,'JAIL_453') for _ in range(2)];c=self.put(g,'JAIL_913');g.players[0].mana=1;costs=[g._cost(b,0) for b in birds];self.prepare(g,c)
        self.assertEqual([g._cost(b,0) for b in birds],[max(0,n-2) for n in costs])
    def test_enemy_jailbird_not_discounted(self):
        g=self.game();b=self.put(g,'JAIL_453',1);c=self.put(g,'JAIL_913');before=g._cost(b,1);self.prepare(g,c);self.assertEqual(g._cost(b,1),before)
    def test_prepare_does_not_trigger_auctioneer(self):
        g=self.game();g._summon(0,'JAIL_718');c=self.put(g,'JAIL_913');n=len(g.players[0].deck);self.prepare(g,c);self.assertEqual(len(g.players[0].deck),n)
    def test_auctioneer_draws_on_spell(self):
        g=self.game();g._summon(0,'JAIL_718');c=self.put(g,'TOKEN_COIN');n=len(g.players[0].deck);self.play(g,c);self.assertEqual(len(g.players[0].deck),n-1)
    def test_geomancer_spell_damage(self):
        g=self.game();g._summon(0,'CATA_EVENT_401');self.assertEqual(g._spell_damage(0),1)
    def test_securitybot_other_minions_only(self):
        g=self.game();m=g._summon(0,'EDR_851t');before=(m.attack,m.health);self.play(g,self.put(g,'JAIL_457'))
        self.assertEqual((m.attack,m.health),(before[0]+1,before[1]+1));bot=next(m for m in g.players[0].minions if m.card_id=='JAIL_457');self.assertEqual(bot.attack,g.cards['JAIL_457']['attack'])
    def test_nathrezim_both_players_minions_only(self):
        g=self.game();m=g._summon(0,'JAIL_890');a=self.put(g,'EDR_851t');b=self.put(g,'EDR_851t',1);s=self.put(g,'TOKEN_COIN')
        self.assertEqual((g._cost(a,0),g._cost(b,1),g._cost(s,0)),(2,2,0));g._silence(m);self.assertEqual(g._cost(a,0),0)
    def test_judgment_snapshots_damaged_current_health(self):
        g=self.game();a=g._summon(0,'JAIL_890');a.health=3;b=g._summon(1,'EDR_851t');atk=a.attack
        self.play(g,self.put(g,'JAIL_326'),a.uid);self.assertEqual((b.attack,b.health,b.max_health),(atk,3,3))
    def test_wannabe_combo_counts_other_plays(self):
        g=self.game();self.play(g,self.put(g,'TOKEN_COIN'));self.play(g,self.put(g,'TOKEN_COIN'));c=self.put(g,'JAIL_909');self.play(g,c)
        m=g.players[0].minions[-1];self.assertEqual(m.attack,g.cards[c.card_id]['attack']+2)
    def test_wannabe_without_combo(self):
        g=self.game();c=self.put(g,'JAIL_909');self.play(g,c);self.assertEqual(g.players[0].minions[-1].attack,g.cards[c.card_id]['attack'])
    def test_hold_them_off(self):
        g=self.game();m=g._summon(0,'EDR_851t');a,h=m.attack,m.health;self.play(g,self.put(g,'JAIL_913'),m.uid)
        self.assertEqual((m.attack,m.health),(a+5,h+5));self.assertIn('LIFESTEAL',m.keywords)
    def test_smuggler(self):
        g=self.game();m=g._summon(0,'EDR_851t');a=m.attack;self.play(g,self.put(g,'JAIL_998'),m.uid)
        self.assertEqual(m.attack,a+2);self.assertIn('RUSH',m.keywords)
    def test_prepare_failure_rolls_back(self):
        g=self.game();c=self.put(g,'JAIL_913');before=deepcopy(g.observe(0))
        with patch.object(g,'_b60_spend_mana',side_effect=RuntimeError('fixture')):
            with self.assertRaises(RuntimeError):self.prepare(g,c)
        self.assertEqual(g.observe(0),before)
    def test_prepare_features_and_opponent_privacy(self):
        g=self.game();c=self.put(g,'JAIL_457');view=g.observe(0)
        self.assertTrue(encode_decision(dict(actor=0,observation=view,actions=view['legal_actions'])))
        self.prepare(g,c);self.assertTrue(g.observe(0)['players'][0]['hand'][0]['rule_state']['prepared'])
        self.assertNotIn('hand',g.observe(1)['players'][0])
