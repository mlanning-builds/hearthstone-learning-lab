"""Action transactions preserve dispatch, ordering, rollback and RNG isolation."""
from copy import deepcopy
from dataclasses import replace
import random
import unittest
from unittest.mock import patch
from expanded import Action
from expanded.action_runner import ActionRunner


class Host:
    def __init__(self, action):
        self.allowed = [action]
        self.current = 0
        self.history = []
        self.events = []
        self.terminal = False
        self.pending_choice = None
        self.rng = random.Random(71)
        self.payload = {'hand': [dict(uid=4, state={'charges': [2]})]}
        self.permanent = None
        self.redirect = False
        self.fail = None
        self.runner = ActionRunner()

    def legal_actions(self): return self.allowed
    def _trace_phase(self, phase, **data): self.events.append((phase, data))
    def _random_action_target(self, action):
        if self.redirect:
            self.rng.randrange(99)
            return replace(action, target=13)
        return action
    def dispatch(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))
        self.payload['hand'][0]['state']['charges'].append(8)
        self.rng.randrange(99)
        if name == 'end': self.current = 1
        if self.fail == name:
            self.introduced_during_action = True
            raise RuntimeError(name)
    def _mulligan(self, choices): self.dispatch('mulligan', choices)
    def _end_turn(self): self.dispatch('end')
    def _power(self, target, **kwargs): self.dispatch('power', target, **kwargs)
    def _attack(self, source, target): self.dispatch('attack', source, target)
    def _play(self, action): self.dispatch('play', action)
    def _trade(self, source): self.dispatch('trade', source)
    def _prepare_card(self, source): self.dispatch('prepare', source)
    def _forge_card(self, source): self.dispatch('forge', source)
    def _permanent_entity(self, source): return self.permanent
    def _activate_permanent(self, action): self.dispatch('permanent', action)
    def _activate_location(self, action): self.dispatch('location', action)
    def _resolve_choice(self, index): self.dispatch('choose', index)
    def _settle(self): self.dispatch('settle')
    def _complete_requested_turn_end(self): self.dispatch('requested_end')
    def assert_invariants(self): self.dispatch('invariants')
    def rewards(self):
        if self.fail == 'rewards': raise RuntimeError('rewards')
        return (0.0, 0.0)


