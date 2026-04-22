# Phase 6 & 7: Architecture Realignment & Algorithmic Integration

Based on a deep analysis of your current codebase and the provided screenshot, there is a discrepancy between the text of the "Handoff Document" and the actual state of the code. **The UI is still utilizing the thick side panels, walls are thick (1.0 width), and the HTML labels are misaligned from the 3D projection.**

This plan will bridge the gap by completely executing the UI overhaul, fixing the 3D visual discrepancies, and successfully anchoring the CS algorithmic data into genuine 3D geometries!

## Current State Analysis (The Truth)
1. **The HUD is still bulky**: You still have the left and right `aside` panels (as seen in the screenshot).
2. **HTML Mismatches**: The "Triage, MRI, etc." labels are currently rendering in 2D HTML absolute space, causing them to drift far away from the respective 3D rooms when projected horizontally in R3F.
3. **The Logic Loop IS active**: The Priority Queue and Tick Loop actually already exist natively inside `page.tsx`, but they remain hooked directly into the legacy 2D `<PatientSprite />` which floats uselessly over the screen.

## Proposed Strategy

---

### Step 1: The Glass-Morphism HUD Rewrite (`page.tsx`)
- Completely delete the `w-[360px]` side panels.
- Build the `fixed bottom-0 w-full h-[120px] backdrop-blur-md bg-slate-900/80` dashboard spanning the full width. 
- Map our native variables (`patients`, `beds`, `Start Sim` button) tightly into the Left "Grid Admin" block.
- Create native `totalSurgeries` and `totalMris` React hooks to permanently track executed actions from the game loop, and map them into the Right "Live Metrics" block.

### Step 2: 3D Visualization Fixes (`HospitalScene3D.tsx`)
- **Thin Walls**: Refactor the inner wall `<boxGeometry>` arrays from depth arrays simulating "thin architectural blueprint" lines (e.g. `[1.0, height, 1.0]` to `[isWall ? 0.2 : 1, height, isWall ? 0.2 : 1]`).
- **Drei HTML Labels**: Strip the HTML text overlays from `page.tsx` entirely! Render `@react-three/drei`'s `<Html>` tags tightly bound inside the `<mesh>` loops of `HospitalScene3D.tsx` so text scales cleanly and anchors physically to the correct coordinates.

### Step 3: 3D Algorithmic Reconnection (The Meeple System)
- Pass our active `waitingQueue` and `treatingPatients` state arrays natively from `page.tsx` downwards as props into `<HospitalScene3D />`.
- Build a new inner `<PatientMeeple />` component (A stylized 3D Cylinder geometry colored via Severity arrays).
- Mount the tokens functionally inside the scene dynamically grabbing exact absolute `x/z` target positions depending on their tracked `currentZone`. (We will use `@react-spring/three` for clean translation animation in a subsequent update, but default to absolute 3D positioning immediately).

## Open Questions
1. **Grid Expansion:** Do you want me to expand the hardcoded matrix to `40x40` adding the Pharmacy and Laboratory immediately inside this rewrite, or should we keep the current `24x16` grid and just nail the UI and 3D Meeples first?
2. **3D Movement Animations:** The `@react-spring/three` library is phenomenal for interpolating `[x,y,z]` token movements. May I install this during implementation to give the Meeples that classic board-game "hopping" aesthetic?
