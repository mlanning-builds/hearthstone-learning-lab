"""Resumable card-effect sequences, with explicit per-operation checkpoints.

Damage batches protect simultaneous hits; this is not a complete replacement for
Hearthstone's trigger/death scheduler. Frames are private engine state and are
included in step's deep-copy rollback, never in player observations.
"""
from contextlib import contextmanager
from dataclasses import dataclass
from engine.cards import UnsupportedCard


@dataclass
class PlayFrame:
    operations: tuple
    context: dict
    next_operation: int = 0


class Resolution:
    @contextmanager
    def _damage_batch(self):
        """Defer settle requests until all hits/healing in this batch finish.

        The caller owns the next checkpoint. Exiting does not run effects,
        including on exceptions; Game.step owns rollback on failure.
        """
        self._damage_batch_depth += 1
        try:
            yield
        finally:
            self._damage_batch_depth -= 1

    def _start_play_effects(self, operations, context):
        if self.pending_frame is not None:
            raise UnsupportedCard('Nested card-effect frames are not supported yet')
        self.pending_frame = PlayFrame(tuple(operations), context)
        return self._resume_play_effects()

    def _resume_play_effects(self):
        """Return True on completion, False while waiting for a choice.

        Advance before dispatch so a resumed choice cannot repeat its own
        operation. If dispatch fails, Game.step restores the entire frame,
        choice, RNG and game state together.
        """
        frame = self.pending_frame
        if frame is None:
            return True
        while not self.terminal and self.pending_choice is None:
            if frame.next_operation == len(frame.operations):
                self.pending_frame = None
                return True
            operation = frame.operations[frame.next_operation]
            frame.next_operation += 1
            self._effect(operation, frame.context)
            self._settle(allow_event_choices=True)
        if self.terminal:
            self.pending_frame = None
            self.pending_choice = None
            self.pending_play = None
            self.phase = 'finished'
            return True
        return False
