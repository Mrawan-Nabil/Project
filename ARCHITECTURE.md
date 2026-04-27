# Hospital Management Game — Architecture & Technical Reference

> **Study guide for the complete 2.5D Isometric Hospital Management Game.**
> Covers every system from pixel math to algorithmic patient routing.

---

## Table of Contents

1. [Project Overview & Core Constraints](#1-project-overview--core-constraints)
2. [The Rendering Engine](#2-the-rendering-engine)
3. [Map Architecture & Zoning](#3-map-architecture--zoning)
4. [UI / UX Implementation](#4-ui--ux-implementation)
5. [The Algorithmic Core](#5-the-algorithmic-core)
6. [Algorithmic-Visual Linkage](#6-algorithmic-visual-linkage)
7. [File Reference](#7-file-reference)

---

## 1. Project Overview & Core Constraints

### Elevator Pitch

A **2.5D isometric hospital management simulation** built entirely in Python and Pygame.
The player configures a hospital's incoming patient load, presses **START SIM**, and watches
a discrete-event engine route patients — in real time — from a waiting area through triage,
wards, MRI suites, ICUs, and operating theatres. Every patient sprite physically moves on
the isometric map when the algorithm assigns them a room.

### The Zero-ML Constraint

> **No machine learning, no neural networks, no probabilistic models.**

Every decision in the simulation is driven by **classic Computer Science algorithms**:

| Problem | Algorithm used |
|---|---|
| Patient prioritisation | Max-priority queue (heapq) |
| Room assignment | Greedy non-blocking scan |
| Sprite depth ordering | Painter's Algorithm (stable sort) |
| Resource counting | Single-pass 2D array scan |
| Spatial tile management | Hash-set occupancy index |

This constraint makes the system fully **deterministic, inspectable, and teachable**.

### Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Rendering | Pygame-CE 2.5 (Community Edition) |
| Data structures | Python `heapq`, `dict`, `set`, `list` |
| Image assets | High-resolution transparent PNG sprites |
| No external ML libs | `numpy`, `torch`, `sklearn` — none used |

### Display Configuration (`src/settings.py`)

```python
SCREEN_WIDTH  = 1024   # pixels
SCREEN_HEIGHT = 768    # pixels
FPS           = 60     # frames per second
TILE_WIDTH    = 128    # isometric tile width in pixels
TILE_HEIGHT   = 64     # isometric tile height in pixels
```

---

## 2. The Rendering Engine

### 2.1 Cartesian-to-Isometric Mathematical Conversion

**File:** `src/isometric_converter.py`

The game world is stored as a standard 2D grid `(row, col)`.
The screen is a flat 2D surface `(x, y)`.
The isometric projection creates the illusion of a 3D diamond-shaped world
by applying a **linear transformation** to every grid coordinate.

#### The Formula

```python
screen_x = (col - row) * (TILE_WIDTH  / 2) + camera_x
screen_y = (col + row) * (TILE_HEIGHT / 2) + camera_y
```

#### Why it works

| Term | Effect |
|---|---|
| `(col - row)` | Creates the **horizontal diamond axis**. Moving right (`col+1`) shifts the sprite right; moving down (`row+1`) shifts it left. |
| `(col + row)` | Creates the **vertical depth axis**. Both `col+1` and `row+1` push the sprite downward on screen. |
| `× TILE_WIDTH/2` | Scales one grid step to half a tile width (64 px). |
| `× TILE_HEIGHT/2` | Scales one grid step to half a tile height (32 px). |
| `+ camera_x/y` | Applies the viewport pan offset. |

#### Worked example

```
Grid (0,0) → screen (0, 0)          # top of the diamond
Grid (1,0) → screen (-64, 32)       # one step down-left
Grid (0,1) → screen ( 64, 32)       # one step down-right
Grid (2,2) → screen (  0, 128)      # two steps in both directions
```

The result is a **diamond (rhombus) grid** where every tile is 128 px wide and 64 px tall.

---

### 2.2 Y-Sorting — The Painter's Algorithm

**File:** `src/y_sorter.py`

#### The Problem

In an isometric view, sprites at different grid positions can visually overlap.
A character standing at `(3,3)` must be drawn **on top of** a wall at `(2,2)`,
because the character is closer to the viewer. If sprites are drawn in arbitrary
order, objects will clip through each other incorrectly.

#### The Solution: Depth = row + col

Every entity is assigned a **depth value**:

```python
depth = entity.row + entity.col
```

This works because in isometric projection, both increasing `row` and increasing `col`
move an object **toward the viewer** (down and to the front of the diamond).
The sum `row + col` is therefore a reliable proxy for visual depth.

#### The Sort

```python
sorted_entities = sorted(entities, key=lambda e: e.depth)
# Draw in ascending order: lowest depth (furthest back) first
```

Python's `sorted()` is **stable** — entities with equal depth values preserve their
original insertion order, preventing flickering when two objects share the same diagonal.

#### Complexity

- **O(n log n)** per frame using Timsort.
- The sort runs on every `render()` call, operating on the full entity list (~959 static entities + dynamic patients).

---

### 2.3 Bottom-Center Anchoring for Tall Sprites

**File:** `src/map_parser.py` — `AnchoredEntity` class

#### The Problem

Floor tiles are exactly 128×64 px — they fit the isometric diamond perfectly.
But a wall sprite might be 128×222 px, and a character sprite 64×136 px.
If all sprites are blitted at their top-left corner at the grid point, tall sprites
appear to **float above the floor** because their visual base is not aligned to the tile.

#### The Solution: Pre-computed Anchor Offsets

When an `AnchoredEntity` is created, the anchor offsets are calculated **once** from
the sprite's actual pixel dimensions:

```python
# Horizontal: centre the sprite over the tile diamond
anchor_offset_x = -(sprite_width  // 2) + (TILE_WIDTH  // 2)

# Vertical: push the sprite up so its BOTTOM aligns with the tile surface
anchor_offset_y = -(sprite_height - TILE_HEIGHT)
```

At render time, these offsets are added to the raw isometric coordinates:

```python
blit_x = iso_x + anchor_offset_x
blit_y = iso_y + anchor_offset_y
```

#### Effect

| Sprite type | anchor_offset_x | anchor_offset_y |
|---|---|---|
| Floor tile (128×64) | 0 | 0 |
| Wall (128×222) | 0 | −158 |
| Character (64×136) | +32 | −72 |

The wall is shifted 158 px upward so its bottom pixel sits exactly on the tile surface.
The character is shifted 32 px right (to centre its narrower body) and 72 px upward.

---

### 2.4 ResourceManager and CUSTOM_SCALES

**File:** `src/resource_manager.py`

#### Loading Pipeline

On startup, `load_assets_from_directory("assets")` scans every `.png` file and applies
a two-stage scaling pipeline **once**, storing the result in a dictionary:

```
PNG file on disk
    → pygame.image.load()
    → .convert_alpha()          # preserve transparency
    → _scale(surface, key)      # resize to grid dimensions
    → self._assets[key]         # cached forever
```

#### Floor Tile Scaling

Floor tiles (filenames containing `"floor"`, `"tile"`, or `"ground"`) are
**force-scaled** to exactly `(TILE_WIDTH, TILE_HEIGHT)` = `(128, 64)`:

```python
if self._is_floor(asset_key):
    target = (128, 64)
```

This guarantees the isometric diamond grid has no gaps regardless of the source resolution.

#### Entity Scaling — CUSTOM_SCALES

All other sprites (characters, equipment, furniture) use a **two-step proportional scale**:

```python
# Step 1: lock width to TILE_WIDTH, scale height proportionally
base_scale = TILE_WIDTH / original_width      # e.g. 128 / 2036 = 0.0629
base_w     = TILE_WIDTH                       # 128 px
base_h     = original_height * base_scale     # e.g. 4096 * 0.0629 = 257 px

# Step 2: apply the per-asset custom multiplier
mult  = CUSTOM_SCALES.get(asset_key, 1.0)
new_w = int(base_w * mult)
new_h = int(base_h * mult)
```

The `CUSTOM_SCALES` dictionary at the top of `resource_manager.py` is the **single place
a developer tunes visual sizes**:

```python
CUSTOM_SCALES = {
    "char_male_doctor_white":   0.5,   # halve the base size
    "equip_mri_scanner":        1.0,   # keep base size
    "furn_reception_desk":      0.6,   # 60% of base size
    # ...
}
```

If a key is absent, the multiplier defaults to `1.0`.
`pygame.transform.smoothscale()` is used for quality; the result is cached so
no per-frame scaling occurs.

---

## 3. Map Architecture & Zoning

### 3.1 The Two-Layer Map System

The hospital layout is defined by **two parallel 30×30 integer/string arrays** in `src/map_data.py`.

#### FLOOR_MAP — The Ground Layer

Every cell contains an **integer zone ID** (0–13).
The `MapParser` reads this layer first and creates one `AnchoredEntity` (floor tile) per non-zero cell.

```python
FLOOR_MAP[row][col] = zone_id   # integer
```

#### ENTITY_MAP — The Object Layer

Every cell contains either `0` (empty), or a **single-character string symbol**
identifying a piece of furniture, equipment, or staff.
The `MapParser` reads this layer second and creates one `AnchoredEntity` per non-zero cell.

```python
ENTITY_MAP[row][col] = 'E'   # exam table
ENTITY_MAP[row][col] = 0     # empty — skip
```

#### Two-Pass Rendering

The `MapParser.parse_maps()` method performs two passes:

1. **Pass 1 — Floors:** Iterate `FLOOR_MAP`, create floor `AnchoredEntity` objects (`is_floor_tile=True`).
2. **Pass 2 — Entities:** Iterate `ENTITY_MAP`, create object `AnchoredEntity` objects (`is_floor_tile=False`).

All entities are added to the `RenderingEngine` list. The Y-sorter then handles correct draw order.

---

### 3.2 Color-Coded Department Zoning

Each integer in `FLOOR_MAP` maps to a specific floor tile asset and represents a hospital department:

| Zone ID | Asset | Department | Visual Color |
|---|---|---|---|
| 0 | — | Void / Background | Deep space blue |
| 1 | `floor_corridor` | Corridors | Grey checkered |
| 2 | `floor_entrance` | Entrance / Waiting | Yellow |
| 3 | `floor_triage` | Triage | Light blue |
| 4 | `floor_ward` | Patient Wards | Mint green |
| 5 | `floor_icu` | ICU | Pink |
| 6 | `floor_recovery` | Recovery Bay | Gold |
| 7 | `floor_mri` | MRI Suite | Lavender |
| 8 | `floor_surgery` | Operating Theatres | White |
| 9 | `floor_diagnostics` | Diagnostics / Lab | Silver |
| 10 | `floor_pharmacy` | Pharmacy | Deep blue |
| 11 | `floor_sterilization` | Sterilisation | Pure white |
| 12 | `floor_admin` | Administration | Cream |
| 13 | `floor_research` | Research Wing | Cyan |

The `MAP_LEGEND` dictionary in `map_data.py` is the single source of truth mapping
both integer zone IDs and string entity symbols to asset keys.

---

### 3.3 The Dynamic Resource Parser

**Function:** `calculate_resources(entity_map)` in `src/map_data.py`

Rather than hardcoding resource counts, the system **scans the live `ENTITY_MAP`
at startup** to count every piece of equipment and staff:

```python
def calculate_resources(entity_map: list) -> dict:
    counts = {'beds': 0, 'mris': 0, 'doctors': 0,
              'icus': 0, 'operating_rooms': 0}
    for row in entity_map:
        for cell in row:
            if   cell == 'E':              counts['beds']            += 1
            elif cell == 'M':              counts['mris']            += 1
            elif cell in ('X', 'S', 'G'): counts['doctors']         += 1
            elif cell == 'O':              counts['icus']            += 1
            elif cell == 'L':              counts['operating_rooms'] += 1
    return counts
```

#### Symbol-to-Resource Mapping

| Symbol | Asset | Counted as |
|---|---|---|
| `'E'` | `equip_exam_table` | Beds (patient capacity) |
| `'M'` | `equip_mri_scanner` | MRI machines |
| `'X'` | `char_male_doctor_white` | Doctors |
| `'S'` | `char_male_surgeon_green` | Doctors (surgeons) |
| `'G'` | `char_female_surgeon_green` | Doctors (surgeons) |
| `'O'` | `equip_medical_monitor` | ICU bays |
| `'L'` | `equip_surgical_light` | Operating rooms |

#### Why this matters

`SimulationState.__init__()` calls `calculate_resources(ENTITY_MAP)` and stores the
results as its static resource fields. The `SimulationManager` then uses these counts
to set `Room` capacities. **If you add an `'E'` to the map, the bed count and Ward
capacity both increase automatically — no other code changes required.**

---

## 4. UI / UX Implementation

### 4.1 Glass-Morphism HUD with `pygame.SRCALPHA`

**File:** `src/dashboard_ui.py`

The HUD panels are rendered using **alpha-composited surfaces** — they are translucent
overlays that float on top of the isometric scene without obscuring it entirely.

#### How it works

```python
# Create a surface that supports per-pixel alpha
bg = pygame.Surface((width, height), pygame.SRCALPHA)

# Fill with a colour that includes an alpha value (0=transparent, 255=opaque)
bg.fill((12, 22, 40, 215))   # dark navy, 84% opaque

# Blit onto the main screen — Pygame composites the alpha automatically
screen.blit(bg, (x, y))
```

The `pygame.SRCALPHA` flag tells Pygame to allocate a 32-bit surface with a full
alpha channel. When blitted to the display, Pygame performs **alpha blending**:

```
output_pixel = (src_alpha / 255) * src_colour
             + (1 - src_alpha / 255) * dst_colour
```

This produces the glass-morphism effect: the hospital map shows through the panel.

#### Panel Architecture

Two independent HUD classes exist:

| Class | Position | Content |
|---|---|---|
| `ResourceHUD` | Top-left, 190×120 px | Static hospital resources (Beds, MRIs, Doctors, ICU Bays, Operating Rooms) |
| `DashboardUI` | Bottom 22% of screen | Patient input, patient breakdown, live simulation metrics |

Both are drawn **after** `rendering_engine.render()` so they always appear on top.

---

### 4.2 SimulationState vs DashboardUI — Strict Separation

The project enforces a **Model-View separation**:

| Layer | Class | Responsibility |
|---|---|---|
| **Data (Model)** | `SimulationState` | Holds all numeric values. No Pygame imports. |
| **Renderer (View)** | `DashboardUI`, `ResourceHUD` | Reads from state, draws to screen. No business logic. |

`SimulationState` is the single source of truth. The simulation engine writes to it;
the HUD reads from it. Neither knows about the other's internals.

```python
# Engine writes:
state.update_wait_time(avg_wait)
state.update_mortality_risk(mort_pct)

# HUD reads:
label = f"{state.avg_wait_time:.1f} min"
```

This means the HUD can be completely redesigned without touching the simulation,
and the simulation can be run headlessly (no window) for testing.

---

### 4.3 Interactive Text Input — "Incoming Patients"

**Method:** `DashboardUI.handle_event()` and `DashboardUI._draw_input_row()`

The input box is a **custom Pygame widget** — there is no built-in text input in Pygame.

#### State variables (stored on `DashboardUI`)

```python
self.input_text   = "30"    # current string content
self.input_active = False   # whether the box has keyboard focus
self.input_rect   = pygame.Rect(...)  # hit-test rectangle
```

#### Focus management (mouse click)

```python
if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    self.input_active = self.input_rect.collidepoint(event.pos)
```

Clicking inside the rect activates the box; clicking anywhere else deactivates it.

#### Character input (keyboard)

```python
elif event.type == pygame.KEYDOWN and self.input_active:
    if event.key == pygame.K_BACKSPACE:
        self.input_text = self.input_text[:-1]          # delete last char
    elif event.unicode.isnumeric() and len(self.input_text) < 3:
        self.input_text += event.unicode                # append digit
```

- Only numeric characters are accepted (`isnumeric()`).
- Maximum 3 characters prevents absurdly large patient counts.
- `event.unicode` gives the typed character as a string, handling keyboard layouts correctly.

#### Sync to simulation

When START SIM is clicked, `input_text` is parsed and written to `SimulationState`
**before** `start_sim()` is called:

```python
state.set_incoming_patients(int(self.input_text or "0"))
state.start_sim()
```

#### Visual rendering

The box is drawn with a **white border when active, grey when idle**:

```python
border_col = (255, 255, 255) if self.input_active else (100, 120, 150)
pygame.draw.rect(screen, border_col, self.input_rect, 1, border_radius=3)
```

A `|` cursor character is appended to `input_text` when the box is focused,
giving the user a clear visual cue.

---

## 5. The Algorithmic Core

### 5.1 The Tick Engine — Discrete Time Steps

**File:** `src/simulation_manager.py`

The simulation runs on a **discrete event model**: time advances in fixed steps called
**ticks**. One tick represents one second of in-game time.

#### Timer setup (in `main.py`)

```python
TICK_EVENT       = pygame.USEREVENT + 1
TICK_INTERVAL_MS = 1000   # 1000 ms = 1 second
pygame.time.set_timer(TICK_EVENT, TICK_INTERVAL_MS)
```

Pygame fires `TICK_EVENT` into the event queue every 1000 ms.
The main loop catches it and calls `sim_manager.tick()`:

```python
elif event.type == TICK_EVENT:
    if state.sim_running:
        sim_manager.tick()
```

#### The 7-Step Tick Sequence

Every call to `tick()` executes these steps **in order**:

```
Step 1  Increment wait_time for every WAITING_IN_QUEUE patient (+1 tick)
Step 2  Mortality check — critical patients who waited too long may die
Step 3  Rebuild the priority queue (wait_times changed → priorities changed)
Step 4  Greedy allocation — assign waiting patients to available rooms
Step 5  Advance IN_TRANSIT → IN_TREATMENT (instant transition)
Step 6  Tick treatment timers; discharge patients whose timer reaches 0
Step 7  Compute aggregate metrics and push to SimulationState for the HUD
```

This ordering is deliberate: wait times are incremented **before** the queue is
rebuilt, so the new wait times are reflected in the priority ordering of the
current tick's allocation pass.

---

### 5.2 The Priority Queue

**File:** `src/patient_queue.py`

#### Data structure

`PatientQueue` wraps Python's `heapq` module (a **min-heap**).
Because `heapq` is a min-heap but we want **max priority** (highest severity first),
all keys are **negated**:

```python
def priority_key(self) -> tuple[int, int]:
    return (-self.severity, -self.wait_time)
    # severity 10 → key -10 (smallest → popped first by min-heap)
    # wait_time 5  → key -5
```

Each heap entry is a 4-tuple to avoid comparing `Patient` objects directly:

```python
entry = (-severity, -wait_time, sequence_number, patient)
heapq.heappush(self._heap, entry)
```

The `sequence_number` is a monotonically increasing integer that breaks ties
when both severity and wait_time are equal, ensuring deterministic ordering.

#### Sort order

| Priority | Rule |
|---|---|
| 1st (primary) | **Severity descending** — severity 10 before severity 1 |
| 2nd (secondary) | **Wait time descending** — longer-waiting patients go first |
| 3rd (tie-breaker) | **Insertion order** — earlier-inserted patients go first |

#### Rebuild after each tick

Because `wait_time` changes every tick, the heap becomes stale.
`rebuild()` is called once per tick after incrementing wait times:

```python
def rebuild(self) -> None:
    live = [p for (*_, p) in self._heap
            if p.state == PatientState.WAITING_IN_QUEUE]
    self._heap = []
    self._seq  = 0
    for patient in live:
        self.push(patient)   # re-inserts with updated priority keys
```

---

### 5.3 The Greedy Allocation Algorithm

**File:** `src/simulation_manager.py` — `_greedy_allocate()`

This is the core routing algorithm. It runs once per tick after the queue is rebuilt.

#### Step-by-step breakdown

```python
def _greedy_allocate(self) -> None:
    waiting        = self._queue.all_waiting()   # sorted list, highest priority first
    full_this_tick = set()                        # room types confirmed full this tick

    for patient in waiting:
        tx = patient.required_treatment           # e.g. 'MRI', 'Ward', 'Surgery'

        # Optimisation: skip if we already know this room type is full
        if tx in full_this_tick:
            continue

        room = self._rooms.get(tx)
        if room is None:
            continue   # unknown treatment type — skip gracefully

        if room.is_available:
            # ── ALLOCATE ──────────────────────────────────────────────
            patient.allocate(room)               # state → IN_TRANSIT, room slot locked
            self._grid.release_tile(patient.grid_pos)   # free spawn tile
            patient.grid_pos = self._grid.claim_zone_tile(tx)  # move to room zone
        else:
            # ── ROOM FULL — do NOT block ──────────────────────────────
            full_this_tick.add(tx)
            # Continue to next patient — a Ward patient is not blocked
            # just because the MRI is full
```

#### The non-blocking guarantee

The `full_this_tick` set is the key to non-blocking behaviour.
When a room type is found to be full, it is recorded in the set.
**All subsequent patients needing that same room type are skipped,
but patients needing a different room type are still processed.**

Example scenario:
```
Queue (sorted): [Patient A: MRI, Patient B: MRI, Patient C: Ward, Patient D: Surgery]
MRI capacity: 2/2 (full)
Ward capacity: 3/19 (available)
Surgery capacity: 0/6 (available)

Tick result:
  Patient A → MRI full → add 'MRI' to full_this_tick
  Patient B → MRI in full_this_tick → skip
  Patient C → Ward available → ALLOCATE ✓
  Patient D → Surgery available → ALLOCATE ✓
```

Without this design, Patient C and D would be stuck behind the full MRI queue.

#### Room capacity source

Room capacities come directly from `SimulationState`, which was populated by
`calculate_resources(ENTITY_MAP)` at startup:

```python
self._rooms = {
    'Ward':    Room('Ward',    state.beds),            # count of 'E' in ENTITY_MAP
    'MRI':     Room('MRI',     state.mris),            # count of 'M'
    'ICU':     Room('ICU',     state.icus),            # count of 'O'
    'Surgery': Room('Surgery', state.operating_rooms), # count of 'L'
}
```

---

## 6. Algorithmic-Visual Linkage

### 6.1 State-Based Teleportation

The simulation engine is **headless** — it has no knowledge of Pygame, pixels, or
screen coordinates. It operates purely on logical `Patient` objects and `Room` objects.

The visual layer is **driven by state**: the render loop reads each patient's `grid_pos`
attribute and blits a sprite at the corresponding isometric screen position.

When the algorithm changes a patient's state, it also updates `grid_pos`.
This is the bridge between the two worlds.

#### The full lifecycle of a patient's visual position

```
1. START SIM clicked
   → SimulationState.generate_patients() creates raw dicts
   → SimulationManager.load_patients() converts them to Patient objects
   → GridIndex.claim_spawn_tile() returns a free (row, col) in zone 2 or 3
   → patient.grid_pos = (25, 8)   ← patient appears in the Entrance/Waiting area

2. Tick N — patient reaches top of queue, room is available
   → _greedy_allocate() calls patient.allocate(room)
   → GridIndex.release_tile(patient.grid_pos)   ← free the spawn tile
   → patient.grid_pos = GridIndex.claim_zone_tile('MRI')
   → patient.grid_pos = (5, 19)   ← patient teleports to the MRI zone

3. Tick N+15 — MRI treatment complete (duration = 15 ticks)
   → _tick_treatments() calls patient.discharge()
   → GridIndex.release_tile(patient.grid_pos)   ← free the MRI tile
   → patient.grid_pos = None   ← patient disappears from the map
   → patient.state = DISCHARGED
```

#### The render pass (in `main.py`)

```python
for patient in sim_manager.get_visible_patients():
    row, col = patient.grid_pos
    raw_x, raw_y = IsometricConverter.grid_to_screen(row, col, 0, 0)
    iso_x = int(raw_x * zoom_level) + cam_x
    iso_y = int(raw_y * zoom_level) + cam_y
    # Bottom-center anchor
    blit_x = iso_x + int(half_tile_w) - zoomed_w // 2
    blit_y = iso_y - zoomed_h + int(half_tile_h * 2)
    screen.blit(patient_sprite_z, (blit_x, blit_y))
```

`get_visible_patients()` returns only patients in `WAITING_IN_QUEUE`,
`IN_TRANSIT`, or `IN_TREATMENT` states that have a non-`None` `grid_pos`.
`DISCHARGED` and `DECEASED` patients have `grid_pos = None` and are invisible.

#### GridIndex — the spatial occupancy manager

**File:** `src/grid_index.py`

`GridIndex` maintains a **hash set of occupied tiles** and pre-built **zone pools**:

```python
# At construction: scan FLOOR_MAP and ENTITY_MAP
# Build zone_pools[zone_id] = [(row, col), ...]
# Only include cells with no static furniture in ENTITY_MAP

# claim_spawn_tile(): iterate zone 2 then zone 3, return first unoccupied tile
# claim_zone_tile(treatment): look up TREATMENT_ZONE[treatment], return first free tile
# release_tile(pos): remove pos from self._occupied
```

The treatment-to-zone mapping:

```python
TREATMENT_ZONE = {
    'Ward':    4,   # mint green zone
    'ICU':     5,   # pink zone
    'MRI':     7,   # lavender zone
    'Surgery': 8,   # white zone
}
```

This ensures patients always teleport to a tile that is:
- Inside the correct department zone
- Not occupied by static furniture
- Not already occupied by another patient

---

## 7. File Reference

| File | Purpose |
|---|---|
| `src/settings.py` | Global constants (screen size, FPS, tile dimensions) |
| `src/isometric_converter.py` | Cartesian → isometric coordinate math |
| `src/y_sorter.py` | Painter's algorithm depth sort |
| `src/entity.py` | Base entity class (row, col, depth, sprite_path) |
| `src/map_parser.py` | `AnchoredEntity`, `MapParser`, `create_hospital_entities()` |
| `src/map_data.py` | `FLOOR_MAP`, `ENTITY_MAP`, `MAP_LEGEND`, `calculate_resources()` |
| `src/resource_manager.py` | Asset loading, `CUSTOM_SCALES`, proportional scaling |
| `src/rendering_engine.py` | Main render loop with zoom, anchor math, Y-sort |
| `src/camera.py` | Camera offset state (`camera_x`, `camera_y`) |
| `src/patient.py` | `Patient` class, `PatientState` enum, treatment durations |
| `src/room.py` | `Room` class — capacity, occupancy, admit/discharge |
| `src/patient_queue.py` | `PatientQueue` — heapq-backed max-priority queue |
| `src/grid_index.py` | `GridIndex` — spatial tile occupancy manager |
| `src/simulation_manager.py` | `SimulationManager` — 7-step tick engine |
| `src/simulation_state.py` | `SimulationState` — all HUD data, patient generation |
| `src/dashboard_ui.py` | `DashboardUI`, `ResourceHUD` — glass-morphism HUD panels |
| `src/main.py` | Entry point — Pygame init, game loop, event handling, draw calls |

---

*Content was written from direct analysis of the project source code.*
