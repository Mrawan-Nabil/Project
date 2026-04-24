# Tasks

## Task List

- [x] 1. Blueprint-Style Thin Walls
  - [x] 1.1 Change wall boxGeometry args to [0.15, height, 0.15] in HospitalScene3D
  - [x] 1.2 Verify floor tile geometry remains [1, height, 1]
  - [x] 1.3 Confirm void tiles (value 0) still return null and produce no mesh

- [x] 2. Expanded Hospital Floorplan
  - [x] 2.1 Replace FLOORPLAN constant with a 32×22 matrix retaining tiles 3–7 and adding tiles 8 (Pharmacy) and 9 (Laboratory)
  - [x] 2.2 Add color cases for tile 8 (#fde68a) and tile 9 (#c7d2fe) in getTileColor
  - [x] 2.3 Update HOSPITAL_ZONES in page.tsx to add Pharmacy and Laboratory entries with valid coordinates from the new grid

- [x] 3. Isometric Camera with OrbitControls
  - [x] 3.1 Update OrthographicCamera props: position=[20,20,20], zoom=28, makeDefault, onUpdate calls lookAt(0,0,0)
  - [x] 3.2 Add OrbitControls from @react-three/drei inside Canvas with minZoom=10, maxZoom=80, maxPolarAngle=Math.PI/2.2
  - [x] 3.3 Confirm ambientLight and directionalLight props are unchanged
