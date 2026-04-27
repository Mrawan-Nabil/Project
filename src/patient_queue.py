"""PatientQueue — max-priority queue backed by Python's heapq (min-heap).

Sort order (highest priority first):
  1. severity   — descending  (severity 10 before severity 1)
  2. wait_time  — descending  (longer wait breaks ties)

Both keys are negated so the standard min-heap gives max-priority behaviour.
Strictly zero ML/AI — pure classic CS data structure.
"""

import heapq
from typing import List, Optional
from src.patient import Patient


class PatientQueue:
    """Thread-safe-ish priority queue for waiting patients.

    Internally stores tuples of (priority_key, insertion_order, patient)
    so that heapq never needs to compare Patient objects directly.

    Usage
    -----
    q = PatientQueue()
    q.push(patient)
    top = q.peek()          # inspect without removing
    patient = q.pop()       # remove highest-priority patient
    q.rebuild()             # call after wait_times are updated each tick
    """

    def __init__(self) -> None:
        self._heap:  List[tuple] = []   # (neg_severity, neg_wait, seq, patient)
        self._seq:   int         = 0    # tie-breaker for equal priority keys

    # ── Core operations ───────────────────────────────────────────────────────

    def push(self, patient: Patient) -> None:
        """Add *patient* to the queue."""
        entry = (*patient.priority_key(), self._seq, patient)
        heapq.heappush(self._heap, entry)
        self._seq += 1

    def pop(self) -> Optional[Patient]:
        """Remove and return the highest-priority patient, or None if empty."""
        while self._heap:
            _, _, _, patient = heapq.heappop(self._heap)
            # Skip stale entries (patient was removed externally)
            from src.patient import PatientState
            if patient.state == PatientState.WAITING_IN_QUEUE:
                return patient
        return None

    def peek(self) -> Optional[Patient]:
        """Return the highest-priority patient without removing them."""
        # Scan past any stale entries
        from src.patient import PatientState
        for entry in sorted(self._heap):
            patient = entry[3]
            if patient.state == PatientState.WAITING_IN_QUEUE:
                return patient
        return None

    def rebuild(self) -> None:
        """Rebuild the heap after wait_times have been updated.

        Must be called once per tick AFTER incrementing wait_times,
        because the priority keys depend on wait_time.
        """
        from src.patient import PatientState
        # Keep only patients still waiting
        live = [p for (*_, p) in self._heap
                if p.state == PatientState.WAITING_IN_QUEUE]
        self._heap = []
        self._seq  = 0
        for patient in live:
            self.push(patient)

    def all_waiting(self) -> List[Patient]:
        """Return all waiting patients sorted by priority (non-destructive)."""
        from src.patient import PatientState
        candidates = [p for (*_, p) in self._heap
                      if p.state == PatientState.WAITING_IN_QUEUE]
        # Sort by priority key: (-severity, -wait_time)
        return sorted(candidates, key=lambda p: p.priority_key())

    # ── Queries ───────────────────────────────────────────────────────────────

    def __len__(self) -> int:
        from src.patient import PatientState
        return sum(1 for (*_, p) in self._heap
                   if p.state == PatientState.WAITING_IN_QUEUE)

    def is_empty(self) -> bool:
        return len(self) == 0

    def __repr__(self) -> str:
        return f"PatientQueue(waiting={len(self)})"
