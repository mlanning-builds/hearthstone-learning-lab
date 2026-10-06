import unittest
from expanded.discover_offer import capture_offer
from expanded.generation_cards import pool,discover
from expanded import Action
import test_expanded_generation as fixtures
class DiscoverOfferTests(unittest.TestCase):
 def test_snapshot_survives_choice_mutation(self):
  c=dict(owner=0,kind='generation_discover',options=[dict(card_id='a',stats=[1]),dict(card_id='b')]);o=capture_offer(c,0);c['options'][0]['stats'][0]=9;c['options'].clear();self.assertEqual(o.selected['stats'],[1]);self.assertEqual(o.unchosen,({'card_id':'b'},))
 def test_equal_options_exclude_only_selected_position(self):
  o=capture_offer(dict(owner=0,kind='x',options=[dict(card_id='a'),dict(card_id='a')]),1);self.assertEqual(len(o.unchosen),1)
 def test_small_offer_has_no_invented_options(self):
  o=capture_offer(dict(owner=0,kind='x',options=[dict(card_id='a')]),0);self.assertEqual(o.unchosen,())
 def test_bad_index_rejected(self):
  for i in (-1,True,2):
   with self.assertRaises(ValueError):capture_offer(dict(owner=0,kind='x',options=[{}]),i)
 def game(self):
  fx=fixtures.GenerationTests();g=fx.game();r=pool();fx.install(g,r,['TOKEN_COIN','CORE_CS2_029']);events=[];old=g._queue_event
  def capture(kind,**data):
   if kind=='discover_completed':events.append(data)
   return old(kind,**data)
  g._queue_event=capture
  return fx,g,r,events
 def test_completed_discover_publishes_original_offer(self):
  fx,g,r,events=self.game();fx.run_ops(g,[discover(r)]);offered=[dict(x) for x in g.pending_choice['options']];g.step(Action('choose',choices=(0,)));self.assertEqual(events[0]['offer'].selected,offered[0]);self.assertEqual(events[0]['offer'].unchosen,tuple(offered[1:]));self.assertEqual(g.players[0].discoveries_total,1)
 def test_no_event_before_selection(self):
  fx,g,r,events=self.game();fx.run_ops(g,[discover(r)]);self.assertEqual(events,[])
 def test_consecutive_offers_remain_separate(self):
  fx,g,r,events=self.game();fx.run_ops(g,[discover(r),discover(r)]);g.step(Action('choose',choices=(0,)));g.step(Action('choose',choices=(1,)));self.assertEqual(len(events),2);self.assertEqual([e['offer'].selected_index for e in events],[0,1])
 def test_public_history_does_not_publish_unchosen_ids(self):
  fx,g,r,events=self.game();fx.run_ops(g,[discover(r)]);g.step(Action('choose',choices=(0,)));logs=[e for e in g.events if e.get('event')=='discover'];self.assertTrue(logs);self.assertTrue(all('offer' not in e and 'options' not in e for e in logs))
