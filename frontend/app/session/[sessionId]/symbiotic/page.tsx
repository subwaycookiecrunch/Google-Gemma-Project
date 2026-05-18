'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { parasiteAPI } from '@/lib/api';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, Activity, FileCode2, Info, Download } from 'lucide-react';
import { LoadingParasite } from '@/components/parasite/LoadingParasite';
import { HealingPlanCard } from '@/components/parasite/HealingPlanCard';
import { DefensePathCard } from '@/components/parasite/DefensePathCard';
import { HardeningGuide } from '@/components/parasite/HardeningGuide';
import { usePersonality } from '@/lib/PersonalityContext';

type TabType = 'healing' | 'defense' | 'hardening' | 'verdict';

export default function SymbioticDashboard() {
  const paramsObj = useParams();
  const sessionId = paramsObj.sessionId as string;
  const router = useRouter();
  const { personality } = usePersonality();
  
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabType>('healing');
  
  const [healingPlans, setHealingPlans] = useState<any[]>([]);
  const [defensePaths, setDefensePaths] = useState<any[]>([]);
  const [hardeningGuide, setHardeningGuide] = useState<any>(null);
  const [verdict, setVerdict] = useState<string>('');
  const [generatingReport, setGeneratingReport] = useState(false);

  // If personality switches back to PARASITIC, bounce them to the reveal page
  useEffect(() => {
    if (personality === 'PARASITIC') {
      router.push(`/session/${sessionId}/reveal`);
    }
  }, [personality, router, sessionId]);

  useEffect(() => {
    const fetchSymbioticData = async () => {
      try {
        // First ensure symbiotic engine has run for this session
        await parasiteAPI.runSymbiotic(sessionId);
        
        // Then fetch all the data
        const [hp, dp, hg, v] = await Promise.all([
          parasiteAPI.getHealingPlans(sessionId),
          parasiteAPI.getDefensePaths(sessionId),
          parasiteAPI.getHardeningGuide(sessionId),
          parasiteAPI.getSymbioticVerdict(sessionId)
        ]);
        
        setHealingPlans(hp.healing_plans);
        setDefensePaths(dp.defense_paths);
        setHardeningGuide(hg.hardening_guide);
        setVerdict(v.symbiotic_verdict);
      } catch (e) {
        console.error("Symbiotic API Error:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchSymbioticData();
  }, [sessionId]);

  if (loading) return <LoadingParasite />;

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

  const tabs = [
    { id: 'healing', name: 'HEALING PLANS', icon: Activity },
    { id: 'defense', name: 'DEFENSE PATHS', icon: Shield },
    { id: 'hardening', name: 'HARDENING GUIDE', icon: FileCode2 },
    { id: 'verdict', name: 'SYMBIOTIC VERDICT', icon: Info },
  ];

  return (
    <div className="flex w-full h-[calc(100vh-56px)] bg-void overflow-hidden text-text-primary">
      {/* LOCAL SIDEBAR */}
      <div className="w-[320px] flex-shrink-0 bg-surface/80 backdrop-blur border-r border-border-dim flex flex-col z-10">
        <div className="p-6 border-b border-border-dim bg-parasite-green/5">
          <h2 className="text-xs text-text-dim font-bold tracking-widest mb-4 flex items-center">
            <Shield className="w-4 h-4 mr-2 text-parasite-green" />
            SYMBIOTIC MODE
          </h2>
          {hardeningGuide && (
            <div className="space-y-4">
              <div className="flex justify-between items-end">
                <span className="text-sm text-text-secondary">Grade</span>
                <span className={`text-3xl font-bold font-mono ${hardeningGuide.risk_score < 50 ? 'text-parasite-green' : 'text-warning-amber'}`}>
                  {hardeningGuide.risk_grade}
                </span>
              </div>
              <div className="h-1 bg-border-dim rounded-full overflow-hidden">
                <div 
                  className={`h-full ${hardeningGuide.risk_score < 50 ? 'bg-parasite-green' : 'bg-warning-amber'}`}
                  style={{ width: `${100 - hardeningGuide.risk_score}%` }}
                />
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-elevated p-2 border border-border-dim rounded-sm">
                  <div className="text-text-dim mb-1">ISSUES</div>
                  <div className="text-text-primary font-bold">{hardeningGuide.critical_findings}</div>
                </div>
                <div className="bg-elevated p-2 border border-border-dim rounded-sm">
                  <div className="text-text-dim mb-1">QUICK WINS</div>
                  <div className="text-parasite-green font-bold">{hardeningGuide.quick_wins.length}</div>
                </div>
              </div>
            </div>
          )}
        </div>

        <nav className="p-4 space-y-2">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`w-full flex items-center px-4 py-3 text-sm tracking-wider rounded-sm transition-colors ${
                activeTab === tab.id 
                  ? 'bg-parasite-green/10 text-parasite-green border border-parasite-green/30' 
                  : 'text-text-secondary hover:text-text-primary hover:bg-elevated'
              }`}
            >
              <tab.icon className="w-4 h-4 mr-3" />
              {tab.name}
            </button>
          ))}
        </nav>
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 overflow-y-auto p-8 relative">
        <AnimatePresence mode="wait">
          {activeTab === 'healing' && (
            <motion.div key="healing" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="max-w-4xl mx-auto space-y-6">
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-text-primary mb-2">Healing Plans</h2>
                <p className="text-text-secondary">Specific code remediation strategies for identified vulnerabilities.</p>
              </div>
              {healingPlans.map((plan, i) => (
                <HealingPlanCard key={i} plan={plan} />
              ))}
            </motion.div>
          )}

          {activeTab === 'defense' && (
            <motion.div key="defense" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="max-w-4xl mx-auto space-y-6">
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-text-primary mb-2">Defense Paths</h2>
                <p className="text-text-secondary">Architectural defenses to prevent complex attack chains.</p>
              </div>
              {defensePaths.map((path, i) => (
                <DefensePathCard key={i} path={path} />
              ))}
            </motion.div>
          )}

          {activeTab === 'hardening' && hardeningGuide && (
            <motion.div key="hardening" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="max-w-4xl mx-auto space-y-6">
               <div className="mb-8">
                <h2 className="text-2xl font-bold text-text-primary mb-2">Security Hardening Guide</h2>
                <p className="text-text-secondary">Comprehensive strategy to secure the system architecture.</p>
              </div>
              <HardeningGuide guide={hardeningGuide} />
            </motion.div>
          )}

          {activeTab === 'verdict' && (
            <motion.div key="verdict" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="max-w-3xl mx-auto flex flex-col items-center justify-center min-h-[500px]">
              <div className="bg-void border border-parasite-green/20 p-12 rounded-sm shadow-[0_0_50px_rgba(0,255,136,0.05)] relative overflow-hidden mb-8">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-parasite-green to-transparent opacity-50" />
                <Shield className="w-12 h-12 text-parasite-green mb-8 opacity-50" />
                <p className="text-xl text-parasite-green/90 leading-relaxed font-mono">
                  {verdict}
                </p>
                <div className="mt-8 flex items-center">
                  <span className="w-3 h-6 bg-parasite-green animate-pulse" />
                </div>
              </div>
              
              <button 
                onClick={handleGenerateReport}
                disabled={generatingReport}
                className="flex items-center px-6 py-3 bg-parasite-green text-black font-bold tracking-widest rounded-sm hover:bg-parasite-green/80 transition-colors disabled:opacity-50"
              >
                {generatingReport ? (
                  <span className="animate-pulse">GENERATING REPORT...</span>
                ) : (
                  <>
                    <Download className="w-5 h-5 mr-3" />
                    DOWNLOAD AUTOPSY REPORT
                  </>
                )}
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
