"""Paid and opening paths with complete real decks and the production registry."""
import unittest
from expanded import Game,Action,cards
from expanded.decks import Deck,eligible,validate
from expanded.fabled_decks import BUNDLES,expand_bundle_ids

class ImbueAzureAdmissionTests(unittest.TestCase):
 def deck(self,hero,root,nature=False):
  records=cards.registry();runes=(1,1,1) if hero=='DEATHKNIGHT' else (0,0,0)
  selected=[root];limit=30-len(BUNDLES.get(root,()))
  for cid in sorted(cards.COLLECTIBLE_IDS):
   c=records[cid]
   if cid==root or cid in BUNDLES or c['type']!='MINION' or not eligible(c,hero,runes):continue
   selected.append(cid)
   if len(selected)==limit:break
  d=Deck(hero,tuple(selected),runes);self.assertEqual(validate(d),[]);return d
 def game(self,hero,root):
  g=Game([self.deck(hero,root),self.deck('WARRIOR','CORE_EX1_162')],seed=33)
  g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
  for p in g.players:p.hand=[];p.board=[];p.deck=[];p.mana=p.max_mana=10;p.health=30;p.armor=0
  return g
 def play(self,g,cid,target=0):
  p=g.players[0];p.mana=10;c=g._add(0,cid);cost=g._cost(c,0)
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
  self.assertEqual(p.mana,10-cost);g.assert_invariants()
 def test_houndmaster_draws_beast_and_installs_live_hunter_power(self):
  g=self.game('HUNTER','EDR_226');p=g.players[0];p.deck=['CORE_EX1_162'];self.play(g,'EDR_226')
  self.assertEqual(p.imbue_count,1);self.assertEqual(p.primary_power['card_id'],'EDR_850p')
  g.step(Action('power'));self.assertEqual(p.hand[0].attack_bonus,1);self.assertEqual(p.hand[0].cost_delta,-1)
 def test_umbraclaw_real_death_imbues_once(self):
  g=self.game('HUNTER','EDR_227');self.play(g,'EDR_227');m=g.players[0].minions[0];m.health=0;g._settle()
  self.assertEqual(g.players[0].imbue_count,1)
 def test_hamuul_original_minion_only_deck_imbues_at_opening(self):
  g=self.game('DRUID','EDR_845');p=g.players[0];self.assertTrue(p.hamuul_active);self.assertEqual(p.imbue_count,1)
  g.step(Action('power'));self.assertEqual(p.minions[0].card_id,'EDR_847pt2')
 def test_spirit_gatherer_adds_wisp_and_installs_mage_power(self):
  g=self.game('MAGE','EDR_871');self.play(g,'EDR_871');p=g.players[0]
  self.assertEqual([c.card_id for c in p.hand],['EDR_851t']);self.assertEqual(p.imbue_count,1)
  g.step(Action('power'));self.assertEqual(g.players[1].health,29)
 def test_wisprider_free_power_has_real_summon_and_damage(self):
  g=self.game('MAGE','EDR_519');self.play(g,'EDR_519');p=g.players[0]
  self.assertEqual(p.imbue_count,1);self.assertIn('EDR_851t',[m.card_id for m in p.minions]);self.assertEqual(g.players[1].health,29)
  self.assertFalse(p.power_used)
 def test_finality_installs_passive_and_buffs_next_played_undead(self):
  g=self.game('DEATHKNIGHT','END_003');p=g.players[0]
  cid=next(cid for cid,c in g.cards.items() if cid in cards.COLLECTIBLE_IDS and c['type']=='MINION' and 'UNDEAD' in c.get('races',()) and c['cost']<=10)
  p.deck=[cid];self.play(g,'END_003');self.assertEqual(p.imbue_count,2)
  self.assertFalse(any(a.kind=='power' for a in g.legal_actions()))
  card=p.hand[0];before=g.cards[cid]['attack'];g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==card.uid))
  self.assertEqual(p.minions[0].attack,before+2)
 def test_azure_bundle_real_deck_and_arcane_repetition(self):
  g=self.game('MAGE','TIME_852');p=g.players[0]
  self.assertTrue({'TIME_852','TIME_852t1','TIME_852t3'}<=set(p.starting_deck))
  self.play(g,'TIME_852');self.play(g,'TIME_852t1');self.play(g,'JAIL_881')
  self.assertEqual(g.players[1].health,22)
  p.minions[0].health=0;g._settle();self.play(g,'TIME_852t3')
  self.assertEqual(sum(m.card_id=='TIME_852' for m in p.minions),1)

if __name__=='__main__':unittest.main()
