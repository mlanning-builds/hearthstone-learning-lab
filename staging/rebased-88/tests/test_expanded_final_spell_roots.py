"""Focused checks for the final historical roots; no training entrypoints."""
import unittest
from engine.game import Card
from expanded import Action
from expanded import cards,gelbin
from expanded.historical_final_spell_roots import op,ALLIANCE,HORDE,TWOS
import test_expanded_generation as fixtures

class FinalSpellRootTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
 def run_ops(self,operations,**kw):
  context=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False)
  context.update(kw);self.g._start_play_effects(operations,context);self.g._settle(allow_event_choices=True)
 def test_celestial_preserves_damage_and_does_not_refresh(self):
  m=self.g._summon(0,'CS2_231');self.g._buff(m,2,2)
  self.g._damage(m.uid,2)
  damage=m.max_health-m.health
  self.run_ops(cards.RULES['GDB_140'][1],card_id='GDB_140')
  self.assertEqual((m.attack,m.max_health,m.health),(10,10,10-damage))
  self.g._damage(m.uid,2);remaining=m.health
  self.g._refresh_auras();self.assertEqual(m.health,remaining)
  self.g._buff(m,2,2);self.g._refresh_auras();self.assertEqual((m.attack,m.max_health),(12,12))
 def test_celestial_detaches_and_reattaches_on_solo_transition(self):
  m=self.g._summon(0,'CS2_231');base=(m.attack,m.max_health)
  self.run_ops(cards.RULES['GDB_140'][1],card_id='GDB_140')
  extra=self.g._summon(0,'CS2_231');self.g._refresh_auras()
  self.assertEqual((m.attack,m.max_health),base)
  extra.health=0;self.g._settle(allow_event_choices=True)
  self.assertEqual((m.attack,m.max_health),(10,10))
 def test_gelbin_direct_celestial_placement_does_not_cast(self):
  self.p.deck=[Card(self.g._new_id(),'GDB_140')];m=self.g._summon(0,'CS2_231')
  self.run_ops([('gelbin_auras',)])
  self.assertFalse(self.p.deck);self.assertFalse(self.p.spells_turn)
  self.assertEqual(m.attack,10);self.assertIn('GDB_140',gelbin.AURA_RULES)
 def test_graveyard_doubles_minion_and_weapon_without_stacking_doublers(self):
  self.run_ops(cards.RULES['AV_400'][1],card_id='AV_400')
  self.assertEqual(self.g._deathrattle_repetitions(0),2)
  self.assertEqual(self.g._deathrattle_repetitions(0,weapon=True),2)
  self.g._summon(0,'FP1_031')
  self.assertEqual(self.g._deathrattle_repetitions(0),2)
  self.assertEqual(self.g._deathrattle_repetitions(1),1)
 def test_champions_uses_closed_faction_pool_and_discount(self):
  for side,allowed in ((0,ALLIANCE),(1,HORDE)):
   self.setUp();self.run_ops(cards.RULES['WON_113'][1],card_id='WON_113')
   self.g.step(Action('choose',choices=(side,)))
   self.assertEqual(len(self.p.hand),2)
   for card in self.p.hand:self.assertIn(card.card_id,allowed);self.assertEqual(card.cost_delta,-2)
 def test_dwarf_planet_fills_free_slots_then_forces_attacks(self):
  fixtures.GenerationTests().install(self.g,TWOS,('CORE_EX1_162',))
  self.run_ops(cards.RULES['GDB_233'][1],card_id='GDB_233')
  self.assertEqual(len(self.p.minions),7)
  self.assertLess(self.q.health,30)
 def test_impfestation_summons_per_enemy_and_fights(self):
  for _ in range(2):self.g._summon(1,'CS2_231')
  self.run_ops(cards.RULES['ONY_033'][1],card_id='ONY_033')
  self.assertFalse(self.q.minions);self.assertEqual(len(self.p.minions),2)
  self.assertEqual({m.card_id for m in self.p.minions},{'AV_316t'})
 def test_kangor_keeps_only_magnetic_stats(self):
  m=self.g._summon(0,'BOT_020')
  part=Card(self.g._new_id(),'BOT_020');part.attack_bonus=2
  self.assertTrue(self.g._magnetic_attach(part,0,self.p.board.index(m),()))
  magnetic_attack=self.g.cards['BOT_020']['attack']+self.g._card_stat(part,'attack',0)
  self.g._buff(m,5,5);m.health=0;self.g._settle(allow_event_choices=True)
  self.run_ops(cards.RULES['BOT_912'][1],card_id='BOT_912')
  self.assertEqual(len(self.p.minions),1)
  returned=self.p.minions[0]
  self.assertEqual(returned.attack,magnetic_attack)
  self.assertEqual(len(returned.rule_state['magnetic_parts']),1)
  self.assertEqual(len(returned._magnetic_upgrades),1)
 def test_darkness_replaces_only_designated_class_cards(self):
  from expanded.generation_cards import pool
  from expanded.selectors import HERO_CLASSES
  from expanded.pools import GenerationPool
  from expanded.generation import request_matches
  from expanded.herald import herald_related
  self.g._generation_pools={}
  # The frozen members have genuine class eligibility; no production pool is narrowed.
  candidates={hero:next(cid for cid,data in self.g.cards.items() if data.get('collectible') and data.get('cardClass')==hero and cid not in ('OG_118','VAC_941') and request_matches(pool(classes=hero),data,self.p.hero_class) and not herald_related(data)) for hero in HERO_CLASSES}
  for hero,cid in candidates.items():
   self.g._generation_pools[(pool(classes=hero),self.p.hero_class)]=GenerationPool('fixture only',(cid,),'Controlled class conversion witness')
  warlock=Card(self.g._new_id(),candidates['WARLOCK']);neutral=Card(self.g._new_id(),'CS2_231')
  self.p.hand=[warlock,neutral]
  self.run_ops(cards.RULES['OG_118'][1],card_id='OG_118')
  self.assertIs(self.p.hand[1],neutral);self.assertEqual(self.p.hand[0].cost_delta,-1)
  self.assertNotEqual(self.g.cards[self.p.hand[0].card_id]['cardClass'],'WARLOCK')
