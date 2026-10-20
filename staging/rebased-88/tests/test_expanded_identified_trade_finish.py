"""Prepared controlled rules for identified spell families and physical trades."""
from copy import deepcopy
import unittest
from expanded import Game,Action,random_deck
from engine.game import Card
from expanded.historical_identified_spell_finish import FORMS
class IdentifiedTradeFinishTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  g=Game([random_deck('MAGE',31),random_deck('MAGE',53)],seed=71)
  g.step(Action('mulligan'));g.step(Action('mulligan'))
  for p in g.players:p.hand=[];p.board=[];p.deck=[];p.mana=p.max_mana=10;p.health=30;p.armor=0
  cls.prototype=g
 def game(self):return deepcopy(self.prototype)
 def play(self,g,cid,target=0):
  card=g._add(0,cid)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid and a.target==target))
  return card
 def test_identification_preserves_physical_identity_and_modifiers(self):
  for root,forms in FORMS.items():
   g=self.game();c=Card(g._new_id(),root,attack_bonus=2,health_bonus=3);g._enter_hand(0,c)
   self.assertIs(g.players[0].hand[0],c);self.assertIn(c.card_id,forms);self.assertEqual((c.attack_bonus,c.health_bonus),(2,3))
   cid=c.card_id;g.players[0].hand.remove(c);g._enter_hand(0,c);self.assertEqual(c.card_id,cid)
 def test_recruitment_resets_target_enchantments_in_hand(self):
  g=self.game();m=g._summon(1,'CS2_182');g._buff(m,4,4);self.play(g,'DAL_366t2',m.uid)
  self.assertNotIn(m,g.players[1].minions);c=g.players[0].hand[0]
  self.assertEqual(c.card_id,'CS2_182');self.assertEqual(g._card_stat(c,'attack',0),4)
 def test_turncoat_uses_victim_attack_not_spell_damage(self):
  g=self.game();left=g._summon(1,'CS2_182');victim=g._summon(1,'CS2_182');right=g._summon(1,'CS2_182');g._summon(0,'CS2_052')
  self.play(g,'DAL_366t4',victim.uid)
  self.assertEqual((left.health,right.health),(1,1));self.assertNotIn(victim,g.players[1].minions)
 def test_shadow_copy_is_one_one_after_original_buff(self):
  g=self.game();m=g._summon(0,'CS2_182');self.play(g,'LOOT_278t3',m.uid)
  self.assertEqual((m.attack,m.health),(6,7));copy=g.players[0].minions[1];self.assertEqual((copy.attack,copy.health),(1,1))
 def test_hope_returns_printed_card_after_death(self):
  g=self.game();m=g._summon(0,'CS2_182');self.play(g,'LOOT_278t4',m.uid);m.health=0;g._settle()
  self.assertEqual([c.card_id for c in g.players[0].hand],['CS2_182']);self.assertEqual(g._card_stat(g.players[0].hand[0],'attack',0),4)
 def test_shield_outcomes_use_actual_weapon_and_body(self):
  for cid in ('LOOT_285t','LOOT_285t3','LOOT_285t4'):
   g=self.game();self.play(g,cid);self.assertEqual(g.players[0].armor,15 if cid=='LOOT_285t' else 5)
   if cid=='LOOT_285t3':self.assertEqual([(m.card_id,m.attack,m.health) for m in g.players[0].minions],[('LOOT_285t3t',5,5)])
   if cid=='LOOT_285t4':self.assertEqual((g.players[0].weapon['attack'],g.players[0].weapon['durability']),(5,2))
 def test_shipment_keeps_traded_physical_upgrade(self):
  g=self.game();card=g._add(0,'DED_504');drawn=Card(g._new_id(),'CS2_182');g.players[0].deck=[drawn]
  g.step(Action('trade',card.uid));self.assertIs(g.players[0].deck[0],card);self.assertIs(g.players[0].hand[0],drawn)
  g.players[0].deck.remove(card);g._enter_hand(0,card)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid))
  self.assertEqual([m.card_id for m in g.players[0].minions],['CORE_GIL_191t']*4)
 def test_amulet_resurrects_only_printed_deathrattle(self):
  g=self.game();m=g._summon(0,'CS2_182');m.health=0;g._settle();m=g._summon(0,'EX1_029');m.health=0;g._settle()
  self.play(g,'DED_512');self.assertEqual([m.card_id for m in g.players[0].minions],['EX1_029'])
 def test_biscuit_trade_has_friendly_target_choice(self):
  g=self.game();m=g._summon(0,'CS2_182');g._summon(1,'CS2_182');g.players[0].deck=['CS2_182'];card=g._add(0,'DED_009')
  g.step(Action('trade',card.uid));self.assertEqual(g.pending_choice['kind'],'historical_trade_biscuit')
  self.assertEqual([o['target_uid'] for o in g.pending_choice['options']],[m.uid])
  g.step(g.legal_actions()[0]);self.assertIn('RUSH',g._effective_keywords(m))
