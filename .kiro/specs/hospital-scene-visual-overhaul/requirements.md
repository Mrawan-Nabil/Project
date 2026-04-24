# Requirements Document

## Introduction

This feature is a visual overhaul of the existing 3D hospital simulation scene rendered in `HospitalScene3D.tsx`. The overhaul has three distinct goals: (1) replace thick voxel walls with thin blueprint-style wall geometry, (2) expand the hospital floorplan grid beyond its current 24×16 bounds to include additional clinical rooms, and (3) replace the current ad-hoc camera setup with a mathematically correct isometric projection using `OrthographicCamera` and `OrbitControls` for interactive pan, zoom, and rotate.

## Glossary

- **HospitalScene3D**: The React Three Fiber component in `src/components/HospitalScene3D.tsx` that renders the 3D hospital map.
- **FLOORPLAN**: The 2D integer matrix that encodes tile types for the hospital grid.
- **Wall_Tile**: A FLOORPLAN cell with value `1`, rendered as a vertical box geometry.
- **Floor_Tile**: A FLOORPLAN cell with a non-wall, non-void value (2–9), rendered as a flat slab.
- **Void_Tile**: A FLOORPLAN cell with value `0`; not rendered.
- **OrthographicCamera**: A Three.js camera that projects the scene without perspective distortion, enabling a true isometric view.
- **OrbitControls**: The `@react-three/drei` control component that provides mouse/touch-driven pan, zoom, and rotate interactions.
- **Isometric_Projection**: A standard axonometric projection achieved by positioning the `OrthographicCamera` at equal angles along all three axes (e.g. position `[1, 1, 1]` normalised) and looking at the scene origin.
- **Blueprint_Wall**: A Wall_Tile rendered with a narrow cross-section (0.15 units wide) to mimic architectural blueprint line weight.
- **Expanded_Grid**: The new FLOORPLAN matrix with dimensions of at least 32 columns × 22 rows, replacing the current 24×16 matrix.
- **Pharmacy_Room**: A new clinical zone added to the Expanded_Grid, encoded as tile value `8`.
- **Laboratory_Room**: A new clinical zone added to the Expanded_Grid, encoded as tile value `9`.
- **Zoom_Level**: The `zoom` property of the `OrthographicCamera`, controlling how many world units fit within the viewport.
- **Page**: The Next.js page component in `src/app/page.tsx` that hosts `HospitalScene3D`.

---

## Requirements

### Requirement 1: Blueprint-Style Thin Walls

**User Story:** As a player, I want hospital walls to appear as thin lines, so that the scene reads like an architectural blueprint and rooms are clearly legible.

#### Acceptance Criteria

1. THE `HospitalScene3D` SHALL render every `Wall_Tile` using a `boxGeometry` with X and Z dimensions of `0.15` world units and a Y dimension equal to the wall height.
2. THE `HospitalScene3D` SHALL render every `Floor_Tile` using a `boxGeometry` with X and Z dimensions of `1.0` world units (full cell width).
3. WHEN the FLOORPLAN contains adjacent `Wall_Tile` cells, THE `HospitalScene3D` SHALL position each wall mesh so that its centre aligns with the cell's grid coordinate, producing continuous thin-wall lines without gaps or overlaps at corners.
4. IF a cell value is `0` (Void_Tile), THEN THE `HospitalScene3D` SHALL not render any geometry for that cell.
5. THE `HospitalScene3D` SHALL preserve the existing colour mapping for all tile types after the geometry change (wall colour `#475569`, corridor checker, room colours).

---

### Requirement 2: Expanded Hospital Floorplan

**User Story:** As a player, I want a larger hospital map with more rooms, so that the simulation feels like a real hospital with distinct clinical departments.

#### Acceptance Criteria

1. THE `FLOORPLAN` constant SHALL define a grid of at least 32 columns × 22 rows, replacing the current 24×16 matrix.
2. THE `FLOORPLAN` SHALL include a `Pharmacy_Room` zone (tile value `8`) enclosed by `Wall_Tile` cells and connected to a corridor.
3. THE `FLOORPLAN` SHALL include a `Laboratory_Room` zone (tile value `9`) enclosed by `Wall_Tile` cells and connected to a corridor.
4. THE `FLOORPLAN` SHALL retain all existing room zones: Triage (value `3`), MRI (value `4`), Ward (value `5`), ICU (value `6`), and Operating Room (value `7`).
5. THE `HospitalScene3D` SHALL update the `offsetX` and `offsetZ` centering calculations to use the new column and row counts so the expanded map remains centred at world origin `[0, 0, 0]`.
6. THE `getTileColor` function SHALL return a distinct colour for `Pharmacy_Room` tiles and a distinct colour for `Laboratory_Room` tiles, different from all existing tile colours.
7. WHEN the `FLOORPLAN` is updated, THE `Page` SHALL update the `HOSPITAL_ZONES` coordinate map to include entries for `Pharmacy` and `Laboratory` that reference valid cell positions within the new grid.

---

### Requirement 3: Isometric Camera with Interactive Controls

**User Story:** As a player, I want a proper isometric camera with pan, zoom, and rotate controls, so that I can navigate the hospital map comfortably and appreciate the 3D depth.

#### Acceptance Criteria

1. THE `HospitalScene3D` SHALL configure the `OrthographicCamera` with an initial position of `[20, 20, 20]` and a `lookAt` target of `[0, 0, 0]`, producing a standard 45° isometric angle.
2. THE `HospitalScene3D` SHALL set the initial `zoom` of the `OrthographicCamera` to a value that fits the entire `Expanded_Grid` within the viewport at a 1920×1080 reference resolution (zoom value of `28` or adjusted equivalent).
3. THE `HospitalScene3D` SHALL mount an `OrbitControls` component from `@react-three/drei` as a child of the `Canvas`, enabling mouse-drag rotation, scroll-wheel zoom, and right-click/middle-click pan.
4. WHEN `OrbitControls` is active, THE `HospitalScene3D` SHALL constrain the minimum zoom to `10` and the maximum zoom to `80` to prevent the camera from clipping through the floor or zooming out to an unusable distance.
5. WHEN `OrbitControls` is active, THE `HospitalScene3D` SHALL constrain the vertical polar angle (`maxPolarAngle`) to `Math.PI / 2.2` so the camera cannot rotate below the floor plane.
6. THE `HospitalScene3D` SHALL retain the existing `ambientLight` and `directionalLight` configuration so lighting is unaffected by the camera change.
7. WHEN the viewport is resized, THE `OrthographicCamera` SHALL update its frustum bounds so the scene does not stretch or compress.
