import { readFileSync } from 'fs';

const files = [
  'public/models/doctor.glb',
  'public/models/nurse.glb', 
  'public/models/patient.glb',
  'public/models/hospital_bed.glb',
  'public/models/intake_desk.glb',
  'public/models/mri_scanner.glb',
  'public/models/operating_table2.glb',
  'public/models/surgical_doctor.glb',
];

for (const f of files) {
  const buf = readFileSync(f);
  const size = buf.length;
  console.log(`${f}: ${(size/1024).toFixed(1)} KB`);
}
