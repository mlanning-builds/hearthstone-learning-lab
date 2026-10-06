import unittest
from expanded import Game,Action,random_deck
from expanded.cards import registry,COLLECTIBLE_IDS
from expanded.decks import Deck,eligible,validate
from expanded.fabled_decks import BUNDLES
from engine.game import Card

class PassiveAdmissionTests(unittest.TestCase):
 def deck(self,hero,root,cheap=False):
  records=registry()
  ids=[c for c in sorted(COLLECTIBLE_IDS) if c not in BUNDLES and c not in ('JAIL_397','JAIL_430',root) and eligible(records[c],hero,(0,0,0)) and (not cheap or records[c]['cost']<=3)]
  self.assertGreaterEqual(len(ids),29)
  d=Deck(hero,(root,)+tuple(ids[:29]));self.assertEqual(validate(d),[]);return d
 def game(self,hero,root,cheap=False):
  g=Game([self.deck(hero,root,cheap),random_deck('WARRIOR',99)],seed=98)
  g.step(Action('mulligan'));g.step(Action('mulligan'));return g
 def play(self,g,cid,target=0):
  g.current=0;g.players[0].mana=g.players[0].max_mana=10;c=g._add(0,cid)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
 def test_champion_paid_buff_adds_one_extra_pair(self):
  g=self.game('PALADIN','JAIL_330');g.players[0].hand=[];self.play(g,'JAIL_330')
  m=next(m for m in g.players[0].minions if m.card_id=='JAIL_330');a,h=m.attack,m.max_health
  self.play(g,'CORE_BT_292',m.uid)
  self.assertEqual((m.attack,m.max_health),(a+3,h+2))
  g._champion_checkpoint();self.assertEqual((m.attack,m.max_health),(a+3,h+2))
 def test_champion_silence_stops_extra_stat_gain(self):
  g=self.game('PALADIN','JAIL_330');g.players[0].hand=[];self.play(g,'JAIL_330')
  m=g.players[0].minions[0];g._silence(m);a,h=m.attack,m.max_health
  self.play(g,'CORE_BT_292',m.uid);self.assertEqual((m.attack,m.max_health),(a+2,h+1))
 def test_godfrey_overdraw_returns_same_discounted_modified_card_after_paid_play(self):
  g=self.game('WARLOCK','JAIL_509');p=g.players[0];self.assertTrue(p.overdraw_return_active)
  p.hand=[]
  for _ in range(9):g._add(0,'CORE_CS2_029')
  coin=g._add(0,'TOKEN_COIN');card=Card(g._new_id(),'CORE_EX1_162');card.attack_bonus=2;card.health_bonus=3;p.deck=[card]
  g._draw(0);g._settle(allow_event_choices=True)
  self.assertEqual(p.overdraw_cache,[card]);self.assertNotIn(card,p.hand)
  g.current=0
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==coin.uid))
  self.assertIn(card,p.hand);self.assertFalse(p.overdraw_cache)
  self.assertEqual((card.attack_bonus,card.health_bonus,card.cost_delta),(2,3,-1))
 def test_godfrey_generated_after_start_does_not_enable_recovery(self):
  g=Game([random_deck('MAGE',2),random_deck('WARRIOR',3)],seed=4)
  self.assertFalse(g.players[0].overdraw_return_active)
  g._summon(0,'JAIL_509');self.assertFalse(g.players[0].overdraw_return_active)
 def test_chef_grants_mana_after_fifth_owner_turn(self):
  g=self.game('DRUID','JAIL_860',cheap=True);p=g.players[0];ends=0
  while ends<5:
   owner=g.current
   if owner==0 and ends<4:self.assertLess(p.max_mana,10)
   g.step(Action('end'))
   if owner==0:ends+=1
  self.assertEqual(p.max_mana,10)
  g.step(Action('end'));self.assertEqual((p.max_mana,p.mana),(10,10))
 def test_chef_ineligible_original_deck_does_not_install_deadline(self):
  g=self.game('DRUID','JAIL_860');p=g.players[0]
  self.assertTrue(any(g.cards[c]['cost']>3 for c in p.starting_deck))
  for _ in range(10):g.step(Action('end'))
  self.assertLess(p.max_mana,10)
