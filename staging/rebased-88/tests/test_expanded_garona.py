import unittest,gzip,json
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
import test_expanded_generation as fixtures
from expanded import cards,garona as rules,Action
from engine.game import Card
from engine.cards import UnsupportedCard

class GaronaTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(self.records[cid]) for cid in (*rules.RULES,*rules.TOKEN_RULES)})
  for table,values in ((cards.RULES,{**rules.RULES,**rules.TOKEN_RULES}),(cards.WEAPON_TRIGGERS,rules.WEAPON_TRIGGERS)):
   p=patch.dict(table,values);p.start();self.addCleanup(p.stop)
 def run_ops(self,ops,**kw):
  ctx=dict(owner=0,source=None,target=0,bonus=0,lifesteal=False);ctx.update(kw)
  self.g._start_play_effects(ops,ctx);self.g._settle(allow_event_choices=True)
 def play(self,cid):
  card=self.g._add(0,cid);self.p.mana=10
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid));return card
 def original(self,owner):
  c=Card(self.g._new_id(),'TIME_875t');c._starting_owner=owner;c._starting_identity=self.records[c.card_id]['dbfId'];return c
 def test_opening_transfer_preserves_physical_origin(self):
  c=self.original(0);self.p.deck=[c];self.q.deck=[];self.g._garona_start()
  self.assertFalse(self.p.deck);self.assertIs(self.q.deck[0],c);self.assertTrue(self.g._started_in_deck(c,0));self.assertFalse(self.g._started_in_deck(c,1));self.assertFalse(self.q.shuffle_history)
 def test_both_original_kings_move_once(self):
  a=self.original(0);b=self.original(1);self.p.deck=[a];self.q.deck=[b];self.g._garona_start()
  self.assertEqual(self.p.deck,[b]);self.assertEqual(self.q.deck,[a])
 def test_generated_nonoriginal_king_does_not_receive_start_trigger(self):
  c=Card(self.g._new_id(),'TIME_875t');self.p.deck=[c];self.q.deck=[];self.g._garona_start();self.assertEqual(self.p.deck,[c]);self.assertFalse(self.q.deck)
 def test_garona_removes_king_without_discard_and_halves_current_health(self):
  king=self.g._add(1,'TIME_875t');self.q.health=17;self.q.armor=10;self.play('TIME_875')
  self.assertNotIn(king,self.q.hand);self.assertFalse(self.q.discard_history);self.assertEqual((self.q.health,self.q.max_health,self.q.armor),(8,30,10));self.assertTrue(self.q.hero_health_changed_turn);self.assertEqual(self.q.hero_damage_events_turn,0)
 def test_one_health_is_lethal(self):
  self.g._add(1,'TIME_875t');self.q.health=1;self.play('TIME_875');self.assertTrue(self.g.terminal);self.assertEqual(self.g.winner,0)
 def test_no_held_king_does_not_affect_health(self):
  self.g._summon(1,'TIME_875t');self.q.deck=['TIME_875t'];self.play('TIME_875');self.assertEqual(self.q.health,30)
 def test_own_king_does_not_qualify(self):
  self.g._add(0,'TIME_875t');self.play('TIME_875');self.assertEqual(self.q.health,30)
 def test_duplicate_held_kings_reject_paid_play_and_rollback(self):
  self.g._add(1,'TIME_875t');self.g._add(1,'TIME_875t');card=self.g._add(0,'TIME_875');before=deepcopy(self.g.observe(0));action=next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid)
  with self.assertRaises(UnsupportedCard):self.g.step(action)
  self.assertEqual(self.g.observe(0),before)
 def test_king_draws_before_reshuffling_from_board(self):
  self.p.deck=['CORE_CS2_029'];self.play('TIME_875t');self.assertFalse(self.p.board);self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029']);self.assertEqual([c.card_id for c in self.p.deck],['TIME_875t']);self.assertEqual(len(self.p.shuffle_history),1);self.assertFalse(self.p.death_history)
 def test_king_shuffle_drops_buffs_preserves_starting_origin(self):
  card=self.original(0);card.attack_bonus=8;self.p.hand=[card];self.p.deck=['CORE_CS2_029'];self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid))
  c=self.p.deck[0];self.assertEqual(c.attack_bonus,0);self.assertTrue(self.g._started_in_deck(c,0))
 def test_removed_source_cannot_be_shuffled_again(self):
  m=self.g._summon(0,'TIME_875t');self.p.board.remove(m);before=len(self.p.deck);self.run_ops([('garona_king_shuffle',)],source=m);self.assertEqual(len(self.p.deck),before)
 def test_kingslayers_draws_actual_legendary_for_both_players(self):
  a=Card(self.g._new_id(),'TIME_875');b=Card(self.g._new_id(),'TIME_875');self.p.deck=['CORE_CS2_029',a];self.q.deck=[b,'CORE_CS2_029']
  self.run_ops([('garona_kingslayers',)]);self.assertIs(self.p.hand[0],a);self.assertIs(self.q.hand[0],b)
 def test_kingslayers_no_matching_cards_does_not_fatigue(self):
  self.p.deck=[];self.q.deck=[];self.run_ops([('garona_kingslayers',)]);self.assertEqual((self.p.fatigue,self.q.fatigue),(0,0))
 def test_kingslayers_last_durability_still_triggers(self):
  self.play('TIME_875t1');self.p.weapon['durability']=1;self.p.deck=['TIME_875'];self.q.deck=['TIME_875'];self.g.step(next(a for a in self.g.legal_actions() if a.kind=='attack' and a.source<0 and a.target==self.g.hero_id(1)))
  self.assertIsNone(self.p.weapon);self.assertEqual([c.card_id for c in self.p.hand],['TIME_875']);self.assertEqual([c.card_id for c in self.q.hand],['TIME_875'])

 def test_opening_hook_accepts_legacy_string_fixture_decks(self):
  self.p.deck=['CORE_CS2_029','TIME_875t'];self.q.deck=['NEW1_034']
  self.g._garona_start();self.assertEqual(self.p.deck,['CORE_CS2_029','TIME_875t']);self.assertEqual(self.q.deck,['NEW1_034'])
