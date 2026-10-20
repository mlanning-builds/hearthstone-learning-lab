"""Paid Inspector paths; client timing certification remains separate.

Rule references: Inven's June 17 original reveal and Blizzard's 36.0.1
hotfix (Inspector cannot trigger on the investigating player's own turn).
"""
import unittest
from copy import deepcopy
from expanded import Action
import test_expanded_passive_admission as admission

class HolmesAdmissionTests(unittest.TestCase):
 def game(self):
  helper=admission.PassiveAdmissionTests()
  g=helper.game('MAGE','JAIL_851');g.current=0
  for p in g.players:
   p.hand=[];p.board=[];p.deck=['CORE_CS2_029']*12
   p.mana=p.max_mana=10;p.health=30;p.armor=0
  return g
 def play(self,g,owner,cid,target=0):
  self.assertEqual(g.current,owner)
  g.players[owner].mana=10;c=g._add(owner,cid)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
  return c
 def inspect(self,g,cid='CORE_CS2_029'):
  g._add(1,cid);self.play(g,0,'JAIL_851')
  index=next(i for i,o in enumerate(g.pending_choice['options']) if o['card_id']==cid)
  g.step(next(a for a in g.legal_actions() if a.kind=='choose' and a.choices==(index,)))
 def coins(self,g):return sum(c.card_id=='TOKEN_COIN' for c in g.players[0].hand)
 def end(self,g):g.step(Action('end'))
 def test_paid_body_and_private_offer(self):
  g=self.game()
  for cid in ['CORE_CS2_029']*6:g._add(1,cid)
  self.play(g,0,'JAIL_851');self.assertEqual(g.players[0].mana,6)
  self.assertEqual((g.players[0].minions[0].attack,g.players[0].minions[0].health),(4,5))
  self.assertEqual(len(g.pending_choice['options']),4)
  self.assertTrue(g.observe(1)['pending_choice']['waiting'])
  self.assertEqual(len(g.observe(0)['pending_choice']['options']),4)
 def test_short_hand_offers_every_physical_card(self):
  g=self.game();g._add(1,'CORE_CS2_029');g._add(1,'CORE_CS2_029');self.play(g,0,'JAIL_851')
  self.assertEqual(len(g.pending_choice['options']),2)
 def test_empty_hand_leaves_no_choice_or_watch(self):
  g=self.game();self.play(g,0,'JAIL_851');self.assertIsNone(g.pending_choice)
  self.assertFalse(getattr(g.players[0],'_hand_investigations',[]))
 def test_next_enemy_turn_pays_once(self):
  g=self.game();self.inspect(g);self.end(g);self.play(g,1,'CORE_CS2_029',-1)
  self.assertEqual(self.coins(g),3);self.play(g,1,'CORE_CS2_029',-1);self.assertEqual(self.coins(g),3)
 def test_watch_is_private_after_choice(self):
  g=self.game();self.inspect(g)
  self.assertEqual(g.observe(0)['players'][0]['hand_investigations'][0]['name'],'Fireball')
  self.assertNotIn('hand_investigations',g.observe(1)['players'][0])
 def test_source_silence_and_death_do_not_cancel_commitment(self):
  g=self.game();self.inspect(g);m=g.players[0].minions[0]
  g._silence(m);m.health=0;g._settle();self.end(g);self.play(g,1,'CORE_CS2_029',-1)
  self.assertEqual(self.coins(g),3)
 def test_unmatched_watch_expires_at_end_of_enemy_turn(self):
  g=self.game();self.inspect(g);self.end(g);self.end(g)
  self.assertFalse(g.observe(0)['players'][0]['hand_investigations'])
  self.end(g);self.play(g,1,'CORE_CS2_029',-1);self.assertEqual(self.coins(g),0)
 def test_extra_investigator_turn_does_not_expire_watch(self):
  g=self.game();self.inspect(g);g.players[0].extra_turns_pending=1
  self.end(g);self.assertEqual(g.current,0);self.play(g,0,'CORE_CS2_029',-2)
  self.assertEqual(self.coins(g),0);self.end(g);self.play(g,1,'CORE_CS2_029',-1);self.assertEqual(self.coins(g),3)
 def test_multiple_commitments_each_pay_once(self):
  g=self.game();self.inspect(g);self.play(g,0,'JAIL_851')
  g.step(next(a for a in g.legal_actions() if a.kind=='choose' and a.choices==(0,)))
  self.end(g);self.play(g,1,'CORE_CS2_029',-1);self.assertEqual(self.coins(g),6)
 def test_full_hand_burns_reward_without_deferred_payment(self):
  g=self.game();self.inspect(g)
  for _ in range(10):g._add(0,'CORE_CS2_029')
  self.end(g);self.play(g,1,'CORE_CS2_029',-1)
  self.assertEqual(len(g.players[0].hand),10);self.assertEqual(self.coins(g),0)
  g.players[0].hand=[];self.play(g,1,'CORE_CS2_029',-1);self.assertEqual(self.coins(g),0)
 def test_clone_commitments_are_independent(self):
  g=self.game();self.inspect(g);clone=deepcopy(g)
  self.end(g);self.play(g,1,'CORE_CS2_029',-1)
  self.assertEqual(self.coins(g),3);self.assertEqual(self.coins(clone),0)
  self.assertEqual(len(clone.players[0]._hand_investigations),1)
 def test_different_identity_with_same_name_matches(self):
  g=self.game();self.inspect(g);self.end(g)
  # Isolate the printed-name contract without admitting another card body.
  g.cards['CORE_EX1_162']=dict(g.cards['CORE_EX1_162'],name='Fireball')
  self.play(g,1,'CORE_EX1_162');self.assertEqual(self.coins(g),3)
 def test_enemy_play_notification_on_investigator_turn_cannot_pay(self):
  g=self.game();self.inspect(g);c=g.players[1].hand[0]
  g.players[1].turns_taken+=1
  g._investigation_played(1,c);g._settle();self.assertEqual(self.coins(g),0)
  self.assertEqual(len(g.players[0]._hand_investigations),1)
 def test_internal_cast_does_not_count_as_a_paid_play(self):
  g=self.game();self.inspect(g);self.end(g)
  g._start_play_effects([('damage_enemy_hero',1)],dict(owner=1,source=None,target=0,bonus=0,lifesteal=False,card_id='CORE_CS2_029',spell=True))
  g._settle();self.assertEqual(self.coins(g),0)
 def test_countered_paid_spell_still_counts_as_played(self):
  g=self.game();self.inspect(g);g._place_secret(0,'CORE_EX1_287');self.end(g)
  health=g.players[0].health;self.play(g,1,'CORE_CS2_029',-1)
  self.assertEqual(g.players[0].health,health);self.assertEqual(self.coins(g),3)

if __name__=='__main__':unittest.main()
