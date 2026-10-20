import gzip,json,unittest
import test_expanded_generation as fixtures
from expanded import cards

WEAPONS={'CS2_080':(4,2,5),'CS2_106':(2,3,2),'CS2_112':(5,5,2)}

class HistoricalWeaponTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:cls.records={d['id']:d for d in json.load(f)}
 def game(self):
  g=fixtures.GenerationTests().game()
  for cid in WEAPONS:g.cards[cid]=self.records[cid]
  return g
 def test_paid_equipment_preserves_frozen_stats_and_physical_identity(self):
  for cid,(cost,attack,durability) in WEAPONS.items():
   with self.subTest(cid=cid):
    g=self.game();p=g.players[0];c=g._add(0,cid)
    g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
    self.assertEqual(p.last_paid_cost,cost)
    self.assertEqual(p.equipped_card.uid,c.uid)
    self.assertEqual((p.weapon['attack'],p.weapon['durability']),(attack,durability))
    self.assertEqual(p.weapon['card_id'],cid);g.assert_invariants()
 def test_attacks_consume_durability_and_break_at_zero(self):
  for cid,(_,attack,durability) in WEAPONS.items():
   with self.subTest(cid=cid):
    g=self.game();p,q=g.players;g._equip(0,cid)
    for remaining in range(durability-1,-1,-1):
     p.hero_attacks=0
     action=next(a for a in g.legal_actions() if a.kind=='attack' and a.source==g.hero_id(0) and a.target==g.hero_id(1))
     g.step(action)
     self.assertEqual(q.health,30-attack*(durability-remaining))
     if remaining:self.assertEqual(p.weapon['durability'],remaining)
     else:self.assertIsNone(p.weapon);self.assertIsNone(p.equipped_card)
