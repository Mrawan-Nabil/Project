# Design Document

## Overview

This document describes the technical design for the hospital scene visual overhaul. The changes are confined to two files: `src/components/HospitalScene3D.tsx` (the R3F scene) and `src/app/page.tsx` (the host page that owns `HOSPITAL_ZONES`). No new files are introduced.

The three goals are independent and can be implemented in sequence:

1. **Blueprint walls** — change `boxGeometry` args for wall tiles from `[1, h, 1]` to `[0.15, h, 0.15]`
2. **Expanded floorplan** — replace the 24×16 `FLOORPLAN` matrix with a 32×22 one that adds Pharmacy (tile 8) and Laboratory (tile 9)
3. **Isometric camera** — replace the ad-hoc `OrthographicCamera` setup with a properly configured one at `[20,20,20]` zoom 28, plus `OrbitControls` with zoom and polar-angle constraints

---

## Architecture

The feature is entirely client-side and lives within the existing Next.js App Router project. No server components, API routes, or data-fetching changes are involved.

```
src/app/page.tsx
  └─ HOSPITAL_ZONES (updated: adds Pharmacy, Laboratory entries)
  └─ <HospitalScene3D />

src/components/HospitalScene3D.tsx
  └─ FLOORPLAN (updated: 32×22, tiles 8 & 9 added)
  └─ getTileColor (updated: cases for 8 & 9)
  └─ <Canvas>
       ├─ <OrthographicCamera makeDefault position=[20,20,20] zoom=28 />
       ├─ <OrbitControls minZoom=10 maxZoom=80 maxPolarAngle=PI/2.2 />
       ├─ <ambientLight />
       ├─ <directionalLight />
       └─ <group> (tile meshes) </group>
```

---

## Components and Interfaces

### `FLOORPLAN` (exported constant, `HospitalScene3D.tsx`)

A 2D `number[][]` matrix. Tile value semantics:

| Value | Meaning        | Geometry         |
|-------|----------------|------------------|
| 0     | Void           | not rendered     |
| 1     | Wall           | box 0.15 × h × 0.15 |
| 2     | Corridor       | box 1 × 0.05 × 1 |
| 3     | Triage         | box 1 × 0.05 × 1 |
| 4     | MRI            | box 1 × 0.05 × 1 |
| 5     | Ward           | box 1 × 0.05 × 1 |
| 6     | ICU            | box 1 × 0.05 × 1 |
| 7     | Operating Room | box 1 × 0.05 × 1 |
| 8     | Pharmacy       | box 1 × 0.05 × 1 |
| 9     | Laboratory     | box 1 × 0.05 × 1 |

### `getTileColor(val, r, c)` (pure function, `HospitalScene3D.tsx`)

Returns a hex color string for a given tile value. Extended with:
- `8` → `#fde68a` (amber, Pharmacy)
- `9` → `#c7d2fe` (indigo, Laboratory)

Both colors are visually distinct from all existing tile colors.

### `HospitalScene3D` (default export, `HospitalScene3D.tsx`)

R3F `<Canvas>` component. Key changes:
- `OrthographicCamera` props: `position={[20, 20, 20]}`, `zoom={28}`, `makeDefault`, `onUpdate={(self) => self.lookAt(0, 0, 0)}`
- `OrbitControls` from `@react-three/drei`: `minZoom={10}`, `maxZoom={80}`, `maxPolarAngle={Math.PI / 2.2}`
- Wall mesh geometry: `<boxGeometry args={[0.15, height, 0.15]} />`
- Floor mesh geometry: `<boxGeometry args={[1, height, 1]} />` (unchanged)
- `offsetX` / `offsetZ` derived from `FLOORPLAN[0].length` and `FLOORPLAN.length` (already dynamic — no code change needed beyond updating the matrix)

### `HOSPITAL_ZONES` (`page.tsx`)

Record mapping zone names to `{ r, c }` grid coordinates. New entries added:
- `Pharmacy`: coordinates pointing to a valid Pharmacy tile in the new grid
- `Laboratory`: coordinates pointing to a valid Laboratory tile in the new grid

---

## Data Models

### Expanded FLOORPLAN layout (32 columns × 22 rows)

The new layout preserves the existing five rooms in the upper portion and adds Pharmacy and Laboratory rooms in a new lower wing. Corridor rows connect all rooms.

```
Row  0: void border
Row  1: top wall of upper wing (Triage left, MRI right)
Rows 2–4: Triage (col 2–6) | void gap | MRI (col 16–20)
Row  5: bottom wall of upper wing with door gaps
Rows 6–8: main corridor (full width)
Row  9: top wall of middle wing (Ward, ICU, Ops Room)
Rows 10–12: Ward (col 2–6) | ICU (col 9–13) | Ops Room (col 16–20)
Row 13: bottom wall of middle wing
Rows 14–15: lower corridor (full width)
Row 16: top wall of lower wing (Pharmacy left, Laboratory right)
Rows 17–19: Pharmacy (col 2–8) | Laboratory (col 12–20)
Row 20: bottom wall of lower wing
Row 21: void border
```

Columns 0 and 31 are void borders. The grid is 32 wide × 22 tall.

### Centering

