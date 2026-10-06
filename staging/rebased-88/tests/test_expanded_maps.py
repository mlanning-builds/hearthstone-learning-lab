"""Map choices preserve physical identity, options, expiry and information."""
import unittest
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import Action,cards,maps
from expanded.game import Card
from standard.catalog import load_all_records
from engine.cards import UnsupportedCard
class MapTests(unittest.TestCase):
 def setUp(self):
  self.h=fixtures.GenerationTests();self.g=self.h.game();self.p=self.g.players[0]
  records={c['id']:c for c in load_all_records()};self.g.cards.update({cid:records[cid] for cid in maps.RULES})
  p=patch.dict(cards.RULES,maps.RULES);p.start();self.addCleanup(p.stop)
 def play(self,cid):
  self.p.mana=10;c=Card(self.g._new_id(),cid);self.p.hand.append(c);self.play_card(c);return c
 def play_card(self,c):
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
 def choose(self,index=0):self.g.step(Action('choose',choices=(index,)))
 def install(self,cid,**extra):
  ids=[]
  for n in range(3):
   d=deepcopy(self.g.cards['CS3_025']);d.update(id='MAP_TEST_'+str(n),dbfId=-600-n,cost=0,races=['MURLOC'],attack=3,**extra)
   self.g.cards[d['id']]=d;ids.append(d['id'])
  p=patch.dict(cards.RULES,{cid:('none',[]) for cid in ids});p.start();self.addCleanup(p.stop)
  self.h.install(self.g,maps.REQUESTS[cid],ids);return ids
 def test_all_six_staged(self):self.assertEqual(len(maps.RULES),6);self.assertFalse(set(maps.RULES)&cards.COLLECTIBLE_IDS)
 def test_first_choice_remembers_exact_others(self):
  self.install('TLC_442');self.play('TLC_442');options=deepcopy(self.g.pending_choice['options']);self.choose()
  self.assertEqual(self.p.hand[0]._follow_effects[0]['map_options'],options[1:]);self.assertEqual(self.p.discoveries_total,1)
 def test_play_opens_original_options_only_once(self):
  self.install('TLC_442');self.play('TLC_442');self.choose();c=self.p.hand[0];others=deepcopy(c._follow_effects[0]['map_options']);self.play_card(c)
  self.assertEqual(self.g.pending_choice['options'],others);self.choose();self.assertEqual(self.p.discoveries_total,1)
  self.assertFalse(getattr(self.p.hand[0],'_follow_effects',[]))
 def test_followup_expires_at_turn_end(self):
  self.install('TLC_442');self.play('TLC_442');self.choose();c=self.p.hand[0]
  self.g.step(Action('end'));self.g.step(Action('end'));self.play_card(c);self.assertIsNone(self.g.pending_choice)
 def test_summoning_is_not_playing(self):
  self.install('TLC_442');self.play('TLC_442');self.choose();self.g._summon(0,self.p.hand[0].card_id);self.g._settle();self.assertIsNone(self.g.pending_choice)
 def test_pending_choice_clone(self):
  self.install('TLC_442');self.play('TLC_442');other=deepcopy(self.g);a=Action('choose',choices=(1,));self.g.step(a);other.step(a)
  self.assertEqual(self.g.observe(0),other.observe(0))
 def test_options_hidden_from_enemy_hand_view(self):
  ids=self.install('TLC_442');self.play('TLC_442');self.choose()
  self.assertFalse(any(cid in str(self.g.observe(1,include_events=False)) for cid in ids))
 def test_missing_pool_rolls_back(self):
  c=Card(self.g._new_id(),'TLC_442');self.p.hand.append(c);a=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid)
  with self.assertRaises(UnsupportedCard):self.g.step(a)
  self.assertEqual(len(self.g.players[0].hand),1)
 def test_deck_map_removes_card_without_draw_event(self):
  self.p.deck=['CS3_025','CORE_CS2_029','TOKEN_COIN'];self.play('TLC_515');before=len(self.p.deck);self.choose()
  self.assertEqual(len(self.p.deck),before-1);self.assertEqual(len(self.p.hand),1)
 def test_deck_follow_tracks_uid_after_shuffle(self):
  self.p.deck=['CS3_025','CORE_CS2_029','TOKEN_COIN'];self.play('TLC_515');i=next(i for i,o in enumerate(self.g.pending_choice['options']) if o['card_id']=='TOKEN_COIN');self.choose(i)
  self.p.deck.reverse();self.play_card(self.p.hand[0]);self.assertEqual(len(self.g.pending_choice['options']),2);self.choose();self.assertEqual(len(self.p.deck),1)
 def test_deck_follow_does_not_choose_card_already_drawn(self):
  self.p.deck=['CS3_025','CORE_CS2_029','TOKEN_COIN'];self.play('TLC_515');i=next(i for i,o in enumerate(self.g.pending_choice['options']) if o['card_id']=='TOKEN_COIN');self.choose(i)
  coin=self.p.hand[0];self.g._draw(0);self.g._settle();self.play_card(coin);self.assertEqual(len(self.g.pending_choice['options']),1)
 def test_odd_attack_filter_uses_printed_attack(self):
  ids=self.install('TLC_824');
  for cid in ids:self.g.cards[cid]['races']=['BEAST']
  self.g.cards[ids[0]]['attack']=2;self.play('TLC_824');self.assertEqual(len(self.g.pending_choice['options']),2)
 def test_unplayed_type_uses_whole_game_history(self):
  ids=self.install('TLC_464');self.p.played_history=[dict(card_id=ids[0],cost=0)]
  self.g.cards[ids[1]]['races']=['MURLOC','DRAGON'];self.play('TLC_464');self.assertEqual([o['card_id'] for o in self.g.pending_choice['options']],[ids[1]])
 def test_frost_rune_pool(self):
  ids=self.install('TLC_435',runeCost={'frost':1});self.play('TLC_435');self.choose();self.assertIn(self.p.hand[0].card_id,ids)
 def test_fel_spell_pool_and_play_followup(self):
  ids=self.install('TLC_900',type='SPELL',spellSchool='FEL')
  self.play('TLC_900');self.choose();self.play_card(self.p.hand[0]);self.assertEqual(len(self.g.pending_choice['options']),2)
 def test_full_hand_burn_does_not_attach_followup(self):
  self.install('TLC_442');self.play('TLC_442')
  self.p.hand=[Card(500+i,'CORE_CS2_029') for i in range(10)];self.choose();self.assertTrue(all(not getattr(c,'_follow_effects',[]) for c in self.p.hand))
 def test_copy_does_not_share_mutable_option_list(self):
  self.install('TLC_442');self.play('TLC_442');self.choose();c=self.p.hand[0];copy=self.g._copy_card(c)
  copy._follow_effects[0]['map_options'].clear();self.assertEqual(len(c._follow_effects[0]['map_options']),2)
