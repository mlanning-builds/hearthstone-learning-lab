"""Controlled staged fixtures; not a client-conformance certificate."""
import gzip,json,unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
import test_expanded_generation as fixtures
from engine.game import Card
from engine.cards import UnsupportedCard
from expanded import Action,cards,muradin as rules
from expanded.features import SCHEMA,encode_decision

class MuradinTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  with gzip.open(Path(__file__).resolve().parents[1]/'data/standard/all_cards.json.gz','rt') as f:cls.records={c['id']:c for c in json.load(f)}
 def setUp(self):
  self.fx=fixtures.GenerationTests();self.g=self.fx.game();self.p,self.q=self.g.players
  self.g.cards.update({cid:deepcopy(c) for cid,c in self.records.items() if cid.startswith('TIME_209')})
  self.g.cards['TEST_MURADIN_TARGET']=dict(self.g.cards['NEW1_032'],id='TEST_MURADIN_TARGET',mechanics=[])
  for table,values in ((cards.RULES,{**rules.RULES,**rules.TOKEN_RULES}),(cards.DEATH_EFFECTS,rules.DEATH_EFFECTS)):
   patcher=patch.dict(table,values);patcher.start();self.addCleanup(patcher.stop)
 def play(self,cid,target=0):
  self.p.mana=10;c=self.g._add(0,cid)
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid and a.target==target))
  return c
 def take(self):
  self.play('TIME_209');return self.p.minions[-1]
 def run_ops(self,ops,**kw):self.fx.run_ops(self.g,ops,**kw)
 def avatar(self,target):self.play('TIME_209t2',target)
 def attack(self,source,target=-2):self.g.step(Action('attack',source=source,target=target))
 def test_deck_hammer_moves_without_draw(self):
  c=Card(self.g._new_id(),rules.HAMMER);c.attack_bonus=4;c.health_bonus=1;c.cost_delta=-1;self.p.deck=[c]
  m=self.take();self.assertFalse(self.p.deck);self.assertIs(m._muradin_hammer['card'],c);self.assertEqual((m.attack,m.max_health),(10,7));self.assertFalse(self.p.hand)
  self.assertFalse(any(e.get('kind')=='draw' and e.get('card')==rules.HAMMER for e in self.g.events))
 def test_deck_takes_priority_over_hand_and_equipped(self):
  deck=Card(self.g._new_id(),rules.HAMMER);self.p.deck=[deck];hand=self.g._add(0,rules.HAMMER);self.g._equip(0,rules.HAMMER);equipped=self.p.equipped_card
  m=self.take();self.assertIs(m._muradin_hammer['card'],deck);self.assertIn(hand,self.p.hand);self.assertIs(self.p.equipped_card,equipped)
 def test_hand_takes_priority_over_equipped(self):
  c=self.g._add(0,rules.HAMMER);self.g._equip(0,rules.HAMMER);equipped=self.p.equipped_card;m=self.take();self.assertIs(m._muradin_hammer['card'],c);self.assertIs(self.p.equipped_card,equipped)
 def test_equipped_retrieval_does_not_break_or_upgrade(self):
  self.g._equip(0,rules.HAMMER);card=self.p.equipped_card;self.p.weapon['attack']=7;self.p.weapon['durability']=2
  m=self.take();self.assertEqual((m.attack,m.health),(10,4));self.assertIs(m._muradin_hammer['card'],card);self.assertIsNone(self.p.weapon);self.assertIsNone(self.p.equipped_card);self.assertEqual(card.attack_bonus,4)
  self.assertFalse(any(e.get('kind')=='weapon_broken' for e in self.g.events))
 def test_no_hammer_has_no_bonus_or_return(self):
  m=self.take();self.assertEqual((m.attack,m.health),(3,2));self.assertNotIn('WINDFURY',self.g._effective_keywords(m));m.health=0;self.g._settle();self.assertFalse(self.p.hand)
 def test_other_players_hammer_not_retrieved(self):
  c=self.g._add(1,rules.HAMMER);m=self.take();self.assertIn(c,self.q.hand);self.assertFalse(hasattr(m,'_muradin_hammer'))
 def test_death_returns_same_card_and_held_modifiers(self):
  c=self.g._add(0,rules.HAMMER);c.attack_bonus=6;c.cost_delta=-2;m=self.take();m.health=0;self.g._settle();self.assertIs(self.p.hand[0],c);self.assertEqual((c.attack_bonus,c.cost_delta),(6,-2))
 def test_full_hand_return_burns_instead_of_duplicating(self):
  self.g._add(0,rules.HAMMER);m=self.take()
  for _ in range(10):self.g._add(0,'NEW1_034')
  m.health=0;self.g._settle();self.assertEqual(len(self.p.hand),10);self.assertFalse(hasattr(m,'_muradin_hammer'))
 def test_silence_preserves_external_hammer_but_removes_rush(self):
  self.g._add(0,rules.HAMMER);m=self.take();self.g._buff(m,4,4);self.g._silence(m)
  self.assertEqual((m.attack,m.max_health),(6,6));self.assertIn('WINDFURY',self.g._effective_keywords(m));self.assertNotIn('RUSH',self.g._effective_keywords(m));m.health=0;self.g._settle();self.assertEqual(self.p.hand[0].card_id,rules.HAMMER)
 def test_copy_has_independent_hammer_identity_and_correct_stats(self):
  self.g._add(0,rules.HAMMER);m=self.take();self.g._damage(m.uid,2);copy=self.g._summon(0,m.card_id,copy_from=m)
  self.assertEqual((copy.attack,copy.health,copy.max_health),(6,4,6));self.assertIsNot(copy._muradin_hammer['card'],m._muradin_hammer['card']);self.assertNotEqual(copy._muradin_hammer['card'].uid,m._muradin_hammer['card'].uid)
  m.health=copy.health=0;self.g._settle();self.assertEqual(len(self.p.hand),2)
 def test_transformation_drops_attachment(self):
  self.g._add(0,rules.HAMMER);m=self.take();new=self.g._transform(m,'NEW1_034');new.health=0;self.g._settle();self.assertFalse(self.p.hand)
 def test_control_change_returns_to_new_controller(self):
  self.g._add(0,rules.HAMMER);m=self.take();self.p.board.remove(m);self.q.board.append(m);m.owner=1;m.health=0;self.g._settle();self.assertFalse(self.p.hand);self.assertEqual(self.q.hand[0].card_id,rules.HAMMER)
 def test_repeated_return_moves_only_once(self):
  self.g._add(0,rules.HAMMER);m=self.take();self.run_ops([('muradin_return',),('muradin_return',)],source=m);self.assertEqual(len(self.p.hand),1)
 def test_second_distinct_binding_rejects(self):
  self.g._add(0,rules.HAMMER);m=self.take();c=self.g._add(0,rules.HAMMER)
  with self.assertRaises(UnsupportedCard):self.run_ops([('muradin_take',)],source=m)
  self.assertIn(c,self.p.hand)
 def test_equipped_hammer_windfury_allows_two_attacks(self):
  self.play(rules.HAMMER);self.attack(-1);self.attack(-1);self.assertEqual(self.q.health,24);self.assertFalse(any(a.kind=='attack' and a.source==-1 for a in self.g.legal_actions()))
 def test_hammer_break_upgrades_original_and_can_be_equipped_again(self):
  c=self.play(rules.HAMMER);self.p.weapon['attack']=9;self.p.weapon['durability']=1;self.attack(-1)
  self.assertIsNone(self.p.equipped_card);self.assertIn(c,self.p.deck);self.assertEqual(c.attack_bonus,8)
  self.p.deck.remove(c);self.g._enter_hand(0,c);self.p.mana=10;self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual((self.p.weapon['attack'],self.p.weapon['durability']),(11,4));self.assertIs(self.p.equipped_card,c)
 def test_hammer_replacement_also_shuffles(self):
  c=self.play(rules.HAMMER);self.g._equip(0,'CS2_082');self.assertIn(c,self.p.deck);self.assertEqual(c.attack_bonus,2)
 def test_repeated_shuffle_does_not_duplicate_physical_card(self):
  c=Card(self.g._new_id(),rules.HAMMER);weapon=dict(card_id=rules.HAMMER,attack=3,durability=0)
  self.run_ops([('hammer_shuffle',),('hammer_shuffle',)],broken_weapon=weapon,broken_weapon_card=c);self.assertEqual(sum(v is c for v in self.p.deck),1);self.assertEqual(c.attack_bonus,2)
 def test_avatar_hero_attack_and_wave(self):
  enemy=self.g._summon(1,'TEST_MURADIN_TARGET');self.avatar(-1);self.attack(-1);self.assertEqual(self.q.health,26);self.assertEqual(enemy.health,2)
 def test_avatar_minion_attack_and_wave(self):
  m=self.g._summon(0,'NEW1_034');enemy=self.g._summon(1,'TEST_MURADIN_TARGET');self.avatar(m.uid);self.attack(m.uid);self.assertEqual(self.q.health,22);self.assertEqual(enemy.health,2)
 def test_avatar_stacks_separate_waves(self):
  self.avatar(-1);self.avatar(-1);self.attack(-1);self.assertEqual(self.q.health,22)
 def test_avatar_expires_for_hero_and_minion(self):
  m=self.g._summon(0,'NEW1_034');self.avatar(-1);self.avatar(m.uid);self.g.step(Action('end'));self.assertFalse(self.p.avatar_form);self.assertNotIn('avatar_form',m.rule_state);self.assertEqual(m.attack,4);self.assertEqual(self.g._hero_attack(0),0)
 def test_avatar_silence_removes_effect(self):
  m=self.g._summon(0,'NEW1_034');self.avatar(m.uid);self.g._silence(m);m.summoned_turn=-1;self.attack(m.uid);self.assertEqual(self.q.health,26)
 def test_avatar_can_be_applied_after_silence(self):
  m=self.g._summon(0,'NEW1_034');self.g._silence(m);m.summoned_turn=-1;self.avatar(m.uid);self.attack(m.uid);self.assertEqual(self.q.health,22)
 def test_avatar_copy_retains_effect_until_end_of_turn(self):
  m=self.g._summon(0,'NEW1_034');self.avatar(m.uid);copy=self.g._summon(0,m.card_id,copy_from=m);self.attack(copy.uid);self.assertEqual(self.q.health,22)
 def test_avatar_forced_attack_uses_same_hook(self):
  m=self.g._summon(0,'NEW1_032');self.avatar(m.uid);self.g._force_attack(m.uid,-2);self.assertEqual(self.q.health,22);self.assertEqual(m.attacks,0)
 def test_avatar_mortally_wounded_attacker_fires_before_death(self):
  m=self.g._summon(0,'NEW1_034');enemy=self.g._summon(1,'TEST_MURADIN_TARGET');self.avatar(m.uid);self.attack(m.uid,enemy.uid);self.assertEqual(self.q.health,28);self.assertNotIn(m,self.p.board)
 def test_avatar_poisonous_wave_kills_other_minions(self):
  m=self.g._summon(0,'NEW1_034');m.keywords.add('POISONOUS');enemy=self.g._summon(1,'TEST_MURADIN_TARGET');self.avatar(m.uid);self.attack(m.uid);self.assertNotIn(enemy,self.q.board)
 def test_avatar_lifesteal_wave_heals_as_character_damage(self):
  self.p.health=10;m=self.g._summon(0,'NEW1_034');m.keywords.add('LIFESTEAL');self.g._summon(1,'TEST_MURADIN_TARGET');self.avatar(m.uid);self.attack(m.uid);self.assertEqual(self.p.health,20)
 def test_avatar_is_not_spell_damage(self):
  self.g.cards['TIME_890t']=deepcopy(self.records['TIME_890t']);self.g._equip(0,'TIME_890t');m=self.g._summon(0,'NEW1_034');self.avatar(m.uid);self.attack(m.uid);self.assertEqual(self.q.health,22);self.assertEqual(self.p.spell_damage_turn,0)
 def test_hero_avatar_survives_last_weapon_charge(self):
  self.play(rules.HAMMER);self.p.weapon['durability']=1;self.avatar(-1);self.attack(-1);self.assertEqual(self.q.health,23);self.assertIsNone(self.p.weapon)
 def test_public_view_exposes_effect_not_private_card(self):
  self.g._add(0,rules.HAMMER);m=self.take();m._muradin_hammer['card'].rule_state={'private_marker':123};self.avatar(-1)
  for viewer in (0,1):
   view=self.g.observe(viewer);self.assertEqual(view['players'][0]['avatar_form'],1);self.assertEqual(view['players'][0]['board'][0]['held_hammer']['attack'],3);self.assertNotIn('private_marker',json.dumps(view))
  view=self.g.observe(0);rows=encode_decision(dict(observation=view,actor=0,actions=view['legal_actions']));self.assertIn('avatar_form',str(rows));self.assertEqual(SCHEMA,'visible-action-features-v58')
 def test_root_remains_staged(self):self.assertNotIn('TIME_209',cards.COLLECTIBLE_IDS)
 def test_durability_enchantment_survives_damage_and_shuffle(self):
  c=self.play(rules.HAMMER);self.g._buff_weapon(0,2,3);self.p.weapon['durability']=1;self.attack(-1);self.assertEqual((c.attack_bonus,c.health_bonus),(4,3))
  self.p.deck.remove(c);self.g._equip(0,rules.HAMMER,attack_bonus=c.attack_bonus,physical_card=c);self.assertEqual(self.p.weapon['durability'],7)
 def test_bounce_does_not_return_held_hammer(self):
  self.g._add(0,rules.HAMMER);m=self.take();self.g._bounce(m);self.g._settle();self.assertEqual([c.card_id for c in self.p.hand],['TIME_209'])
 def test_hand_overflow_before_take_is_not_required(self):
  c=Card(self.g._new_id(),rules.HAMMER);self.p.deck=[c]
  for _ in range(9):self.g._add(0,'NEW1_034')
  m=self.take();self.assertEqual(len(self.p.hand),9);self.assertIs(m._muradin_hammer['card'],c)
 def test_public_avatar_has_count_without_internal_binding_ids(self):
  m=self.g._summon(0,'NEW1_034');self.avatar(m.uid);view=self.g.observe(1);self.assertEqual(view['players'][0]['board'][0]['rule_state']['avatar_form'],1)
 def test_hero_poisonous_avatar_uses_attack_keyword_snapshot(self):
  self.play(rules.HAMMER);self.p.weapon['poisonous_until']=self.g.turn;self.p.weapon['durability']=1;enemy=self.g._summon(1,'TEST_MURADIN_TARGET');self.avatar(-1);self.attack(-1);self.assertNotIn(enemy,self.q.board)
 def test_hero_lifesteal_avatar_heals_damage_wave(self):
  self.p.health=10;self.p.hero_lifesteal_until=self.g.turn;self.g._summon(1,'TEST_MURADIN_TARGET');self.avatar(-1);self.attack(-1);self.assertEqual(self.p.health,16)
