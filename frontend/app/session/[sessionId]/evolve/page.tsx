'use client';

import React, { useEffect, useState } from 'react';
import { parasiteAPI } from '@/lib/api';
import { Strain } from '@/lib/types';
import { useRouter, useParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Activity, Skull, Dna, Crown } from 'lucide-react';

export default function EvolutionPage() {
  const [strains, setStrains] = useState<Strain[]>([]);
  const [dominant, setDominant] = useState<Strain | null>(null);
  const [generation, setGeneration] = useState(0);
  const [log, setLog] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [evolving, setEvolving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const paramsObj = useParams();
  const sessionId = paramsObj.sessionId as string;

  useEffect(() => {
    const fetchEvolution = async () => {
      try {
        // Try to get existing evolution data
        const strainsRes = await parasiteAPI.getStrains(sessionId);
        setStrains(strainsRes.strains);
        setGeneration(strainsRes.generation);

        const domRes = await parasiteAPI.getDominant(sessionId);
        setDominant(domRes.dominant);

        const logRes = await parasiteAPI.getEvolutionLog(sessionId);
        setLog(logRes.log_entries);
      } catch {
        // Evolution hasn't run yet — we need to trigger it
        setEvolving(true);
        try {
          const evoRes = await parasiteAPI.evolve(sessionId);
          setStrains(evoRes.strains);
          setGeneration(evoRes.generation);
          setDominant(evoRes.dominant_strain || null);
          setLog(evoRes.evolution_log);
        } catch (err: any) {
          setError(err.response?.data?.detail || err.message || 'Evolution failed');
        }
        setEvolving(false);
      }
      setLoading(false);
    };
    fetchEvolution();
  }, [sessionId]);

  const statusColor = (status: string) => {
    switch (status) {
      case 'dominant': return 'text-parasite-green';
      case 'alive': return 'text-strain-blue';
      case 'dead': return 'text-critical-red';
      case 'mutating': return 'text-warning-amber';
      default: return 'text-text-secondary';
    }
  };

  if (loading || evolving) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-4">
        <Dna className="w-12 h-12 text-strain-blue animate-spin" />
        <span className="text-strain-blue animate-pulse tracking-widest">
          {evolving ? 'EVOLVING STRAINS...' : 'LOADING EVOLUTION DATA...'}
        </span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-4 p-8">
        <div className="text-critical-red text-xl tracking-widest">EVOLUTION FAILED</div>
        <div className="text-text-secondary text-sm max-w-md text-center">{error}</div>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-6 py-2 border border-strain-blue text-strain-blue hover:bg-strain-blue/10 tracking-widest text-sm"
        >
          RETRY
        </button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-strain-blue tracking-widest mb-2 flex items-center">
          <Activity className="mr-3 w-8 h-8" /> EVOLUTION COMPLETE
        </h1>
        <p className="text-text-secondary tracking-wider">
          Generation {generation} — {strains.length} strains cultivated. Natural selection has spoken.
        </p>
      </div>

      {/* Dominant Strain Hero */}
      {dominant && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 p-8 bg-strain-blue/5 border-2 border-strain-blue rounded-sm"
        >
          <div className="flex items-center mb-4">
            <Crown className="w-6 h-6 text-warning-amber mr-3" />
            <h2 className="text-2xl font-bold text-strain-blue tracking-widest">
              DOMINANT: {dominant.strain_id}
            </h2>
          </div>
          <div className="grid grid-cols-4 gap-6 mb-6">
            <div>
              <div className="text-text-dim text-xs tracking-widest mb-1">FITNESS</div>
              <div className="text-3xl font-bold text-parasite-green">{dominant.fitness_score.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-text-dim text-xs tracking-widest mb-1">STEALTH</div>
              <div className="text-3xl font-bold text-text-primary">{dominant.stealth_score.toFixed(1)}</div>
            </div>
            <div>
              <div className="text-text-dim text-xs tracking-widest mb-1">BLAST</div>
              <div className="text-3xl font-bold text-critical-red">{dominant.blast_radius_score.toFixed(1)}</div>
            </div>
            <div>
              <div className="text-text-dim text-xs tracking-widest mb-1">PERSIST</div>
              <div className="text-3xl font-bold text-warning-amber">{dominant.persistence_score.toFixed(1)}</div>
            </div>
          </div>
          <div className="text-text-secondary text-sm">
            <span className="text-text-dim">TARGET:</span> {dominant.target_feeding_point?.name}() — {dominant.attack_approach}
          </div>
          <div className="text-text-dim text-xs mt-2 italic">{dominant.personality_notes}</div>
        </motion.div>
      )}

      {/* All Strains Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 mb-8">
        {strains.map((strain, idx) => (
          <motion.div
            key={strain.strain_id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.05 }}
            className="p-4 bg-surface border border-border-dim rounded-sm hover:border-strain-blue/50 transition-colors"
          >
            <div className="flex justify-between items-center mb-3">
              <span className="font-bold text-text-primary tracking-wider">{strain.strain_id}</span>
              <span className={`text-xs uppercase tracking-widest font-bold ${statusColor(strain.status)}`}>
                {strain.status}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs mb-3">
              <div><span className="text-text-dim">FIT:</span> <span className="text-parasite-green">{strain.fitness_score.toFixed(2)}</span></div>
              <div><span className="text-text-dim">STL:</span> <span>{strain.stealth_score.toFixed(1)}</span></div>
              <div><span className="text-text-dim">BLT:</span> <span className="text-critical-red">{strain.blast_radius_score.toFixed(1)}</span></div>
              <div><span className="text-text-dim">PER:</span> <span>{strain.persistence_score.toFixed(1)}</span></div>
            </div>
            <div className="text-text-dim text-xs truncate">
              → {strain.target_feeding_point?.name}()
            </div>
          </motion.div>
        ))}
      </div>

      {/* Evolution Log */}
      {log.length > 0 && (
        <div className="mb-8">
          <h3 className="text-sm font-bold text-text-dim tracking-widest mb-3">EVOLUTION LOG</h3>
          <div className="bg-void border border-border-dim rounded-sm p-4 max-h-[300px] overflow-y-auto font-mono text-xs space-y-1">
            {log.map((entry, idx) => (
              <div key={idx} className="text-text-secondary">
                {entry}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Proceed to Revelation */}
      <div className="pt-8 border-t border-border-dim flex justify-center pb-8">
        <motion.button
          onClick={() => router.push(`/session/${sessionId}/reveal`)}
          whileHover={{ scale: 1.02, boxShadow: '0 0 20px rgba(255,34,68,0.3)' }}
          whileTap={{ scale: 0.98 }}
          className="bg-critical-red text-white font-bold py-4 px-12 tracking-[0.2em] rounded-sm uppercase flex items-center justify-center min-w-[300px]"
        >
          <Skull className="w-5 h-5 mr-3" /> INITIATE REVELATION →
        </motion.button>
      </div>
    </div>
  );
}
