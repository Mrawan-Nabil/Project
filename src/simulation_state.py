"""SimulationState — single source of truth for all HUD data.

Static resources (beds, mris, doctors, icus, operating_rooms) are displayed
in the top-left ResourceHUD and never change during a run.

The only controllable pre-sim input on the bottom dashboard is
incoming_patients.  Clicking START SIM calls generate_patients() which
builds the patient pool and populates the breakdown counters.
"""

import random
from typing import List, Dict

from src.map_data import ENTITY_MAP, calculate_resources


# Realistic treatment distribution weights
# Surgery ~10 %, MRI ~20 %, ICU ~15 %, Ward ~55 %
_TREATMENT_WEIGHTS = {
    'Surgery': 10,
    'MRI':     20,
    'ICU':     15,
    'Ward':    55,
}
_TREATMENTS  = list(_TREATMENT_WEIGHTS.keys())
_WEIGHTS     = list(_TREATMENT_WEIGHTS.values())


class SimulationState:
    """Holds every value displayed across all HUD panels.

    Static resources (top-left panel):
        beds, mris, doctors, icus, operating_rooms

    Controllable input (bottom dashboard, col 1):
        incoming_patients

    Patient pool (populated on START SIM):
        patients          – list of patient dicts
        n_surgery         – count needing Surgery
        n_mri             – count needing MRI
        n_icu             – count needing ICU
        n_ward            – count needing Ward

    Live metrics (bottom dashboard, cols 2 & 3):
        total_patients, avg_wait_time, mortality_risk,
        resource_util, surgeries_today, mri_scans
    """

    def __init__(self) -> None:
        # ── Static resources — derived by scanning the live ENTITY_MAP ───
        # calculate_resources() counts 'E', 'M', 'X'/'S'/'G', 'O', 'L'
        # so the top-left HUD always reflects the actual map contents.
        _res = calculate_resources(ENTITY_MAP)

        self.beds:            int = _res['beds']
        self.mris:            int = _res['mris']
        self.doctors:         int = _res['doctors']
        self.icus:            int = _res['icus']
        self.operating_rooms: int = _res['operating_rooms']

        # ── Controllable input ───────────────────────────────────────────
        self.incoming_patients: int = 30

        # ── Patient pool ─────────────────────────────────────────────────
        self.patients:  List[Dict] = []
        self.n_surgery: int = 0
        self.n_mri:     int = 0
        self.n_icu:     int = 0
        self.n_ward:    int = 0

        # ── Live metrics ─────────────────────────────────────────────────
        self.total_patients:  int   = 0
        self.avg_wait_time:   float = 0.0
        self.mortality_risk:  float = 0.0
        self.resource_util:   float = 0.0
        self.surgeries_today: int   = 0
        self.mri_scans:       int   = 0

        # ── Flags ────────────────────────────────────────────────────────
        self.sim_running: bool = False

    # ── Static resource setters ──────────────────────────────────────────

    def set_beds(self, v: int)            -> None: self.beds            = max(0, int(v))
    def set_mris(self, v: int)            -> None: self.mris            = max(0, int(v))
    def set_doctors(self, v: int)         -> None: self.doctors         = max(0, int(v))
    def set_icus(self, v: int)            -> None: self.icus            = max(0, int(v))
    def set_operating_rooms(self, v: int) -> None: self.operating_rooms = max(0, int(v))

    # ── Controllable input setter ────────────────────────────────────────

    def set_incoming_patients(self, v: int) -> None:
        self.incoming_patients = max(0, int(v))

    # ── Patient generation ───────────────────────────────────────────────

    def generate_patients(self) -> None:
        """Build a pool of *incoming_patients* mock patient dicts.

        Each patient has:
            id               – sequential integer
            severity         – random int 1-10  (10 = most critical)
            required_treatment – one of 'Surgery', 'MRI', 'ICU', 'Ward'

        Breakdown counters (n_surgery, n_mri, n_icu, n_ward) are updated
        so the dashboard can display them immediately.
        """
        n = self.incoming_patients
        treatments = random.choices(_TREATMENTS, weights=_WEIGHTS, k=n)

        self.patients = [
            {
                'id':                   i + 1,
                'severity':             random.randint(1, 10),
                'required_treatment':   treatments[i],
            }
            for i in range(n)
        ]

        self.n_surgery = treatments.count('Surgery')
        self.n_mri     = treatments.count('MRI')
        self.n_icu     = treatments.count('ICU')
        self.n_ward    = treatments.count('Ward')

        # Seed live metrics from the generated pool
        self.total_patients = n

    # ── Live metric setters ──────────────────────────────────────────────

    def update_total_patients(self, v: int)   -> None: self.total_patients  = max(0, int(v))
    def update_wait_time(self, v: float)      -> None: self.avg_wait_time   = max(0.0, float(v))
    def update_mortality_risk(self, v: float) -> None: self.mortality_risk  = max(0.0, min(100.0, float(v)))
    def update_resource_util(self, v: float)  -> None: self.resource_util   = max(0.0, min(100.0, float(v)))

    def increment_surgeries(self, n: int = 1) -> None: self.surgeries_today += n
    def increment_mri_scans(self, n: int = 1) -> None: self.mri_scans       += n
    def reset_daily_counters(self)            -> None:
        self.surgeries_today = 0
        self.mri_scans       = 0

    # ── Sim control ──────────────────────────────────────────────────────

    def start_sim(self) -> None:
        """Generate patients then mark simulation as running."""
        self.generate_patients()
        self.sim_running = True

    def stop_sim(self) -> None:
        self.sim_running = False
