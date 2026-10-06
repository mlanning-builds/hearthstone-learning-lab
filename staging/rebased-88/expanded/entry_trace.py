"""Opt-in private diagnostics. Records current behavior; never dispatches rules.

Traces may contain hidden card identities. They are not player observations or
learner features. Storage is bounded and disabled by default.
"""
from collections import deque
from copy import deepcopy


class EntryTrace:
    def configure_entry_trace(self, limit=2000):
        """Clear diagnostics and retain at most limit records; zero disables."""
        if type(limit) is not int or not 0 <= limit <= 100000:
            raise ValueError('Trace limit must be an integer from 0 to 100000')
        self._entry_trace_limit = limit
        self._entry_trace_rows = deque(maxlen=limit or None)
        self._entry_trace_serial = 0

    def entry_trace(self):
        """Return an independent diagnostic snapshot, never a policy input."""
        rows = deepcopy(list(self._entry_trace_rows))
        return dict(schema=1, scope='private engine diagnostics; not rules certification',
                    capacity=self._entry_trace_limit, recorded=self._entry_trace_serial,
                    dropped=max(0,self._entry_trace_serial-len(rows)), records=rows)

    def _trace_phase(self, phase, **fields):
        if not self._entry_trace_limit:
            return
        self._entry_trace_serial += 1
        self._entry_trace_rows.append(dict(sequence=self._entry_trace_serial,
            phase=phase, turn=self.turn, current_player=self.current, **fields))

    def _trace_entity(self, phase, entity, **fields):
        if not self._entry_trace_limit:
            return
        snapshot = None if entity is None else dict(uid=entity.uid, card_id=entity.card_id,
            owner=entity.owner, attack=entity.attack, health=entity.health,
            max_health=entity.max_health, stored_keywords=sorted(entity.keywords))
        self._trace_phase(phase, entity=snapshot, **fields)
