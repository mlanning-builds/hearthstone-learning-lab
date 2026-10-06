"""Exercise new choice types through the exact policy-facing interface."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'staging/rebased-88'))
from expanded import random_deck
from expanded.environment import PolicyEnvironment
from expanded.game import Card

class PolicyChoiceTests(unittest.TestCase):
    def prepare(self,cid,other=()):
        env=PolicyEnvironment(experimental=True)
        d=env.reset([random_deck('HUNTER',31),random_deck('WARRIOR',53)],seed=71,max_actions=30)
        for _ in range(2):d=env.step(0,revision=d['revision'])
        # Fixture construction happens outside the policy boundary.
        g=env._game;p=g.players[0];p.hand=[];p.mana=p.max_mana=10
        for name in other:p.hand.append(Card(g._new_id(),name))
        c=Card(g._new_id(),cid);p.hand.append(c)
        d=env.decision();index=next(i for i,a in enumerate(d['actions']) if a['kind']=='play' and a['source']==c.uid)
        return env,env.step(index,revision=d['revision'])
    def choose(self,env,d,index):return env.step(index,revision=d['revision'])
    def test_fixed_summon_choice_through_policy(self):
        env,d=self.prepare('MEND_301')
        self.assertEqual(d['action_mask'],[True]*3)
        self.assertEqual([a['kind'] for a in d['actions']],['choose']*3)
        chosen=d['observation']['pending_choice']['options'][2]['card_id']
        after=self.choose(env,d,2)
        self.assertEqual(after['observation']['players'][0]['board'][-1]['card_id'],chosen)
        self.assertIsNone(after['observation']['pending_choice'])
    def test_self_effect_choice_has_labels_without_internal_effects(self):
        env,d=self.prepare('TLC_242');options=d['observation']['pending_choice']['options']
        self.assertEqual([o['label'] for o in options],['Taunt','Poisonous','+1/+1'])
        self.assertTrue(all('operation' not in o for o in options))
        after=self.choose(env,d,1)
        self.assertIn('POISONOUS',after['observation']['players'][0]['board'][0]['keywords'])
    def test_hand_transform_choice_preserves_specific_duplicate_identity(self):
        env,d=self.prepare('CATA_200',('CORE_EX1_506','CORE_EX1_506'))
        options=d['observation']['pending_choice']['options'];first_uid=options[0]['uid']
        after=self.choose(env,d,1);hand=after['observation']['players'][0]['hand']
        self.assertEqual(hand[0]['uid'],first_uid);self.assertEqual(hand[1]['card_id'],'TOKEN_COIN')
        with self.assertRaises(ValueError):env.step(0,revision=d['revision'])
    def test_hand_copy_choice_through_policy_keeps_identity_private(self):
        env,d=self.prepare('CATA_697',('CORE_BT_035','CORE_CS2_029'))
        options=d['observation']['pending_choice']['options']
        self.assertEqual(len(options),1);self.assertEqual(options[0]['card_id'],'CORE_BT_035')
        self.assertNotIn('options',env._game.observe(1)['pending_choice'])
        after=self.choose(env,d,0);hand=after['observation']['players'][0]['hand']
        copies=[c for c in hand if c['card_id']=='CORE_BT_035']
        self.assertEqual(len(copies),2);self.assertNotEqual(copies[0]['uid'],copies[1]['uid'])
        self.assertIsNone(after['observation']['pending_choice'])
    def test_hand_shuffle_resumes_draw_through_policy(self):
        env,d=self.prepare('CATA_721',('CORE_EX1_506','CORE_EX1_506'))
        options=d['observation']['pending_choice']['options'];first_uid=options[0]['uid']
        before_deck=len(env._game.players[0].deck)
        self.assertEqual(d['action_mask'],[True,True])
        after=self.choose(env,d,1);hand=after['observation']['players'][0]['hand']
        self.assertEqual(hand[0]['uid'],first_uid);self.assertEqual(len(hand),2)
        self.assertEqual(len(env._game.players[0].deck),before_deck)
        self.assertIsNone(after['observation']['pending_choice'])
        with self.assertRaises(ValueError):env.step(0,revision=d['revision'])
    def test_opponent_owned_choice_routes_to_its_owner(self):
        env,d=self.prepare('CATA_697',('CORE_BT_035',))
        g=env._game;g.pending_choice['owner']=1
        c=Card(g._new_id(),'CORE_BT_035');g.players[1].hand=[c]
        g.pending_choice['options']=[dict(card_id=c.card_id,uid=c.uid)]
        d=env.decision()
        self.assertEqual(d['actor'],1);self.assertEqual(g.current,0)
        self.assertEqual(d['observation']['pending_choice']['options'][0]['uid'],c.uid)
        self.assertNotIn('hand',d['observation']['players'][0])
        after=self.choose(env,d,0)
        self.assertEqual(len(g.players[1].hand),2);self.assertEqual(after['actor'],0)
