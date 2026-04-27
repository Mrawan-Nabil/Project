"""Hospital map data and blueprints.

Layout based on the reference image: a sprawling multi-wing hospital complex
with distinct colour-coded zones, open-plan dollhouse view, densely populated
with staff and equipment.  30 × 30 grid.

Zone colour key (matches reference image):
  0  = void / deep-space background
  1  = floor_corridor   (grey checkered walkways)
  2  = floor_entrance   (yellow — waiting area / lobby)
  3  = floor_triage     (light blue — triage)
  4  = floor_ward       (mint green — patient wards)
  5  = floor_icu        (pink — ICU)
  6  = floor_recovery   (gold — recovery bay)
  7  = floor_mri        (lavender — MRI suite)
  8  = floor_surgery    (white — operating theatres)
  9  = floor_diagnostics (silver — diagnostics / lab)
  10 = floor_pharmacy   (deep blue — pharmacy)
  11 = floor_sterilization (pure white — sterilisation)
  12 = floor_admin      (cream — admin offices)
  13 = floor_research   (cyan — research wing)
"""

# ---------------------------------------------------------------------------
# MAP LEGEND
# ---------------------------------------------------------------------------
MAP_LEGEND = {
    # ── Void ────────────────────────────────────────────────────────────────
    0:  None,

    # ── Floor zones ─────────────────────────────────────────────────────────
    1:  'floor_corridor',
    2:  'floor_entrance',
    3:  'floor_triage',
    4:  'floor_ward',
    5:  'floor_icu',
    6:  'floor_recovery',
    7:  'floor_mri',
    8:  'floor_surgery',
    9:  'floor_diagnostics',
    10: 'floor_pharmacy',
    11: 'floor_sterilization',
    12: 'floor_admin',
    13: 'floor_research',

    # ── Medical equipment ────────────────────────────────────────────────────
    'M': 'equip_mri_scanner',
    'E': 'equip_exam_table',
    'V': 'equip_iv_stand',
    'L': 'equip_surgical_light',
    'O': 'equip_medical_monitor',

    # ── Furniture ────────────────────────────────────────────────────────────
    'R': 'furn_reception_desk',
    'B': 'furn_waiting_bench_orange',
    'T': 'furn_lab_workbench',

    # ── Characters ───────────────────────────────────────────────────────────
    'P': 'char_male_patient_gown',
    'Q': 'char_female_patient_gown',
    'N': 'char_female_staff_blue_scrubs',
    'A': 'char_male_staff_blue_scrubs',
    'S': 'char_male_surgeon_green',
    'G': 'char_female_surgeon_green',
    'X': 'char_male_doctor_white',
    'F': 'char_female_staff_white_blue',

    # ── Empty entity cell ────────────────────────────────────────────────────
    ' ': None,
}

# ---------------------------------------------------------------------------
# FLOOR MAP  (30 × 30)
# ---------------------------------------------------------------------------
# Wing layout (top-left origin, isometric view looks NW→SE):
#
#  Col:  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29
#
#  Row 0-4   : ICU (pink, top-left)  |  corridor  |  OPS ROOM (white, top-right)
#  Row 5-9   : WARD 1A (mint)        |  corridor  |  MRI suite (lavender)
#  Row 10-14 : TRIAGE (light blue)   |  corridor  |  SURGERY THEATRE (white)
#  Row 15-19 : DIAGNOSTICS (silver)  |  corridor  |  PHARMACY (deep blue)
#  Row 20-24 : RESEARCH (cyan)       |  corridor  |  ADMIN (cream)
#  Row 25-29 : ENTRANCE / WAITING (yellow)  — bottom lobby spanning full width

