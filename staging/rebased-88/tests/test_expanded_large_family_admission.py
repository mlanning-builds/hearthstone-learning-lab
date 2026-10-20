"""Real registry and complete-pool scenarios for the remaining large families."""
import unittest
from expanded import Game,Action,cards
from expanded.decks import Deck,eligible,validate
from expanded.fabled_decks import BUNDLES
from expanded.reviewed_large_families import ROOT_IDS,FIXED_TOKEN_IDS,HERALD_IDS,COLOSSAL_IDS
from expanded.herald import SOLDIERS,CATACLYSMS
from expanded.generation_cards import pool
from engine.cards import UnsupportedCard
import test_expanded_generation as fixtures
class LargeFamilyAdmissionTests(unittest.TestCase):
 def game(self,hero='WARRIOR'):
  records=cards.registry();runes=(1,1,1) if hero=='DEATHKNIGHT' else (0,0,0)
  ids=[cid for cid in sorted(cards.COLLECTIBLE_IDS) if cid not in BUNDLES and cid not in ('JAIL_397','JAIL_430','JAIL_831') and eligible(records[cid],hero,runes)]
  deck=Deck(hero,tuple(ids[:30]),runes);self.assertEqual(validate(deck),[])
  opponent=Deck('HUNTER',tuple(cid for cid in sorted(cards.COLLECTIBLE_IDS) if cid not in BUNDLES and cid not in ('JAIL_397','JAIL_430','JAIL_831') and eligible(records[cid],'HUNTER',(0,0,0)))[:30])
  g=Game([deck,opponent],seed=122);g.step(Action('mulligan'));g.step(Action('mulligan'));g.current=0
  for p in g.players:p.hand=[];p.board=[];p.deck=['CORE_EX1_162']*12;p.health=30;p.armor=0;p.mana=p.max_mana=10
  return g
 def play(self,g,cid,target=0):
  c=g._add(0,cid);g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target));return c
 def test_all_roots_and_exact_dependencies_are_registered(self):
  self.assertEqual(len(ROOT_IDS),13);self.assertTrue(ROOT_IDS<=cards.COLLECTIBLE_IDS);self.assertTrue(FIXED_TOKEN_IDS<=cards.TOKEN_IDS);self.assertFalse(FIXED_TOKEN_IDS&cards.COLLECTIBLE_IDS)
 def test_native_sources_summon_real_soldiers(self):
  for cid,hero in (('CATA_156','ROGUE'),('CATA_497','WARRIOR'),('CATA_722','WARRIOR'),('CATA_780','DEATHKNIGHT'),('CATA_785','ROGUE')):
   with self.subTest(card=cid):
    g=self.game(hero);self.play(g,cid);self.assertEqual(g.players[0].herald_count,1);self.assertIn(SOLDIERS[hero],[m.card_id for m in g.players[0].minions])
 def test_follower_heralds_on_death_with_private_discounted_generated_spell(self):
  g=self.game('ROGUE');self.play(g,'CATA_158');source=next(m for m in g.players[0].minions if m.card_id=='CATA_158');self.assertEqual(g.players[0].herald_count,0);source.health=0;g._settle();self.assertEqual(g.players[0].herald_count,1);self.assertEqual(len(g.players[0].hand),1);self.assertEqual(g.players[0].hand[0].cost_delta,-1)
 def test_location_activation_runs_herald_before_shared_draw(self):
  g=self.game();self.play(g,'CATA_492');loc=g.players[0].locations[0];self.assertEqual(g.players[0].herald_count,0);g.step(next(a for a in g.legal_actions() if a.kind=='activate' and a.source==loc.uid));self.assertEqual(g.players[0].herald_count,1);self.assertEqual(len(g.players[0].hand),1)
 def test_ultraxion_discounts_exact_deathwing_current_hand_copy(self):
  g=self.game();g.players[0].herald_count=2;wing=g._add(0,'CATA_190h');before=g._cost(wing,0);self.play(g,'CATA_497');self.assertEqual(g.players[0].herald_count,3);self.assertEqual(g._cost(wing,0),before-3)
 def test_stolen_single_class_herald_falls_back_to_card_class(self):
  g=self.game('MAGE');self.play(g,'CATA_160');self.assertEqual(g.players[0].herald_count,1);self.assertIn('CATA_580t',[m.card_id for m in g.players[0].minions]);soldier=next(m for m in g.players[0].minions if m.card_id=='CATA_580t');self.assertIn('RUSH',soldier.keywords)
 def test_native_herald_class_takes_precedence_over_stolen_source_class(self):
  g=self.game('DEMONHUNTER');self.play(g,'CATA_160');self.assertIn('CATA_525t',[m.card_id for m in g.players[0].minions]);self.assertNotIn('CATA_580t',[m.card_id for m in g.players[0].minions])
 def test_ambiguous_multiclass_herald_rejects_without_inventing_army(self):
  g=self.game('MAGE');c=g._add(0,'CATA_722');before=g.observe(0);rng=g.rng.getstate()
  with self.assertRaisesRegex(UnsupportedCard,'ambiguous'):g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual(g.observe(0),before);self.assertEqual(g.rng.getstate(),rng)
 def test_deathwing_gains_armor_replaces_power_and_offers_distinct_cataclysms(self):
  g=self.game();g.players[0].herald_count=4;self.play(g,'CATA_190h');self.assertEqual(g.players[0].armor,12);self.assertEqual(g.players[0].primary_power['card_id'],'CATA_190p');self.assertEqual(g.pending_choice['remaining'],4)
  chosen=[]
  while g.pending_choice:
   options=[o['card_id'] for o in g.pending_choice['options']];self.assertFalse(set(chosen)&set(options));chosen.append(options[0]);g.step(Action('choose',choices=(0,)))
  self.assertEqual(set(chosen),set(CATACLYSMS));self.assertEqual(len(g.players[0].deck),17);self.assertIn('CATA_190t14',[m.card_id for m in g.players[0].minions]);self.assertFalse(g.players[0].spells_turn)
 def test_deathwing_power_attack_expires_at_end_turn(self):
  g=self.game();self.play(g,'CATA_190h');g.step(Action('choose',choices=(0,)));g.players[0].mana=10;g.step(Action('power'));self.assertEqual(g._hero_attack(0),5);g.step(Action('end'));self.assertEqual(g._hero_attack(0),0)
 def test_alakir_generated_cost_matches_attack_after_appendage_aura(self):
  g=self.game('SHAMAN');self.play(g,'CATA_153');body=next(m for m in g.players[0].minions if m.card_id=='CATA_153');self.assertEqual(len(g.players[0].hand),2);self.assertTrue(all(g.cards[c.card_id]['cost']==body.attack and c.set_cost==1 for c in g.players[0].hand))
 def test_sinestra_foreign_spell_repeats_once_with_one_payment(self):
  g=self.game('ROGUE');self.play(g,'CATA_154');g.players[0].hand=[];self.play(g,'CORE_CS2_029',-2);self.assertEqual(g.players[1].health,18);self.assertEqual(g.players[0].mana,6);self.assertEqual(len(g.players[0].spells_turn),1)
 def test_onyxia_replaces_own_turn_health_loss_without_healing_event(self):
  g=self.game('DEATHKNIGHT');self.play(g,'CATA_155');before=g.players[0].health;g._damage(-1,4);self.assertEqual(g.players[0].health,before+4);self.assertEqual(g.players[0].max_health,34)
  g.current=1;g._damage(-1,4);self.assertEqual(g.players[0].health,before)
 def test_vulcanos_end_turn_damages_others_and_generates_plume_rewards(self):
  g=self.game('MAGE');self.play(g,'CATA_488');body=next(m for m in g.players[0].minions if m.card_id=='CATA_488');before=body.health;enemy=g._summon(1,'CORE_EX1_162');g.step(Action('end'));self.assertEqual(body.health,before);self.assertFalse(g.players[1].minions);self.assertEqual(len(g.players[0].hand),2);self.assertTrue(all(g.cards[c.card_id].get('spellSchool')=='FIRE' and c.cost_delta==-3 for c in g.players[0].hand))
 def test_thornveil_summons_with_taunt_and_imbues_without_fixture_pool(self):
  g=self.game('DRUID');self.play(g,'EDR_264');self.assertEqual(len(g.players[0].all_minions),1);m=g.players[0].all_minions[0];self.assertEqual(g.cards[m.card_id]['cost'],2);self.assertIn('TAUNT',m.keywords);self.assertEqual(g.players[0].imbue_count,1)
