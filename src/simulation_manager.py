"""SimulationManager — the headless discrete-event engine.

Architecture
------------
- Strictly zero ML/AI.  All logic is deterministic rule-based CS.
- One tick() call = one unit of simulation time (≈ 1 real-time second).
- The manager owns the Room pool and the PatientQueue.
- It reads the initial configuration from SimulationState and writes
  live metrics back to it so the HUD stays current.

Tick sequence (executed in order every tick)
--------------------------------------------
1. Increment wait_time for every WAITING_IN_QUEUE patient.
2. Apply mortality check to critical patients who have waited too long.
3. Rebuild the priority queue (wait_times changed → priorities changed).
4. Greedy allocation: scan the sorted queue and assign patients to rooms
   without blocking on a full room type (non-blocking scan).
5. Advance IN_TRANSIT patients to IN_TREATMENT (instant for now; visual
   transit animation will be layered on top in Phase 4).
6. Tick treatment timers; discharge completed patients.
7. Push updated metrics back to SimulationState for the HUD.

Greedy Allocation (non-blocking)
---------------------------------
Classic greedy: iterate the priority-sorted waiting list.  For each
patient, check if their required room has a free slot.  If yes → allocate.
If no → skip (do NOT block; continue to the next patient).  This ensures
a Ward patient is not stuck behind a Surgery patient when Ward has space.
"""

import random
from typing import Dict, List, Optional

from src.patient          import Patient, PatientState, MORTALITY_SEV_THRESHOLD, \
                                  MORTALITY_WAIT_THRESHOLD, MORTALITY_CHANCE
from src.room             import Room
from src.patient_queue    import PatientQueue
from src.simulation_state import SimulationState
from src.grid_index       import GridIndex


# ── Default room capacities (overridden by SimulationState values) ────────────
_DEFAULT_CAPACITIES: Dict[str, int] = {
    'Ward':    10,
    'MRI':      2,
    'ICU':      4,
    'Surgery':  2,
}


