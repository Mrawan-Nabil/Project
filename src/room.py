"""Room / Resource entity — represents a hospital department or machine.

Each Room has a fixed capacity and tracks which patients currently occupy it.
Strictly zero ML/AI.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from src.patient import Patient


class Room:
    """A hospital room or resource pool (e.g., Ward, MRI, ICU, Surgery).

    Attributes
    ----------
    room_type : str
        Matches Patient.required_treatment exactly.
    capacity : int
        Maximum concurrent patients this room can hold.
    current_occupants : list[Patient]
        Patients currently IN_TREATMENT here.
    """

    def __init__(self, room_type: str, capacity: int) -> None:
        self.room_type:         str            = room_type
        self.capacity:          int            = max(1, capacity)
        self.current_occupants: List[Patient]  = []

    # ── Capacity queries ──────────────────────────────────────────────────────

    @property
    def current_occupancy(self) -> int:
        """Number of patients currently occupying this room."""
        return len(self.current_occupants)

    @property
    def is_available(self) -> bool:
        """True if at least one slot is free."""
        return self.current_occupancy < self.capacity

    @property
    def slots_free(self) -> int:
        """Number of free slots remaining."""
        return self.capacity - self.current_occupancy

    @property
    def utilisation(self) -> float:
        """Occupancy as a fraction 0.0–1.0."""
        return self.current_occupancy / self.capacity if self.capacity else 0.0

    # ── Slot management ───────────────────────────────────────────────────────

    def admit(self, patient: "Patient") -> None:
        """Reserve a slot for *patient* (called by Patient.allocate)."""
        if not self.is_available:
            raise RuntimeError(
                f"Room '{self.room_type}' is full "
                f"({self.current_occupancy}/{self.capacity})"
            )
        self.current_occupants.append(patient)

    def discharge(self, patient: "Patient") -> None:
        """Release the slot held by *patient*."""
        try:
            self.current_occupants.remove(patient)
        except ValueError:
            pass   # already removed — safe to ignore

    # ── Representation ────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (f"Room(type={self.room_type}, "
                f"{self.current_occupancy}/{self.capacity})")
