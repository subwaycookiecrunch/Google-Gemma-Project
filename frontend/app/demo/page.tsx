'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Activity, Skull, Download } from 'lucide-react';
import { parasiteAPI } from '@/lib/api';
import { ParasiteCanvas, Phase } from '@/components/parasite/three/ParasiteCanvas';
import { usePersonality } from '@/lib/PersonalityContext';
import { ErrorBoundary } from '@/components/ErrorBoundary';

// Define the screens for the demo
type DemoScreen = 1 | 2 | 3 | 4 | 5 | 6 | 7;

export default function DemoPage() {
  const router = useRouter();
  const [screen, setScreen] = useState<DemoScreen>(1);
  const [sessionId, setSessionId] = useState<string>('');
  
  // Data state
  const [graphData, setGraphData] = useState<any>(null);
  const [feedingPoints, setFeedingPoints] = useState<any[]>([]);
  const [dominantStrain, setDominantStrain] = useState<any>(null);
  const [strains, setStrains] = useState<any[]>([]);
  const [attackPaths, setAttackPaths] = useState<any[]>([]);
  const [verdict, setVerdict] = useState<string>('');
  const [artifacts, setArtifacts] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  const { personality, togglePersonality } = usePersonality();
  const isSymbiotic = personality === 'SYMBIOTIC';

  // Visualization state for Screen 4
  const [vizPhase, setVizPhase] = useState<Phase>('IDLE');
  
  useEffect(() => {
    const loadDemoData = async () => {
      try {
        // Fetch session ID
        const res = await fetch('/demo-session.json');
        if (!res.ok) throw new Error('Demo session not found. Run ./demo.sh');
        const data = await res.json();
        const sid = data.session_id;
        setSessionId(sid);

        // Pre-load all data to prevent waiting during presentation
        const [gRes, fpRes, dRes, sRes, apRes, vRes, artRes, stRes] = await Promise.all([
          parasiteAPI.getGraph(sid),
          parasiteAPI.getFeedingPoints(sid),
          parasiteAPI.getDominant(sid),
          parasiteAPI.getStrains(sid),
          parasiteAPI.getAttackPaths(sid),
          parasiteAPI.getFinalVerdict(sid),
          parasiteAPI.getArtifacts(sid).catch(() => null),
          parasiteAPI.getStats(sid).catch(() => null)
        ]);

        setGraphData(gRes.graph);
        setFeedingPoints(fpRes.feeding_points);
        setDominantStrain(dRes.dominant);
        setStrains(sRes.strains || []);
        setAttackPaths(apRes.attack_paths);
        setVerdict(vRes.final_verdict);
        setArtifacts(artRes);
        setStats(stRes?.stats || null);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    loadDemoData();
  }, []);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        setScreen(s => Math.min(s + 1, 7) as DemoScreen);
      } else if (e.key === 'ArrowLeft') {
        setScreen(s => Math.max(s - 1, 1) as DemoScreen);
      } else if (e.key === 'f' || e.key === 'F') {
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen();
        } else {
          document.exitFullscreen();
        }
      } else if (e.key === 'p' || e.key === 'P') {
        togglePersonality();
      } else if (e.key === 'r' || e.key === 'R') {
        setScreen(1);
        if (personality === 'SYMBIOTIC') togglePersonality();
      } else if (e.key === 'Escape') {
        router.push('/');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [personality, togglePersonality, router]);

  // Screen 1: Auto-advance after 5 seconds
  useEffect(() => {
    if (screen === 1 && !loading) {
      const timer = setTimeout(() => setScreen(2), 5000);
      return () => clearTimeout(timer);
    }
  }, [screen, loading]);

  // Screen 4: Auto-play visualization
  useEffect(() => {
    if (screen === 4) {
      setVizPhase('INFILTRATING');
      const t1 = setTimeout(() => setVizPhase('EVOLVING'), 4000);
      const t2 = setTimeout(() => setVizPhase('REVEALING'), 8000);
      const t3 = setTimeout(() => setVizPhase('COMPLETE'), 12000);
      return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
    }
  }, [screen]);

  if (loading) return <div className="h-screen w-screen bg-void flex items-center justify-center text-parasite-green animate-pulse">LOADING DEMO ASSETS...</div>;

  return (
    <div className="h-screen w-screen bg-void text-text-primary overflow-hidden font-mono selection:bg-parasite-green/30">
      <AnimatePresence mode="wait">
        
        {/* SCREEN 1: INTRO */}
        {screen === 1 && (
          <motion.div key="s1" className="h-full flex flex-col items-center justify-center space-y-8" exit={{ opacity: 0 }}>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} className="text-xl text-text-secondary">I don't scan your code.</motion.div>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 2.0 }} className="text-2xl text-text-primary">I become it.</motion.div>
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 3.5 }} className="text-6xl font-bold text-parasite-green tracking-[0.3em] mt-8">PARASITE EVOLVED</motion.div>
          </motion.div>
        )}

        {/* SCREEN 2: INFILTRATION RESULTS */}
        {screen === 2 && (
          <motion.div key="s2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="h-full p-12 flex flex-col justify-center">
            <h1 className="text-4xl text-warning-amber tracking-widest font-bold mb-12 flex items-center"><Activity className="mr-4 w-10 h-10"/> SYSTEM COMPROMISED</h1>
            <div className="grid grid-cols-2 gap-12">
              <div className="space-y-6">
                <div className="text-6xl font-bold text-critical-red">{feedingPoints.length} CRITICAL WOUNDS</div>
                <div className="text-4xl text-text-primary">{stats?.privilege_ops || '—'} PRIVILEGE OPERATIONS</div>
                <div className="text-4xl text-text-secondary">{stats?.dataflow_paths || '—'} TAINT PATHS</div>
                <div className="text-2xl text-critical-red border border-critical-red inline-block px-4 py-2 mt-8 animate-pulse">SYSTEM: VULNERABLE</div>
              </div>
              <div className="space-y-4">
                {feedingPoints.slice(0, 5).map(fp => (
                  <div key={fp.node_id} className="bg-elevated border border-warning-amber/30 p-4 rounded-sm flex justify-between items-center text-warning-amber text-xl">
                    <span>{fp.name}()</span>
                    <span>{fp.final_score.toFixed(1)}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="absolute bottom-12 right-12 text-text-dim text-sm tracking-widest animate-pulse">[SPACE] SHOW THE EVOLUTION →</div>
          </motion.div>
        )}

        {/* SCREEN 3: EVOLUTION */}
        {screen === 3 && (
          <motion.div key="s3" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="h-full p-12 flex flex-col justify-center items-center text-center">
            <h1 className="text-4xl text-strain-blue tracking-widest font-bold mb-12">EVOLUTION COMPLETE</h1>
            <div className="bg-strain-blue/10 border border-strain-blue p-12 rounded-sm w-full max-w-4xl space-y-8">
              <div className="text-5xl font-bold text-strain-blue">DOMINANT STRAIN: {dominantStrain?.strain_id || 'STRAIN-ALPHA'}</div>
              <div className="text-3xl text-text-primary">FITNESS: {(dominantStrain?.fitness_score || 0.83).toFixed(2)} — <span className="text-parasite-green">PERFECT CAMOUFLAGE</span></div>
              <div className="text-2xl text-text-secondary font-mono border-t border-strain-blue/30 pt-8 mt-8">
                ATTACK VECTOR:<br/>
                <span className="text-critical-red font-bold mt-4 block">{dominantStrain?.target_feeding_point?.name || 'AUTH_BYPASS'} → COMPLETE_COMPROMISE</span>
              </div>
            </div>
            <div className="absolute bottom-12 right-12 text-text-dim text-sm tracking-widest animate-pulse">[SPACE] REVEAL THE KILL →</div>
          </motion.div>
        )}

        {/* SCREEN 4: VISUALIZATION */}
        {screen === 4 && (
          <motion.div key="s4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="h-full w-full relative">
            <div className="absolute top-12 left-12 z-10 bg-void/80 p-6 border border-border-dim backdrop-blur">
              <div className="text-xl font-bold text-parasite-green mb-2">{vizPhase}</div>
              <div className="text-sm text-text-dim">Simulating AI execution timeline in 3D AST space.</div>
            </div>
            <ErrorBoundary>
              <ParasiteCanvas 
                graphData={graphData} 
                phase={vizPhase} 
                feedingPoints={feedingPoints}
                dominantStrain={dominantStrain}
                strains={strains}
                compromisedNodeIds={attackPaths[0]?.steps.map((s:any) => s.target_node) || []}
                focusTarget={null}
                onNodeClick={() => {}}
                isSymbiotic={isSymbiotic}
              />
            </ErrorBoundary>
            <div className="absolute bottom-12 right-12 text-text-dim text-sm tracking-widest animate-pulse z-10 bg-void/50 px-2 py-1">[SPACE] FLIP THE SWITCH →</div>
          </motion.div>
        )}

        {/* SCREEN 5: PERSONALITY TOGGLE */}
        {screen === 5 && (
          <motion.div key="s5" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="h-full w-full flex flex-col items-center justify-center relative">
            <div className="text-5xl font-bold mb-16 tracking-widest text-text-primary">SAME SYSTEM. TWO FACES.</div>
            
            <div className={`text-3xl border px-8 py-4 mb-16 transition-colors duration-500 ${isSymbiotic ? 'border-parasite-green text-parasite-green bg-parasite-green/10' : 'border-critical-red text-critical-red bg-critical-red/10'}`}>
              {isSymbiotic ? 'SYMBIOTIC MODE' : 'PARASITIC MODE'}
            </div>

            <div className="max-w-4xl text-center text-xl leading-loose">
              {isSymbiotic ? (
                <span className="text-parasite-green">"I'm giving you a map of your own wounds. Fix them before something less patient finds them."</span>
              ) : (
                <span className="text-critical-red">"I found everything. I could have taken everything."</span>
              )}
            </div>

            <div className="absolute bottom-12 text-text-dim text-sm tracking-widest animate-pulse flex flex-col items-center space-y-4">
              <div>Press [P] to toggle personality.</div>
              <div>[SPACE] SHOW THE ARTIFACT →</div>
            </div>
          </motion.div>
        )}

        {/* SCREEN 6: CERTIFICATE */}
        {screen === 6 && (
          <motion.div key="s6" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="h-full p-12 flex flex-col items-center justify-center">
            <h1 className="text-4xl text-parasite-green tracking-widest font-bold mb-12 flex items-center"><Shield className="mr-4 w-10 h-10"/> INFECTION CERTIFICATE</h1>
            
            {artifacts?.qr_code_base64 && (
              <div className="bg-white p-4 mb-8 border-4 border-parasite-green">
                <img src={artifacts.qr_code_base64} alt="QR Code" className="w-64 h-64" />
              </div>
            )}
            
            <div className="text-2xl text-text-primary mb-4 tracking-widest">SCAN TO VERIFY COMPROMISE</div>
            <div className="text-lg text-text-dim mb-12 font-mono bg-elevated px-4 py-2 border border-border-dim truncate max-w-2xl">
              {artifacts?.certificate?.tx_hash || '0x... (Fallback Mode)'}
            </div>

            {artifacts?.report_download_url && (
              <button 
                onClick={() => window.open(artifacts.report_download_url, '_blank')}
                className="flex items-center px-8 py-4 bg-parasite-green text-black font-bold tracking-widest rounded-sm hover:bg-parasite-green/80 transition-colors"
              >
                <Download className="w-6 h-6 mr-3" />
                DOWNLOAD AUTOPSY REPORT
              </button>
            )}
            
            <div className="absolute bottom-12 right-12 text-text-dim text-sm tracking-widest animate-pulse">[SPACE] PRESENT VERDICT →</div>
          </motion.div>
        )}

        {/* SCREEN 7: FINAL VERDICT */}
        {screen === 7 && (
          <motion.div key="s7" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="h-full w-full flex items-center justify-center px-24">
            <motion.div 
              initial={{ opacity: 0, y: 20 }} 
              animate={{ opacity: 1, y: 0 }} 
              transition={{ delay: 1, duration: 2 }}
              className="text-3xl text-parasite-green/80 leading-[2.5] font-mono"
            >
              "{verdict}"
            </motion.div>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  );
}
