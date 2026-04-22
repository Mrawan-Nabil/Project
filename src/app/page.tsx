"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Patient, PriorityQueue, generateRandomPatient, Zone } from "@/lib/algorithms";
import HospitalScene3D from "@/components/HospitalScene3D";

const HOSPITAL_ZONES: Record<string, { r: number; c: number }> = {
  Triage: { r: 3, c: 4 },
  MRI: { r: 3, c: 18 },
  WARD: { r: 11, c: 4 },
  ICU: { r: 11, c: 11 },
  OPS_ROOM: { r: 11, c: 18 },
  DISCHARGED: { r: 7, c: 26 }, // Off screen
};

export default function Dashboard() {
  const [patients, setPatients] = useState(50);
  const [beds, setBeds] = useState(20);
  const [mris, setMris] = useState(2);
  const [doctors, setDoctors] = useState(10);
  const [icus, setIcus] = useState(5);
  const [operatingRooms, setOperatingRooms] = useState(3);
  
  const [isSimulating, setIsSimulating] = useState(false);
  const [tick, setTick] = useState(0);

  const [waitingQueue, setWaitingQueue] = useState<Patient[]>([]);
  const [treatingPatients, setTreatingPatients] = useState<Patient[]>([]);

  useEffect(() => {
    if (!isSimulating) return;
    const interval = setInterval(() => setTick((t) => t + 1), 2000);
    return () => clearInterval(interval);
  }, [isSimulating]);

  useEffect(() => {
    if (!isSimulating || tick === 0) return;

    let newWaiting = [...waitingQueue];
    let newTreating = [...treatingPatients];

    newTreating.forEach((p) => (p.waitTime += 1));
    newTreating = newTreating.filter((p) => p.waitTime <= 3);

    const spawnCount = Math.floor(Math.random() * 2) + 1;
    for (let i = 0; i < spawnCount; i++) {
       newWaiting.push(generateRandomPatient());
    }

    newWaiting.forEach((p) => (p.waitTime += 1));
    
    const pq = new PriorityQueue(newWaiting);
    newWaiting = pq.getQueue();

    const treatingCount = {
      MRI: newTreating.filter((p) => p.requiredResource === "MRI").length,
      OPS_ROOM: newTreating.filter((p) => p.requiredResource === "OPS_ROOM").length,
      ICU: newTreating.filter((p) => p.requiredResource === "ICU").length,
      WARD: newTreating.filter((p) => p.requiredResource === "WARD").length,
    };

    const capacity = {
      MRI: mris,
      OPS_ROOM: operatingRooms,
      ICU: icus,
      WARD: beds,
    };

    const unallocated: Patient[] = [];

    for (const patient of newWaiting) {
      const res = patient.requiredResource;
      if (treatingCount[res] < capacity[res]) {
        treatingCount[res]++;
        patient.currentZone = res;
        patient.status = "IN_TREATMENT";
        patient.waitTime = 0;
        newTreating.push(patient);
      } else {
        unallocated.push(patient);
      }
    }

    setWaitingQueue(unallocated);
    setTreatingPatients(newTreating);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick]);

  const handleStartSimulation = () => {
    setIsSimulating(!isSimulating);
  };

  const totalWaitTime = waitingQueue.reduce((acc, p) => acc + p.waitTime, 0);
  const avgWaitTime = waitingQueue.length > 0 ? (totalWaitTime / waitingQueue.length).toFixed(1) : "0.0";

  const totalCapacity = mris + operatingRooms + icus + beds;
  const resourceUtil = totalCapacity > 0 ? ((treatingPatients.length / totalCapacity) * 100).toFixed(1) : "0.0";

  return (
    <main className="h-screen w-screen overflow-hidden relative flex bg-slate-900 text-slate-800">
      {/* Background purely aesthetic behind logic */}
      <div className="absolute inset-0 pointer-events-none z-[-10]" />

      <div className="flex h-full w-full justify-between items-stretch p-6 gap-6 pointer-events-none z-0">
        
        {/* LEFT PANEL: Simulation Controls */}
        <aside className="w-[360px] flex flex-col pointer-events-auto bg-white border-[6px] border-slate-700 rounded-3xl shadow-[8px_8px_0_rgba(51,65,85,1)] overflow-hidden">
          <div className="bg-blue-500 border-b-[6px] border-slate-700 px-6 py-4">
            <h1 className="text-2xl font-extrabold text-white tracking-wide uppercase drop-shadow-md">
              Hospital Admin
            </h1>
          </div>
          <div className="flex-1 px-6 py-6 flex flex-col gap-6 overflow-y-auto custom-scrollbar">
            <div className="flex flex-col gap-2">
              <label className="text-sm font-bold text-slate-600 uppercase tracking-wider">Incoming Patients</label>
              <input type="number" min="0" value={patients} onChange={(e) => setPatients(Number(e.target.value))} className="text-2xl font-extrabold px-4 py-3 bg-blue-50 border-4 border-slate-300 rounded-xl focus:outline-none focus:border-blue-500 focus:bg-white transition-colors" />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-bold text-slate-600 uppercase tracking-wider">Available Beds</label>
              <input type="number" min="0" value={beds} onChange={(e) => setBeds(Number(e.target.value))} className="text-2xl font-extrabold px-4 py-3 bg-blue-50 border-4 border-slate-300 rounded-xl focus:outline-none focus:border-blue-500 focus:bg-white transition-colors" />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-bold text-slate-600 uppercase tracking-wider">MRI Machines</label>
              <input type="number" min="0" value={mris} onChange={(e) => setMris(Number(e.target.value))} className="text-2xl font-extrabold px-4 py-3 bg-blue-50 border-4 border-slate-300 rounded-xl focus:outline-none focus:border-blue-500 focus:bg-white transition-colors" />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-bold text-slate-600 uppercase tracking-wider">Available Doctors</label>
              <input type="number" min="0" value={doctors} onChange={(e) => setDoctors(Number(e.target.value))} className="text-2xl font-extrabold px-4 py-3 bg-blue-50 border-4 border-slate-300 rounded-xl focus:outline-none focus:border-blue-500 focus:bg-white transition-colors" />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-bold text-slate-600 uppercase tracking-wider">ICUs (Intensive Care)</label>
              <input type="number" min="0" value={icus} onChange={(e) => setIcus(Number(e.target.value))} className="text-2xl font-extrabold px-4 py-3 bg-blue-50 border-4 border-slate-300 rounded-xl focus:outline-none focus:border-blue-500 focus:bg-white transition-colors" />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm font-bold text-slate-600 uppercase tracking-wider">Operating Rooms</label>
              <input type="number" min="0" value={operatingRooms} onChange={(e) => setOperatingRooms(Number(e.target.value))} className="text-2xl font-extrabold px-4 py-3 bg-blue-50 border-4 border-slate-300 rounded-xl focus:outline-none focus:border-blue-500 focus:bg-white transition-colors" />
            </div>
          </div>
          <div className="p-6 bg-slate-100 border-t-[6px] border-slate-700">
            <button
              onClick={handleStartSimulation}
              className={`w-full py-4 px-6 text-2xl font-extrabold text-white uppercase tracking-widest rounded-2xl border-[6px] border-slate-700 transform transition-transform active:translate-y-2 active:shadow-none hover:-translate-y-1 ${
                isSimulating ? "bg-red-500 hover:bg-red-400 shadow-[6px_6px_0_rgba(51,65,85,1)]" : "bg-green-500 hover:bg-green-400 shadow-[6px_6px_0_rgba(51,65,85,1)]"
              }`}
            >
              {isSimulating ? "Stop Sim" : "Start Sim"}
            </button>
          </div>
        </aside>

        {/* CENTER STAGE: Tilemap Grid */}
        <div className="flex-1 relative pointer-events-auto border-[8px] border-slate-800 rounded-3xl overflow-hidden shadow-[8px_8px_0_rgba(51,65,85,1)] bg-[#e2f1e2]">
          
          {/* Physical Grid Layer (R3F Upgrade) */}
          <div className="absolute inset-0 z-0 overflow-hidden rounded-3xl">
            <HospitalScene3D />
          </div>

          {/* Room Labels Layer */}
          {Object.entries(HOSPITAL_ZONES).map(([name, coords]) => {
            if (name === "DISCHARGED") return null;

            const left = `${(coords.c + 0.5) * (100 / 24)}%`;
            const top = `${(coords.r + 0.5) * (100 / 16)}%`;

            let label = "";
            if (name === "Triage") label = "📋 Triage";
            if (name === "MRI") label = "🧲 MRI";
            if (name === "WARD") label = "🛏️ Ward";
            if (name === "ICU") label = "🩺 ICU";
            if (name === "OPS_ROOM") label = "🔪 Ops Room";

            return (
              <div
                key={`label-${name}`}
                className="absolute flex items-center justify-center font-extrabold text-slate-700/60 text-2xl lg:text-3xl uppercase tracking-wide transform -translate-x-1/2 -translate-y-1/2 pointer-events-none"
                style={{ left, top }}
              >
                {label}
              </div>
            );
          })}

          {/* Animated Patients Layer */}
          {[...waitingQueue, ...treatingPatients].map((patient) => (
            <PatientSprite key={patient.id} patient={patient} />
          ))}

        </div>

        {/* RIGHT PANEL: Metrics Panel */}
        <aside className="w-[360px] flex flex-col pointer-events-auto bg-white border-[6px] border-slate-700 rounded-3xl shadow-[8px_8px_0_rgba(51,65,85,1)] overflow-hidden">
          <div className="bg-red-500 border-b-[6px] border-slate-700 px-6 py-4">
            <h2 className="text-2xl font-extrabold text-white tracking-wide uppercase drop-shadow-md">
              Live Metrics
            </h2>
          </div>
          <div className="flex-1 px-6 py-6 flex flex-col gap-6 overflow-y-auto bg-slate-50 border-t-[6px] border-slate-700 lg:border-t-0">
            <div className="bg-white border-4 border-slate-300 rounded-2xl p-5 flex flex-col items-center shadow-sm">
              <span className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-1">
                Avg Wait Time
              </span>
              <span className="text-4xl font-extrabold text-slate-800">
                {avgWaitTime}<span className="text-2xl text-slate-400 ml-1">ticks</span>
              </span>
            </div>
            <div className="bg-white border-4 border-red-300 rounded-2xl p-5 flex flex-col items-center shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-red-500" />
              <span className="text-sm font-bold text-red-500 uppercase tracking-widest mb-1">
                Mortality Risk
              </span>
              <span className="text-4xl font-extrabold text-red-600">
                4.2<span className="text-2xl text-red-400 ml-1">%</span>
              </span>
            </div>
            <div className="bg-white border-4 border-blue-300 rounded-2xl p-5 flex flex-col items-center shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-blue-500" />
              <span className="text-sm font-bold text-blue-500 uppercase tracking-widest mb-1">
                Resource Util.
              </span>
              <span className="text-4xl font-extrabold text-blue-600">
                {resourceUtil}<span className="text-2xl text-blue-400 ml-1">%</span>
              </span>
            </div>
          </div>
        </aside>

      </div>
    </main>
  );
}

