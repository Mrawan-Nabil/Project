import { readFileSync } from 'fs';

function readGLB(path) {
  const buf = readFileSync(path);
  // GLB header: magic(4) + version(4) + length(4) = 12 bytes
  // Chunk 0: chunkLength(4) + chunkType(4) + chunkData
  const chunkLength = buf.readUInt32LE(12);
  const jsonStr = buf.slice(20, 20 + chunkLength).toString('utf8').replace(/\0/g, '');
  const json = JSON.parse(jsonStr);
  
  // Get mesh names and accessor min/max if available
  const meshNames = (json.meshes || []).map(m => m.name);
  const nodeNames = (json.nodes || []).map(n => ({ name: n.name, scale: n.scale, translation: n.translation }));
  
  console.log(`\n=== ${path} ===`);
  console.log('Meshes:', meshNames.slice(0, 5));
  console.log('Root nodes:', nodeNames.slice(0, 3));
  
  // Check accessors for bounding box hints
  if (json.accessors) {
    const posAccessors = json.accessors.filter(a => a.min && a.max && a.min.length === 3);
    if (posAccessors.length > 0) {
      const first = posAccessors[0];
      console.log('First position bounds - min:', first.min, 'max:', first.max);
    }
  }
}

const files = [
  'public/models/doctor.glb',
  'public/models/hospital_bed.glb',
  'public/models/mri_scanner.glb',
  'public/models/operating_table2.glb',
  'public/models/patient.glb',
  'public/models/intake_desk.glb',
];

for (const f of files) {
  try { readGLB(f); } catch(e) { console.log(`${f}: ERROR - ${e.message}`); }
}
