import unittest
import test_expanded_generation as fixtures
from expanded import cards,zone_triggers,Action
class ZoneDeathrattleTests(unittest.TestCase):
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
 def test_paid_impfernal_uses_real_registry_and_battlefield_deathrattle(self):
  self.assertIn('JAIL_398',cards.COLLECTIBLE_IDS)
  self.p.mana=10;c=self.g._add(0,'JAIL_398')
  cost=self.g._cost(c,0);self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(self.p.mana,10-cost)
  m=next(m for m in self.p.minions if m.card_id=='JAIL_398');m.health=0;self.g._settle()
  self.assertEqual((self.p.health,self.q.health),(27,27));self.g.assert_invariants()
 def test_discard_damages_both_heroes_and_board(self):
  m=self.g._summon(1,'CORE_EX1_162');c=self.g._add(0,'JAIL_398');self.g._discard_card(0,c);self.g._settle();self.assertEqual((self.p.health,self.q.health),(27,27));self.assertNotIn(m,self.q.board)
 def test_board_death_uses_same_damage(self):
  m=self.g._summon(0,'JAIL_398');m.health=0;self.g._settle();self.assertEqual((self.p.health,self.q.health),(27,27))
 def test_explicit_deathrattle_does_not_damage_source(self):
  m=self.g._summon(0,'JAIL_398');self.fx.run_ops(self.g,zone_triggers.DEATH_EFFECTS['JAIL_398'],source=m);self.assertEqual(m.health,6);self.assertEqual(self.q.health,27)
 def test_deck_destruction_triggers_without_discard_event(self):
  self.p.deck=[];self.q.deck=['JAIL_398'];self.fx.run_ops(self.g,[('empty_deck_destroy_enemy_top',1)]);self.assertEqual((self.p.health,self.q.health),(27,27));self.assertFalse(self.q.discard_history)
 def test_draw_does_not_trigger(self):
  self.p.deck=['JAIL_398'];self.g._draw(0);self.g._settle();self.assertEqual(self.p.health,30)
 def test_batch_discard_captures_each_physical_card(self):
  a=self.g._add(0,'JAIL_398');b=self.g._add(0,'JAIL_398');self.g._discard_cards(0,[a,b]);self.g._settle();self.assertEqual((self.p.health,self.q.health),(24,24))
 def test_other_discard_does_not_trigger(self):
  self.g._discard_card(0,self.g._add(0,'TOKEN_COIN'));self.g._settle();self.assertEqual(self.p.health,30)
 def test_silenced_board_death_does_not_trigger(self):
  m=self.g._summon(0,'JAIL_398');self.g._silence(m);m.health=0;self.g._settle();self.assertEqual(self.p.health,30)

 def test_normal_overdraw_runs_zone_deathrattle(self):
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.p.deck=['JAIL_398'];self.g._draw(0);self.g._settle();self.assertEqual(self.p.health,27);self.assertFalse(self.p.discard_history)
 def test_generated_overflow_is_not_a_deck_death(self):
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.g._add(0,'JAIL_398');self.g._settle();self.assertEqual(self.p.health,30)
 def test_godfrey_caches_card_and_still_triggers_destruction(self):
  self.p.overdraw_return_active=True
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.p.deck=['JAIL_398'];self.g._draw(0);self.g._settle();self.assertEqual(self.p.health,27);self.assertEqual(self.p.overdraw_cache[0].card_id,'JAIL_398')

 def test_godfrey_return_does_not_repeat_destruction(self):
  self.p.overdraw_return_active=True
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.p.deck=['JAIL_398'];self.g._draw(0);self.g._settle()
  cached=self.p.overdraw_cache[0];self.p.hand.pop();self.g._recover_overdraw();self.g._settle()
  self.assertIs(self.p.hand[-1],cached);self.assertEqual((self.p.health,self.q.health),(27,27));self.assertFalse(self.p.overdraw_cache)
 def test_godfrey_cache_limit_does_not_suppress_destruction(self):
  from engine.game import Card
  self.p.overdraw_return_active=True
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.p.overdraw_cache=[Card(self.g._new_id(),'TOKEN_COIN') for _ in range(99)]
  self.p.deck=['JAIL_398'];self.g._draw(0);self.g._settle()
  self.assertEqual(len(self.p.overdraw_cache),99);self.assertTrue(all(c.card_id=='TOKEN_COIN' for c in self.p.overdraw_cache));self.assertEqual(self.p.health,27)

 def test_deck_discover_overflow_uses_godfrey_cache(self):
  from expanded import Action
  self.p.overdraw_return_active=True
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.p.deck=['JAIL_398'];self.g._discover_deck(0);self.g.step(Action('choose',choices=(0,)))
  self.assertEqual(self.p.health,27);self.assertEqual(self.p.overdraw_cache[0].card_id,'JAIL_398');self.assertEqual(self.p.discoveries_total,1)
 def test_bottom_deck_selection_overflow_uses_godfrey_cache(self):
  from expanded import Action
  self.p.overdraw_return_active=True
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.p.deck=['JAIL_398'];self.g._open_zone_choice(0,0,'deck','draw_bottom');self.g.step(Action('choose',choices=(0,)))
  self.assertEqual(self.p.health,27);self.assertEqual(self.p.overdraw_cache[0].card_id,'JAIL_398');self.assertFalse(self.p.deck)