function PatientSprite({ patient }: { patient: Patient }) {
  const coords = HOSPITAL_ZONES[patient.currentZone];
  if (!coords) return null;

  const left = `${(coords.c + 0.5) * (100 / 24)}%`;
  const top = `${(coords.r + 0.5) * (100 / 16)}%`;

  let hash = 0;
  for (let i = 0; i < patient.id.length; i++) {
    hash = patient.id.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  const isTriage = patient.currentZone === "Triage";
  const offsetX = isTriage ? (hash % 80) - 40 : 0; 
  const offsetY = isTriage ? ((hash >> 4) % 80) - 40 : 0;

  const severityColor = 
    patient.severity >= 8 ? 'bg-red-500' :
    patient.severity >= 4 ? 'bg-orange-500' :
    'bg-green-500';

  return (
    <motion.div
      initial={false}
      animate={{ 
        left, 
        top,
        translateX: `calc(-50% + ${offsetX}px)`,
        translateY: `calc(-50% + ${offsetY}px)` 
      }}
      transition={{ type: "spring", stiffness: 100, damping: 12 }}
      className={`absolute w-10 h-10 rounded-full ${severityColor} border-[4px] border-slate-700 shadow-[4px_4px_0_rgba(51,65,85,1)] z-[100] flex items-center justify-center text-md font-bold text-white`}
    >
      {patient.severity}
    </motion.div>
  );
}
