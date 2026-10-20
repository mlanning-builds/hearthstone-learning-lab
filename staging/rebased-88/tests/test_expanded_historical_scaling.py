"""Resolution-time scaling fixtures, not pool or client certification."""
import gzip,json,unittest
import test_expanded_generation as fixtures
from expanded import Action
from engine.game import Card
from expanded.historical_scaling import HistoricalScaling,RULES

class HistoricalScalingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open('data/standard/all_cards.json.gz','rt') as f:cls.records={d['id']:d for d in json.load(f) if d['id'] in RULES}
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.g.cards.update(self.records);self.p,self.q=self.g.players
 def scale(self,cid):
  m=self.g._summon(0,cid);before=(m.attack,m.max_health)
  HistoricalScaling._historical_scaling_effect(self.g,RULES[cid][1][0],dict(owner=0,source=m))
  return (m.attack-before[0],m.max_health-before[1])
 def test_other_friendly_excludes_entered_source(self):
  self.g._summon(0,'CORE_EX1_162')
  self.assertEqual(self.scale('CS2_226'),(1,1))
  self.assertEqual(self.scale('DAL_560'),(4,4))
 def test_hand_spell_counts_use_current_physical_identity(self):
  self.g._add(0,'CORE_CS2_029');self.g._add(0,'CORE_EX1_162')
  for cid,expected in [('BOT_413',(0,1)),('DAL_095',(1,0)),('DMF_121',(1,1)),('GIL_507',(0,2)),('OG_320',(2,0))]:
   with self.subTest(cid=cid):self.assertEqual(self.scale(cid),expected)
 def test_hero_damage_and_both_players_deaths(self):
  self.p.hero_damage_taken_turn=7;self.p.minions_died_turn=2;self.q.minions_died_turn=3
  self.assertEqual(self.scale('BOT_226'),(7,0));self.assertEqual(self.scale('ICC_904'),(5,5))
 def test_opponent_hand(self):
  for _ in range(3):self.g._add(1,'TOKEN_COIN')
  self.assertEqual(self.scale('DRG_060'),(3,0))
 def test_damaged_minions_both_sides_excludes_healthy(self):
  a=self.g._summon(0,'CORE_EX1_162');b=self.g._summon(1,'CORE_EX1_162');a.health-=1;b.health-=1
  self.assertEqual(self.scale('ICC_450'),(2,2))
 def test_spells_cast_counter_distinct_from_paid_hand_history(self):
  self.p.spells_cast_turn=4;self.p.spells_turn=[]
  self.assertEqual(self.scale('TSC_213'),(4,4))

 def test_paid_internal_counterspell_and_reset(self):
  spell=self.g._add(0,'CORE_CS2_029');self.p.mana=10
  self.g.step(Action('play',spell.uid,-2))
  self.assertEqual(self.p.spells_cast_turn,1)
  self.fx.run_ops(self.g,(('cast_fixed_spell','CORE_CS2_029','random'),))
  self.assertEqual(self.p.spells_cast_turn,2)
  self.q.secrets.append(Card(self.g._new_id(),'CORE_EX1_287'))
  spell=self.g._add(0,'CORE_CS2_029');self.p.mana=10
  self.g.step(Action('play',spell.uid,-2))
  self.assertEqual(self.p.spells_cast_turn,2)
  self.g.step(Action('end'))
  self.assertEqual(self.p.spells_cast_turn,0)

 def test_totem_pirate_and_frost_printed_selectors(self):
  self.g.cards['CORE_EX1_162']=dict(self.g.cards['CORE_EX1_162'],races=['ALL'])
  self.g._summon(0,'CORE_EX1_162')
  self.assertEqual(self.scale('AT_047'),(1,1))
  self.assertEqual(self.scale('TRL_071'),(1,1))
  self.g.cards['CORE_CS2_029']=dict(self.g.cards['CORE_CS2_029'],spellSchool='FROST')
  self.g._add(0,'CORE_CS2_029');self.g._add(0,'TOKEN_COIN')
  self.assertEqual(self.scale('RLK_110'),(1,0))
 def test_live_attached_deathrattle_counts_once(self):
  m=self.g._summon(1,'CORE_EX1_162');m.attached_death_effects=[('armor',1),('armor',2)]
  self.assertEqual(self.scale('GVG_097'),(1,1))

class ScalingProductionTests(unittest.TestCase):
 def test_automatic_cast_counter_drives_paid_queensguard_and_features(self):
  import test_expanded_generation as fixtures
  from expanded.features import encode_decision,SCHEMA
  from expanded import cards
  g=fixtures.GenerationTests().game()
  fixtures.GenerationTests().run_ops(g,(('cast_fixed_spell','TOKEN_COIN','random'),))
  g.players[0].mana=10
  c=g._add(0,'TSC_213');base=g.cards[c.card_id]
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  m=next(m for m in g.players[0].minions if m.card_id==c.card_id)
  self.assertEqual((m.attack,m.max_health),(base['attack']+1,base['health']+1))
  view=g.observe(0)
  rows=encode_decision(dict(observation=view,actor=0,actions=view['legal_actions']))
  self.assertIn('spells_cast_turn',str(rows));self.assertEqual(SCHEMA,'visible-action-features-v62')
  self.assertFalse(set(__import__('expanded.historical_scaling',fromlist=['GENERATED_IDS']).GENERATED_IDS)&cards.COLLECTIBLE_IDS)

if __name__=='__main__':unittest.main()
