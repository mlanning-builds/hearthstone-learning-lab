"""Turn-based policy interface. No policy, training loop, or implicit opponent.

Actions are indices into the returned legal candidates. Revisions prevent a
policy from accidentally applying an index from an older decision or episode.
Only Game.observe(actor) crosses the policy boundary, never private Game state.
"""
from copy import deepcopy
from dataclasses import asdict
from .game import Game
from .status import require_full_standard


class PolicyEnvironment:
    def __init__(self, *, experimental=False):
        if not experimental:require_full_standard()
        self.experimental=experimental
        self._game=None
        self._revision=0
        self._steps=0
        self._limit=0

    def reset(self,decks,*,seed,max_actions,first_player=0):
        if type(seed) is not int:raise ValueError('Seed must be an integer')
        if type(max_actions) is not int or max_actions<1:
            raise ValueError('An explicit positive action budget is required')
        if type(first_player) is not int or first_player not in (0,1):
            raise ValueError('First player must be 0 or 1')
        game=Game(decks,seed=seed,first_player=first_player)
        self._game=game;self._steps=0;self._limit=max_actions;self._revision+=1
        return self.decision()

    def decision(self):
        if self._game is None:raise RuntimeError('Reset the environment first')
        game=self._game;terminated=game.terminal
        truncated=not terminated and self._steps>=self._limit
        actor=(game.pending_choice["owner"]
               if game.phase=="choice" and game.pending_choice is not None
               else game.current)
        view=game.observe(actor)
        actions=[] if terminated or truncated else game.legal_actions()
        view['legal_actions']=[asdict(action) for action in actions]
        return dict(revision=self._revision,actor=actor,observation=view,
                    actions=deepcopy(view['legal_actions']),action_mask=[True]*len(actions),
                    rewards=list(game.rewards()),terminated=terminated,truncated=truncated,
                    steps=self._steps,experimental=self.experimental,
                    end_reason=game.end_reason if terminated else 'action_limit' if truncated else None,
                    first_player=game.first_player)

    def step(self,action_index,*,revision):
        before=self.decision()
        if type(revision) is not int or revision!=self._revision:
            raise ValueError('Stale decision revision; request a fresh decision')
        if before['terminated'] or before['truncated']:
            raise RuntimeError('Episode ended; reset before taking another action')
        actions=self._game.legal_actions()
        if type(action_index) is not int or not 0<=action_index<len(actions):
            raise ValueError('Action index must select a current legal candidate')
        self._game.step(actions[action_index])
        self._steps+=1;self._revision+=1
        return self.decision()
