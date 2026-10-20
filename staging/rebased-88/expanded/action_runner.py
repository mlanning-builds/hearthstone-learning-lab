"""Stateless action transaction orchestration for an explicitly composed Game.

The host supplies game rules. This component owns only action dispatch and the
existing full-state rollback boundary; it retains no host or mutable state.
"""
from copy import deepcopy
from dataclasses import asdict


class ActionRunner:
    __slots__ = ()

    def run(self, game, action):
        if action not in game.legal_actions():
            raise ValueError('Illegal action; state unchanged')
        # Snapshot after legal-action validation, matching the original boundary.
        before = deepcopy(game.__dict__)
        try:
            game._trace_phase('action_begin', action=action.kind, actor=game.current)
            actor = game.current
            game.history.append(dict(player=actor, action=asdict(action)))
            action = game._random_action_target(action)
            if action.kind == 'mulligan':
                game._mulligan(action.choices)
            elif action.kind == 'end':
                game._end_turn()
            elif action.kind == 'power':
                if action.choices == (1,):
                    game._power(action.target, secondary=True)
                else:
                    game._power(action.target)
            elif action.kind == 'attack':
                game._attack(action.source, action.target)
            elif action.kind == 'play':
                game._play(action)
            elif action.kind == 'trade':
                game._trade(action.source)
            elif action.kind == 'prepare':
                game._prepare_card(action.source)
            elif action.kind == 'forge':
                game._forge_card(action.source)
            elif action.kind == 'activate':
                activate=getattr(game,'_activate_board_action',None)
                if activate is not None:
                    activate(action)
                elif game._permanent_entity(action.source) is not None:
                    game._activate_permanent(action)
                else:
                    game._activate_location(action)
            elif action.kind == 'choose':
                game._resolve_choice(action.choices[0])
            else:
                raise ValueError('Unknown action')
            game._settle()
            game._complete_requested_turn_end()
            game._settle()
            after_rules=getattr(game,'_after_action_rules',None)
            if after_rules is not None:after_rules()
            game.assert_invariants()
            game._trace_phase('action_end', action=action.kind, actor=actor,
                              terminal=game.terminal,
                              waiting_choice=game.pending_choice is not None)
            return game.rewards(), game.terminal
        except Exception:
            game.__dict__.clear()
            game.__dict__.update(before)
            raise
