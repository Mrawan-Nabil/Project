# Hospital Scene Visual Overhaul — Implementation Plan

## Project Overview

**Goal:** Visual overhaul of the 3D hospital simulation scene in `HospitalScene3D.tsx`.  
**Scope:** Two files only — `src/components/HospitalScene3D.tsx` and `src/app/page.tsx`.  
**Stack:** Next.js (App Router), React, TypeScript, React Three Fiber, @react-three/drei, Tailwind CSS.

---

## The Three Goals

| # | Goal | Files Affected |
|---|------|----------------|
| 1 | Blueprint-style thin walls (0.15 units) | `HospitalScene3D.tsx` |
| 2 | Expanded floorplan 32×22 + Pharmacy & Laboratory rooms | `HospitalScene3D.tsx`, `page.tsx` |
| 3 | Isometric OrthographicCamera + OrbitControls | `HospitalScene3D.tsx` |

---

## Task Breakdown

### Task 1 — Blueprint-Style Thin Walls

Change wall geometry from thick voxels `[1, h, 1]` to thin blueprint lines `[0.15, h, 0.15]`.

- **1.1** In `HospitalScene3D.tsx`, find the wall tile render branch and change `boxGeometry args` to `[0.15, height, 0.15]`.
- **1.2** Verify floor tile geometry stays at `[1, height, 1]` — no change needed there.
- **1.3** Confirm void tiles (value `0`) still return `null` and produce no mesh.

**Expected result:** Walls look like thin architectural blueprint lines. Rooms become clearly legible.

---

### Task 2 — Expanded Hospital Floorplan

Replace the current 24×16 `FLOORPLAN` matrix with a new 32×22 matrix that adds two new rooms.

- **2.1** Replace the `FLOORPLAN` constant with a 32×22 matrix. Keep existing tiles 3–7 (Triage, MRI, Ward, ICU, OR). Add tile `8` (Pharmacy) and tile `9` (Laboratory) in a new lower wing.
- **2.2** In `getTileColor`, add color cases:
  - Tile `8` (Pharmacy) → `#fde68a` (amber)
  - Tile `9` (Laboratory) → `#c7d2fe` (indigo)
- **2.3** In `page.tsx`, update `HOSPITAL_ZONES` to add `Pharmacy` and `Laboratory` entries with valid `{ r, c }` coordinates from the new grid.

**New floorplan layout:**
```
Row  0      : void border
Row  1      : top wall — upper wing
Rows 2–4    : Triage (cols 2–6)  |  MRI (cols 16–20)
Row  5      : bottom wall — upper wing (with door gaps)
Rows 6–8    : main corridor (full width)
Row  9      : top wall — middle wing
Rows 10–12  : Ward (cols 2–6)  |  ICU (cols 9–13)  |  OR (cols 16–20)
Row 13      : bottom wall — middle wing
Rows 14–15  : lower corridor (full width)
Row 16      : top wall — lower wing
Rows 17–19  : Pharmacy (cols 2–8)  |  Laboratory (cols 12–20)
Row 20      : bottom wall — lower wing
Row 21      : void border
Cols 0, 31  : void borders
```

**Centering math (already dynamic — no extra code needed):**
```ts
const offsetX = FLOORPLAN[0].length / 2;  // 16
const offsetZ = FLOORPLAN.length / 2;     // 11
// mesh position: x = c - offsetX,  z = r - offsetZ
```

---

### Task 3 — Isometric Camera with OrbitControls

Replace the ad-hoc camera setup with a mathematically correct isometric projection.

- **3.1** Update `OrthographicCamera` props inside `<Canvas>`:
  ```tsx
  <OrthographicCamera
    makeDefault
    position={[20, 20, 20]}
    zoom={28}
    onUpdate={(self) => self.lookAt(0, 0, 0)}
  />
  ```
- **3.2** Add `OrbitControls` from `@react-three/drei` inside `<Canvas>`:
  ```tsx
  <OrbitControls
    minZoom={10}
    maxZoom={80}
    maxPolarAngle={Math.PI / 2.2}
  />
  ```
- **3.3** Leave `ambientLight` and `directionalLight` props completely unchanged.

**Camera behavior:**
- Position `[20, 20, 20]` → standard 45° isometric angle on all three axes
- `zoom={28}` → fits the full 32×22 grid at 1920×1080
- `minZoom=10 / maxZoom=80` → prevents clipping or zooming out too far
- `maxPolarAngle=PI/2.2` → camera cannot rotate below the floor plane
- Scroll wheel → zoom, left-drag → rotate, right/middle-drag → pan

---

## Tile Reference Table

| Value | Room | Color | Geometry |
|-------|------|-------|----------|
| 0 | Void | — | Not rendered |
| 1 | Wall | `#475569` | `0.15 × h × 0.15` |
| 2 | Corridor | checker | `1 × 0.05 × 1` |
| 3 | Triage | blue | `1 × 0.05 × 1` |
| 4 | MRI | purple | `1 × 0.05 × 1` |
| 5 | Ward | green | `1 × 0.05 × 1` |
| 6 | ICU | red | `1 × 0.05 × 1` |
| 7 | Operating Room | orange | `1 × 0.05 × 1` |
| 8 | Pharmacy *(new)* | `#fde68a` amber | `1 × 0.05 × 1` |
| 9 | Laboratory *(new)* | `#c7d2fe` indigo | `1 × 0.05 × 1` |

---

## Execution Order

```
Task 1 (Thin Walls)  →  Task 2 (Expanded Map)  →  Task 3 (Camera)
```

Each task is independent and can be verified visually before moving to the next.

---

## Correctness Properties

These are the formal guarantees the implementation must satisfy:

1. Every wall tile renders with X and Z geometry of exactly `0.15`.
2. Every floor tile renders with X and Z geometry of exactly `1.0`.
3. Every tile mesh is centered at `(c - cols/2, y, r - rows/2)` in world space.
4. No mesh is rendered for void tiles (value `0`).
5. `getTileColor` returns a non-empty, distinct color for every tile value 1–9.
