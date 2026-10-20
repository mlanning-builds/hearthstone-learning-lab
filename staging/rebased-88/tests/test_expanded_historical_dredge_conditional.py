"""Exact generated identities and conditional Dredge interaction boundaries."""
import unittest
from expanded import Action,cards
import test_expanded_generation as fixtures
class ConditionalDredgeTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def deck(self,g,cid):
  p=g.players[0];c=g._add(0,cid);p.hand.remove(c);p.deck=[c];return c
 def play(self,g,cid):
  c=g._add(0,cid);g.players[0].mana=10
  g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));return c
 def choose(self,g):g.step(Action('choose',choices=(0,)))
 def test_harpoon_after_attack_reduces_beast_only_and_survives_last_durability(self):
  for cid,delta in (('CATA_130',-2),('CS2_200',0)):
   for durability in (1,2):
    g=self.game();c=self.deck(g,cid);self.play(g,'TSC_070');g.players[0].weapon['durability']=durability
    g.step(Action('attack',-1,-2));self.assertEqual(g.observe(1)['pending_choice'],{'owner':0,'waiting':True});self.choose(g)
    self.assertEqual(getattr(c,'cost_delta',0),delta);self.assertEqual(g.players[0].cards_played,1)
    self.assertEqual(g.players[0].weapon is None,durability==1)
 def test_harpoon_does_not_trigger_on_friendly_minion_attack(self):
  g=self.game();self.deck(g,'CORE_EX1_162');self.play(g,'TSC_070');m=g._summon(0,'CORE_EX1_162');m.summoned_turn=-1
  g.step(Action('attack',m.uid,-2));self.assertIsNone(g.pending_choice)
 def test_swordfish_buffs_exact_weapon_and_pirate_without_drawing(self):
  for cid,bonus in (('CORE_NEW1_018',2),('CORE_EX1_162',0)):
   g=self.game();c=self.deck(g,cid);weapon=self.play(g,'TSC_086');self.choose(g)
   self.assertEqual(c.attack_bonus,bonus);self.assertIs(g.players[0].deck[-1],c);self.assertFalse(g.players[0].hand)
   self.assertEqual(g.players[0].weapon['attack'],2+bonus);self.assertEqual(g.players[0].equipped_card.uid,weapon.uid)
 def test_swordfish_choice_does_not_buff_a_replacement_weapon(self):
  g=self.game();c=self.deck(g,'CORE_NEW1_018');self.play(g,'TSC_086');g._equip(0,'CS2_106');before=g.players[0].weapon['attack'];self.choose(g)
  self.assertEqual(c.attack_bonus,2);self.assertEqual(g.players[0].weapon['attack'],before)
 def test_aquatic_form_compares_remaining_mana_and_current_cost(self):
  for mana,delta,draw in ((3,0,False),(4,0,True),(3,-1,True)):
   g=self.game();c=self.deck(g,'CORE_CS2_029');c.cost_delta=delta;s=g._add(0,'TSC_654');g.players[0].mana=mana
   g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==s.uid));self.choose(g)
   self.assertEqual(c in g.players[0].hand,draw);self.assertEqual(c in g.players[0].deck,not draw);self.assertEqual(g.players[0].mana,mana)
 def test_aquatic_form_uses_successful_draw_events_and_full_hand_burn(self):
  g=self.game();c=self.deck(g,'CORE_EX1_162');g._summon(1,'CORE_SCH_717');self.play(g,'TSC_654');self.choose(g)
  self.assertIn(c,g.players[0].hand);self.assertEqual(len(g.players[1].hand),1)
  g=self.game();c=self.deck(g,'CORE_EX1_162');self.play(g,'TSC_654')
  for _ in range(10):g._add(0,'CORE_CS2_029')
  self.choose(g);self.assertFalse(g.players[0].deck);self.assertNotIn(c,g.players[0].hand);self.assertEqual(len(g.players[0].hand),10)
 def test_vilefin_grants_permanent_health_payment_to_only_selected_murloc(self):
  for cid,health in (('CORE_EX1_506',True),('CORE_EX1_162',False)):
   g=self.game();c=self.deck(g,cid);self.play(g,'TSC_753');self.choose(g)
   self.assertEqual(bool(getattr(c,'rule_state',{}).get('health_payment')),health)
   g._draw(0);g.turn+=10;self.assertEqual(g._payment_kind(c,0),'health' if health else 'mana')
   if health:
    g.players[0].mana=0;before=g.players[0].health;cost=g._cost(c,0)
    g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid));self.assertEqual(g.players[0].health,before-cost)
 def test_topple_reveals_selected_identity_and_uses_spell_damage(self):
  g=self.game();c=self.deck(g,'CORE_EX1_162');c.cost_delta=-1;spell_source=g._summon(0,'CORE_EX1_012');g._buff(spell_source,0,5);own=g._summon(0,'CS2_200');enemy=g._summon(1,'CS2_200');a,b=own.health,enemy.health
  self.play(g,'TID_703');self.choose(g);self.assertEqual((own.health,enemy.health),(a-2,b-2));self.assertIs(g.players[0].deck[-1],c)
  self.assertTrue(any(e['event']=='reveal_dredge' and e['card']==c.card_id and e['cost']==1 for e in g.observe(1)['events']))
 def test_topple_empty_deck_does_not_damage_even_with_spell_damage(self):
  g=self.game();g.players[0].deck=[];m=g._summon(0,'CORE_EX1_012');before=m.health;self.play(g,'TID_703');self.assertIsNone(g.pending_choice);self.assertEqual(m.health,before)
 def test_rock_bottom_summons_literal_children_before_and_after_dredge(self):
  for cid,count in (('CORE_EX1_506',2),('CORE_EX1_162',1)):
   g=self.game();c=self.deck(g,cid);self.play(g,'TSC_925');self.assertEqual([m.card_id for m in g.players[0].minions],['TSC_925t']);self.choose(g)
   self.assertEqual([m.card_id for m in g.players[0].minions],['TSC_925t']*count);self.assertIs(g.players[0].deck[-1],c)
 def test_rock_bottom_full_board_still_dredges_and_keeps_selected_card(self):
  g=self.game();c=self.deck(g,'CORE_EX1_506')
  for _ in range(7):g._summon(0,'CORE_EX1_162')
  self.play(g,'TSC_925');self.choose(g);self.assertEqual(len(g.players[0].board),7);self.assertIs(g.players[0].deck[-1],c)
 def test_internal_spells_resolve_automatic_choices_and_resume_parent(self):
  for cid in ('TSC_654','TID_703','TSC_925'):
   g=self.game();self.deck(g,'CORE_EX1_506');self.assertTrue(g._supports_internal_spell(cid,0))
   g._start_play_effects([('cast_fixed_spell',cid,'random'),('armor',2)],dict(owner=0,source=None,target=0,bonus=0,lifesteal=False));g._settle(allow_event_choices=True)
   self.assertIsNone(g.pending_choice);self.assertEqual(g.players[0].armor,2);self.assertEqual(g.players[0].cards_played,0)
 def test_generated_only_exact_root_and_child_registry(self):
  ids={'TSC_070','TSC_086','TSC_654','TSC_753','TID_703','TSC_925','TSC_925t'}
  self.assertTrue(ids<=cards.TOKEN_IDS&cards.PLAYABLE_TOKENS);self.assertFalse(ids&cards.COLLECTIBLE_IDS)

 def test_k9_recruits_selected_physical_minion_and_retains_hand_enchantments(self):
  g=self.game();c=self.deck(g,'CORE_EX1_506');c.cost_delta=-1;c.attack_bonus=3;c.health_bonus=2;g._summon(1,'CORE_SCH_717')
  self.play(g,'TID_099');self.choose(g);self.assertFalse(g.players[0].deck);self.assertFalse(g.players[1].hand)
  m=next(m for m in g.players[0].minions if m.card_id==c.card_id);self.assertEqual((m.attack,m.health),(5,3));self.assertFalse(any(e['event']=='draw' for e in g.events if e.get('card')==c.card_id))
 def test_k9_full_board_leaves_selected_card_on_top(self):
  g=self.game();c=self.deck(g,'CORE_EX1_506');c.cost_delta=-1
  for _ in range(6):g._summon(0,'CORE_EX1_162')
  self.play(g,'TID_099');self.choose(g);self.assertIs(g.players[0].deck[-1],c);self.assertEqual(len(g.players[0].board),7)
 def test_k9_rejects_spells_and_non_one_cost_minions(self):
  for cid in ('CORE_CS2_029','CORE_EX1_162'):
   g=self.game();c=self.deck(g,cid);self.play(g,'TID_099');self.choose(g);self.assertIs(g.players[0].deck[-1],c)
 def test_burrower_copies_selected_murloc_as_two_two_before_entry_callbacks(self):
  g=self.game();c=self.deck(g,'CORE_EX1_506');c.attack_bonus=7;c.health_bonus=6
  self.play(g,'TID_003');seen=[];capture=g._capture_summon_event
  def record(m,origin):
   if m.card_id==c.card_id:seen.append((m.attack,m.health,origin))
   return capture(m,origin)
  g._capture_summon_event=record;self.choose(g)
  self.assertIs(g.players[0].deck[-1],c);self.assertEqual((c.attack_bonus,c.health_bonus),(7,6))
  self.assertEqual(seen,[(2,2,'copy')]);self.assertEqual(len(g.players[0].board),2)
  m=g.players[0].minions[-1];g._silence(m);self.assertEqual((m.attack,m.max_health),(2,1))
 def test_burrower_full_board_and_non_murloc_leave_selected_card_in_deck(self):
  for cid,fill,count in (('CORE_EX1_506',6,7),('CORE_EX1_162',0,1)):
   g=self.game();c=self.deck(g,cid)
   for _ in range(fill):g._summon(0,'CORE_EX1_162')
   self.play(g,'TID_003');self.choose(g);self.assertIs(g.players[0].deck[-1],c);self.assertEqual(len(g.players[0].board),count)
 def test_explicit_copy_entry_stats_are_validated_before_body_creation(self):
  from engine.cards import UnsupportedCard
  for stats in ((2,0),(True,2),'bad'):
   g=self.game();rng=g.rng.getstate();uid=g._new_id()
   with self.assertRaises(UnsupportedCard):g._summon(0,'CORE_EX1_506',entry_stats=stats)
   self.assertFalse(g.players[0].board);self.assertEqual(g._new_id(),uid+1);self.assertEqual(g.rng.getstate(),rng)
