"""Unpatched production paths for physical recruits and hero resurrection."""
import unittest
from expanded import Game,Action,random_deck
from expanded.cards import registry,COLLECTIBLE_IDS
from expanded.decks import Deck,eligible,validate
from expanded.fabled_decks import BUNDLES

class ZoneAdmissionTests(unittest.TestCase):
 def game(self,hero,root):
  r=(1,1,1) if hero=='DEATHKNIGHT' else (0,0,0);cards=registry()
  ids=[c for c in sorted(COLLECTIBLE_IDS) if c!=root and c not in BUNDLES and c not in ('JAIL_397','JAIL_430') and eligible(cards[c],hero,r)]
  d=Deck(hero,(root,)+tuple(ids[:29]),r);self.assertEqual(validate(d),[])
  g=Game([d,random_deck('MAGE',81)],seed=82)
  g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
  for p in g.players:p.hand=[];p.deck=[];p.board=[];p.health=30;p.armor=0;p.mana=p.max_mana=10
  return g
 def test_husk_paid_battlecry_survives_silence_and_consumes_once(self):
  g=self.game('DEATHKNIGHT','TIME_618');p=g.players[0];c=g._add(0,'TIME_618')
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  g._silence(p.minions[0]);p.corpses=27;g._damage(-1,100);g._settle(allow_event_choices=True)
  self.assertEqual((p.health,p.corpses,p.eternal_life),(20,7,False));self.assertFalse(g.terminal)
  g._damage(-1,100);g._settle(allow_event_choices=True);self.assertTrue(g.terminal)
 def test_husk_zero_corpses_does_not_resurrect(self):
  g=self.game('DEATHKNIGHT','TIME_618');c=g._add(0,'TIME_618')
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  g._damage(-1,100);g._settle(allow_event_choices=True);self.assertTrue(g.terminal)
 def test_warptooth_recruits_same_buffed_card_without_playing_it(self):
  g=self.game('WARRIOR','JAIL_421');p=g.players[0];c=g._add(0,'JAIL_421');c.attack_bonus=2;c.health_bonus=3
  for _ in range(3):
   m=g._summon(0,'NEW1_034');g._damage(m.uid,1)
  g._damage(-1,1);g._settle(allow_event_choices=True)
  m=next(m for m in p.minions if m.card_id=='JAIL_421')
  self.assertEqual((m.attack,m.health),(5,6));self.assertNotIn(c,p.hand);self.assertEqual(p.cards_played,0)
  self.assertTrue(any(a.kind=='attack' and a.source==m.uid for a in g.legal_actions()))
 def test_warptooth_damage_on_opponent_turn_does_not_recruit(self):
  g=self.game('WARRIOR','JAIL_421');p=g.players[0];c=g._add(0,'JAIL_421');g.current=1
  for _ in range(3):
   m=g._summon(0,'NEW1_034');g._damage(m.uid,1)
  g._damage(-1,1);g._settle(allow_event_choices=True)
  self.assertIn(c,p.hand);self.assertFalse(any(m.card_id=='JAIL_421' for m in p.minions))
