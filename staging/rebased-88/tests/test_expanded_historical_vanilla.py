"""Historical dependencies use ordinary paid plays; no approved outcome pools."""
import unittest
from expanded import Game,Action,random_deck
from expanded.cards import registry,COLLECTIBLE_IDS,TOKEN_IDS
from expanded.historical_vanilla import GENERATED_IDS
from expanded.historical_generation import validate_past_candidates
from expanded.generation_cards import pool
from engine.cards import UnsupportedCard

class HistoricalVanillaTests(unittest.TestCase):
 def game(self):
  g=Game([random_deck('MAGE',1),random_deck('HUNTER',2)],seed=97)
  g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
  for p in g.players:
   p.hand=[];p.board=[];p.deck=[];p.health=30;p.armor=0;p.mana=p.max_mana=p.mana_capacity=10
  return g
 def play(self,g,cid):
  c=g._add(0,cid);g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  return next(m for m in g.players[0].minions if m.card_id==cid)
 def test_every_declared_body_pays_printed_cost_and_uses_pinned_stats(self):
  records=registry()
  for cid in sorted(GENERATED_IDS):
   with self.subTest(cid=cid):
    g=self.game();m=self.play(g,cid);d=records[cid]
    self.assertEqual((m.attack,m.health,m.max_health),(d['attack'],d['health'],d['health']))
    self.assertEqual(g.players[0].mana,10-d['cost'])
    self.assertTrue(set(d.get('mechanics',()))<=g._effective_keywords(m));g.assert_invariants()
 def test_historical_dependencies_do_not_enter_standard_decks(self):
  records=registry();self.assertEqual(len(GENERATED_IDS),170)
  self.assertTrue(GENERATED_IDS<=TOKEN_IDS);self.assertFalse(GENERATED_IDS&COLLECTIBLE_IDS)
  validate_past_candidates(GENERATED_IDS,records)
  for hero in ('MAGE','HUNTER','DRUID','PALADIN','DEATHKNIGHT'):
   self.assertFalse(GENERATED_IDS&set(random_deck(hero,11).cards))
 def test_historical_membership_remains_unapproved_before_rng_or_state_changes(self):
  g=self.game();before=g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'no reviewed membership'):
   g._generation_candidates(pool(era='past',card_type='MINION'),0)
  self.assertEqual(before,g.rng.getstate());self.assertFalse(g.players[0].board)
 def test_charge_and_rush_have_different_first_turn_hero_legality(self):
  for cid,hero_allowed in (('CS2_124',True),('BOT_603',False)):
   g=self.game();m=self.play(g,cid);enemy=g._summon(1,'NEW1_034')
   attacks=[a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid]
   self.assertTrue(any(a.target==enemy.uid for a in attacks))
   self.assertEqual(any(a.target==-2 for a in attacks),hero_allowed)
 def test_old_stealth_and_elusive_preserve_targeting_restrictions(self):
  for cid in ('AT_095','DEEP_006'):
   g=self.game();m=self.play(g,cid)
   self.assertNotIn(m.uid,g._targets_for('CORE_CS2_029',1))
 def test_old_divine_shield_absorbs_one_hit(self):
  g=self.game();m=self.play(g,'AT_087');h=m.health
  g._damage(m.uid,1);self.assertEqual(m.health,h)
  self.assertNotIn('DIVINE_SHIELD',g._effective_keywords(m));g._damage(m.uid,1);self.assertEqual(m.health,h-1)
 def test_old_reborn_creates_fresh_one_health_body_without_reborn(self):
  g=self.game();m=self.play(g,'ULD_205');uid=m.uid;m.health=0;g._settle(allow_event_choices=True)
  reborn=next(m for m in g.players[0].minions if m.card_id=='ULD_205')
  self.assertNotEqual(uid,reborn.uid);self.assertEqual(reborn.health,1)
  self.assertNotIn('REBORN',g._effective_keywords(reborn))
 def test_old_lifesteal_and_poisonous_use_combat_path(self):
  g=self.game();m=self.play(g,'BOT_050');g.players[0].health=20;m.summoned_turn=g.turn-1
  g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid and a.target==-2))
  self.assertEqual(g.players[0].health,20+m.attack)
  g=self.game();m=self.play(g,'EX1_170');enemy=g._summon(1,'CORE_EX1_162');enemy.health=enemy.max_health=20;m.summoned_turn=g.turn-1
  g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid and a.target==enemy.uid))
  self.assertNotIn(enemy,g.players[1].board)
 def test_old_windfury_allows_two_attacks_and_taunt_blocks_hero(self):
  g=self.game();m=self.play(g,'CFM_666');m.summoned_turn=g.turn-1
  for _ in range(2):g.step(next(a for a in g.legal_actions() if a.kind=='attack' and a.source==m.uid and a.target==-2))
  self.assertFalse(any(a.kind=='attack' and a.source==m.uid for a in g.legal_actions()))
  g=self.game();g._summon(1,'AT_097');m=self.play(g,'CS2_124')
  self.assertFalse(any(a.kind=='attack' and a.source==m.uid and a.target==-2 for a in g.legal_actions()))