class SimulationManager:
    """Headless simulation engine.  No Pygame imports.

    Parameters
    ----------
    state : SimulationState
        Shared state object; manager reads config from it and writes
        live metrics back to it every tick.

    Usage
    -----
    manager = SimulationManager(state)
    manager.load_patients(state.patients)   # called once on START SIM
    # inside the game loop (once per second):
    if state.sim_running:
        manager.tick()
    """

    def __init__(self, state: SimulationState,
                 grid_index: Optional[GridIndex] = None) -> None:
        self._state = state
        self._grid  = grid_index   # may be None until injected

        # Build the room pool from SimulationState resource counts
        self._rooms: Dict[str, Room] = self._build_rooms(state)

        # Priority queue — populated by load_patients()
        self._queue: PatientQueue = PatientQueue()

        # All patients ever loaded (for metrics calculation)
        self._all_patients: List[Patient] = []

        # Tick counter
        self._tick_count: int = 0

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _build_rooms(self, state: SimulationState) -> Dict[str, Room]:
        """Construct Room objects from SimulationState resource counts."""
        return {
            'Ward':    Room('Ward',    state.beds),
            'MRI':     Room('MRI',     state.mris),
            'ICU':     Room('ICU',     state.icus),
            'Surgery': Room('Surgery', state.operating_rooms),
        }

    def load_patients(self, patient_dicts: List[Dict]) -> None:
        """Convert raw patient dicts (from SimulationState) into Patient
        objects, assign spawn grid positions, and push into the priority queue.

        Called once when the user clicks START SIM.
        """
        self._all_patients.clear()
        self._queue      = PatientQueue()
        self._tick_count = 0

        # Reset room occupancy for a fresh run
        for room in self._rooms.values():
            room.current_occupants.clear()

        # Reset grid occupancy
        if self._grid:
            self._grid.reset()

        for d in patient_dicts:
            p = Patient(
                patient_id         = d['id'],
                severity           = d['severity'],
                required_treatment = d['required_treatment'],
            )
            # Assign a visual spawn tile in the Entrance / Triage zone
            if self._grid:
                p.grid_pos = self._grid.claim_spawn_tile()

            self._all_patients.append(p)
            self._queue.push(p)

        print(f"[SimulationManager] Loaded {len(self._all_patients)} patients "
              f"into the priority queue.")

    def reset(self, state: SimulationState) -> None:
        """Full reset — rebuild rooms from updated state and clear queue."""
        self._rooms = self._build_rooms(state)
        self._all_patients.clear()
        self._queue      = PatientQueue()
        self._tick_count = 0
        if self._grid:
            self._grid.reset()

    def set_grid_index(self, grid_index: GridIndex) -> None:
        """Inject the GridIndex after construction (called from main.py)."""
        self._grid = grid_index

    # ── Core tick ─────────────────────────────────────────────────────────────

    def tick(self) -> None:
        """Advance the simulation by one discrete time unit.

        This is the only method the game loop needs to call.
        """
        self._tick_count += 1

        # ── Step 1: Increment wait times ──────────────────────────────────
        self._increment_wait_times()

        # ── Step 2: Mortality check ───────────────────────────────────────
        self._apply_mortality()

        # ── Step 3: Rebuild priority queue (wait_times changed) ───────────
        self._queue.rebuild()

        # ── Step 4: Greedy allocation ─────────────────────────────────────
        self._greedy_allocate()

        # ── Step 5: Advance IN_TRANSIT → IN_TREATMENT ─────────────────────
        self._begin_treatments()

        # ── Step 6: Tick treatment timers; discharge completed patients ────
        self._tick_treatments()

        # ── Step 7: Push metrics to SimulationState ───────────────────────
        self._update_state_metrics()

    # ── Step implementations ──────────────────────────────────────────────────

    def _increment_wait_times(self) -> None:
        """Add 1 tick to every patient still waiting in the queue."""
        for patient in self._all_patients:
            if patient.state == PatientState.WAITING_IN_QUEUE:
                patient.wait_time += 1

    def _apply_mortality(self) -> None:
        """Stochastic mortality check for critical patients.

        A patient dies if ALL three conditions hold:
          - severity > MORTALITY_SEV_THRESHOLD  (default 7)
          - wait_time > MORTALITY_WAIT_THRESHOLD (default 20 ticks)
          - random roll < MORTALITY_CHANCE       (default 5 % per tick)

        Using random.random() — deterministic given a fixed seed, but
        intentionally non-seeded here for varied gameplay.
        """
        for patient in self._all_patients:
            if patient.state != PatientState.WAITING_IN_QUEUE:
                continue
            if (patient.severity   > MORTALITY_SEV_THRESHOLD and
                    patient.wait_time > MORTALITY_WAIT_THRESHOLD and
                    random.random()   < MORTALITY_CHANCE):
                patient.mark_deceased()
                if self._grid:
                    self._grid.release_tile(patient.grid_pos)
                    patient.grid_pos = None
                print(f"[Tick {self._tick_count}] ⚠  Patient {patient.id} "
                      f"(sev={patient.severity}) deceased after "
                      f"{patient.wait_time} ticks waiting.")

    def _greedy_allocate(self) -> None:
        """Non-blocking greedy scan: assign patients to available rooms.

        Algorithm
        ---------
        1. Get the full priority-sorted waiting list.
        2. Track which room types are known-full this tick to avoid
           redundant checks (small optimisation).
        3. For each patient (highest priority first):
           a. If their required room is known-full → skip.
           b. Check the room object.  If available → allocate.
           c. If not available → mark that room type as full for this tick.
        """
        waiting        = self._queue.all_waiting()
        full_this_tick = set()   # room types confirmed full this tick

        for patient in waiting:
            tx = patient.required_treatment

            # Fast-skip if we already know this room type is full
            if tx in full_this_tick:
                continue

            room = self._rooms.get(tx)
            if room is None:
                # Unknown treatment type — skip gracefully
                continue

            if room.is_available:
                patient.allocate(room)
                # ── Visual move: release spawn tile, claim a room tile ────
                if self._grid:
                    self._grid.release_tile(patient.grid_pos)
                    patient.grid_pos = self._grid.claim_zone_tile(tx)
                print(f"[Tick {self._tick_count}] ✓  Patient {patient.id} "
                      f"(sev={patient.severity}) → {tx} "
                      f"(slot {room.current_occupancy}/{room.capacity}) "
                      f"grid={patient.grid_pos}")
            else:
                # Room is full — record it so we skip future patients
                # needing the same room type this tick
                full_this_tick.add(tx)

    def _begin_treatments(self) -> None:
        """Transition IN_TRANSIT patients to IN_TREATMENT.

        In Phase 4 this will be gated on a visual transit animation
        completing.  For now the transition is instant (same tick).
        """
        for patient in self._all_patients:
            if patient.state == PatientState.IN_TRANSIT:
                patient.begin_treatment()

    def _tick_treatments(self) -> None:
        """Decrement treatment timers; discharge patients who finish."""
        for patient in self._all_patients:
            if patient.state != PatientState.IN_TREATMENT:
                continue

            complete = patient.tick_treatment()
            if complete:
                tx = patient.required_treatment
                # Release grid tile before discharge clears assigned_room
                if self._grid:
                    self._grid.release_tile(patient.grid_pos)
                    patient.grid_pos = None
                patient.discharge()
                print(f"[Tick {self._tick_count}] ✔  Patient {patient.id} "
                      f"discharged from {tx}.")

                # Update throughput counters on SimulationState
                if tx == 'Surgery':
                    self._state.increment_surgeries()
                elif tx == 'MRI':
                    self._state.increment_mri_scans()

    # ── Metrics calculation ───────────────────────────────────────────────────

    def _update_state_metrics(self) -> None:
        """Compute aggregate metrics and push them to SimulationState."""
        waiting   = [p for p in self._all_patients
                     if p.state == PatientState.WAITING_IN_QUEUE]
        active    = [p for p in self._all_patients
                     if p.state in (PatientState.IN_TRANSIT,
                                    PatientState.IN_TREATMENT)]
        deceased  = [p for p in self._all_patients
                     if p.state == PatientState.DECEASED]

        total_active = len(waiting) + len(active)
        self._state.update_total_patients(total_active)

        # Average wait time across all currently-waiting patients
        if waiting:
            avg_wait = sum(p.wait_time for p in waiting) / len(waiting)
        else:
            avg_wait = 0.0
        self._state.update_wait_time(avg_wait)

        # Mortality risk: percentage of patients who have died
        total = len(self._all_patients)
        mort  = (len(deceased) / total * 100.0) if total else 0.0
        self._state.update_mortality_risk(mort)

        # Resource utilisation: average occupancy across all rooms
        if self._rooms:
            util = (sum(r.utilisation for r in self._rooms.values())
                    / len(self._rooms) * 100.0)
        else:
            util = 0.0
        self._state.update_resource_util(util)

    # ── Inspection helpers (for debugging / Phase 4 visual hooks) ────────────

    @property
    def rooms(self) -> Dict[str, Room]:
        """Read-only view of the room pool."""
        return self._rooms

    @property
    def tick_count(self) -> int:
        return self._tick_count

    def queue_snapshot(self) -> List[Patient]:
        """Current priority-sorted waiting list (non-destructive)."""
        return self._queue.all_waiting()

    def patients_in_state(self, state: PatientState) -> List[Patient]:
        """All patients currently in *state*."""
        return [p for p in self._all_patients if p.state == state]

    def get_visible_patients(self) -> List[Patient]:
        """All patients that have a grid_pos and should be rendered.

        Includes WAITING, IN_TRANSIT, and IN_TREATMENT patients.
        Excludes DISCHARGED and DECEASED (they have no grid_pos).
        """
        visible_states = {
            PatientState.WAITING_IN_QUEUE,
            PatientState.IN_TRANSIT,
            PatientState.IN_TREATMENT,
        }
        return [p for p in self._all_patients
                if p.state in visible_states and p.grid_pos is not None]