```ts
const rows = FLOORPLAN.length;        // 22
const cols = FLOORPLAN[0].length;     // 32
const offsetX = cols / 2;             // 16
const offsetZ = rows / 2;             // 11
```

Mesh position: `x = c - offsetX`, `z = r - offsetZ`. This keeps the map centred at world origin `[0, 0, 0]`.

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Wall tile geometry dimensions

*For any* FLOORPLAN cell with value `1`, the rendered `boxGeometry` args must have X dimension `0.15` and Z dimension `0.15`.

**Validates: Requirements 1.1**

### Property 2: Floor tile geometry dimensions

*For any* FLOORPLAN cell with a non-wall, non-void value (2–9), the rendered `boxGeometry` args must have X dimension `1.0` and Z dimension `1.0`.

**Validates: Requirements 1.2**

### Property 3: Tile mesh centering

*For any* FLOORPLAN of dimensions R×C, and any rendered tile at row `r`, column `c`, the mesh's world-space X position must equal `c - C/2` and Z position must equal `r - R/2`.

**Validates: Requirements 1.3, 2.5**

### Property 4: Void tiles produce no geometry

*For any* FLOORPLAN, no mesh is rendered at a position corresponding to a cell with value `0`.

**Validates: Requirements 1.4**

### Property 5: Color mapping completeness and distinctness

*For any* tile value `v` in `{1, 2, 3, 4, 5, 6, 7, 8, 9}`, `getTileColor(v, r, c)` returns a non-empty string, and `getTileColor(8, r, c)` differs from `getTileColor(9, r, c)` and from `getTileColor(v, r, c)` for all `v` in `{1, 3, 4, 5, 6, 7}`.

**Validates: Requirements 1.5, 2.6**

---

## Error Handling

| Scenario | Handling |
|---|---|
| FLOORPLAN row with inconsistent column count | `offsetX` is derived from `FLOORPLAN[0].length`; jagged rows will misalign but not crash. All rows must be the same length. |
| `OrbitControls` zoom below `minZoom` or above `maxZoom` | Clamped automatically by Three.js `OrbitControls` — no custom handler needed. |
| `maxPolarAngle` exceeded | Clamped automatically by `OrbitControls`. |
| Unknown tile value in `getTileColor` | Falls through to the default `return "#dcfce7"` (grass green) — safe fallback. |
| `HOSPITAL_ZONES` entry references out-of-bounds coordinates | `PatientSprite` returns `null` when `coords` is undefined — already handled in `page.tsx`. |

---

## Testing Strategy

PBT is applicable here: `getTileColor` is a pure function, and the geometry/centering logic is deterministic pure computation over the FLOORPLAN matrix. These are ideal candidates for property-based testing.

**Library**: [fast-check](https://fast-check.io/) — works with Jest/Vitest, TypeScript-native, no extra setup.

### Unit tests (example-based)

- FLOORPLAN dimensions: assert `FLOORPLAN.length >= 22` and `FLOORPLAN[0].length >= 32`
- Tile presence: assert values 3–9 each appear at least once in the matrix
- Pharmacy adjacency: assert at least one tile-8 cell is adjacent to a corridor tile (value 2)
- Laboratory adjacency: assert at least one tile-9 cell is adjacent to a corridor tile (value 2)
- `HOSPITAL_ZONES` keys: assert `"Pharmacy"` and `"Laboratory"` keys exist with in-bounds coordinates
- Camera props: assert `OrthographicCamera` receives `position={[20,20,20]}`, `zoom={28}`, `makeDefault`
- OrbitControls props: assert `minZoom={10}`, `maxZoom={80}`, `maxPolarAngle={Math.PI / 2.2}`

### Property-based tests (fast-check, minimum 100 iterations each)

Each test is tagged with the property it validates.

**Feature: hospital-scene-visual-overhaul, Property 1: Wall tile geometry dimensions**
- Generator: arbitrary FLOORPLAN-like matrix with some cells set to `1`
- Assertion: for every wall cell, the geometry args satisfy `args[0] === 0.15 && args[2] === 0.15`

**Feature: hospital-scene-visual-overhaul, Property 2: Floor tile geometry dimensions**
- Generator: arbitrary FLOORPLAN-like matrix with cells in range 2–9
- Assertion: for every floor cell, the geometry args satisfy `args[0] === 1.0 && args[2] === 1.0`

**Feature: hospital-scene-visual-overhaul, Property 3: Tile mesh centering**
- Generator: arbitrary (rows, cols) dimensions and (r, c) tile positions
- Assertion: mesh x === `c - cols/2`, mesh z === `r - rows/2`

**Feature: hospital-scene-visual-overhaul, Property 4: Void tiles produce no geometry**
- Generator: arbitrary FLOORPLAN with some void cells
- Assertion: no mesh exists at void cell positions

**Feature: hospital-scene-visual-overhaul, Property 5: Color mapping completeness and distinctness**
- Generator: arbitrary tile values in `{1..9}` and arbitrary `(r, c)` pairs
- Assertion: `getTileColor(v, r, c)` is a non-empty string; `getTileColor(8, ...)` !== `getTileColor(9, ...)`; `getTileColor(8, ...)` !== `getTileColor(v, ...)` for v in `{1,3,4,5,6,7}`
