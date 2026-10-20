"""Focused physical and timing checks; never training or full-suite entrypoints."""
import unittest
from engine.game import Card
from expanded import Action
from expanded import cards
from expanded.historical_obligation_spells import op,paid
import test_expanded_generation as fixtures

class ObligationSpellTests(unittest.TestCase):
 def setUp(self):
  self.g=fixtures.GenerationTests().game();self.p,self.q=self.g.players
 def run_ops(self,ops,owner=0,**kwargs):
  context=dict(owner=owner,source=None,target=0,bonus=0,lifesteal=False)
  context.update(kwargs);self.g._start_play_effects(ops,context);self.g._settle(allow_event_choices=True)
 def test_flanking_replacement_is_not_itself_watched(self):
  self.run_ops(cards.RULES['AV_269'][1],card_id='AV_269')
  original=self.p.minions[0];original.health=0;self.g._settle(allow_event_choices=True)
  self.assertEqual(len(self.p.minions),1)
  self.assertNotEqual(self.p.minions[0].uid,original.uid)
  self.p.minions[0].health=0;self.g._settle(allow_event_choices=True)
  self.assertFalse(self.p.minions)
 def test_performers_wait_for_every_physical_summon(self):
  self.run_ops(cards.RULES['DMF_224'][1],card_id='DMF_224')
  originals=list(self.p.minions);self.assertEqual(len(originals),7)
  for m in originals[:-1]:m.health=0
  self.g._settle(allow_event_choices=True);self.assertEqual(len(self.p.minions),1)
  originals[-1].health=0;self.g._settle(allow_event_choices=True)
  self.assertEqual(len(self.p.minions),7)
  self.assertFalse({m.uid for m in originals}&{m.uid for m in self.p.minions})
 def test_delayed_summon_does_not_survive_turn(self):
  self.run_ops(cards.RULES['AV_269'][1],card_id='AV_269');self.g.turn+=1
  self.p.minions[0].health=0;self.g._settle(allow_event_choices=True)
  self.assertFalse(self.p.minions)
 def test_shout_current_and_future_summons_and_silence(self):
  a=self.g._summon(0,'CORE_EX1_162');self.run_ops([op('shout')])
  b=self.g._summon(0,'CORE_EX1_162')
  for m in (a,b):self.g._damage(m.uid,50);self.assertEqual(m.health,1)
  self.g._silence(b);self.g._damage(b.uid,50);self.assertLessEqual(b.health,0)
  self.g.turn+=1;self.g._damage(a.uid,50);self.assertLessEqual(a.health,0)
 def test_acrobatics_tracks_drawn_occurrences(self):
  self.p.deck=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(4)]
  self.run_ops([op('acrobatics')]);drawn=list(self.p.hand)
  self.assertEqual(len(drawn),2)
  paid(self.g,0,Card(self.g._new_id(),'CORE_CS2_029'));self.g._settle(allow_event_choices=True)
  self.assertEqual(len(self.p.hand),2)
  paid(self.g,0,drawn[0]);self.g._settle(allow_event_choices=True);self.assertEqual(len(self.p.hand),2)
  paid(self.g,0,drawn[1]);self.g._settle(allow_event_choices=True);self.assertEqual(len(self.p.hand),4)
 def test_passage_moves_without_draw_then_returns_only_borrowed_survivors(self):
  saved=Card(self.g._new_id(),'CORE_CS2_029');saved.cost_delta=-1;self.p.hand=[saved]
  original=[Card(self.g._new_id(),'CORE_EX1_162') for _ in range(6)];self.p.deck=list(original)
  self.run_ops([op('passage')]);self.assertEqual(len(self.p.hand),4);self.assertEqual(len(self.p.deck),2)
  task=next(iter(self.p._historical_passages));self.p.hand.pop()
  generated=Card(self.g._new_id(),'CORE_CS2_029');self.p.hand.append(generated)
  self.run_ops([op('passage_restore',task,0)])
  self.assertEqual(self.p.hand,[generated,saved]);self.assertEqual(saved.cost_delta,-1)
  self.assertEqual(len(self.p.deck),5)
 def test_shadow_keeps_physical_snapshot_and_replaces_draw(self):
  target=self.g._summon(1,'CORE_EX1_162');self.g._buff(target,3,4)
  self.p.deck=[];self.run_ops([op('shadows')],target=target.uid)
  self.assertEqual(len(self.p.deck),3)
  self.assertTrue(all(c.card_id=='ULD_286t' for c in self.p.deck))
  self.p.deck=[Card(self.g._new_id(),'CORE_CS2_029'),self.p.deck[0]]
  self.run_ops([('draw',1)])
  self.assertEqual(len(self.p.minions),1);self.assertEqual(self.p.minions[0].attack,target.attack)
  self.assertEqual([c.card_id for c in self.p.hand],['CORE_CS2_029'])
 def test_yoink_free_cost_and_restores_after_two_activations(self):
  from copy import deepcopy
  restore=deepcopy(self.p.primary_power)
  self.run_ops([op('yoink')]);self.assertEqual(len(self.g.pending_choice['options']),3)
  self.assertTrue(all(o['hero_class']!='MAGE' for o in self.g.pending_choice['options']))
  self.g.step(Action('choose',choices=(0,)))
  power=self.p.primary_power;self.assertEqual(power['cost'],0)
  self.run_ops([op('yoink_used',power['uid'])]);self.assertEqual(self.p.primary_power['yoink_remaining'],1)
  self.run_ops([op('yoink_used',power['uid'])]);self.assertEqual(self.p.primary_power,restore)
 def test_guidance_only_both_overloads(self):
  for both in (False,True):
   self.setUp();self.run_ops([op('guidance')],card_id='YOP_024')
   options=self.g.pending_choice['options'];index=next(i for i,v in enumerate(options) if v['both']==both)
   self.g.step(Action('choose',choices=(index,)))
   self.assertEqual(len(self.p.hand),2 if both else 1);self.assertEqual(self.p.overload_next,1 if both else 0)
 def test_mana_burn_suppresses_refresh_without_creating_overload(self):
  self.run_ops([op('mana_burn')]);self.assertEqual(self.q.historical_mana_burn_next,2)
  self.q.historical_mana_burn_active=2;self.q.mana=0
  from expanded.mana_accounting import refresh_permanent
  refresh_permanent(self.q,20)
  self.assertEqual(self.q.mana,8);self.assertEqual(self.q.locked_mana,0);self.assertEqual(self.q.overload_next,0)

 def test_passage_returns_at_end_of_current_turn(self):
  original=Card(self.g._new_id(),'CORE_CS2_029');self.p.hand=[original]
  self.run_ops([op('passage')]);self.assertNotIn(original,self.p.hand)
  self.g.step(Action('end'))
  self.assertIn(original,self.p.hand);self.assertEqual(self.g.current,1)
 def test_nested_passages_unwind_in_reverse_order_as_one_trigger(self):
  original=Card(self.g._new_id(),'CORE_CS2_029');self.p.hand=[original]
  self.run_ops([op('passage')]);first=next(iter(self.p._historical_passages))
  first_added=Card(self.g._new_id(),'CORE_CS2_029');self.p.hand.append(first_added)
  self.run_ops([op('passage')])
  second_added=Card(self.g._new_id(),'CORE_CS2_029');self.p.hand.append(second_added)
  self.assertEqual(len([e for e in self.p.scheduled_effects if e.get('source_card_id')=='SCH_305']),1)
  self.run_ops([op('passage_restore',first,0)])
  self.assertEqual(self.p.hand,[second_added,first_added,original])
 def test_acrobatics_bonus_waits_for_actual_paid_play_completion(self):
  self.p.deck=[Card(self.g._new_id(),'CORE_CS2_029') for _ in range(4)]
  self.run_ops([op('acrobatics')]);originals=list(self.p.hand)
  for card in originals:
   self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid and a.target==-2))
  self.assertEqual(len(self.p.hand),2);self.assertEqual(len(self.p.replay_history),2)
 def test_paid_guidance_both_has_one_overload_and_records_actual_branch(self):
  card=self.g._add(0,'YOP_024')
  self.g.step(next(a for a in self.g.legal_actions() if a.kind=='play' and a.source==card.uid))
  choice=self.g.pending_choice;index=next(i for i,o in enumerate(choice['options']) if o['both'])
  self.g.step(Action('choose',choices=(index,)))
  self.assertEqual(self.p.overload_next,1)
  self.assertTrue(self.p.played_history[-1]['overload_card'])
  self.assertEqual(len(self.p.replay_history),1)

 def test_obligations_publish_state_without_leaking_set_aside_hand(self):
  original=Card(self.g._new_id(),'CORE_CS2_029');self.p.hand=[original]
  self.run_ops([op('passage')]);self.run_ops([op('comet')]);self.run_ops([op('mana_burn')])
  own=self.g.observe(0)['players'][0];enemy=self.g.observe(1)['players'][0]
  self.assertEqual(own['secret_passage_hands'][0][0]['card_id'],'CORE_CS2_029')
  self.assertNotIn('secret_passage_hands',enemy);self.assertNotIn('acrobatics_cards',enemy)
  self.assertEqual(enemy['historical_spell_obligations']['lucky_comet_charges'],1)
  self.assertEqual(self.g.observe(0)['players'][1]['historical_spell_obligations']['mana_burn_next'],2)
