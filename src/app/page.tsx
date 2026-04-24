"use client";

import { useState, useEffect, useCallback } from "react";
import { useTheme } from "next-themes";
import {
  Patient, SimCapacity,
  PriorityQueue, greedyAllocate, generateRandomPatient,
} from "@/lib/algorithms";
import { ThemeToggle } from "@/components/ThemeToggle";
import HospitalScene3D from "@/components/HospitalScene3D";

// ─── Stat card ────────────────────────────────────────────────────────────────
function StatCard({ label, value, unit, accent }: {
  label: string; value: string | number; unit?: string; accent: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center px-4">
      <span className={`text-[10px] font-bold uppercase tracking-widest mb-0.5 ${accent}`}>{label}</span>
      <span className="text-white font-black text-2xl leading-none">
        {value}
        {unit && <span className="text-sm font-normal text-white/50 ml-1">{unit}</span>}
      </span>
    </div>
  );
}

// ─── Control knob ─────────────────────────────────────────────────────────────
function Knob({ label, value, onChange, min = 0, max = 99 }: {
  label: string; value: number; onChange: (v: number) => void; min?: number; max?: number;
}) {
  return (
    <div className="flex flex-col items-center gap-0.5">
      <span className="text-[9px] text-white/50 uppercase tracking-widest font-bold">{label}</span>
      <div className="flex items-center gap-1">
        <button
          onClick={() => onChange(Math.max(min, value - 1))}
          className="w-5 h-5 rounded bg-white/10 hover:bg-white/20 text-white text-xs font-bold flex items-center justify-center transition-colors"
        >−</button>
        <span className="text-white font-black text-base w-6 text-center">{value}</span>
        <button
          onClick={() => onChange(Math.min(max, value + 1))}
          className="w-5 h-5 rounded bg-white/10 hover:bg-white/20 text-white text-xs font-bold flex items-center justify-center transition-colors"
        >+</button>
      </div>
    </div>
  );
}

