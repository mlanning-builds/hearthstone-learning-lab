import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,broxigar as rules,Action,Game,random_deck
from expanded.decks import Deck
from engine.game import Card
from engine.cards import UnsupportedCard

class BroxigarTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in (*rules.RULES,*rules.TOKEN_RULES)})
  for table,values in ((cards.RULES,{**rules.RULES,**rules.TOKEN_RULES}),(cards.DEATH_EFFECTS,rules.DEATH_EFFECTS),(cards.WEAPON_TRIGGERS,rules.WEAPON_TRIGGERS)):
   p=patch.dict(table,values);p.start();self.addCleanup(p.stop)
 def run_ops(self,ops,**kw):
  ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False);ctx.update(kw)
  self.g._start_play_effects(ops,ctx);self.g._settle(allow_event_choices=True)
 def play(self,cid):
  card=self.g._add(self.g.current,cid);self.g.players[self.g.current].mana=10
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid));return card
 def original(self,owner=0):
  c=Card(self.g._new_id(),'TIME_020');c._starting_owner=owner;c._starting_identity=self.records[c.card_id]['dbfId'];return c
 def hide(self):
  c=self.original();self.p.deck.append(c);self.g._brox_start();return c
 def kill(self,m):m.health=0;self.g._settle(allow_event_choices=True)
 def test_original_disappears_without_drawing_or_dying(self):
  c=self.hide();self.assertNotIn(c,self.p.deck);self.assertEqual(self.g._broxigar_waiting,[c]);self.assertFalse(self.p.hand or self.p.death_history)
  self.g._brox_start();self.assertEqual(self.g._broxigar_waiting,[c])
 def test_start_ignores_generated_and_legacy_string_cards(self):
  c=Card(self.g._new_id(),'TIME_020');self.p.deck=[c,'TIME_020'];self.g._brox_start();self.assertEqual(self.p.deck,[c,'TIME_020']);self.assertFalse(self.g._broxigar_waiting)
 def test_real_game_expands_bundle_then_hides_before_opening_hands(self):
  metadata=cards.registry();metadata.update({cid:self.records[cid] for cid in (*rules.RULES,*rules.TOKEN_RULES)})
  d=Deck('DEMONHUNTER',('TIME_020',)+random_deck('DEMONHUNTER',8).cards[:27])
  other=random_deck('HUNTER',2)
  with patch('expanded.game.registry',return_value=metadata),patch('expanded.decks.COLLECTIBLE_IDS',set(cards.COLLECTIBLE_IDS)|{'TIME_020'}):g=Game([d,other],seed=1)
  self.assertEqual(len(g.players[0].starting_deck),30);self.assertEqual(len(g.players[0].deck)+len(g.players[0].hand),29);self.assertEqual(len(g._broxigar_waiting),1)
  self.assertFalse(any(c.card_id=='TIME_020' for c in g.players[0].hand))
 def test_all_four_portals_summon_exact_opposing_demons(self):
  for portal,demon in zip(rules.PORTALS,rules.DEMONS):
   self.play(portal);m=self.q.minions[-1];self.assertEqual(m.card_id,demon);self.assertEqual((m.attack,m.health),(self.records[demon]['attack'],1))
 def test_full_opposing_board_does_not_progress_chain(self):
  c=self.hide()
  for _ in range(7):self.g._summon(1,'NEW1_034')
  before=len(self.p.deck);self.play(rules.PORTALS[0]);self.assertEqual(len(self.p.deck),before);self.assertEqual(self.g._broxigar_waiting,[c])
 def test_each_nonfinal_death_draws_before_inserting_exact_next_portal(self):
  for index,demon in enumerate(rules.DEMONS[:-1]):
   self.p.hand=[];self.p.deck=['CORE_CS2_029'];m=self.g._summon(1,demon);self.kill(m)
   self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029']);self.assertEqual([c.card_id for c in self.p.deck],[rules.PORTALS[index+1]])
 def test_empty_deck_draw_fatigues_before_portal_is_shuffled(self):
  self.p.deck=[];self.kill(self.g._summon(1,rules.DEMONS[0]));self.assertEqual(self.p.health,29);self.assertEqual(self.p.fatigue,1);self.assertEqual(self.p.deck[0].card_id,rules.PORTALS[1])
 def test_changed_demon_controller_changes_reward_recipient(self):
  self.p.deck=['CORE_CS2_029'];self.q.deck=['CORE_CS2_029'];self.kill(self.g._summon(0,rules.DEMONS[0]));self.assertFalse(self.p.hand);self.assertEqual(len(self.q.hand),1);self.assertEqual(self.q.deck[0].card_id,rules.PORTALS[1])
 def test_silenced_demon_has_no_reward(self):
  m=self.g._summon(1,rules.DEMONS[0]);self.g._silence(m);self.kill(m);self.assertFalse(self.p.hand);self.assertFalse(self.p.shuffle_history)
 def test_final_returns_same_physical_card_only_once(self):
  c=self.hide();self.kill(self.g._summon(1,rules.DEMONS[-1]));self.assertIs(self.p.hand[-1],c);self.assertTrue(self.g._started_in_deck(c,0))
  self.kill(self.g._summon(1,rules.DEMONS[-1]));self.assertEqual(sum(x.card_id=='TIME_020' for x in self.p.hand),1)
 def test_opponent_can_claim_original_without_generating_copy(self):
  c=self.hide();self.g.current=1;self.play(rules.PORTALS[-1]);self.kill(self.p.minions[-1]);self.assertIs(self.q.hand[-1],c);self.assertFalse(self.g._started_in_deck(c,1));self.assertFalse(self.g._broxigar_waiting)
 def test_no_original_means_no_reward(self):
  self.kill(self.g._summon(1,rules.DEMONS[-1]));self.assertFalse(self.p.hand)
 def test_full_hand_consumes_return_without_overdraw_recovery(self):
  c=self.hide();self.p.overdraw_return_active=True
  for _ in range(10):self.g._add(0,'TOKEN_COIN')
  self.kill(self.g._summon(1,rules.DEMONS[-1]));self.assertFalse(self.g._broxigar_waiting);self.assertFalse(self.p.overdraw_cache);self.assertNotIn(c,self.p.hand)
 def test_multiple_originals_fail_before_consuming_either(self):
  a=self.hide();b=self.original(1);self.q.deck.append(b);self.g._brox_start()
  with self.assertRaisesRegex(UnsupportedCard,'Multiple disappeared'):self.run_ops([('brox_return',)],owner=1)
  self.assertEqual(self.g._broxigar_waiting,[a,b])
 def test_internal_portal_cast_is_supported_and_not_a_paid_play(self):
  self.run_ops([('cast_fixed_spell',rules.PORTALS[0],'random')]);self.assertEqual(self.q.minions[0].card_id,rules.DEMONS[0]);self.assertFalse(self.p.played_history)
 def test_returned_broxigar_has_charge(self):
  self.hide();self.kill(self.g._summon(1,rules.DEMONS[-1]));c=self.p.hand[0];self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertTrue(any(a.kind=='attack' and a.source==self.p.minions[0].uid and a.target==self.g.hero_id(1) for a in self.g.legal_actions()))
 def test_waiting_state_clones_without_shared_cards(self):
  c=self.hide();clone=deepcopy(self.g);self.kill(self.g._summon(1,rules.DEMONS[-1]));self.assertEqual(len(clone._broxigar_waiting),1);self.assertIsNot(clone._broxigar_waiting[0],c)
 def test_public_waiting_count_has_no_physical_payload(self):
  self.hide()
  for viewer in (0,1):
   view=self.g.observe(viewer);self.assertEqual(view['players'][0]['broxigar_waiting'],1);self.assertNotIn('_broxigar_waiting',str(view))
 def test_axe_kill_draws_physical_portal_and_heals(self):
  self.play('TIME_020t1');self.p.health=20;m=self.g._summon(1,'NEW1_034');m.attack=0;portal=Card(self.g._new_id(),rules.PORTALS[0]);self.p.deck=[portal,'CORE_CS2_029']
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='attack' and a.source<0 and a.target==m.uid));self.assertIn(portal,self.p.hand);self.assertGreater(self.p.health,20)
 def test_axe_nonlethal_attack_does_not_draw(self):
  self.play('TIME_020t1');m=self.g._summon(1,'NEW1_034');self.g._buff(m,0,10);self.p.deck=[rules.PORTALS[0]]
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='attack' and a.source<0 and a.target==m.uid));self.assertFalse(self.p.hand)
 def test_axe_hero_attack_does_not_draw(self):
  self.play('TIME_020t1');self.p.deck=[rules.PORTALS[0]];self.g.step(next(a for a in self.g.legal_actions() if a.kind=='attack' and a.source<0 and a.target==self.g.hero_id(1)));self.assertFalse(self.p.hand)
 def test_axe_last_durability_kill_still_draws(self):
  self.play('TIME_020t1');self.p.weapon['durability']=1;m=self.g._summon(1,'NEW1_034');self.p.deck=[rules.PORTALS[2]]
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='attack' and a.source<0 and a.target==m.uid));self.assertIsNone(self.p.weapon);self.assertEqual(self.p.hand[0].card_id,rules.PORTALS[2])
 def test_unrelated_minion_kill_with_axe_equipped_does_not_draw(self):
  self.play('TIME_020t1');self.p.deck=[rules.PORTALS[0]];self.kill(self.g._summon(1,'NEW1_034'));self.assertFalse(self.p.hand)
 def test_complete_portal_chain_releases_original(self):
  original=self.hide();self.play(rules.PORTALS[0])
  for index in range(4):
   self.kill(self.q.minions[0])
   if index<3:
    card=self.g._draw(0,predicate=lambda d:d['id']==rules.PORTALS[index+1])
    self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid))
  self.assertIn(original,self.p.hand);self.assertFalse(self.g._broxigar_waiting);self.assertEqual(len(self.p.shuffle_history),3)

 def test_axe_does_not_claim_kill_caused_by_weapon_deathrattle(self):
  self.play('TIME_020t1');self.p.weapon['durability']=1;self.p.weapon['attached_death_effects']=[('area_damage','enemy_minions',1)]
  m=self.g._summon(1,'NEW1_034');self.g._buff(m,0,2);self.p.deck=[rules.PORTALS[0]]
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='attack' and a.source<0 and a.target==m.uid))
  self.assertFalse(self.p.hand);self.assertNotIn(m,self.q.minions)
