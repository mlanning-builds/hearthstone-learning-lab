"""Production historical identities and physical Dredge; no generation-pool narrowing."""
import unittest
from expanded import Action,cards
import test_expanded_generation as fixtures
class HistoricalColossalTests(unittest.TestCase):
 def game(self):return fixtures.GenerationTests().game()
 def test_exact_appendages_and_board_room(self):
  for cid,count in (('TSC_026',1),('TSC_029',2),('TSC_030',1)):
   for occupied in (0,5,6,7):
    g=self.game();p=g.players[0]
    for _ in range(occupied):g._summon(0,'CORE_CS2_188')
    body=g._summon(0,cid);self.assertEqual(len(p.board),min(7,occupied+1+count))
    if body:self.assertEqual(len(body.rule_state['colossal_appendages']),min(count,6-occupied))
    else:self.assertEqual(occupied,7)
 def test_attack_dredges_physical_bottom_preserving_modifiers_then_claw_draws_it(self):
  g=self.game();p=g.players[0];body=g._summon(0,'TSC_030');body.summoned_turn=-1;p.deck=[]
  for cid in ('CORE_CS2_029','CORE_EX1_162','CORE_CS2_188','CORE_CS2_029'):
   c=g._add(0,cid);p.hand.remove(c);p.deck.append(c)
  bottom=list(p.deck[:3]);bottom[1].attack_bonus=4;uid=bottom[1].uid;state=g.rng.getstate();discoveries=p.discoveries_total
  g.step(Action('attack',body.uid,-2));self.assertEqual(g.phase,'choice');self.assertEqual(g.pending_choice['mode'],'dredge')
  self.assertEqual([o['snapshot'].uid for o in g.pending_choice['options']],[c.uid for c in bottom])
  self.assertEqual(g.observe(1)['pending_choice'],{'owner':0,'waiting':True})
  g.step(Action('choose',choices=(1,)));self.assertEqual(p.deck[-1].uid,uid);self.assertEqual(p.deck[-1].attack_bonus,4)
  self.assertEqual(g.rng.getstate(),state);self.assertEqual(p.discoveries_total,discoveries);g.assert_invariants()
  claw=next(m for m in p.minions if m.card_id=='TSC_030t2');claw.summoned_turn=-1
  g.step(Action('attack',claw.uid,-2));self.assertEqual(p.hand[-1].uid,uid)
 def test_empty_dredge_and_claw_fatigue(self):
  g=self.game();p=g.players[0];p.deck=[];body=g._summon(0,'TSC_030');body.summoned_turn=-1
  g.step(Action('attack',body.uid,-2));self.assertIsNone(g.pending_choice);self.assertEqual(p.fatigue,0)
  claw=next(m for m in p.minions if m.card_id=='TSC_030t2');claw.summoned_turn=-1
  g.step(Action('attack',claw.uid,-2));self.assertEqual(p.fatigue,1)
 def test_silence_stops_attack_dredge(self):
  g=self.game();body=g._summon(0,'TSC_030');body.summoned_turn=-1;g._silence(body)
  g.step(Action('attack',body.uid,-2));self.assertIsNone(g.pending_choice)
 def test_colaque_immunity_follows_shell_presence_and_body_silence(self):
  g=self.game();body=g._summon(0,'TSC_026');shell=next(m for m in g.players[0].minions if m.card_id=='TSC_026t')
  self.assertEqual(g._damage(body.uid,3),0);g._silence(shell);self.assertEqual(g._damage(body.uid,3),0)
  shell.health=0;g._settle();self.assertNotIn('IMMUNE',g._effective_keywords(body));self.assertEqual(g.players[0].armor,0)
  shell=g._summon(0,'TSC_026t');g._silence(body);self.assertEqual(g._damage(body.uid,2),2)
  shell.health=0;g._settle();self.assertEqual(g.players[0].armor,8)
 def test_enemy_shell_does_not_protect(self):
  g=self.game()
  for _ in range(6):g._summon(0,'CORE_CS2_188')
  body=g._summon(0,'TSC_026');g._summon(1,'TSC_026t');self.assertNotIn('IMMUNE',g._effective_keywords(body))
 def test_gaia_friendly_mech_attack_includes_self(self):
  for cid,owner,expected in (('TSC_029',0,1),('TSC_029t',0,1),('CORE_EX1_162',0,0),('TSC_029t',1,0)):
   g=self.game();g.current=owner;gaia=g._summon(0,'TSC_029');enemy=g._summon(1,'CS2_200');enemy.attack=0
   attacker=gaia if cid=='TSC_029' else g._summon(owner,cid);attacker.summoned_turn=-1
   before=g.players[1].health;eh=enemy.health
   g.step(Action('attack',attacker.uid,g.hero_id(1-owner)))
   self.assertEqual(g.players[1].health,before-(attacker.attack if owner==0 else 0)-expected);self.assertEqual(enemy.health,eh-expected)
 def test_paid_body_and_generated_only_registry(self):
  g=self.game();c=g._add(0,'TSC_030');g.step(next(a for a in g.legal_actions() if a.kind=='play' and a.source==c.uid))
  self.assertEqual([m.card_id for m in g.players[0].minions],['TSC_030','TSC_030t2'])
  identities={'TSC_026','TSC_026t','TSC_029','TSC_029t','TSC_029t2','TSC_030','TSC_030t2'}
  self.assertTrue(identities<=cards.TOKEN_IDS&cards.PLAYABLE_TOKENS);self.assertFalse(identities&cards.COLLECTIBLE_IDS)
