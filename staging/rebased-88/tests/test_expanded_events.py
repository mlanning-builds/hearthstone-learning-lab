"""User-run event contracts. Synthetic hooks do not define real card effects."""
import unittest
from unittest.mock import patch
from expanded import Game, Action, random_deck
from expanded.cards import TRIGGERS
from engine.cards import UnsupportedCard


class EventContractsTests(unittest.TestCase):
    def setUp(self):
        self.g=Game([random_deck('MAGE',31),random_deck('WARRIOR',53)],seed=71)
        self.g.step(Action('mulligan'));self.g.step(Action('mulligan'))
        self.p,self.q=self.g.players
        self.parent=self.g._summon(0,'Core_CS2_200')
        self.child=self.g._summon(0,'CORE_EX1_007')
        self.trace=[]

    def dispatch(self, effect, parent_ops=(('emit',),('parent_done',))):
        rules={self.parent.card_id:('spell_cast',parent_ops),
               self.child.card_id:('hero_attack',[('child',)])}
        with patch.dict(TRIGGERS,rules,clear=True), patch.object(self.g,'_effect',side_effect=effect):
            self.g._queue_event('spell_cast',owner=0)
            self.g._drain_events()

    def effect(self,op,ctx):
        self.trace.append(op[0])
        if op[0]=='emit': self.g._queue_event('hero_attack',owner=0)

    def test_child_resolves_before_next_parent_operation(self):
        self.dispatch(self.effect)
        self.assertEqual(self.trace,['emit','child','parent_done'])

    def test_child_resolves_before_preexisting_sibling(self):
        def effect(op,ctx):
            self.effect(op,ctx)
        rules={self.parent.card_id:('spell_cast',[('emit',),('parent_done',)]),
               self.child.card_id:('hero_attack',[('child',)])}
        with patch.dict(TRIGGERS,rules,clear=True),patch.object(self.g,'_effect',side_effect=effect):
            self.g._queue_event('spell_cast',owner=0)
            self.g._queue_event('hero_attack',owner=0)
            self.g._drain_events()
        self.assertEqual(self.trace,['emit','child','parent_done','child'])

    def test_removed_listener_is_skipped_before_its_turn(self):
        def effect(op,ctx):
            self.effect(op,ctx)
            if op[0]=='emit': self.p.board.remove(self.child)
        self.dispatch(effect)
        self.assertEqual(self.trace,['emit','parent_done'])

    def test_listener_created_after_event_does_not_receive_old_event(self):
        self.p.board.remove(self.child)
        def effect(op,ctx):
            self.effect(op,ctx)
            if op[0]=='emit': self.g._summon(0,self.child.card_id)
        self.dispatch(effect)
        self.assertEqual(self.trace,['emit','parent_done'])

    def test_deaths_wait_until_outer_checkpoint(self):
        def effect(op,ctx):
            self.effect(op,ctx)
            if op[0]=='emit':
                self.child.health=0
                self.g._settle()
            if op[0]=='child': self.assertIn(self.child,self.p.board)
        self.dispatch(effect)
        self.assertEqual(self.trace,['emit','child','parent_done'])
        self.g._settle()
        self.assertNotIn(self.child,self.p.board)

    def test_reentrant_trigger_fails_explicitly_and_releases_dispatch_guard(self):
        def effect(op,ctx): self.g._queue_event('spell_cast',owner=0)
        with self.assertRaisesRegex(UnsupportedCard,'Re-entrant'):
            self.dispatch(effect)
        self.assertFalse(self.g._draining_events)

    def test_trigger_choice_fails_explicitly_instead_of_running_ahead(self):
        def effect(op,ctx): self.g.pending_choice={'owner':0}
        with self.assertRaisesRegex(UnsupportedCard,'Choices inside'):
            self.dispatch(effect)
        self.assertFalse(self.g._draining_events)

    def test_spell_transform_is_not_a_summon_or_death(self):
        self.parent.summoned_turn=-1;self.parent.attacks=0
        self.g._buff(self.parent,3,3)
        position=self.p.board.index(self.parent)
        corpses=self.p.corpses;offset=len(self.g.events)
        replacement=self.g._transform(self.parent,'Core_CS2_200')
        events=self.g.events[offset:]
        self.assertFalse(any(e['event'] in ('summon','death') for e in events))
        self.assertTrue(any(e['event']=='transform' for e in events))
        self.assertEqual(self.p.corpses,corpses)
        self.assertEqual(self.p.board.index(replacement),position)
        self.assertEqual(replacement.summoned_turn,self.g.turn)
        self.assertNotEqual(replacement.uid,self.parent.uid)
        base=self.g.cards[replacement.card_id]
        self.assertEqual((replacement.attack,replacement.health),(base['attack'],base['health']))
        self.assertFalse(any(a.kind=='attack' and a.source==replacement.uid for a in self.g.legal_actions()))
