"use client";

import { Suspense, useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { useGLTF, OrbitControls, Environment, Text } from "@react-three/drei";
import * as THREE from "three";
import { Patient } from "@/lib/algorithms";

// ─── Preload ──────────────────────────────────────────────────────────────────
const MODELS = {
  doctor:    "/models/doctor.glb",
  nurse:     "/models/nurse.glb",
  patient:   "/models/patient.glb",
  bed:       "/models/hospital_bed.glb",
  desk:      "/models/intake_desk.glb",
  mri:       "/models/mri_scanner.glb",
  opTable:   "/models/operating_table2.glb",
  surgeon:   "/models/surgical_doctor.glb",
};
Object.values(MODELS).forEach(u => useGLTF.preload(u));

const SCALES: Record<string, number> = {
  [MODELS.doctor]:  0.0028,
  [MODELS.nurse]:   0.9,
  [MODELS.patient]: 0.00014,
  [MODELS.bed]:     0.018,
  [MODELS.desk]:    0.55,
  [MODELS.mri]:     1.4,
  [MODELS.opTable]: 0.38,
  [MODELS.surgeon]: 0.0085,
};

function Model({ url, position, rotation = [0, 0, 0] }: {
  url: string; position: [number, number, number]; rotation?: [number, number, number];
}) {
  const { scene } = useGLTF(url);
  const clone = useMemo(() => {
    const c = scene.clone(true);
    c.traverse(ch => {
      if ((ch as THREE.Mesh).isMesh) {
        (ch as THREE.Mesh).castShadow = true;
        (ch as THREE.Mesh).receiveShadow = true;
      }
    });
    return c;
  }, [scene]);
  const s = SCALES[url] ?? 1;
  return <primitive object={clone} position={position} rotation={rotation} scale={[s, s, s]} />;
}

// ─── Layout constants ─────────────────────────────────────────────────────────
//
//  Map is 40 × 28 units.
//  Central corridor: X = -2 → +2  (4 units wide), full Z length
//  Left  wing: X = -20 → -2   (4 rooms stacked vertically)
//  Right wing: X =  +2 → +20  (4 rooms stacked vertically)
//  Room size: 16 wide × 6 deep, gap 1 between rooms
//
const CORRIDOR_X  = 0;    // center of corridor
const ROOM_W      = 16;   // room width (X)
const ROOM_D      = 6;    // room depth (Z)
const ROOM_GAP    = 1;    // gap between rooms
const ROOM_OFFSET = 9;    // half-width from corridor center to room center
const WALL_H      = 2.8;
const WALL_T      = 0.1;  // ultra-thin walls

// 4 rooms per side, stacked in Z
const ROOM_Z_POSITIONS = [-10.5, -3.5, 3.5, 10.5]; // centers

// Room definitions
interface RoomDef {
  id: string;
  label: string;
  side: "left" | "right";
  zIdx: number;           // 0–3
  floorLight: string;
  floorDark: string;
  wallLight: string;
  wallDark: string;
}

const ROOM_DEFS: RoomDef[] = [
  // Left side (X negative)
  { id: "Triage",     label: "📋 TRIAGE",     side: "left",  zIdx: 0, floorLight: "#dbeafe", floorDark: "#1e3a5f", wallLight: "#93c5fd", wallDark: "#1d4ed8" },
  { id: "WARD",       label: "🛏️ WARD",       side: "left",  zIdx: 1, floorLight: "#dcfce7", floorDark: "#052e16", wallLight: "#86efac", wallDark: "#166534" },
  { id: "Pharmacy",   label: "💊 PHARMACY",   side: "left",  zIdx: 2, floorLight: "#fef9c3", floorDark: "#422006", wallLight: "#fcd34d", wallDark: "#b45309" },
  { id: "Reception",  label: "🏥 RECEPTION",  side: "left",  zIdx: 3, floorLight: "#f1f5f9", floorDark: "#1e293b", wallLight: "#cbd5e1", wallDark: "#475569" },
  // Right side (X positive)
  { id: "MRI",        label: "🧲 MRI",        side: "right", zIdx: 0, floorLight: "#ede9fe", floorDark: "#2e1065", wallLight: "#c4b5fd", wallDark: "#6d28d9" },
  { id: "ICU",        label: "🩺 ICU",        side: "right", zIdx: 1, floorLight: "#fee2e2", floorDark: "#450a0a", wallLight: "#fca5a5", wallDark: "#b91c1c" },
  { id: "OPS_ROOM",   label: "🔪 OPS ROOM",   side: "right", zIdx: 2, floorLight: "#f0fdf4", floorDark: "#1a2e1a", wallLight: "#86efac", wallDark: "#15803d" },
  { id: "Laboratory", label: "🔬 LABORATORY", side: "right", zIdx: 3, floorLight: "#e0e7ff", floorDark: "#1e1b4b", wallLight: "#a5b4fc", wallDark: "#4338ca" },
];

function getRoomCenter(def: RoomDef): [number, number, number] {
  const cx = def.side === "left" ? -(ROOM_OFFSET) : ROOM_OFFSET;
  const cz = ROOM_Z_POSITIONS[def.zIdx];
  return [cx, 0, cz];
}

// Zone id → world position
const ZONE_POSITIONS: Record<string, [number, number, number]> = {};
ROOM_DEFS.forEach(r => { ZONE_POSITIONS[r.id] = getRoomCenter(r); });
ZONE_POSITIONS["DISCHARGED"] = [0, 0, 20]; // off-map

// ─── Merged floor ─────────────────────────────────────────────────────────────
function Floor({ isDark }: { isDark: boolean }) {
  const geo = useMemo(() => {
    const W = 42, D = 30, offX = -21, offZ = -15;
    const positions: number[] = [], colors: number[] = [], indices: number[] = [];
    const cA = new THREE.Color(isDark ? "#0f172a" : "#e2e8f0");
    const cB = new THREE.Color(isDark ? "#1e293b" : "#f1f5f9");
    let vi = 0;
    for (let x = 0; x < W; x++) {
      for (let z = 0; z < D; z++) {
        const c = (x + z) % 2 === 0 ? cA : cB;
        const px = offX + x, pz = offZ + z;
        positions.push(px-.5,0,pz-.5, px+.5,0,pz-.5, px+.5,0,pz+.5, px-.5,0,pz+.5);
        for (let i = 0; i < 4; i++) colors.push(c.r, c.g, c.b);
        indices.push(vi,vi+1,vi+2, vi,vi+2,vi+3);
        vi += 4;
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    g.setAttribute("color",    new THREE.Float32BufferAttribute(colors, 3));
    g.setIndex(indices);
    g.computeVertexNormals();
    return g;
  }, [isDark]);

  return (
    <mesh geometry={geo} receiveShadow>
      <meshStandardMaterial vertexColors roughness={0.9} />
    </mesh>
  );
}

// ─── Corridor strip ───────────────────────────────────────────────────────────
function Corridor({ isDark }: { isDark: boolean }) {
  return (
    <mesh position={[CORRIDOR_X, 0.01, 0]} receiveShadow>
      <boxGeometry args={[4, 0.02, 30]} />
      <meshStandardMaterial
        color={isDark ? "#1e3a5f" : "#bfdbfe"}
        roughness={0.6}
        opacity={0.85}
        transparent
      />
    </mesh>
  );
}

// ─── Single room ──────────────────────────────────────────────────────────────
function Room({ def, isDark }: { def: RoomDef; isDark: boolean }) {
  const [cx, , cz] = getRoomCenter(def);
  const floor = isDark ? def.floorDark : def.floorLight;
  const wall  = isDark ? def.wallDark  : def.wallLight;

  // Door gap: 1.2 units wide in the wall facing the corridor
  const doorW = 1.4;
  const wallFacing = ROOM_W / 2 - WALL_T / 2; // distance from center to inner wall
  const doorSide = def.side === "left" ? wallFacing : -wallFacing;

  return (
    <group position={[cx, 0, cz]}>
      {/* Floor */}
      <mesh position={[0, 0.02, 0]} receiveShadow>
        <boxGeometry args={[ROOM_W, 0.04, ROOM_D]} />
        <meshStandardMaterial color={floor} roughness={0.75} />
      </mesh>

      {/* Back wall (far from corridor) */}
      <mesh position={[def.side === "left" ? -ROOM_W/2+WALL_T/2 : ROOM_W/2-WALL_T/2, WALL_H/2, 0]} castShadow>
        <boxGeometry args={[WALL_T, WALL_H, ROOM_D]} />
        <meshStandardMaterial color={wall} roughness={0.4} />
      </mesh>

      {/* Top wall (Z-) */}
      <mesh position={[0, WALL_H/2, -ROOM_D/2+WALL_T/2]} castShadow>
        <boxGeometry args={[ROOM_W, WALL_H, WALL_T]} />
        <meshStandardMaterial color={wall} roughness={0.4} />
      </mesh>

      {/* Bottom wall (Z+) */}
      <mesh position={[0, WALL_H/2, ROOM_D/2-WALL_T/2]} castShadow>
        <boxGeometry args={[ROOM_W, WALL_H, WALL_T]} />
        <meshStandardMaterial color={wall} roughness={0.4} />
      </mesh>

      {/* Corridor-facing wall — split into 2 segments with door gap */}
      <mesh position={[doorSide, WALL_H/2, -(doorW/2 + (ROOM_D/2 - doorW)/2)]} castShadow>
        <boxGeometry args={[WALL_T, WALL_H, ROOM_D/2 - doorW/2]} />
        <meshStandardMaterial color={wall} roughness={0.4} />
      </mesh>
      <mesh position={[doorSide, WALL_H/2, (doorW/2 + (ROOM_D/2 - doorW)/2)]} castShadow>
        <boxGeometry args={[WALL_T, WALL_H, ROOM_D/2 - doorW/2]} />
        <meshStandardMaterial color={wall} roughness={0.4} />
      </mesh>
      {/* Door lintel */}
      <mesh position={[doorSide, WALL_H - 0.3, 0]} castShadow>
        <boxGeometry args={[WALL_T, 0.6, doorW]} />
        <meshStandardMaterial color={wall} roughness={0.4} />
      </mesh>

      {/* Room label */}
      <Text
        position={[def.side === "left" ? 2 : -2, WALL_H + 0.5, 0]}
        fontSize={0.42}
        fontWeight="bold"
        color={isDark ? "#ffffff" : "#1e293b"}
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.05}
        outlineColor={wall}
        maxWidth={8}
      >
        {def.label}
      </Text>
    </group>
  );
}

// ─── Furniture per room ───────────────────────────────────────────────────────
function RoomFurniture({ isDark }: { isDark: boolean }) {
  return (
    <Suspense fallback={null}>
      {/* Triage — left, zIdx 0 → center [-9, 0, -10.5] */}
      <Model url={MODELS.desk}   position={[-14, 0.05, -11.5]} rotation={[0, Math.PI*0.5, 0]} />
      <Model url={MODELS.nurse}  position={[-11, 0.05, -10]}   rotation={[0, Math.PI*0.3, 0]} />

      {/* Ward — left, zIdx 1 → center [-9, 0, -3.5] */}
      <Model url={MODELS.bed}    position={[-14, 0.05, -4.5]}  rotation={[0, 0, 0]} />
      <Model url={MODELS.bed}    position={[-14, 0.05, -2.5]}  rotation={[0, 0, 0]} />
      <Model url={MODELS.bed}    position={[-11, 0.05, -4.5]}  rotation={[0, 0, 0]} />
      <Model url={MODELS.nurse}  position={[-9,  0.05, -3]}    rotation={[0, Math.PI, 0]} />

      {/* Pharmacy — left, zIdx 2 → center [-9, 0, 3.5] */}
      <Model url={MODELS.desk}   position={[-14, 0.05,  2.5]}  rotation={[0, Math.PI*0.5, 0]} />
      <Model url={MODELS.nurse}  position={[-11, 0.05,  3.5]}  rotation={[0, Math.PI*1.5, 0]} />

      {/* Reception — left, zIdx 3 → center [-9, 0, 10.5] */}
      <Model url={MODELS.desk}   position={[-14, 0.05,  9.5]}  rotation={[0, Math.PI*0.5, 0]} />
      <Model url={MODELS.doctor} position={[-11, 0.05, 10.5]}  rotation={[0, Math.PI*0.8, 0]} />

      {/* MRI — right, zIdx 0 → center [9, 0, -10.5] */}
      <Model url={MODELS.mri}    position={[9,   0.05, -10.5]} rotation={[0, Math.PI*0.5, 0]} />
      <Model url={MODELS.nurse}  position={[13,  0.05, -10]}   rotation={[0, Math.PI, 0]} />

      {/* ICU — right, zIdx 1 → center [9, 0, -3.5] */}
      <Model url={MODELS.bed}    position={[7,   0.05, -4.5]}  rotation={[0, 0, 0]} />
      <Model url={MODELS.bed}    position={[7,   0.05, -2.5]}  rotation={[0, 0, 0]} />
      <Model url={MODELS.bed}    position={[10,  0.05, -4.5]}  rotation={[0, 0, 0]} />
      <Model url={MODELS.doctor} position={[13,  0.05, -3.5]}  rotation={[0, Math.PI*1.7, 0]} />

      {/* OPS Room — right, zIdx 2 → center [9, 0, 3.5] */}
      <Model url={MODELS.opTable}  position={[9,   0.05,  3.5]}  rotation={[0, Math.PI*0.5, 0]} />
      <Model url={MODELS.surgeon}  position={[7.5, 0.05,  3]}    rotation={[0, Math.PI*0.3, 0]} />
      <Model url={MODELS.surgeon}  position={[10.5,0.05,  4]}    rotation={[0, Math.PI*1.7, 0]} />

      {/* Laboratory — right, zIdx 3 → center [9, 0, 10.5] */}
      <Model url={MODELS.desk}   position={[7,   0.05,  9.5]}  rotation={[0, Math.PI*1.5, 0]} />
      <Model url={MODELS.nurse}  position={[11,  0.05, 10.5]}  rotation={[0, Math.PI*0.5, 0]} />

      {/* Corridor staff */}
      <Model url={MODELS.doctor} position={[0, 0.05, -7]}  rotation={[0, Math.PI*0.5, 0]} />
      <Model url={MODELS.nurse}  position={[0, 0.05,  0]}  rotation={[0, Math.PI*1.2, 0]} />
      <Model url={MODELS.doctor} position={[0, 0.05,  7]}  rotation={[0, Math.PI*1.8, 0]} />
    </Suspense>
  );
}

// ─── Patient meeple ───────────────────────────────────────────────────────────
function Meeple({ patient }: { patient: Patient }) {
  const ref    = useRef<THREE.Group>(null);
  const target = useMemo(() => {
    const base = ZONE_POSITIONS[patient.currentZone] ?? [0, 0, 0];
    let h = 0;
    for (let i = 0; i < patient.id.length; i++) h = patient.id.charCodeAt(i) + ((h << 5) - h);
    // Scatter within room bounds (stay inside room)
    const maxScatter = 2.5;
    const ox = ((Math.abs(h)       % 200) / 200 - 0.5) * maxScatter * 2;
    const oz = ((Math.abs(h >> 8)  % 200) / 200 - 0.5) * maxScatter;
    return new THREE.Vector3(base[0] + ox, 0, base[2] + oz);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patient.currentZone, patient.id]);

  const pos = useRef(target.clone());

  useFrame(() => {
    if (!ref.current) return;
    pos.current.lerp(target, 0.06);
    ref.current.position.set(
      pos.current.x,
      0.25 + Math.sin(Date.now() * 0.003 + target.x) * 0.04,
      pos.current.z
    );
  });

  const color =
    patient.severity >= 8 ? "#ef4444" :
    patient.severity >= 4 ? "#f97316" : "#22c55e";

  return (
    <group ref={ref} position={[target.x, 0.25, target.z]}>
      {/* Body cylinder */}
      <mesh castShadow>
        <cylinderGeometry args={[0.18, 0.22, 0.5, 10]} />
        <meshStandardMaterial color={color} roughness={0.4} emissive={color} emissiveIntensity={0.25} />
      </mesh>
      {/* Head */}
      <mesh position={[0, 0.38, 0]} castShadow>
        <sphereGeometry args={[0.16, 10, 10]} />
        <meshStandardMaterial color={color} roughness={0.3} />
      </mesh>
      {/* Severity ring on floor */}
      <mesh position={[0, -0.24, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.24, 0.32, 20]} />
        <meshStandardMaterial color={color} transparent opacity={0.5} />
      </mesh>
      {/* Severity label */}
      <Text
        position={[0, 0.72, 0]}
        fontSize={0.2}
        fontWeight="bold"
        color="#ffffff"
        outlineWidth={0.03}
        outlineColor={color}
        anchorX="center"
        anchorY="middle"
      >
        {String(patient.severity)}
      </Text>
    </group>
  );
}

// ─── Full world ───────────────────────────────────────────────────────────────
function World({ patients, isDark }: { patients: Patient[]; isDark: boolean }) {
  return (
    <>
      <Floor isDark={isDark} />
      <Corridor isDark={isDark} />

      {ROOM_DEFS.map(def => (
        <Room key={def.id} def={def} isDark={isDark} />
      ))}

      <RoomFurniture isDark={isDark} />

      {patients.map(p => <Meeple key={p.id} patient={p} />)}
    </>
  );
}

// ─── Canvas ───────────────────────────────────────────────────────────────────
interface Props { patients: Patient[]; isDark: boolean; }

export default function HospitalScene3D({ patients, isDark }: Props) {
  return (
    <Canvas
      shadows="soft"
      orthographic
      camera={{ position: [28, 28, 28], zoom: 38, near: 0.1, far: 1000 }}
      frameloop="demand"
      gl={{
        antialias: true,
        powerPreference: "high-performance",
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.1,
      }}
      style={{ background: isDark ? "#0a0f1e" : "#e0f2fe" }}
    >
      {/* Lighting */}
      <ambientLight intensity={isDark ? 0.65 : 0.85} />
      <directionalLight
        castShadow
        position={[20, 30, 20]}
        intensity={isDark ? 1.3 : 1.9}
        shadow-mapSize={[1024, 1024]}
        shadow-camera-left={-30}
        shadow-camera-right={30}
        shadow-camera-top={30}
        shadow-camera-bottom={-30}
        shadow-bias={-0.001}
      />
      <directionalLight
        position={[-15, 10, -15]}
        intensity={0.3}
        color={isDark ? "#6366f1" : "#fef3c7"}
      />

      <Environment preset={isDark ? "night" : "apartment"} />

      <Suspense fallback={null}>
        <World patients={patients} isDark={isDark} />
      </Suspense>

      <OrbitControls
        makeDefault
        enablePan
        enableZoom
        enableRotate
        minZoom={18}
        maxZoom={100}
        minPolarAngle={Math.PI / 6}
        maxPolarAngle={Math.PI / 2.8}
        target={[0, 0, 0]}
      />
    </Canvas>
  );
}
