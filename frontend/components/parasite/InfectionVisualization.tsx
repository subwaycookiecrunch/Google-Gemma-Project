'use client';

import React, { useState, useEffect } from 'react';
import * as THREE from 'three';
import { parasiteAPI } from '@/lib/api';
import { GraphData, FeedingPoint, Strain, AttackPath, KillSimulation, TimeToImpact } from '@/lib/types';
import { ParasiteCanvas, Phase } from './three/ParasiteCanvas';
import { StatusTerminal } from './StatusTerminal';
import { Shield, Activity, Skull, TerminalSquare, RefreshCw, Download } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePersonality } from '@/lib/PersonalityContext';
import { PersonalityToggle } from './PersonalityToggle';
import { useRouter } from 'next/navigation';
import { ErrorBoundary } from '@/components/ErrorBoundary';

interface Props {
  sessionId: string;
}

export const InfectionVisualization: React.FC<Props> = ({ sessionId }) => {
  const [phase, setPhase] = useState<Phase>('IDLE');
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [feedingPoints, setFeedingPoints] = useState<FeedingPoint[]>([]);
  const [dominantStrain, setDominantStrain] = useState<Strain | undefined>(undefined);
  const [strains, setStrains] = useState<Strain[]>([]);
  const [attackPaths, setAttackPaths] = useState<AttackPath[]>([]);
  const [killSim, setKillSim] = useState<KillSimulation | null>(null);
  const [timeImpact, setTimeImpact] = useState<TimeToImpact | null>(null);
  const [verdict, setVerdict] = useState<string>('');
  const [logs, setLogs] = useState<string[]>([]);
  const [focusTarget, setFocusTarget] = useState<THREE.Vector3 | null>(null);
  const [compromisedNodeIds, setCompromisedNodeIds] = useState<string[]>([]);
  const [generatingReport, setGeneratingReport] = useState(false);

  const { personality, tokens } = usePersonality();
  const isSymbiotic = personality === 'SYMBIOTIC';
  const router = useRouter();

  useEffect(() => {
    // Load initial graph data
    const init = async () => {
      try {
        const { graph } = await parasiteAPI.getGraph(sessionId);
        setGraphData(graph);
        setLogs(prev => [...prev, '[SYSTEM] Graph data loaded into 3D context.']);
      } catch (e) {
        console.error(e);
      }
    };
    init();
  }, [sessionId]);

  const runSequence = async () => {
    try {
      // 1. INFILTRATING
      setPhase('INFILTRATING');
      setLogs(prev => [...prev, '[INFILTRATION] Analyzing AST nodes and computing privilege flow...']);
      const fpData = await parasiteAPI.getFeedingPoints(sessionId);
      setFeedingPoints(fpData.feeding_points);
      setLogs(prev => [...prev, `[INFILTRATION] ${fpData.count} feeding points detected.`]);
      await new Promise(r => setTimeout(r, 2000));

      // 2. EVOLVING — trigger evolution if not already done
      setPhase('EVOLVING');
      setLogs(prev => [...prev, '[EVOLUTION] Spawning genetic mutations...']);
      try {
        // Try to get existing data first
        const [domData, strainsData] = await Promise.all([
          parasiteAPI.getDominant(sessionId),
          parasiteAPI.getStrains(sessionId)
        ]);
        setDominantStrain(domData.dominant);
        setStrains(strainsData.strains || []);
        setLogs(prev => [...prev, `[EVOLUTION] Dominant strain: ${domData.dominant.strain_id}`]);
      } catch {
        // Evolution hasn't been run — trigger it
        setLogs(prev => [...prev, '[EVOLUTION] No evolution data found. Running evolution...']);
        const evoRes = await parasiteAPI.evolve(sessionId);
        setStrains(evoRes.strains || []);
        setDominantStrain(evoRes.dominant_strain || undefined);
        setLogs(prev => [...prev, `[EVOLUTION] Evolution complete. ${evoRes.strains?.length || 0} strains.`]);
      }
      await new Promise(r => setTimeout(r, 2000));

      // 3. REVEALING — trigger revelation if not already done
      setPhase('REVEALING');
      setLogs(prev => [...prev, '[REVELATION] Simulating attack execution timeline...']);
      try {
        // Try to get existing data first
        const [apData, killData, timeData, verdictData] = await Promise.all([
          parasiteAPI.getAttackPaths(sessionId),
          parasiteAPI.getKillSimulation(sessionId),
          parasiteAPI.getTimeToImpact(sessionId),
          parasiteAPI.getFinalVerdict(sessionId)
        ]);
        setAttackPaths(apData.attack_paths);
        setKillSim(killData.kill_simulation);
        setTimeImpact(timeData.time_to_impact);
        setVerdict(verdictData.final_verdict);
        
        if (apData.attack_paths.length > 0) {
          const bestPath = apData.attack_paths[0];
          setCompromisedNodeIds(bestPath.steps.map(s => s.target_node));
        }
        setLogs(prev => [...prev, `[REVELATION] Time to impact: ${timeData.time_to_impact.minutes_to_complete_attack}m`]);
      } catch {
        // Revelation hasn't been run — trigger it
        setLogs(prev => [...prev, '[REVELATION] No revelation data found. Running revelation...']);
        const revRes = await parasiteAPI.reveal(sessionId);
        setAttackPaths(revRes.attack_paths || []);
        setKillSim(revRes.kill_simulation || null);
        setTimeImpact(revRes.time_to_impact || null);
        setVerdict(revRes.final_verdict || '');
        
        if (revRes.attack_paths?.length > 0) {
          setCompromisedNodeIds(revRes.attack_paths[0].steps.map((s: any) => s.target_node));
        }
        setLogs(prev => [...prev, `[REVELATION] Revelation complete.`]);
      }
      await new Promise(r => setTimeout(r, 3000));

      // 4. COMPLETE
      setPhase('COMPLETE');
      setLogs(prev => [...prev, '[SYSTEM] INFECTION COMPLETE.']);

    } catch (e: any) {
      setLogs(prev => [...prev, `[ERROR] ${e.message}`]);
    }
  };

  const handleNodeClick = (nodeId: string, position: THREE.Vector3) => {
    setFocusTarget(position);
  };

  const resetView = () => {
    setFocusTarget(null);
  };

  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    try {
      const res = await parasiteAPI.generateArtifacts(sessionId);
      if (res.report_download_url) {
        window.open(res.report_download_url, '_blank');
      }
    } catch (e) {
      console.error(e);
      alert('Failed to generate report');
    } finally {
      setGeneratingReport(false);
    }
  };

  const getPhaseIndicator = () => {
    const phases: Phase[] = ['IDLE', 'INFILTRATING', 'EVOLVING', 'REVEALING', 'COMPLETE'];
    return (
      <div className="flex items-center space-x-2 text-xs font-mono mb-6 pb-4 border-b border-border-dim">
        {phases.map((p, i) => {
          const isActive = p === phase;
          const isPast = phases.indexOf(phase) > i;
          return (
            <React.Fragment key={p}>
              <div className={`flex items-center ${isActive ? 'text-parasite-green' : isPast ? 'text-text-dim' : 'text-border-dim'}`}>
                {isActive ? '●' : '○'} <span className="ml-1 hidden sm:inline">{p}</span>
              </div>
              {i < phases.length - 1 && <span className="text-border-dim">-</span>}
            </React.Fragment>
          );
        })}
      </div>
    );
  };

  return (
    <div className="flex w-full h-[calc(100vh-56px)] bg-void overflow-hidden text-text-primary">
      
      {/* LEFT PANEL */}
      <div className="w-[380px] flex-shrink-0 bg-surface/80 backdrop-blur border-r border-border-dim flex flex-col z-10">
        <div className="p-6 flex-1 overflow-y-auto">
          <div className="mb-6 flex justify-between items-center">
            {getPhaseIndicator()}
            <PersonalityToggle size="sm" />
          </div>

          <AnimatePresence mode="wait">
            {phase === 'IDLE' && (
              <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                <h3 className="text-parasite-green font-bold tracking-widest text-lg">SYSTEM READY</h3>
                <p className="text-text-secondary text-sm">3D context initialized. Codebase mapped.</p>
                <div className="bg-elevated p-4 border border-border-dim rounded-sm">
                  <div className="flex justify-between text-sm mb-2"><span className="text-text-dim">NODES:</span> <span>{graphData?.nodes.length || 0}</span></div>
                  <div className="flex justify-between text-sm"><span className="text-text-dim">EDGES:</span> <span>{graphData?.edges.length || 0}</span></div>
                </div>
                <button 
                  onClick={runSequence}
                  className="w-full bg-parasite-green text-black font-bold py-3 uppercase tracking-widest rounded-sm hover:shadow-[0_0_15px_#00ff8844] transition-all"
                >
                  BEGIN INFILTRATION
                </button>
              </motion.div>
            )}

            {phase === 'INFILTRATING' && (
              <motion.div key="infiltrating" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                <h3 className={`font-bold tracking-widest flex items-center ${isSymbiotic ? 'text-parasite-green' : 'text-warning-amber'}`}>
                  <Activity className="mr-2 w-4 h-4" /> {isSymbiotic ? 'DIAGNOSING VULNERABILITIES' : 'SCANNING FOR VULNERABILITIES'}
                </h3>
                <div className="space-y-2">
                  {feedingPoints.slice(0, 5).map(fp => (
                    <div key={fp.node_id} className={`text-xs bg-elevated border p-2 rounded-sm flex justify-between ${isSymbiotic ? 'border-parasite-green/30 text-parasite-green' : 'border-warning-amber/30 text-warning-amber'}`}>
                      <span className="truncate max-w-[200px]">{fp.name}()</span>
                      <span className="text-text-dim">{fp.final_score.toFixed(1)}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {phase === 'EVOLVING' && dominantStrain && (
              <motion.div key="evolving" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                <h3 className="text-strain-blue font-bold tracking-widest flex items-center"><TerminalSquare className="mr-2 w-4 h-4" /> STRAIN EVOLUTION</h3>
                <div className="bg-strain-blue/10 border border-strain-blue p-4 rounded-sm">
                  <div className="text-strain-blue text-lg font-bold mb-1">DOMINANT: {dominantStrain.strain_id}</div>
                  <div className="text-xs text-text-secondary mb-4">Fitness: {dominantStrain.fitness_score.toFixed(2)}</div>
                  <div className="text-xs text-text-primary break-words">Target: {dominantStrain.target_feeding_point.name}</div>
                </div>
              </motion.div>
            )}

            {phase === 'REVEALING' && attackPaths.length > 0 && (
              <motion.div key="revealing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                <h3 className={`font-bold tracking-widest flex items-center ${isSymbiotic ? 'text-parasite-green' : 'text-critical-red'}`}>
                  <Skull className="mr-2 w-4 h-4" /> {isSymbiotic ? 'DEFENSE BLUEPRINT' : 'KILL SEQUENCE MAPPED'}
                </h3>
                <div className={`${isSymbiotic ? 'bg-parasite-green/10 border-parasite-green' : 'bg-critical-glow border-critical-red'} border p-4 rounded-sm`}>
                  <div className={`${isSymbiotic ? 'text-parasite-green' : 'text-critical-red'} font-bold mb-2`}>{attackPaths[0].name}</div>
                  <div className="space-y-2">
                    {attackPaths[0].steps.slice(0, 4).map((s, i) => (
                      <div key={i} className="text-[10px] flex items-start">
                        <span className={`${isSymbiotic ? 'text-parasite-green' : 'text-critical-red'} mr-2`}>[{i+1}]</span>
                        <span className="text-text-primary">{isSymbiotic ? `Secure ${s.target_node}` : s.action}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {phase === 'COMPLETE' && (
              <motion.div key="complete" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-4">
                <h3 className="text-parasite-green font-bold tracking-widest flex items-center"><Shield className="mr-2 w-4 h-4" /> SYSTEM COMPROMISED</h3>
                {timeImpact && (
                  <div className="flex gap-4 mb-4">
                    <div className="bg-elevated border border-border-dim p-3 rounded-sm flex-1">
                      <div className="text-[10px] text-text-dim mb-1">ATTACK TIME</div>
                      <div className="text-parasite-green font-bold">{timeImpact.minutes_to_complete_attack}m</div>
                    </div>
                    <div className="bg-elevated border border-border-dim p-3 rounded-sm flex-1">
                      <div className="text-[10px] text-text-dim mb-1">SURVIVAL</div>
                      <div className="text-parasite-green font-bold">{(killSim?.survival_rate || 0) * 100}%</div>
                    </div>
                  </div>
                )}
                <div className="bg-void border border-parasite-dim p-4 rounded-sm">
                  <div className="text-parasite-dim text-[11px] leading-relaxed italic">
                    "{verdict.substring(0, 150)}..."
                  </div>
                </div>
                
                <button 
                  onClick={handleGenerateReport}
                  disabled={generatingReport}
                  className="w-full flex items-center justify-center px-4 py-3 bg-transparent border border-parasite-green text-parasite-green font-bold tracking-widest rounded-sm hover:bg-parasite-green hover:text-black transition-colors disabled:opacity-50 mt-4"
                >
                  {generatingReport ? (
                    <span className="animate-pulse">GENERATING AUTOPSY...</span>
                  ) : (
                    <>
                      <Download className="w-4 h-4 mr-2" />
                      DOWNLOAD AUTOPSY REPORT
                    </>
                  )}
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Terminal Log at Bottom of Panel */}
        <div className="h-64 border-t border-border-dim mt-auto bg-void">
          <StatusTerminal logs={logs} title="SYSTEM.LOG" height="h-full" />
        </div>
      </div>

      {/* RIGHT PANEL - 3D CANVAS */}
      <div className="flex-1 relative">
        <ErrorBoundary>
          <ParasiteCanvas 
            graphData={graphData} 
            phase={phase} 
            feedingPoints={feedingPoints}
            dominantStrain={dominantStrain}
            strains={strains}
            compromisedNodeIds={compromisedNodeIds}
            focusTarget={focusTarget}
            onNodeClick={handleNodeClick}
            isSymbiotic={isSymbiotic}
          />
        </ErrorBoundary>
        
        {/* Overlays */}
        <div className="absolute top-6 right-6 flex items-center space-x-2 bg-void/80 border border-border-dim px-4 py-2 rounded-sm backdrop-blur">
          <span className="w-2 h-2 rounded-full bg-parasite-green animate-pulse"></span>
          <span className="text-xs font-mono text-parasite-green tracking-widest">LIVE VIEW</span>
        </div>

        {focusTarget && (
          <button 
            onClick={resetView}
            className="absolute bottom-6 right-6 flex items-center space-x-2 bg-surface/80 border border-border-dim px-4 py-2 rounded-sm backdrop-blur hover:bg-elevated hover:text-parasite-green transition-colors text-xs font-mono text-text-primary"
          >
            <RefreshCw className="w-4 h-4" />
            <span>RESET CAMERA</span>
          </button>
        )}
      </div>
    </div>
  );
};