class ActionRunnerTests(unittest.TestCase):
    def test_every_action_dispatch_preserves_arguments(self):
        cases = [
            (Action('mulligan', choices=(0, 2)), 'mulligan', ((0, 2),), {}),
            (Action('end'), 'end', (), {}),
            (Action('power', target=9), 'power', (9,), {}),
            (Action('power', target=9, choices=(1,)), 'power', (9,), {'secondary': True}),
            (Action('attack', source=4, target=9), 'attack', (4, 9), {}),
            (Action('play', source=4, target=9), 'play', None, {}),
            (Action('trade', source=4), 'trade', (4,), {}),
            (Action('prepare', source=4), 'prepare', (4,), {}),
            (Action('forge', source=4), 'forge', (4,), {}),
            (Action('activate', source=4), 'location', None, {}),
            (Action('choose', choices=(2,)), 'choose', (2,), {}),
        ]
        runner = ActionRunner()
        for action, name, args, kwargs in cases:
            with self.subTest(kind=action.kind, choices=action.choices):
                host = Host(action)
                self.assertEqual(runner.run(host, action), ((0.0, 0.0), False))
                self.assertEqual(host.events[1], (name, (action,) if args is None else args, kwargs))
                self.assertEqual([event[0] for event in host.events], ['action_begin', name, 'settle', 'requested_end', 'settle', 'invariants', 'action_end'])

    def test_permanent_activation_uses_composed_host_lookup(self):
        action = Action('activate', source=4); host = Host(action); host.permanent = object()
        ActionRunner().run(host, action)
        self.assertEqual(host.events[1], ('permanent', (action,), {}))

    def test_history_keeps_original_action_before_random_redirect(self):
        from dataclasses import asdict
        action = Action('attack', source=4, target=9); host = Host(action); host.redirect = True
        ActionRunner().run(host, action)
        self.assertEqual(host.history, [dict(player=0, action=asdict(action))])
        self.assertEqual(host.events[1], ('attack', (4, 13), {}))

    def test_end_trace_keeps_original_actor_after_turn_change(self):
        action = Action('end'); host = Host(action); ActionRunner().run(host, action)
        self.assertEqual(host.current, 1)
        self.assertEqual(host.events[-1][1]['actor'], 0)

    def test_dispatch_and_post_action_failures_restore_full_state(self):
        for phase in ('play', 'settle', 'requested_end', 'invariants', 'rewards'):
            with self.subTest(phase=phase):
                action = Action('play', source=4); host = Host(action); host.fail = phase; host.redirect = True
                before = deepcopy(host.__dict__); rng = host.rng.getstate()
                with self.assertRaisesRegex(RuntimeError, phase): ActionRunner().run(host, action)
                self.assertEqual(host.rng.getstate(), rng)
                self.assertEqual(host.payload, before['payload'])
                self.assertEqual(host.events, before['events']); self.assertEqual(host.history, [])
                self.assertEqual(set(host.__dict__), set(before))

    def test_illegal_action_does_not_enter_transaction_or_consume_rng(self):
        host = Host(Action('end')); before = deepcopy(host.__dict__); rng = host.rng.getstate()
        with patch('expanded.action_runner.deepcopy', side_effect=AssertionError('snapshot should not run')):
            with self.assertRaisesRegex(ValueError, 'Illegal action'): ActionRunner().run(host, Action('play', source=4))
        self.assertEqual(host.payload, before['payload']); self.assertEqual(host.rng.getstate(), rng)
        self.assertEqual(host.events, []); self.assertEqual(host.history, [])

    def test_legal_validation_error_stays_outside_snapshot_boundary(self):
        host = Host(Action('end'))
        with patch.object(host, 'legal_actions', side_effect=RuntimeError('validation')):
            with patch('expanded.action_runner.deepcopy', side_effect=AssertionError('snapshot should not run')):
                with self.assertRaisesRegex(RuntimeError, 'validation'): ActionRunner().run(host, Action('end'))

    def test_stateless_component_has_no_host_reference_and_can_serve_copies(self):
        runner = ActionRunner(); action = Action('end'); a = Host(action); b = deepcopy(a)
        self.assertFalse(hasattr(runner, '__dict__'))
        with self.assertRaises(AttributeError): runner.host = a
        runner.run(a, action); self.assertEqual(b.history, [])
        runner.run(b, action); self.assertEqual(a.history, b.history); self.assertEqual(a.rng.getstate(), b.rng.getstate())

    def test_real_game_failure_preserves_frozen_metadata_identity(self):
        import test_expanded_generation as fixtures
        game = fixtures.GenerationTests().game(); shared = game.cards['CORE_CS2_029']; rng = game.rng.getstate()
        before = deepcopy(game.players); history = deepcopy(game.history)
        with patch.object(game, '_end_turn', side_effect=RuntimeError('injected')):
            with self.assertRaisesRegex(RuntimeError, 'injected'): ActionRunner().run(game, Action('end'))
        self.assertIs(game.cards['CORE_CS2_029'], shared)
        self.assertEqual(game.players, before); self.assertEqual(game.history, history); self.assertEqual(game.rng.getstate(), rng)

    def test_real_paid_spell_uses_runner_without_training(self):
        import test_expanded_generation as fixtures
        game = fixtures.GenerationTests().game(); card = game._add(0, 'CORE_CS2_029')
        action = next(a for a in game.legal_actions() if a.kind == 'play' and a.source == card.uid and a.target == -2)
        before_health = game.players[1].health; before_mana = game.players[0].mana; cost = game._cost(card, 0)
        ActionRunner().run(game, action)
        self.assertEqual(game.players[1].health, before_health - 6)
        self.assertEqual(game.players[0].mana, before_mana - cost)
        self.assertNotIn(card.uid, [c.uid for c in game.players[0].hand]); game.assert_invariants()

    def test_real_pending_choice_resolves_through_runner(self):
        import test_expanded_generation as fixtures
        game = fixtures.GenerationTests().game()
        game._start_play_effects([('discover_deck',)], dict(owner=0, source=None, target=0, bonus=0, lifesteal=False))
        game._settle(allow_event_choices=True)
        self.assertIsNotNone(game.pending_choice)
        before = len(game.players[0].hand)
        action = next(a for a in game.legal_actions() if a.kind == 'choose')
        ActionRunner().run(game, action)
        self.assertIsNone(game.pending_choice)
        self.assertEqual(len(game.players[0].hand), before + 1)
        game.assert_invariants()
