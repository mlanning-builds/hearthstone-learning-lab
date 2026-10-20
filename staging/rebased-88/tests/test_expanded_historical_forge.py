"""Forge preserves physical hand identity, excludes played-card triggers and privacy leaks."""
import unittest,json
from copy import deepcopy
from unittest.mock import patch
from expanded import Action,cards
import test_expanded_generation as fixtures
class HistoricalForgeTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def test_two_mana_upgrade_preserves_physical_hand_position_modifiers_and_no_play(self):
  g=self.game();p=g.players[0];a=g._add(0,'CORE_CS2_029');c=g._add(0,'YOG_525');b=g._add(0,'CORE_EX1_162')
  c.attack_bonus=3;c.health_bonus=2;c.cost_delta=-1;uid=c.uid;p.mana=2;rng=g.rng.getstate();before_deck=deepcopy(p.deck)
  g.step(Action('forge',source=uid))
  self.assertEqual(p.hand,[a,c,b]);self.assertEqual(c.uid,uid);self.assertEqual(c.card_id,'YOG_525t')
  self.assertEqual((c.attack_bonus,c.health_bonus,c.cost_delta),(3,2,-1));self.assertEqual(p.mana,0)
  self.assertEqual(p.cards_played,0);self.assertFalse(p.played_history);self.assertFalse(p.spells_turn)
  self.assertEqual((b.attack_bonus,b.health_bonus),(0,0));self.assertEqual(g.rng.getstate(),rng);self.assertEqual(p.deck,before_deck)
  self.assertFalse(any(a.kind=='forge' and a.source==uid for a in g.legal_actions()))
 def test_forge_allowed_without_board_room_or_enough_mana_to_play_body(self):
  g=self.game();p=g.players[0]
  for _ in range(7):g._summon(0,'CORE_CS2_188')
  c=g._add(0,'YOG_525');p.mana=2
  self.assertFalse(any(a.kind=='play' and a.source==c.uid for a in g.legal_actions()))
  g.step(Action('forge',source=c.uid));self.assertEqual(c.card_id,'YOG_525t');self.assertEqual(len(p.board),7)
 def test_unforged_and_forged_battlecries_have_distinct_hand_buffs(self):
  for forge,amount in ((False,1),(True,2)):
   with self.subTest(forge=forge):
    g=self.game();p=g.players[0];target=g._add(0,'CORE_EX1_162');c=g._add(0,'YOG_525')
    if forge:g.step(Action('forge',source=c.uid))
    p.mana=10;g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    self.assertEqual((target.attack_bonus,target.health_bonus),(amount,amount));self.assertEqual(p.cards_played,1)
 def test_forging_private_identity_not_leaked_to_opponent(self):
  g=self.game();c=g._add(0,'YOG_525');g.step(Action('forge',source=c.uid));view=g.observe(1)
  self.assertNotIn('YOG_525',str(view));self.assertNotIn('YOG_525t',str(view))
  self.assertEqual([e for e in view['events'] if e['event']=='forge'],[dict(turn=g.turn,event='forge',player=0,spent=2)])
 def test_illegal_or_failed_forge_rolls_back_state_and_rng(self):
  g=self.game();p=g.players[0];c=g._add(0,'YOG_525');p.mana=1;before=deepcopy(g.__dict__)
  with self.assertRaises(ValueError):g.step(Action('forge',source=c.uid))
  self.assertEqual(g.players,before['players']);self.assertEqual(g.rng.getstate(),before['rng'].getstate())
  p.mana=10;before=deepcopy(g.__dict__)
  with patch.object(g,'_b60_spend_mana',side_effect=ValueError('injected')):
   with self.assertRaisesRegex(ValueError,'injected'):g.step(Action('forge',source=c.uid))
  self.assertEqual(g.players,before['players']);self.assertEqual(g.rng.getstate(),before['rng'].getstate())
 def test_forge_is_generated_only(self):
  self.assertTrue({'YOG_525','YOG_525t'}<=cards.TOKEN_IDS&cards.PLAYABLE_TOKENS)
  self.assertFalse({'YOG_525','YOG_525t'}&cards.COLLECTIBLE_IDS)

 def test_visible_feature_encoding_accepts_forge_without_training(self):
  from expanded.features import encode_decision
  g=self.game();c=g._add(0,'YOG_525');view=g.observe(0)
  actions=view['legal_actions'];rows=encode_decision(dict(actor=0,observation=view,actions=actions))
  index=next(i for i,a in enumerate(actions) if a['kind']=='forge' and a['source']==c.uid)
  self.assertEqual(rows[index][json.dumps(['kind','forge'])],1.0)
  self.assertEqual(len(rows),len(actions))
