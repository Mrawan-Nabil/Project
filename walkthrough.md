# Phase 5: R3F Migration

We have migrated out of traditional DOM rendering and elevated the architectural layout physically into 3-Dimensional Real-Time Graphics via a strict Isometric projection.

## What We Built

### 1. Engine Dependencies
Configured the repository utilizing core 3D standards rendering inside the NextJS environment:
- `@react-three/fiber`
- `@react-three/drei`
- `three`

### 2. Scene Rendering (`HospitalScene3D.tsx`)
Bootstrapped the native visual engine hook targeting a pure `2.5D Classic Matrix Perspective` utilizing native Drei implementations:
1. **Camera Constraints**: Mounted the `OrthographicCamera`, applying `max/minZoom` locks while programmatically assigning deterministic tracking bounds targeting `[0,0,0]` allowing perfect 2-axis translation arrays typical of builder games.
2. **Lighting**: Set down global `ambientLight` providing basal environment maps, supplemented heavily by designated `directionalLight` enabling native depth processing (`castShadow`, `receiveShadow`) over the geometric bounds simulating physical light occlusion from overarching walls to floor grids!

### 3. Rendering The Geometric Matrix
Mapped the pre-existing 2D `FLOORPLAN` architecture strictly into ThreeJS primitives!
- Converted dynamic Tailwind CSS styling constraints directly over to mapped Hex strings targeting corresponding `meshStandardMaterial` components.
- Evaluated bounds mathematically, raising "Walls" (Tile 1) vertically up through `z/y` parameters to visually intercept structural corridors whilst rendering standard "Room" tiles flattened down.
- Assigned the entire architectural payload natively centered around the origin `[0,0,0]` balancing the scale naturally avoiding unbounded offset bleeding!

### 4. DOM Integration 
Cleared the heavy CSS/Flex structural layout from `page.tsx` replacing it cleanly with `<HospitalScene3D />`. The prior floating HTML overlay panels still natively hover seamlessly utilizing `absolute z-leveling` bounds over the WebGL Context cleanly integrating React State processing natively separated from the Visual Buffer Context seamlessly bridging native React data flows and strict 3D frame rendering.
