export type Zone =
  | 'Triage'
  | 'MRI'
  | 'OPS_ROOM'
  | 'ICU'
  | 'WARD'
  | 'Pharmacy'
  | 'Laboratory'
  | 'Reception'
  | 'DISCHARGED';

export type Resource = 'MRI' | 'OPS_ROOM' | 'ICU' | 'WARD' | 'Pharmacy' | 'Laboratory';
export type Status = 'WAITING' | 'IN_TREATMENT' | 'COMPLETED';

export interface Patient {
  id: string;
  name: string;
  severity: number;          // 1–10
  requiredResource: Resource;
  currentZone: Zone;
  waitTime: number;          // ticks waited
  status: Status;
}

export interface SimCapacity {
  MRI: number;
  OPS_ROOM: number;
  ICU: number;
  WARD: number;
  Pharmacy: number;
  Laboratory: number;
}

// ─── Priority Queue (max-heap by severity, then waitTime) ────────────────────
export class PriorityQueue {
  private queue: Patient[] = [];

  constructor(initial: Patient[] = []) {
    this.queue = [...initial];
    this.sort();
  }

  enqueue(p: Patient) { this.queue.push(p); this.sort(); }
  dequeue(): Patient | undefined { return this.queue.shift(); }
  peek(): Patient | undefined { return this.queue[0]; }
  getQueue(): Patient[] { return [...this.queue]; }
  get length() { return this.queue.length; }

  private sort() {
    this.queue.sort((a, b) =>
      b.severity !== a.severity
        ? b.severity - a.severity
        : b.waitTime - a.waitTime
    );
  }
}

// ─── Greedy allocator — assigns highest-priority patient to nearest resource ──
export function greedyAllocate(
  waiting: Patient[],
  treating: Patient[],
  capacity: SimCapacity
): { newWaiting: Patient[]; newTreating: Patient[] } {
  const pq = new PriorityQueue(waiting);

  const used: Record<Resource, number> = {
    MRI:        treating.filter(p => p.requiredResource === 'MRI').length,
    OPS_ROOM:   treating.filter(p => p.requiredResource === 'OPS_ROOM').length,
    ICU:        treating.filter(p => p.requiredResource === 'ICU').length,
    WARD:       treating.filter(p => p.requiredResource === 'WARD').length,
    Pharmacy:   treating.filter(p => p.requiredResource === 'Pharmacy').length,
    Laboratory: treating.filter(p => p.requiredResource === 'Laboratory').length,
  };

  const newTreating = [...treating];
  const unallocated: Patient[] = [];

  for (const patient of pq.getQueue()) {
    const res = patient.requiredResource;
    if (used[res] < capacity[res]) {
      used[res]++;
      newTreating.push({
        ...patient,
        currentZone: res as unknown as Zone,
        status: 'IN_TREATMENT',
        waitTime: 0,
      });
    } else {
      unallocated.push(patient);
    }
  }

  return { newWaiting: unallocated, newTreating };
}

// ─── Patient generator ────────────────────────────────────────────────────────
const NAMES = ['Ali', 'Sara', 'Omar', 'Nour', 'Khaled', 'Mona', 'Youssef', 'Layla', 'Ahmed', 'Dina'];
const RESOURCES: Resource[] = ['MRI', 'OPS_ROOM', 'ICU', 'WARD', 'Pharmacy', 'Laboratory'];

export function generateRandomPatient(): Patient {
  return {
    id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
    name: NAMES[Math.floor(Math.random() * NAMES.length)],
    severity: Math.floor(Math.random() * 10) + 1,
    requiredResource: RESOURCES[Math.floor(Math.random() * RESOURCES.length)],
    currentZone: 'Triage',
    waitTime: 0,
    status: 'WAITING',
  };
}
