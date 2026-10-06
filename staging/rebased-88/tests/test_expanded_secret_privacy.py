import json
import unittest
from expanded import Game,Action,random_deck
from expanded.game import Card

class SecretPrivacyTests(unittest.TestCase):
    def game_with_secret(self,cid):
        g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        g.step(Action('mulligan'));g.step(Action('mulligan'))
        p=g.players[0];p.hand=[];p.mana=p.max_mana=10
        c=Card(g._new_id(),cid);p.hand.append(c);g.step(Action('play',c.uid))
        return g
    def test_opponent_history_masks_identity_but_owner_keeps_it(self):
        g=self.game_with_secret('CORE_EX1_287')
        own=g.observe(0)['players'][0];other=g.observe(1)['players'][0]
        self.assertEqual(own['played_history'][-1]['card_id'],'CORE_EX1_287')
        self.assertEqual(other['played_history'][-1]['card_id'],'SECRET')
        self.assertEqual(other['rule_counters']['spells_turn'],['SECRET'])
        self.assertEqual(other['kindred_history']['played_schools'],[])
        self.assertTrue(other['kindred_history']['played_schools_hidden'])
    def test_same_cost_hidden_secrets_have_identical_opponent_views(self):
        a=self.game_with_secret('CORE_EX1_287');b=self.game_with_secret('CORE_EX1_289')
        self.assertEqual(a.observe(1),b.observe(1))
    def test_history_stays_masked_after_rotation_to_previous_turn(self):
        g=self.game_with_secret('CORE_EX1_287')
        g.step(Action('end'));g.step(Action('end'))
        other=g.observe(1)['players'][0]
        self.assertEqual(other['rule_counters']['spells_previous'],['SECRET'])
        self.assertEqual(other['kindred_history']['previous_schools'],[])
    def test_observation_redaction_does_not_mutate_engine_history(self):
        g=self.game_with_secret('CORE_EX1_287');before=list(g.players[0].spells_turn)
        g.observe(1);g.observe(1,include_events=False)
        self.assertEqual(g.players[0].spells_turn,before)
        self.assertEqual(g.players[0].played_history[-1]['card_id'],'CORE_EX1_287')