FLOOR_MAP = [
    # row 0
    [ 0, 0, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 8, 8, 8, 8, 8, 8, 8, 8, 0, 0, 0, 0],
    # row 1
    [ 0, 0, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 8, 8, 8, 8, 8, 8, 8, 8, 0, 0, 0, 0],
    # row 2
    [ 0, 0, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 8, 8, 8, 8, 8, 8, 8, 8, 0, 0, 0, 0],
    # row 3
    [ 0, 0, 5, 5, 5, 5, 5, 5, 5, 5, 1, 1, 1, 1, 1, 1, 1, 1, 8, 8, 8, 8, 8, 8, 8, 8, 0, 0, 0, 0],
    # row 4
    [ 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    # row 5
    [ 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 7, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0, 0],
    # row 6
    [ 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 7, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0, 0],
    # row 7
    [ 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 7, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0, 0],
    # row 8
    [ 0, 0, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 7, 7, 7, 7, 7, 7, 7, 7, 0, 0, 0, 0],
    # row 9
    [ 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    # row 10
    [ 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 1, 1, 8, 8, 8, 8, 8, 8, 0, 0],
    # row 11
    [ 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 1, 1, 8, 8, 8, 8, 8, 8, 0, 0],
    # row 12
    [ 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 1, 1, 8, 8, 8, 8, 8, 8, 0, 0],
    # row 13
    [ 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 1, 1, 8, 8, 8, 8, 8, 8, 0, 0],
    # row 14
    [ 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    # row 15
    [ 0, 0, 6, 6, 6, 6, 6, 6, 6, 6, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 1, 1,10,10,10,10,10,10, 0, 0],
    # row 16
    [ 0, 0, 6, 6, 6, 6, 6, 6, 6, 6, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 1, 1,10,10,10,10,10,10, 0, 0],
    # row 17
    [ 0, 0, 6, 6, 6, 6, 6, 6, 6, 6, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 1, 1,10,10,10,10,10,10, 0, 0],
    # row 18
    [ 0, 0, 6, 6, 6, 6, 6, 6, 6, 6, 1, 1, 9, 9, 9, 9, 9, 9, 9, 9, 1, 1,10,10,10,10,10,10, 0, 0],
    # row 19
    [ 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    # row 20
    [ 0, 0,13,13,13,13,13,13,13,13, 1, 1,12,12,12,12,12,12,12,12, 1, 1,11,11,11,11,11,11, 0, 0],
    # row 21
    [ 0, 0,13,13,13,13,13,13,13,13, 1, 1,12,12,12,12,12,12,12,12, 1, 1,11,11,11,11,11,11, 0, 0],
    # row 22
    [ 0, 0,13,13,13,13,13,13,13,13, 1, 1,12,12,12,12,12,12,12,12, 1, 1,11,11,11,11,11,11, 0, 0],
    # row 23
    [ 0, 0,13,13,13,13,13,13,13,13, 1, 1,12,12,12,12,12,12,12,12, 1, 1,11,11,11,11,11,11, 0, 0],
    # row 24
    [ 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    # row 25
    [ 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0],
    # row 26
    [ 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0],
    # row 27
    [ 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0],
    # row 28
    [ 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0],
    # row 29
    [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

# ---------------------------------------------------------------------------
# ENTITY MAP  (30 × 30)
# ---------------------------------------------------------------------------
# Populated to match the reference image density:
# every room has equipment + multiple staff + patients.
#
# Character key:
#   X = doctor (white coat)    N = nurse (blue scrubs)
#   S = surgeon (green)        G = female surgeon
#   P = male patient (gown)    Q = female patient (gown)
#   A = male staff (blue)      F = female staff (white/blue)
#
# Equipment key:
#   E = exam table   V = IV stand   O = monitor
#   L = surgical light   M = MRI scanner   T = lab bench
#   R = reception desk   B = waiting bench

ENTITY_MAP = [
    # row 0  — ICU top row: monitors + patients
    [0, 0, 'O', 0,'P', 0,'O', 0,'Q', 0, 0, 0, 0, 0, 0, 0, 0, 0,'L', 0,'L', 0, 0,'E', 0,'E', 0, 0, 0, 0],
    # row 1  — ICU: nurses + IV stands | OPS: surgeons + lights
    [0, 0, 'N','V', 0,'X', 0,'N','V', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,'S', 0,'G', 0,'S', 0, 0, 0, 0, 0, 0],
    # row 2  — ICU: more patients + monitors | OPS: exam tables
    [0, 0, 'O','P', 0,'O','Q', 0,'O', 0, 0, 0, 0, 0, 0, 0, 0, 0,'E', 0,'E', 0,'O', 0,'N', 0, 0, 0, 0, 0],
    # row 3  — ICU: doctor rounds | OPS: surgical light + staff
    [0, 0, 'X', 0,'N', 0,'A', 0,'F', 0, 0, 0, 0, 0, 0, 0, 0, 0,'L', 0, 0,'X', 0,'G', 0,'A', 0, 0, 0, 0],
    # row 4  — corridor
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # row 5  — WARD: beds + patients | MRI: scanner
    [0, 0, 'E','P', 0,'E','Q', 0,'E', 0, 0, 0, 0, 0, 0, 0, 0, 0, 'M', 0,'M', 0, 'M', 0, 0, 0, 0, 0, 0, 0],
    # row 6  — WARD: nurses + IV | MRI: doctor + monitor
    [0, 0, 'N','V', 0,'N', 0,'V','N', 0, 0, 0, 0, 0, 0, 0, 0, 0,'X', 0, 0,'O', 0,'N', 0, 0, 0, 0, 0, 0],
    # row 7  — WARD: more beds | MRI: patient in scanner
    [0, 0, 'E','Q', 0,'E','P', 0,'E', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,'P', 0, 0,'O', 0, 0, 0, 0, 0, 0, 0],
    # row 8  — WARD: doctor rounds | MRI: staff
    [0, 0, 'X', 0,'A', 0,'F', 0,'X', 0, 0, 0, 0, 0, 0, 0, 0, 0,'N', 0, 0,'A', 0,'F', 0, 0, 0, 0, 0, 0],
    # row 9  — corridor
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # row 10 — TRIAGE: benches + staff | DIAG: lab benches | SURGERY: lights
    [0, 0, 'B', 0, 0,'B', 0, 0,'B', 0, 0, 0,'T', 0,'T', 0,'T', 0,'T', 0, 0, 0,'L', 0,'L', 0,'L', 0, 0, 0],
    # row 11 — TRIAGE: nurses | DIAG: doctors + monitors | SURGERY: surgeons
    [0, 0, 'N', 0,'X', 0,'N', 0,'A', 0, 0, 0,'O','X', 0,'N','O', 0,'X', 0, 0, 0,'S', 0,'G', 0,'S', 0, 0, 0],
    # row 12 — TRIAGE: empty (dynamic patients spawn here) | DIAG: workbenches | SURGERY: exam tables
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,'T', 0,'T', 0,'T', 0,'T', 0, 0, 0,'E', 0,'E', 0,'E', 0, 0, 0],
    # row 13 — TRIAGE: reception | DIAG: staff | SURGERY: monitors + staff
    [0, 0, 'R', 0,'F', 0,'R', 0,'F', 0, 0, 0,'A', 0,'F', 0,'A', 0,'F', 0, 0, 0,'O','N', 0,'O','N', 0, 0, 0],
    # row 14 — corridor
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # row 15 — RECOVERY: beds + patients | DIAG lower: benches | PHARMACY: desks
    [0, 0, 'E','P', 0,'E','Q', 0,'E', 0, 0, 0,'T', 0,'T', 0,'T', 0,'T', 0, 0, 0,'R', 0,'R', 0,'R', 0, 0, 0],
    # row 16 — RECOVERY: nurses + IV | DIAG: monitors | PHARMACY: nurses
    [0, 0, 'N','V', 0,'N','V', 0,'N', 0, 0, 0,'O','X', 0,'N','O', 0,'A', 0, 0, 0,'N', 0,'N', 0,'N', 0, 0, 0],
    # row 17 — RECOVERY: more beds | DIAG: staff | PHARMACY: patients
    [0, 0, 'E','Q', 0,'E','P', 0,'E', 0, 0, 0,'T', 0,'T', 0,'T', 0,'T', 0, 0, 0,'P', 0,'Q', 0,'P', 0, 0, 0],
    # row 18 — RECOVERY: doctor | DIAG: staff | PHARMACY: staff
    [0, 0, 'X', 0,'F', 0,'A', 0,'X', 0, 0, 0,'F', 0,'A', 0,'F', 0,'A', 0, 0, 0,'F', 0,'A', 0,'F', 0, 0, 0],
    # row 19 — corridor
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # row 20 — RESEARCH: benches + staff | ADMIN: desks | STERILISATION: staff
    [0, 0, 'T', 0,'T', 0,'T', 0,'T', 0, 0, 0,'R', 0,'R', 0,'R', 0,'R', 0, 0, 0,'N', 0,'N', 0,'N', 0, 0, 0],
    # row 21 — RESEARCH: doctors | ADMIN: staff | STERILISATION: staff
    [0, 0, 'X', 0,'N', 0,'X', 0,'N', 0, 0, 0,'X', 0,'F', 0,'A', 0,'X', 0, 0, 0,'A', 0,'F', 0,'A', 0, 0, 0],
    # row 22 — RESEARCH: more benches | ADMIN: more desks | STERILISATION
    [0, 0, 'T', 0,'T', 0,'T', 0,'T', 0, 0, 0,'R', 0,'R', 0,'R', 0,'R', 0, 0, 0,'N', 0,'N', 0,'N', 0, 0, 0],
    # row 23 — RESEARCH: staff | ADMIN: staff | STERILISATION: staff
    [0, 0, 'A', 0,'F', 0,'A', 0,'F', 0, 0, 0,'F', 0,'A', 0,'F', 0,'A', 0, 0, 0,'F', 0,'A', 0,'F', 0, 0, 0],
    # row 24 — corridor
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # row 25 — ENTRANCE/WAITING: reception desks + benches only (patients are dynamic)
    [0, 0, 'R', 0,'R', 0,'R', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0, 0, 0],
    # row 26 — WAITING: empty floor (dynamic patients spawn here)
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # row 27 — WAITING: staff only
    [0, 0, 'N', 0,'X', 0,'N', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    # row 28 — WAITING: benches only (dynamic patients spawn here)
    [0, 0, 'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0,'B', 0, 0, 0],
    # row 29 — void
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


# ---------------------------------------------------------------------------
# Utility functions (unchanged)
# ---------------------------------------------------------------------------

def get_map_dimensions():
    """Return (rows, cols) of the hospital map."""
    return len(FLOOR_MAP), len(FLOOR_MAP[0])


def validate_maps():
    """Raise ValueError if FLOOR_MAP and ENTITY_MAP have mismatched dimensions."""
    floor_rows, floor_cols = len(FLOOR_MAP), len(FLOOR_MAP[0])
    entity_rows, entity_cols = len(ENTITY_MAP), len(ENTITY_MAP[0])

    if floor_rows != entity_rows or floor_cols != entity_cols:
        raise ValueError(
            f"Map dimension mismatch: FLOOR_MAP is {floor_rows}×{floor_cols}, "
            f"ENTITY_MAP is {entity_rows}×{entity_cols}"
        )

    for i, row in enumerate(FLOOR_MAP):
        if len(row) != floor_cols:
            raise ValueError(f"FLOOR_MAP row {i} has {len(row)} columns, expected {floor_cols}")

    for i, row in enumerate(ENTITY_MAP):
        if len(row) != entity_cols:
            raise ValueError(f"ENTITY_MAP row {i} has {len(row)} columns, expected {entity_cols}")


def get_legend_info():
    """Return statistics about the map legend."""
    symbols   = list(MAP_LEGEND.keys())
    asset_keys = [v for v in MAP_LEGEND.values() if v is not None]
    return {
        'total_symbols': len(symbols),
        'symbols':       symbols,
        'unique_assets': len(set(asset_keys)),
        'asset_keys':    sorted(set(asset_keys)),
    }


def calculate_resources(entity_map: list) -> dict:
    """Scan *entity_map* and count hospital resources by symbol.

    Counting rules
    --------------
    beds            'E'  — exam tables / patient beds
    mris            'M'  — MRI scanner machines
    doctors         'X' + 'S' + 'G'  — doctors, surgeons (both genders)
    icus            'O'  — medical monitors (designate ICU / high-dependency spots)
    operating_rooms 'L'  — surgical lights (one per operating theatre bay)

    Returns
    -------
    dict with keys: beds, mris, doctors, icus, operating_rooms
    """
    counts = {
        'beds':            0,
        'mris':            0,
        'doctors':         0,
        'icus':            0,
        'operating_rooms': 0,
    }

    for row in entity_map:
        for cell in row:
            if cell == 'E':
                counts['beds']            += 1
            elif cell == 'M':
                counts['mris']            += 1
            elif cell in ('X', 'S', 'G'):
                counts['doctors']         += 1
            elif cell == 'O':
                counts['icus']            += 1
            elif cell == 'L':
                counts['operating_rooms'] += 1

    return counts
