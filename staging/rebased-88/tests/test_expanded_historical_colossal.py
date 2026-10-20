"""Production-registry checks for retired Colossal dependencies."""
import unittest
from expanded import Action,cards
import test_expanded_generation as fixtures
from expanded.historical_colossal import ROOT_IDS,FIXED_TOKEN_IDS,TENTACLES,HEADS,STALKS,CLAWS
class HistoricalColossalTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def play(self,g,cid):
  c=g._add(0,cid);g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid and a.position==0));return g.players[0].minions[0]
 def test_registry_has_roots_and_exact_children_generated_only(self):
  self.assertTrue((ROOT_IDS|FIXED_TOKEN_IDS)<=cards.RULES.keys());self.assertTrue(ROOT_IDS<=cards.TOKEN_IDS);self.assertFalse(ROOT_IDS&cards.COLLECTIBLE_IDS)
 def test_ozumat_fills_board_with_six_exact_tentacles(self):
  g=self.game();g._summon(0,'TID_711')
  self.assertEqual([m.card_id for m in g.players[0].minions],['TID_711',*TENTACLES])
 def test_ozumat_counts_current_controlled_tentacles_and_stops_without_enemies(self):
  g=self.game();body=g._summon(0,'TID_711');g.players[0].board[:]=[body,g.players[0].board[1]]
  for _ in range(3):g._summon(1,'CORE_EX1_162')
  body.health=0;g._settle();self.assertEqual(len(g.players[1].minions),2)
 def test_silenced_ozumat_has_no_destruction(self):
  g=self.game();body=g._summon(0,'TID_711');g._summon(1,'CORE_EX1_162');g._silence(body);body.health=0;g._settle();self.assertEqual(len(g.players[1].minions),1)
 def test_ozumat_simultaneous_dead_tentacles_do_not_count(self):
  g=self.game();body=g._summon(0,'TID_711');g._summon(1,'CORE_EX1_162')
  for m in g.players[0].minions:m.health=0
  g._settle();self.assertEqual(len(g.players[1].minions),1)
 def test_crabatoa_minion_and_weapon_auras_disappear_after_silence(self):
  g=self.game();body=g._summon(0,'TSC_937');claws=[m for m in g.players[0].minions if m.card_id in CLAWS]
  self.assertEqual([m.attack for m in claws],[4,4]);claws[0].health=0;g._settle();self.assertEqual(g.players[0].weapon['card_id'],'TSC_937t2');self.assertEqual(g.players[0].weapon['attack'],4)
  g._silence(body);g._refresh_auras();self.assertEqual(claws[1].attack,2);self.assertEqual(g.players[0].weapon['attack'],2)
 def test_crabatoa_replacement_weapon_does_not_keep_claw_aura(self):
  g=self.game();g._summon(0,'TSC_937');g._equip(0,'TSC_937t2');g._refresh_auras();g._equip(0,'TSC_915');g._refresh_auras();self.assertEqual(g.players[0].weapon['attack'],5)
 def test_hydralodon_paid_battlecry_grants_heads_rush(self):
  g=self.game();self.play(g,'TSC_950');heads=[m for m in g.players[0].minions if m.card_id in HEADS];self.assertEqual(len(heads),2);self.assertTrue(all('RUSH' in m.keywords for m in heads))
 def test_hydralodon_summon_does_not_run_battlecry(self):
  g=self.game();g._summon(0,'TSC_950');self.assertTrue(all('RUSH' not in m.keywords for m in g.players[0].minions if m.card_id in HEADS))
 def test_head_death_replaces_it_with_two_without_replaying_rush(self):
  g=self.game();g._summon(0,'TSC_950');head=next(m for m in g.players[0].minions if m.card_id in HEADS);head.health=0;g._settle();self.assertEqual(sum(m.card_id in HEADS for m in g.players[0].minions),3)
 def test_head_has_no_resummon_without_controlled_hydralodon(self):
  g=self.game();head=g._summon(0,HEADS[0]);head.health=0;g._settle();self.assertFalse(g.players[0].minions)
 def test_xhilag_upgrades_stalks_not_new_standalone_stalks(self):
  g=self.game();body=g._summon(0,'TSC_219');ctx=dict(owner=0,source=body,target=0,bonus=0,lifesteal=False)
  g._effect(('historic_xhilag_upgrade',),ctx);self.assertTrue(all(m.rule_state.get('xhilag_damage')==3 for m in g.players[0].minions if m.card_id in STALKS));new=g._summon(0,STALKS[0]);self.assertEqual(new.rule_state.get('xhilag_damage',2),2)
 def test_stalk_damage_uses_its_enchantment_and_hero_when_no_minions(self):
  g=self.game();stalk=g._summon(0,STALKS[0]);stalk.rule_state['xhilag_damage']=4
  g._effect(('historic_stalk_damage',),dict(owner=0,source=stalk,target=0,bonus=0,lifesteal=False));self.assertEqual(g.players[1].health,26)
 def test_behemoth_lure_forces_enemy_attack_without_spending_its_attack(self):
  g=self.game();body=g._summon(0,'TSC_216');lure=next(m for m in g.players[0].minions if m.card_id=='TSC_216t');enemy=g._summon(1,'CORE_EX1_162');g.players[0].health=15
  g._effect(('historic_behemoth_lure',),dict(owner=0,source=lure,target=0,bonus=0,lifesteal=False));g._settle();self.assertEqual(enemy.attacks,0);self.assertFalse(g.players[1].minions);self.assertGreater(g.players[0].health,15)
 def test_glugg_uses_original_not_buffed_death_stats(self):
  g=self.game();body=g._summon(0,'TSC_639');tail=next(m for m in g.players[0].minions if m.card_id=='TSC_639t');g._buff(tail,5,5);tail.health=0;g._settle();self.assertEqual((body.attack,body.max_health),(5,7))
 def test_sindragosa_destroys_frozen_enemy_and_silence_disables_it(self):
  g=self.game();body=g._summon(0,'NX2_037');enemy=g._summon(1,'CORE_EX1_162');g._freeze(enemy.uid);g._settle();self.assertFalse(g.players[1].minions)
  g._silence(body);enemy=g._summon(1,'CORE_EX1_162');g._freeze(enemy.uid);g._settle();self.assertIn(enemy,g.players[1].minions)
 def test_sindragosa_wing_freezes_surviving_combat_target(self):
  g=self.game();wing=g._summon(0,'NX2_037t');enemy=g._summon(1,'TSC_026');g.players[1].board[:]=[enemy]
  g.step(Action('attack',wing.uid,enemy.uid));self.assertGreaterEqual(enemy.frozen_until,g.turn)
 def test_neptulon_hands_replace_damage_and_preserve_their_attack_allowance(self):
  g=self.game();body=g._summon(0,'TID_712');body.summoned_turn=-1;hands=[m for m in g.players[0].minions if m is not body]
  g.step(Action('attack',body.uid,-2));self.assertEqual(g.players[1].health,22);self.assertEqual(body.attacks,1);self.assertTrue(all(m.attacks==0 for m in hands))
  g.step(Action('attack',body.uid,-2));self.assertEqual(g.players[1].health,14);self.assertEqual(body.attacks,2)
 def test_neptulon_hands_immune_only_when_attacking(self):
  g=self.game();body=g._summon(0,'TID_712');body.summoned_turn=-1;enemy=g._summon(1,'TSC_639');g.players[1].board[:]=[enemy];g._buff(enemy,0,20)
  g.step(Action('attack',body.uid,enemy.uid));self.assertTrue(all(m.health==2 for m in g.players[0].minions if m.card_id in ('TID_712t','TID_712t2')))
  hand=next(m for m in g.players[0].minions if m.card_id=='TID_712t');g._damage(hand.uid,1);self.assertEqual(hand.health,1)
 def test_silenced_neptulon_uses_own_attack_without_other_source(self):
  g=self.game();body=g._summon(0,'TID_712');g._silence(body);body.summoned_turn=-1;g.step(Action('attack',body.uid,-2));self.assertEqual(g.players[1].health,23)
 def test_nellie_three_private_choices_store_crew_until_ship_death(self):
  g=self.game();self.play(g,'TSC_660');chosen=[]
  while g.pending_choice:
   chosen.append(g.pending_choice['options'][0]['card_id']);g.step(Action('choose',choices=(0,)))
  ship=next(m for m in g.players[0].minions if m.card_id=='TSC_660t');self.assertEqual(len(chosen),3);self.assertEqual(ship._nellie_crew,chosen);self.assertFalse(g.players[0].hand)
  self.assertNotIn('_nellie_crew',str(g.observe(1)));ship.health=0;g._settle();self.assertEqual([c.card_id for c in g.players[0].hand],chosen);self.assertTrue(all(c.set_cost==1 for c in g.players[0].hand))
 def test_silenced_ship_does_not_return_crew(self):
  g=self.game();ship=g._summon(0,'TSC_660t');ship._nellie_crew=['CORE_EX1_162'];g._silence(ship);ship.health=0;g._settle();self.assertFalse(g.players[0].hand)
 def test_gigafin_devours_without_deathrattles_then_resummons_exact_identities(self):
  g=self.game();enemy=g._summon(1,'CORE_EX1_110');body=self.play(g,'TSC_962');self.assertFalse(g.players[1].minions);self.assertFalse(g.players[1].death_history)
  body.health=0;g._settle();self.assertEqual([m.card_id for m in g.players[1].minions],['CORE_EX1_110'])
 def test_gigafin_maw_destroys_stored_contents_and_silence_preserves_contents(self):
  for silenced in (False,True):
   g=self.game();g._summon(1,'CORE_EX1_162');body=self.play(g,'TSC_962');maw=next(m for m in g.players[0].minions if m.card_id=='TSC_962t')
   if silenced:g._silence(maw)
   maw.health=0;g._settle();body.health=0;g._settle();self.assertEqual(len(g.players[1].minions),1 if silenced else 0)
 def test_past_colossal_manifest_is_complete_independent_of_runtime_registry(self):
  import hashlib,json
  from pathlib import Path
  from standard.catalog import load_all_records,load_catalog
  from expanded.historical_generation import PAST_SETS
  from expanded.identities import identity_resolver
  records={d['id']:d for d in load_all_records()};canonical=identity_resolver(records);standard={canonical(d) for d in load_catalog()}
  expected={d['id'] for d in records.values() if d.get('collectible') and d.get('type')=='MINION' and d.get('set') in PAST_SETS and 'COLOSSAL' in d.get('mechanics',()) and canonical(d) not in standard}
  manifest=json.loads((Path(__file__).resolve().parents[1]/'expanded/historical_colossal_pool.json').read_text())
  self.assertEqual({m['id'] for m in manifest['members']},expected);self.assertEqual(manifest['count'],13)
  for member in manifest['members']:self.assertEqual(member['sha256'],hashlib.sha256(json.dumps(records[member['id']],sort_keys=True).encode()).hexdigest())
 def test_complete_past_colossal_pool_for_every_class(self):
  from expanded.historical_generation import COLOSSAL
  from expanded.selectors import HERO_CLASSES
  from expanded.game import Game
  from test_expanded_passive_admission import PassiveAdmissionTests
  helper=PassiveAdmissionTests()
  expected={'NX2_037','TID_711','TID_712','TSC_026','TSC_029','TSC_030','TSC_216','TSC_219','TSC_639','TSC_660','TSC_937','TSC_950','TSC_962'}
  for hero_class in sorted(HERO_CLASSES):
   if hero_class=='DEATHKNIGHT':
    from expanded.decks import Deck,eligible,validate
    from expanded.fabled_decks import BUNDLES
    records=cards.registry();ids=[cid for cid in sorted(cards.COLLECTIBLE_IDS) if cid not in BUNDLES and cid not in ('CORE_EX1_162','JAIL_397','JAIL_430') and eligible(records[cid],hero_class,(1,1,1))]
    deck=Deck(hero_class,('CORE_EX1_162',)+tuple(ids[:29]),(1,1,1));self.assertEqual(validate(deck),[])
   else:deck=helper.deck(hero_class,'CORE_EX1_162')
   g=Game([deck,helper.deck('HUNTER','CORE_EX1_162')],seed=97)
   self.assertEqual(set(g._generation_candidates(COLOSSAL,0)),expected)
 def test_timewarped_colossal_paid_play_generates_from_full_past_pool(self):
  g=self.game();c=g._add(0,'CATA_EVENT_000');g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual(len(g.players[0].hand),1)
  from expanded.historical_generation import COLOSSAL
  self.assertIn(g.players[0].hand[0].card_id,g._generation_candidates(COLOSSAL,0))
 def test_new_layouts_match_frozen_left_position_markers(self):
  import json
  from pathlib import Path
  from expanded.historical_colossal import LAYOUTS
  manifest=json.loads((Path(__file__).resolve().parents[1]/'expanded/historical_colossal_layouts.json').read_text())
  flags={row['id']:row['left_marker'] for row in manifest['members']}
  expected={cid for layout in LAYOUTS.values() for cid,_ in layout};self.assertEqual(set(flags),expected)
  for layout in LAYOUTS.values():
   for cid,side in layout:self.assertEqual(side,'left' if flags[cid] else 'right')
 def test_missing_historical_colossal_member_rejects_whole_pool_before_randomness(self):
  from expanded.historical_generation import COLOSSAL
  from engine.cards import UnsupportedCard
  g=self.game();g.cards=dict(g.cards);g.cards.pop('TID_712');before=g.rng.getstate()
  with self.assertRaises(UnsupportedCard):g._generation_candidates(COLOSSAL,0)
  self.assertEqual(g.rng.getstate(),before)
