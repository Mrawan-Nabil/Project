"""Patient entity — the core data object for the simulation engine.

All state transitions are deterministic rule-based logic.
"""

from enum import Enum, auto


class PatientState(Enum):
    """Lifecycle states for a patient inside the hospital."""
    WAITING_IN_QUEUE = auto()   # sitting in the priority queue
    IN_TRANSIT       = auto()   # allocated to a room, walking there
    IN_TREATMENT     = auto()   # actively occupying a room slot
    DISCHARGED       = auto()   # treatment complete, left hospital
    DECEASED         = auto()   # expired due to critical wait time


# Treatment durations in ticks (1 tick ≈ 1 real-time second)
TREATMENT_DURATION: dict[str, int] = {
    'Surgery': 30,   # 30 ticks — longest procedure
    'MRI':     15,   # 15 ticks — imaging scan
    'ICU':     40,   # 40 ticks — intensive monitoring
    'Ward':    20,   # 20 ticks — general admission
}

# Mortality thresholds: (severity_threshold, wait_ticks_threshold)
# A patient with severity > SEV_THRESHOLD who waits > WAIT_THRESHOLD ticks
# has a chance of becoming DECEASED each tick.
MORTALITY_SEV_THRESHOLD  = 7    # severity must exceed this
MORTALITY_WAIT_THRESHOLD = 20   # wait_time must exceed this (ticks)
MORTALITY_CHANCE         = 0.05 # 5 % chance per tick once both thresholds met


class Patient:
    """Represents a single patient moving through the hospital system.

    Attributes
    ----------
    id : int
        Unique sequential identifier.
    severity : int
        Clinical urgency 1–10 (10 = most critical).
    required_treatment : str
        Room type needed: 'Surgery' | 'MRI' | 'ICU' | 'Ward'.
    wait_time : int
        Ticks spent in WAITING_IN_QUEUE state.
    treatment_time_remaining : int
        Ticks left until treatment is complete (set when InTreatment begins).
    state : PatientState
        Current lifecycle state.
    assigned_room : Room | None
        Reference to the Room this patient is currently occupying.
    """

    def __init__(self, patient_id: int, severity: int,
                 required_treatment: str) -> None:
        self.id:                       int          = patient_id
        self.severity:                 int          = max(1, min(10, severity))
        self.required_treatment:       str          = required_treatment
        self.wait_time:                int          = 0
        self.treatment_time_remaining: int          = 0
        self.state:                    PatientState = PatientState.WAITING_IN_QUEUE
        self.assigned_room                          = None   # type: ignore[assignment]
        # Visual grid position — set by GridIndex on spawn / allocation
        self.grid_pos: tuple[int, int] | None       = None

    # ── Comparison operators for heapq (min-heap → negate for max priority) ──

    def priority_key(self) -> tuple[int, int]:
        """Return (neg_severity, neg_wait_time) for use as a min-heap key.

        Highest severity first; ties broken by longest wait first.
        Both are negated so Python's min-heap behaves as a max-heap.
        """
        return (-self.severity, -self.wait_time)

    # ── State transition helpers ──────────────────────────────────────────────

    def allocate(self, room: "Room") -> None:  # type: ignore[name-defined]
        """Mark patient as in-transit and lock a room slot."""
        self.state        = PatientState.IN_TRANSIT
        self.assigned_room = room
        room.admit(self)

    def begin_treatment(self) -> None:
        """Called when the patient arrives at the room."""
        self.state                    = PatientState.IN_TREATMENT
        self.treatment_time_remaining = TREATMENT_DURATION.get(
            self.required_treatment, 20
        )

    def tick_treatment(self) -> bool:
        """Advance treatment by one tick.  Returns True when complete."""
        if self.treatment_time_remaining > 0:
            self.treatment_time_remaining -= 1
        return self.treatment_time_remaining <= 0

    def discharge(self) -> None:
        """Treatment complete — free the room slot."""
        if self.assigned_room:
            self.assigned_room.discharge(self)
            self.assigned_room = None
        self.state = PatientState.DISCHARGED

    def mark_deceased(self) -> None:
        """Patient expired while waiting."""
        if self.assigned_room:
            self.assigned_room.discharge(self)
            self.assigned_room = None
        self.state = PatientState.DECEASED

    # ── Representation ────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (f"Patient(id={self.id}, sev={self.severity}, "
                f"tx={self.required_treatment}, "
                f"wait={self.wait_time}, state={self.state.name})")
