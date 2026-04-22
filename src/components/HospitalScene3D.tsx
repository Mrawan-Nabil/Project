"use client";

import { Canvas } from "@react-three/fiber";
import { OrthographicCamera } from "@react-three/drei";

export const FLOORPLAN = [
  // 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], // 0
  [0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0], // 1
  [0, 1, 3, 3, 3, 3, 3, 1, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 4, 4, 4, 1, 0, 0], // 2
  [0, 1, 3, 3, 3, 3, 3, 1, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 4, 4, 4, 1, 0, 0], // 3
  [0, 1, 3, 3, 3, 3, 3, 1, 0, 0, 0, 0, 0, 0, 0, 1, 4, 4, 4, 4, 4, 1, 0, 0], // 4
  [0, 1, 1, 1, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 1, 1, 1, 0, 0], // 5
  [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0], // 6
  [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0], // 7
  [0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0], // 8
  [0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0, 0], // 9
  [0, 1, 5, 5, 5, 5, 5, 1, 1, 6, 6, 6, 6, 6, 1, 1, 7, 7, 7, 7, 7, 1, 0, 0], // 10
  [0, 1, 5, 5, 5, 5, 5, 1, 1, 6, 6, 6, 6, 6, 1, 1, 7, 7, 7, 7, 7, 1, 0, 0], // 11
  [0, 1, 5, 5, 5, 5, 5, 1, 1, 6, 6, 6, 6, 6, 1, 1, 7, 7, 7, 7, 7, 1, 0, 0], // 12
  [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0], // 13
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], // 14
  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], // 15
];

function getTileColor(val: number, r: number, c: number) {
  if (val === 1) return "#475569"; // Slate wall
  if (val === 2) return (r + c) % 2 === 0 ? "#e2e8f0" : "#f1f5f9"; // Checker corridor
  if (val === 3) return "#bfdbfe"; // Triage Blue
  if (val === 4) return "#e9d5ff"; // MRI Purple
  if (val === 5) return "#a7f3d0"; // Ward Green
  if (val === 6) return "#fecdd3"; // ICU Red
  if (val === 7) return "#f8fafc"; // Ops White
  return "#dcfce7"; // Ground Grass
}

export default function HospitalScene3D() {
  const rows = FLOORPLAN.length;
  const cols = FLOORPLAN[0].length;
  
  // To center at origin [0,0,0]
  const offsetX = cols / 2;
  const offsetZ = rows / 2;

  return (
    <Canvas shadows className="w-full h-full bg-[#1e293b]">
      <OrthographicCamera 
        makeDefault 
        position={[25, 25, 25]} 
        zoom={30} 
        onUpdate={(self) => self.lookAt(0, 0, 0)}
      />
      
      <ambientLight intensity={0.4} />
      <directionalLight 
        castShadow 
        position={[10, 20, 15]} 
        intensity={1.5} 
        shadow-mapSize={[2048, 2048]}
      />

      <group>
        {FLOORPLAN.map((rowArr, r) => 
          rowArr.map((val, c) => {
            if (val === 0) return null; // Ignore void

            const x = c - offsetX;
            const z = r - offsetZ;
            
            const isWall = val === 1;
            const height = isWall ? 1.0 : 0.05;
            const y = height / 2; // Keep bottom flush with 0

            return (
              <mesh 
                key={`${r}-${c}`} 
                position={[x, y, z]} 
                receiveShadow={!isWall} 
                castShadow={isWall}
              >
                <boxGeometry args={[1, height, 1]} />
                <meshStandardMaterial color={getTileColor(val, r, c)} />
              </mesh>
            );
          })
        )}
      </group>
    </Canvas>
  );
}
