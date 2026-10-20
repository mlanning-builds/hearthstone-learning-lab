"""Production registry paths for the ordered hand Quest and its reward."""
import unittest
from copy import deepcopy
import test_expanded_passive_admission as admission
from expanded import Action,Game
from engine.game import Card

class EndTimeAdmissionTests(unittest.TestCase):
 def game(self,hero='WARLOCK'):
  g=admission.PassiveAdmissionTests().game(hero,'END_017');g.current=0
  for p in g.players:p.hand=[];p.board=[];p.mana=p.max_mana=10;p.health=30;p.armor=0
  return g
 def play(self,g,cid):
  c=g._add(0,cid);g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def full(self,g):
  self.play(g,'END_017')
  for _ in range(10):g._add(0,'TOKEN_COIN')
  self.assertEqual(g.players[0].quest['progress'],1)
 def test_both_classes_accept_quest_in_legal_starting_deck(self):
  for hero in ('WARLOCK','HUNTER'):
   g=Game([admission.PassiveAdmissionTests().deck(hero,'END_017'),admission.PassiveAdmissionTests().deck('WARRIOR','CORE_CS2_122')],seed=98)
   self.assertIn('END_017',[c.card_id for c in g.players[0].hand])
   g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0;g.players[0].mana=10
   card=next(c for c in g.players[0].hand if c.card_id=='END_017')
   g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid))
   self.assertEqual(g.players[0].quest['card_id'],'END_017');self.assertEqual(g.players[0].mana,9)
 def test_empty_before_full_does_not_complete(self):
  g=self.game();self.play(g,'END_017');g._settle();self.assertEqual(g.players[0].quest['progress'],0)
 def test_playing_last_card_completes_before_its_generated_refill(self):
  g=self.game();self.full(g);g.players[0].hand=[];greenfin=g._add(0,'EDR_999')
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==greenfin.uid))
  self.assertIsNone(g.players[0].quest);self.assertEqual(len(g.players[0].hand),2)
  self.assertEqual(sum(c.card_id=='END_017t' for c in g.players[0].hand),1)
 def test_full_hand_burn_does_not_count_as_empty(self):
  g=self.game();self.full(g);g._add(0,'TOKEN_COIN');g._settle()
  self.assertEqual(len(g.players[0].hand),10);self.assertEqual(g.players[0].quest['progress'],1)
 def test_shuffle_all_physical_hand_cards_delivers_once(self):
  g=self.game();self.full(g);cards=list(g.players[0].hand)
  for c in cards:g._shuffle_hand_card(0,c)
  g._settle();g._settle();self.assertIsNone(g.players[0].quest)
  self.assertEqual([c.card_id for c in g.players[0].hand],['END_017t'])
  self.assertTrue({c.uid for c in cards}<={c.uid for c in g.players[0].deck if isinstance(c,Card)})
 def test_reward_paid_play_fills_hand_and_preserves_physical_draws(self):
  g=self.game();draws=[Card(g._new_id(),'TOKEN_COIN') for _ in range(10)];g.players[0].deck=list(draws)
  self.play(g,'END_017t');self.assertEqual(g.players[0].mana,5)
  self.assertEqual(g.players[0].hand,list(reversed(draws)));m=g.players[0].minions[0];self.assertEqual((m.attack,m.health),(8,8))
 def test_reward_draw_on_empty_deck_applies_each_fatigue(self):
  g=self.game();g.players[0].health=100;g.players[0].deck=[];self.play(g,'END_017t')
  self.assertEqual(g.players[0].fatigue,10);self.assertEqual(g.players[0].health,45)
 def test_reward_death_discards_opponent_and_not_owner(self):
  g=self.game();g.players[0].deck=['TOKEN_COIN']*10;self.play(g,'END_017t')
  for _ in range(3):g._add(1,'TOKEN_COIN')
  before=list(g.players[0].hand);g.players[0].minions[0].health=0;g._settle()
  self.assertEqual(g.players[1].hand,[]);self.assertEqual(g.players[0].hand,before)
 def test_silenced_reward_does_not_discard(self):
  g=self.game();g.players[0].deck=['TOKEN_COIN']*10;self.play(g,'END_017t');other=g._add(1,'TOKEN_COIN')
  m=g.players[0].minions[0];g._silence(m);m.health=0;g._settle();self.assertIn(other,g.players[1].hand)
 def test_clone_progress_and_hand_privacy(self):
  g=self.game();self.full(g);clone=deepcopy(g);clone._discard_cards(0,list(clone.players[0].hand));clone._settle()
  self.assertIsNone(clone.players[0].quest);self.assertEqual(g.players[0].quest['progress'],1)
  view=g.observe(1,include_events=False)['players'][0];self.assertEqual(view['quest']['progress'],1);self.assertNotIn('hand',view)

if __name__=='__main__':unittest.main()
