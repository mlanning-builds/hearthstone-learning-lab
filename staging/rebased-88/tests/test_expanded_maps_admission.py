"""Ordinary registry and physical-card paths for the two closed Maps."""
import unittest
from copy import deepcopy
import test_expanded_passive_admission as admission
from expanded import Action
from expanded.murloc_generation import MURLOC_IDS
from expanded.game import Card

class MapAdmissionTests(unittest.TestCase):
 def game(self,cid):
  hero='PALADIN' if cid=='TLC_442' else 'ROGUE'
  g=admission.PassiveAdmissionTests().game(hero,cid);g.current=0
  for p in g.players:p.hand=[];p.board=[];p.mana=p.max_mana=10
  return g
 def play(self,g,cid):
  c=g._add(0,cid);g.players[0].mana=10;self.play_card(g,c);return c
 def play_card(self,g,c):g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
 def choose(self,g,i=0):g.step(Action('choose',choices=(i,)))
 def test_both_maps_have_legal_starting_decks_and_paid_choices(self):
  for cid in ('TLC_442','TLC_515'):
   with self.subTest(cid=cid):
    g=self.game(cid);g.players[0].deck=['CORE_EX1_509','TOKEN_COIN','CORE_CS2_029'];self.play(g,cid)
    self.assertEqual(g.players[0].mana,10-g.cards[cid]['cost']);self.assertEqual(g.pending_choice['kind'],'map_discover');self.assertEqual(len(g.pending_choice['options']),3)
 def test_submerged_uses_complete_real_pool_and_one_discover(self):
  g=self.game('TLC_442');self.play(g,'TLC_442');options=deepcopy(g.pending_choice['options'])
  self.assertTrue({o['card_id'] for o in options}<=set(MURLOC_IDS));self.assertEqual(len({o['card_id'] for o in options}),3)
  self.choose(g);c=g.players[0].hand[0];others=deepcopy(c._follow_effects[0]['map_options'])
  g.players[0].mana=10;self.play_card(g,c)
  # A selected Holmes may first open its own private investigation.
  while g.pending_choice and g.pending_choice['kind']!='map_follow':self.choose(g)
  self.assertEqual(g.pending_choice['options'],others);self.choose(g);self.assertEqual(g.players[0].discoveries_total,1)
 def test_cultist_can_select_another_physical_copy_of_itself(self):
  g=self.game('TLC_515');physical=Card(g._new_id(),'TLC_515');g.players[0].deck=[physical]
  self.play(g,'TLC_515');self.assertEqual(g.pending_choice['options'][0]['uid'],physical.uid);self.choose(g)
  self.assertIs(g.players[0].hand[0],physical);self.assertEqual(g.players[0].deck,[])
 def test_cultist_follow_uses_original_unchosen_physical_cards_after_shuffle(self):
  g=self.game('TLC_515');g.players[0].deck=['TOKEN_COIN','CORE_EX1_509','CORE_CS2_029'];self.play(g,'TLC_515')
  i=next(i for i,o in enumerate(g.pending_choice['options']) if o['card_id']=='TOKEN_COIN');self.choose(g,i)
  c=g.players[0].hand[0];uids={o['uid'] for o in c._follow_effects[0]['map_options']};g.players[0].deck.reverse();self.play_card(g,c)
  self.assertEqual({o['uid'] for o in g.pending_choice['options']},uids);self.choose(g);self.assertEqual(len(g.players[0].deck),1)
 def test_follow_expires_after_owner_turn(self):
  g=self.game('TLC_515');g.players[0].deck=['TOKEN_COIN','CORE_EX1_509'];self.play(g,'TLC_515')
  i=next(i for i,o in enumerate(g.pending_choice['options']) if o['card_id']=='TOKEN_COIN');self.choose(g,i);c=g.players[0].hand[0]
  g.step(Action('end'));g.step(Action('end'));self.play_card(g,c);self.assertIsNone(g.pending_choice)
 def test_selected_hand_options_are_private(self):
  g=self.game('TLC_515');g.players[0].deck=['TOKEN_COIN','CORE_EX1_509'];self.play(g,'TLC_515');self.choose(g)
  self.assertNotIn('map_options',str(g.observe(1,include_events=False)))
 def test_coin_transformation_removes_only_cultist_follow(self):
  g=self.game('TLC_515');g.players[0].deck=['CORE_EX1_509','CORE_CS2_029'];self.play(g,'TLC_515');self.choose(g);c=g.players[0].hand[0]
  self.assertTrue(c._follow_effects);uid=c.uid;self.play(g,'CATA_200')
  self.assertEqual(g.pending_choice['kind'],'hand_transform')
  i=next(i for i,o in enumerate(g.pending_choice['options']) if o['uid']==uid);self.choose(g,i)
  coin=next(c for c in g.players[0].hand if c.card_id=='TOKEN_COIN')
  self.assertNotEqual(coin.uid,uid);self.assertFalse(getattr(coin,'_follow_effects',[]));self.play_card(g,coin);self.assertIsNone(g.pending_choice)
 def test_empty_deck_map_has_no_choice_or_draw(self):
  g=self.game('TLC_515');g.players[0].deck=[];health=g.players[0].health;self.play(g,'TLC_515')
  self.assertIsNone(g.pending_choice);self.assertEqual(g.players[0].health,health);self.assertEqual(g.players[0].hand,[])
if __name__=='__main__':unittest.main()
