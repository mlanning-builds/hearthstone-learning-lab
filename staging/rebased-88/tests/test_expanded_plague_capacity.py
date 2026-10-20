import gzip,json,unittest
import test_expanded_generation as fixtures

class PlagueCapacityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:cls.records={r['id']:r for r in json.load(f)}
 def game(self):
  g=fixtures.GenerationTests().game()
  g.cards.update({cid:self.records[cid] for cid in ('JAIL_443','JAIL_443t')})
  return g
 def test_full_deck_replacement_has_no_insertion_or_rng(self):
  g=self.game();m=g._summon(0,'JAIL_443');q=g.players[1];q.deck=['CS2_182']*99
  before=list(q.deck);rng=g.rng.getstate();history=list(q.shuffle_history)
  self.assertTrue(g._replace_plague_damage(g.hero_id(1),3,m))
  self.assertEqual(q.deck,before);self.assertEqual(q.health,30)
  self.assertEqual(q.shuffle_history,history);self.assertEqual(g.rng.getstate(),rng)
 def test_one_slot_inserts_one_physical_blight(self):
  g=self.game();m=g._summon(0,'JAIL_443');q=g.players[1];q.deck=['CS2_182']*98
  self.assertTrue(g._replace_plague_damage(g.hero_id(1),5,m))
  self.assertEqual(len(q.deck),99)
  self.assertEqual(sum(getattr(c,'card_id',None)=='JAIL_443t' for c in q.deck),1)
  self.assertEqual(q.shuffle_history[-1]['count'],1)
 def test_silenced_source_does_not_replace(self):
  g=self.game();m=g._summon(0,'JAIL_443');g._silence(m)
  self.assertFalse(g._replace_plague_damage(g.hero_id(1),3,m))
 def test_minion_damage_is_not_replaced(self):
  g=self.game();m=g._summon(0,'JAIL_443');target=g._summon(1,'CS2_182')
  self.assertFalse(g._replace_plague_damage(target.uid,3,m))
