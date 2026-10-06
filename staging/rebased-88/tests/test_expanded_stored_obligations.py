import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,stored_obligations as rules,Action
from engine.game import Card
from engine.cards import UnsupportedCard
from expanded.pools import GenerationPool

class StoredObligationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in rules.RULES})
  p=patch.dict(cards.RULES,rules.RULES);p.start();self.addCleanup(p.stop)
 def run_ops(self,ops,**kw):
  ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False);ctx.update(kw)
  self.g._start_play_effects(ops,ctx);self.g._settle(allow_event_choices=True)
 def void(self):return [entry for entry in self.g._stored_payloads.values() if entry['kind']=='void'][0]
 def take(self):
  key=next(k for k,e in self.g._stored_payloads.items() if e['kind']=='void');self.run_ops([('obligation_void_take',key)])
 def test_irida_retains_one_actual_card_and_moves_rest(self):
  original=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(5)];self.p.deck=original[:]
  self.run_ops([('obligation_void',)]);self.assertEqual(len(self.p.deck),1);self.assertEqual(len(self.void()['values']),4)
  self.assertEqual({c.uid for c in self.p.deck+self.void()['values']},{c.uid for c in original});self.assertFalse(self.p.hand)
 def test_irida_returns_finite_cards_once_preserving_identity_and_modifiers(self):
  original=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(4)]
  for c in original:c.cost_delta=-1;c._starting_owner=0;c._starting_identity=self.g.cards[c.card_id].get('countAsCopyOfDbfId',self.g.cards[c.card_id].get('dbfId',c.card_id))
  self.p.deck=original[:];self.run_ops([('obligation_void',)])
  for _ in range(8):self.take()
  self.assertEqual(len(self.p.hand),3);self.assertTrue(all(c.cost_delta==-1 and self.g._started_in_deck(c,0) for c in self.p.hand));self.assertFalse(self.void()['values'])
 def test_irida_does_not_prevent_regular_draw_or_fatigue(self):
  self.p.deck=['CORE_CS2_029','CORE_CS2_029'];self.run_ops([('obligation_void',)]);self.take();self.g._draw(0);self.g._draw(0)
  self.assertEqual(self.p.fatigue,1);self.assertEqual(self.p.health,29);self.assertEqual(len(self.p.hand),2)
 def test_irida_full_hand_consumes_void_card_without_godfrey_recovery(self):
  self.run_ops([('obligation_void',)]);before=len(self.void()['values']);self.p.overdraw_return_active=True
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.take();self.assertEqual(len(self.void()['values']),before-1);self.assertEqual(len(self.p.hand),10);self.assertFalse(self.p.overdraw_cache)
 def test_irida_trigger_is_player_bound_not_source_bound(self):
  source=self.g._summon(0,'JAIL_719');self.run_ops([('obligation_void',)],source=source);self.g._silence(source);source.health=0;self.g._settle()
  entries=self.g._obligation_turn_entries('start');self.assertEqual(len(entries),1)
  self.run_ops(entries[0]['operations']);self.assertEqual(len(self.p.hand),2)
 def test_void_trigger_is_owner_start_only(self):
  self.run_ops([('obligation_void',)]);self.assertFalse(self.g._obligation_turn_entries('end'));self.g.current=1;self.assertFalse(self.g._obligation_turn_entries('start'))
 def test_empty_and_one_card_decks_do_not_create_extra_cards(self):
  for deck in ([],['CORE_CS2_029']):
   self.p.deck=deck[:];self.run_ops([('obligation_void',)]);self.assertEqual(self.p.deck,deck)
  self.assertFalse(self.g._obligation_turn_entries('start'))
 def test_void_contents_not_exposed_in_either_observation(self):
  self.run_ops([('obligation_void',)])
  for viewer in (0,1):
   view=self.g.observe(viewer)['players'][0];self.assertEqual(view['void_remaining'],11);self.assertNotIn('CORE_CS2_029',str(view.get('set_aside_cards')))
 def toki(self):
  cid='TEST_PAST_TOKI';self.g.cards[cid]=dict(id=cid,name=cid,type='SPELL',cost=0,cardClass='MAGE',set='EXPERT1',collectible=True)
  p=patch.dict(cards.RULES,{cid:('none',[('armor',1)])});p.start();self.addCleanup(p.stop)
  self.g._generation_pools={(rules.PAST_SPELLS,self.p.hero_class):GenerationPool('fixture',(cid,),'Controlled past pool')}
  self.run_ops([('obligation_toki',)]);return cid
 def play(self,card):self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid))
 def test_toki_requires_three_distinct_original_physical_spells(self):
  self.toki();spells=self.p.hand[:]
  for c in spells[:2]:self.play(c)
  self.assertFalse(any(c.card_id=='TIME_861' for c in self.p.hand));self.play(spells[2]);self.assertEqual([c.card_id for c in self.p.hand],['TIME_861'])
 def test_toki_burned_original_keeps_reward_unreachable(self):
  for _ in range(8):self.g._add(0,'TOKEN_COIN')
  cid=self.toki()
  for c in [c for c in self.p.hand if c.card_id==cid]:self.play(c)
  self.assertFalse(any(c.card_id=='TIME_861' for c in self.p.hand));self.assertEqual(self.g._obligation_view(0,0)['toki_tasks_remaining'],[1])
 def test_copy_of_toki_spell_cannot_replace_original(self):
  self.toki();original=self.p.hand[0];copy=self.g._clone_hand_card(0,original);self.play(copy)
  self.assertEqual(self.g._obligation_view(0,0)['toki_tasks_remaining'],[3])
 def test_transformed_minion_does_not_fulfill_spell_requirement(self):
  self.toki();c=self.p.hand[0];self.g._b60_transform_card(c,'NEW1_034');self.play(c)
  self.assertEqual(self.g._obligation_view(0,0)['toki_tasks_remaining'],[3])
 def test_opponent_play_cannot_complete_original_owner_task(self):
  self.toki();c=self.p.hand.pop();self.q.hand.append(c);self.g.current=1;self.play(c)
  self.assertEqual(self.g._obligation_view(0,0)['toki_tasks_remaining'],[3])
 def test_internal_cast_does_not_count_as_player_play(self):
  self.toki();c=self.p.hand[0];self.run_ops([('cast_zone_spell','hand',c.uid,'random')])
  self.assertEqual(self.g._obligation_view(0,0)['toki_tasks_remaining'],[3])
 def test_duplicate_notification_does_not_count_twice(self):
  self.toki();c=self.p.hand[0]
  for _ in range(2):self.g._obligation_event('spell_cast',dict(owner=0,physical_card=c))
  self.assertEqual(self.g._obligation_view(0,0)['toki_tasks_remaining'],[2])
 def test_toki_tasks_clone_without_shared_sets(self):
  self.toki();clone=deepcopy(self.g);self.play(self.p.hand[0]);self.assertEqual(clone._obligation_view(0,0)['toki_tasks_remaining'],[3])
 def test_opponent_cannot_see_toki_private_progress(self):
  self.toki();self.assertNotIn('toki_tasks_remaining',self.g.observe(1)['players'][0]);self.assertEqual(self.g.observe(0)['players'][0]['toki_tasks_remaining'],[3])
 def test_missing_toki_contract_preserves_hand(self):
  with self.assertRaises(UnsupportedCard):self.run_ops([('obligation_toki',)])
  self.assertFalse(self.p.hand)
