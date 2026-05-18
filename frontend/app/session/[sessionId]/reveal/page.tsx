'use client';

import React, { useEffect, useState } from 'react';
import { parasiteAPI } from '@/lib/api';
import { AttackPath, KillSimulation, TimeToImpact } from '@/lib/types';
import { useRouter, useParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { Skull, Shield, Clock, AlertTriangle, Crosshair, Eye } from 'lucide-react';

export default function RevelationPage() {
  const [attackPaths, setAttackPaths] = useState<AttackPath[]>([]);
  const [killSim, setKillSim] = useState<KillSimulation | null>(null);
  const [timeImpact, setTimeImpact] = useState<TimeToImpact | null>(null);
  const [verdict, setVerdict] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [revealing, setRevealing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedPath, setExpandedPath] = useState<string | null>(null);
  const router = useRouter();
  const paramsObj = useParams();
  const sessionId = paramsObj.sessionId as string;

  useEffect(() => {
    const fetchRevelation = async () => {
      try {
        // Try to get existing revelation data
        const [apRes, ksRes, tiRes, vRes] = await Promise.all([
          parasiteAPI.getAttackPaths(sessionId),
          parasiteAPI.getKillSimulation(sessionId),
          parasiteAPI.getTimeToImpact(sessionId),
          parasiteAPI.getFinalVerdict(sessionId),
        ]);
        setAttackPaths(apRes.attack_paths);
        setKillSim(ksRes.kill_simulation);
        setTimeImpact(tiRes.time_to_impact);
        setVerdict(vRes.final_verdict);
      } catch {
        // Revelation hasn't run yet — trigger it
        setRevealing(true);
        try {
          const revRes = await parasiteAPI.reveal(sessionId);
          setAttackPaths(revRes.attack_paths);
          setKillSim(revRes.kill_simulation);
          setTimeImpact(revRes.time_to_impact);
          setVerdict(revRes.final_verdict);
        } catch (err: any) {
          setError(err.response?.data?.detail || err.message || 'Revelation failed');
        }
        setRevealing(false);
      }
      setLoading(false);
    };
    fetchRevelation();
  }, [sessionId]);

  if (loading || revealing) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-4">
        <Skull className="w-12 h-12 text-critical-red animate-pulse" />
        <span className="text-critical-red animate-pulse tracking-widest">
          {revealing ? 'GENERATING KILL SEQUENCES...' : 'LOADING REVELATION DATA...'}
        </span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-4 p-8">
        <div className="text-critical-red text-xl tracking-widest">REVELATION FAILED</div>
        <div className="text-text-secondary text-sm max-w-md text-center">{error}</div>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-6 py-2 border border-critical-red text-critical-red hover:bg-critical-red/10 tracking-widest text-sm"
        >
          RETRY
        </button>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-critical-red tracking-widest mb-2 flex items-center">
          <Skull className="mr-3 w-8 h-8" /> REVELATION
        </h1>
        <p className="text-text-secondary tracking-wider">
          The parasite has revealed its kill plan. {attackPaths.length} lethal pathways mapped.
        </p>
      </div>

      {/* Time-to-Impact Hero */}
      {timeImpact && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 grid grid-cols-4 gap-4"
        >
          <div className="p-6 bg-critical-red/5 border border-critical-red/30 rounded-sm text-center">
            <Clock className="w-6 h-6 text-critical-red mx-auto mb-2" />
            <div className="text-3xl font-bold text-critical-red">{timeImpact.minutes_to_complete_attack}</div>
            <div className="text-text-dim text-xs tracking-widest mt-1">MINUTES TO COMPROMISE</div>
          </div>
          <div className="p-6 bg-warning-amber/5 border border-warning-amber/30 rounded-sm text-center">
            <AlertTriangle className="w-6 h-6 text-warning-amber mx-auto mb-2" />
            <div className="text-3xl font-bold text-warning-amber">{timeImpact.days_until_natural_discovery}</div>
            <div className="text-text-dim text-xs tracking-widest mt-1">DAYS TO DISCOVERY</div>
          </div>
          <div className="p-6 bg-strain-blue/5 border border-strain-blue/30 rounded-sm text-center">
            <Eye className="w-6 h-6 text-strain-blue mx-auto mb-2" />
            <div className="text-3xl font-bold text-strain-blue">{timeImpact.opportunity_window_days}</div>
            <div className="text-text-dim text-xs tracking-widest mt-1">OPPORTUNITY WINDOW (DAYS)</div>
          </div>
          <div className="p-6 bg-parasite-green/5 border border-parasite-green/30 rounded-sm text-center">
            <Shield className="w-6 h-6 text-parasite-green mx-auto mb-2" />
            <div className="text-3xl font-bold text-parasite-green">{timeImpact.urgency_rating}</div>
            <div className="text-text-dim text-xs tracking-widest mt-1">URGENCY RATING</div>
          </div>
        </motion.div>
      )}

      {/* Attack Paths */}
      <h2 className="text-sm font-bold text-text-dim tracking-widest mb-4 flex items-center">
        <Crosshair className="w-4 h-4 mr-2" /> ATTACK PATHS
      </h2>
      <div className="space-y-4 mb-8">
        {attackPaths.map((path, idx) => (
          <motion.div
            key={path.path_id || idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="bg-surface border border-border-dim rounded-sm overflow-hidden"
          >
            <button
              onClick={() => setExpandedPath(expandedPath === path.path_id ? null : path.path_id)}
              className="w-full p-5 flex justify-between items-center hover:bg-elevated/50 transition-colors text-left"
            >
              <div>
                <div className="text-lg font-bold text-text-primary tracking-wider">{path.name}</div>
                <div className="text-text-dim text-xs mt-1">
                  {path.attack_type} — {path.total_steps} steps — Detection: {(path.detection_probability * 100).toFixed(0)}%
                </div>
              </div>
              <div className="text-critical-red text-sm tracking-widest font-bold">
                {path.time_to_execute}
              </div>
            </button>
            {expandedPath === path.path_id && (
              <div className="border-t border-border-dim p-5 bg-void/50">
                <div className="space-y-3">
                  {path.steps.map((step) => (
                    <div key={step.step_number} className="flex items-start space-x-3 text-sm">
                      <span className="text-critical-red font-bold w-6 shrink-0">{step.step_number}.</span>
                      <div>
                        <div className="text-text-primary">{step.action}</div>
                        <div className="text-text-dim text-xs mt-1">
                          → {step.target_node} | {step.technique} | Risk: {step.detection_risk}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 pt-4 border-t border-border-dim text-xs text-text-dim">
                  <div><span className="text-critical-red">DAMAGE:</span> {path.damage_description}</div>
                  <div className="mt-1"><span className="text-warning-amber">BLAST RADIUS:</span> {path.blast_radius}</div>
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Kill Simulation Summary */}
      {killSim && (
        <div className="mb-8 p-6 bg-void border border-critical-red/30 rounded-sm">
          <h3 className="text-sm font-bold text-critical-red tracking-widest mb-4">KILL SIMULATION: {killSim.attack_path_name}</h3>
          <div className="grid grid-cols-3 gap-6 text-sm">
            <div>
              <span className="text-text-dim">Duration:</span>
              <span className="ml-2 text-text-primary">{killSim.total_duration}</span>
            </div>
            <div>
              <span className="text-text-dim">Stealth:</span>
              <span className="ml-2 text-parasite-green">{(killSim.survival_rate * 100).toFixed(0)}% invisible</span>
            </div>
            <div>
              <span className="text-text-dim">Detected:</span>
              <span className={`ml-2 ${killSim.was_detected ? 'text-warning-amber' : 'text-parasite-green'}`}>
                {killSim.was_detected ? `YES at ${killSim.detection_point}` : 'NO — GHOST OP'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Final Verdict */}
      {verdict && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mb-8 p-8 border-l-4 border-critical-red bg-critical-red/5 rounded-sm"
        >
          <h3 className="text-sm font-bold text-critical-red tracking-widest mb-4">PARASITE'S TESTIMONY</h3>
          <p className="text-text-secondary text-sm leading-relaxed italic">"{verdict}"</p>
        </motion.div>
      )}

      {/* Navigation */}
      <div className="pt-8 border-t border-border-dim flex justify-between pb-8">
        <motion.button
          onClick={() => router.push(`/session/${sessionId}/visualization`)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="px-8 py-3 border border-strain-blue text-strain-blue tracking-[0.15em] rounded-sm text-sm hover:bg-strain-blue/10 transition-colors"
        >
          VIEW 3D VISUALIZATION
        </motion.button>
        <motion.button
          onClick={() => router.push(`/session/${sessionId}/symbiotic`)}
          whileHover={{ scale: 1.02, boxShadow: '0 0 20px rgba(0,255,136,0.3)' }}
          whileTap={{ scale: 0.98 }}
          className="bg-parasite-green text-black font-bold py-3 px-8 tracking-[0.15em] rounded-sm uppercase text-sm flex items-center"
        >
          <Shield className="w-4 h-4 mr-2" /> ENTER SYMBIOTIC MODE →
        </motion.button>
      </div>
    </div>
  );
}
