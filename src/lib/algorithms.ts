export type Zone = 'Triage' | 'MRI' | 'OPS_ROOM' | 'ICU' | 'WARD' | 'DISCHARGED';
export type Resource = 'MRI' | 'OPS_ROOM' | 'ICU' | 'WARD';
export type Status = 'WAITING' | 'IN_TREATMENT' | 'COMPLETED';

export interface Patient {
  id: string;
  severity: number;
  requiredResource: Resource;
  currentZone: Zone;
  waitTime: number;
  status: Status;
}

export class PriorityQueue {
  private queue: Patient[] = [];

  constructor(initialQueue: Patient[] = []) {
    this.queue = initialQueue;
    this.sortQueue();
  }

  enqueue(patient: Patient) {
    this.queue.push(patient);
    this.sortQueue();
  }

  dequeue(): Patient | undefined {
    return this.queue.shift();
  }

  peek(): Patient | undefined {
    return this.queue[0];
  }

  getQueue(): Patient[] {
    return [...this.queue];
  }

  // Primary: Severity (Desc), Secondary: waitTime (Desc)
  private sortQueue() {
    this.queue.sort((a, b) => {
      // Highest severity goes first
      if (b.severity !== a.severity) {
        return b.severity - a.severity; 
      }
      // Tie-breaker: Who has waited longer goes first
      return b.waitTime - a.waitTime;
    });
  }
}

export function generateRandomPatient(): Patient {
  const resources: Resource[] = ['MRI', 'OPS_ROOM', 'ICU', 'WARD'];
  
  return {
    id: Date.now().toString(36) + Math.random().toString(36).substring(2, 8),
    severity: Math.floor(Math.random() * 10) + 1, // 1 to 10
    requiredResource: resources[Math.floor(Math.random() * resources.length)],
    currentZone: 'Triage', // Always start in Triage
    waitTime: 0,
    status: 'WAITING',
  };
}