// ─── Main dashboard ───────────────────────────────────────────────────────────
export default function Dashboard() {
  const { theme } = useTheme();
  const isDark = theme !== "light";

  // Sim config
  const [beds,           setBeds]           = useState(6);
  const [mris,           setMris]           = useState(2);
  const [icus,           setIcus]           = useState(3);
  const [ops,            setOps]            = useState(2);
  const [pharmacies,     setPharmacies]     = useState(2);
  const [labs,           setLabs]           = useState(2);

  // Sim state
  const [isRunning,      setIsRunning]      = useState(false);
  const [tick,           setTick]           = useState(0);
  const [waitingQueue,   setWaitingQueue]   = useState<Patient[]>([]);
  const [treating,       setTreating]       = useState<Patient[]>([]);
  const [totalSurgeries, setTotalSurgeries] = useState(0);
  const [totalScans,     setTotalScans]     = useState(0);
  const [discharged,     setDischarged]     = useState(0);

  // Tick clock
  useEffect(() => {
    if (!isRunning) return;
    const id = setInterval(() => setTick(t => t + 1), 1800);
    return () => clearInterval(id);
  }, [isRunning]);

  // Simulation step
  useEffect(() => {
    if (!isRunning || tick === 0) return;

    // Age treating patients, discharge completed ones
    let newTreating = treating
      .map(p => ({ ...p, waitTime: p.waitTime + 1 }))
      .filter(p => p.waitTime <= 4);

    const justDischarged = treating.filter(p => p.waitTime > 4);
    setDischarged(d => d + justDischarged.length);
    setTotalSurgeries(s => s + justDischarged.filter(p => p.requiredResource === 'OPS_ROOM').length);
    setTotalScans(s => s + justDischarged.filter(p => p.requiredResource === 'MRI' || p.requiredResource === 'Laboratory').length);

    // Spawn 1–3 new patients
    const spawn = Math.floor(Math.random() * 3) + 1;
    const newWaiting = [
      ...waitingQueue.map(p => ({ ...p, waitTime: p.waitTime + 1 })),
      ...Array.from({ length: spawn }, generateRandomPatient),
    ];

    // Greedy allocation
    const capacity: SimCapacity = {
      MRI: mris, OPS_ROOM: ops, ICU: icus,
      WARD: beds, Pharmacy: pharmacies, Laboratory: labs,
    };

    const { newWaiting: unallocated, newTreating: allocated } =
      greedyAllocate(new PriorityQueue(newWaiting).getQueue(), newTreating, capacity);

    setWaitingQueue(unallocated);
    setTreating(allocated);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick]);

  const handleToggle = useCallback(() => {
    if (isRunning) {
      setIsRunning(false);
    } else {
      setWaitingQueue([]);
      setTreating([]);
      setTick(0);
      setDischarged(0);
      setTotalSurgeries(0);
      setTotalScans(0);
      setIsRunning(true);
    }
  }, [isRunning]);

  const allPatients = [...waitingQueue, ...treating];
  const totalWait   = waitingQueue.reduce((s, p) => s + p.waitTime, 0);
  const avgWait     = waitingQueue.length > 0 ? (totalWait / waitingQueue.length).toFixed(1) : "0.0";
  const totalCap    = mris + ops + icus + beds + pharmacies + labs;
  const utilPct     = totalCap > 0 ? ((treating.length / totalCap) * 100).toFixed(0) : "0";
  const mortalityPct = waitingQueue.filter(p => p.severity >= 8 && p.waitTime >= 3).length;

  return (
    <main className="h-screen w-screen overflow-hidden relative bg-black">

      {/* ── Full-screen 3D scene ── */}
      <div className="absolute inset-0">
        <HospitalScene3D patients={allPatients} isDark={isDark} />
      </div>

      {/* ── Theme toggle ── */}
      <div className="absolute top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      {/* ── Title ── */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 z-40 pointer-events-none">
        <div className="px-6 py-2 rounded-2xl bg-black/40 backdrop-blur-md border border-white/10">
          <h1 className="text-white font-black text-lg tracking-[0.2em] uppercase">
            🏥 Hospital Crisis Sim
          </h1>
        </div>
      </div>

      {/* ── Glassmorphism bottom HUD ── */}
      <div className="absolute bottom-0 left-0 right-0 z-40">
        <div className="mx-4 mb-4 rounded-2xl overflow-hidden border border-white/15 shadow-2xl"
          style={{ background: "rgba(10,15,30,0.72)", backdropFilter: "blur(20px)" }}>

          <div className="flex items-center justify-between px-4 py-3 gap-2">

            {/* LEFT — Controls */}
            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-white/40 text-[10px] font-bold uppercase tracking-widest hidden sm:block">Config</span>
              <div className="w-px h-8 bg-white/10 hidden sm:block" />
              <Knob label="Beds"    value={beds}       onChange={setBeds} />
              <Knob label="MRI"     value={mris}       onChange={setMris} />
              <Knob label="ICU"     value={icus}       onChange={setIcus} />
              <Knob label="OPS"     value={ops}        onChange={setOps} />
              <Knob label="Pharm"   value={pharmacies} onChange={setPharmacies} />
              <Knob label="Lab"     value={labs}       onChange={setLabs} />
            </div>

            {/* CENTER — Start/Stop */}
            <button
              onClick={handleToggle}
              className={`
                flex-shrink-0 px-8 py-3 rounded-xl font-black text-sm uppercase tracking-widest
                border-2 transition-all duration-200 active:scale-95
                ${isRunning
                  ? "bg-red-500/80 border-red-400 text-white hover:bg-red-500"
                  : "bg-emerald-500/80 border-emerald-400 text-white hover:bg-emerald-500"}
              `}
            >
              {isRunning ? "⏹ Stop" : "▶ Start Sim"}
            </button>

            {/* RIGHT — Live metrics */}
            <div className="flex items-center gap-1">
              <div className="w-px h-8 bg-white/10" />
              <StatCard label="Waiting"    value={waitingQueue.length}  accent="text-yellow-400" />
              <div className="w-px h-8 bg-white/10" />
              <StatCard label="In Care"    value={treating.length}      accent="text-blue-400" />
              <div className="w-px h-8 bg-white/10" />
              <StatCard label="Avg Wait"   value={avgWait} unit="ticks" accent="text-purple-400" />
              <div className="w-px h-8 bg-white/10" />
              <StatCard label="Critical"   value={mortalityPct}         accent="text-red-400" />
              <div className="w-px h-8 bg-white/10" />
              <StatCard label="Util"       value={`${utilPct}%`}        accent="text-cyan-400" />
              <div className="w-px h-8 bg-white/10" />
              <StatCard label="Surgeries"  value={totalSurgeries}       accent="text-green-400" />
              <div className="w-px h-8 bg-white/10" />
              <StatCard label="Scans"      value={totalScans}           accent="text-indigo-400" />
              <div className="w-px h-8 bg-white/10" />
              <StatCard label="Discharged" value={discharged}           accent="text-emerald-400" />
            </div>

          </div>

          {/* Tick progress bar */}
          {isRunning && (
            <div className="h-0.5 bg-white/5">
              <div
                className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transition-all duration-300"
                style={{ width: `${((tick % 10) / 10) * 100}%` }}
              />
            </div>
          )}
        </div>
      </div>

    </main>
  );
}
