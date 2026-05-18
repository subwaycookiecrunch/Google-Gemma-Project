import axios from 'axios';
import {
  InfiltrationResult,
  GraphData,
  FeedingPoint,
  InfiltrationStats,
  EvolutionSession,
  Strain,
  RevelationResult,
  AttackPath,
  KillSimulation,
  TimeToImpact,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000,
});

const withRetry = async <T>(fn: () => Promise<T>, retries = 3): Promise<T> => {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0) {
      console.warn(`API call failed, retrying... (${retries} retries left)`);
      await new Promise(r => setTimeout(r, 1000));
      return withRetry(fn, retries - 1);
    }
    throw error;
  }
};

export const parasiteAPI = {
  // Progress tracking
  getProgress: async (sessionId: string): Promise<any> => {
    const response = await api.get(`/api/progress/${sessionId}`);
    return response.data;
  },

  // Async infiltration (background scan)
  infiltrateStart: async (repoPath: string): Promise<{ session_id: string; status: string }> => {
    const response = await api.post('/api/infiltrate/start', { repo_path: repoPath }, { timeout: 30000 });
    return response.data;
  },

  getInfiltrateResult: async (sessionId: string): Promise<any> => {
    const response = await api.get(`/api/infiltrate/result/${sessionId}`, { timeout: 10000 });
    return response.data;
  },

  // Infiltration (blocking — for backwards compat)
  infiltrate: async (repoPath: string): Promise<InfiltrationResult> => {
    return withRetry(async () => {
      const response = await api.post('/api/infiltrate', { repo_path: repoPath }, { timeout: 300000 });
      return response.data;
    });
  },

  getGraph: async (sessionId: string): Promise<{ session_id: string; graph: GraphData }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/graph/${sessionId}`);
      return response.data;
    });
  },

  getFeedingPoints: async (sessionId: string): Promise<{ session_id: string; feeding_points: FeedingPoint[]; count: number }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/feeding-points/${sessionId}`);
      return response.data;
    });
  },

  getStats: async (sessionId: string): Promise<{ session_id: string; stats: InfiltrationStats }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/stats/${sessionId}`);
      return response.data;
    });
  },

  // Evolution
  evolve: async (sessionId: string): Promise<EvolutionSession> => {
    return withRetry(async () => {
      const response = await api.post('/api/evolve', { session_id: sessionId });
      return response.data;
    });
  },

  getStrains: async (sessionId: string): Promise<{ session_id: string; generation: number; strain_count: number; alive: number; dead: number; strains: Strain[] }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/strains/${sessionId}`);
      return response.data;
    });
  },

  getDominant: async (sessionId: string): Promise<{ session_id: string; dominant: Strain; generation: number; total_mutations: number; survived_mutations: number }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/dominant/${sessionId}`);
      return response.data;
    });
  },

  getEvolutionLog: async (sessionId: string): Promise<{ session_id: string; generation: number; complete: boolean; log_entries: string[]; entry_count: number }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/evolution-log/${sessionId}`);
      return response.data;
    });
  },

  // Revelation
  reveal: async (sessionId: string): Promise<RevelationResult> => {
    return withRetry(async () => {
      const response = await api.post('/api/reveal', { session_id: sessionId });
      return response.data;
    });
  },

  getAttackPaths: async (sessionId: string): Promise<{ session_id: string; attack_paths: AttackPath[]; count: number }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/attack-paths/${sessionId}`);
      return response.data;
    });
  },

  getKillSimulation: async (sessionId: string): Promise<{ session_id: string; kill_simulation: KillSimulation }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/kill-simulation/${sessionId}`);
      return response.data;
    });
  },

  getTimeToImpact: async (sessionId: string): Promise<{ session_id: string; time_to_impact: TimeToImpact }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/time-to-impact/${sessionId}`);
      return response.data;
    });
  },

  getFinalVerdict: async (sessionId: string): Promise<{ session_id: string; dominant_strain: string; dominant_target: string; final_verdict: string }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/final-verdict/${sessionId}`);
      return response.data;
    });
  },

  // Symbiotic
  runSymbiotic: async (sessionId: string): Promise<any> => {
    return withRetry(async () => {
      const response = await api.post('/api/symbiotic', { session_id: sessionId });
      return response.data;
    });
  },

  getHealingPlans: async (sessionId: string): Promise<{ healing_plans: any[] }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/healing-plans/${sessionId}`);
      return response.data;
    });
  },

  getDefensePaths: async (sessionId: string): Promise<{ defense_paths: any[] }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/defense-paths/${sessionId}`);
      return response.data;
    });
  },

  getHardeningGuide: async (sessionId: string): Promise<{ hardening_guide: any }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/hardening-guide/${sessionId}`);
      return response.data;
    });
  },

  getSymbioticVerdict: async (sessionId: string): Promise<{ symbiotic_verdict: string }> => {
    return withRetry(async () => {
      const response = await api.get(`/api/symbiotic-verdict/${sessionId}`);
      return response.data;
    });
  },

  // Artifacts
  generateArtifacts: async (sessionId: string): Promise<any> => {
    return withRetry(async () => {
      const response = await api.post('/api/artifacts', { session_id: sessionId });
      return response.data;
    });
  },

  getArtifacts: async (sessionId: string): Promise<any> => {
    return withRetry(async () => {
      const response = await api.get(`/api/artifacts/${sessionId}`);
      return response.data;
    });
  },
};
