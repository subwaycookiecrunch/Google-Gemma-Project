'use client';

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { parasiteAPI } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Upload, Terminal, Loader2, Zap, FileCode, Shield, Brain } from 'lucide-react';

interface ScanProgress {
  session_id: string;
  phase: string;
  total_files: number;
  files_scanned: number;
  current_file: string;
  functions_found: number;
  privilege_ops_found: number;
  percent: number;
  elapsed_seconds: number;
  eta_seconds: number;
  complete: boolean;
  error: string | null;
}

const PHASE_LABELS: Record<string, string> = {
  INITIALIZING: 'INITIALIZING PARASITE...',
  CLONING: 'CLONING REPOSITORY...',
  DISCOVERING: 'DISCOVERING SOURCE FILES...',
  PRIORITIZING: 'PRIORITIZING HIGH-VALUE TARGETS...',
  PARSING: 'PARSING AST NODES...',
  BUILDING_GRAPH: 'BUILDING INFILTRATION GRAPH...',
  DETECTING_FEEDING_POINTS: 'DETECTING FEEDING POINTS...',
  COMPLETE: 'INFILTRATION COMPLETE',
  ERROR: 'INFILTRATION FAILED',
};

export const UploadZone = () => {
  const [repoPath, setRepoPath] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<ScanProgress | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const pollRef = useRef<NodeJS.Timeout | null>(null);
  const router = useRouter();

  const handleInject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoPath) return;

    setIsLoading(true);
    setError(null);
    setProgress(null);

    try {
      // Start scan in background — returns session_id immediately
      const { session_id } = await parasiteAPI.infiltrateStart(repoPath);
      setSessionId(session_id);

      // Poll until complete
      const waitForCompletion = (): Promise<void> => {
        return new Promise((resolve, reject) => {
          const checkInterval = setInterval(async () => {
            try {
              const p = await parasiteAPI.getProgress(session_id);
              if (p && p.phase !== 'NOT_FOUND') {
                setProgress(p);
              }
              if (p.complete) {
                clearInterval(checkInterval);
                if (p.error) {
                  reject(new Error(p.error));
                } else {
                  resolve();
                }
              }
            } catch {
              // Ignore transient errors
            }
          }, 500);
        });
      };

      await waitForCompletion();

      // Get final results and navigate
      router.push(`/session/${session_id}`);
    } catch (err: any) {
      if (pollRef.current) clearInterval(pollRef.current);
      setError(err.response?.data?.detail || err.message || 'Failed to infiltrate repository');
      setIsLoading(false);
      setProgress(null);
      setSessionId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="w-full max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative"
        >
          <div className="w-full border-2 border-parasite-green/30 bg-surface/80 backdrop-blur p-8 rounded-sm">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <Loader2 className="w-6 h-6 text-parasite-green animate-spin" />
                  <div className="absolute inset-0 animate-ping">
                    <Loader2 className="w-6 h-6 text-parasite-green/30" />
                  </div>
                </div>
                <h3 className="text-parasite-green font-bold tracking-widest text-sm">
                  {progress ? PHASE_LABELS[progress.phase] || progress.phase : 'INFILTRATING...'}
                </h3>
              </div>
              {progress && progress.elapsed_seconds > 0 && (
                <span className="text-text-dim text-xs font-mono">
                  {Math.floor(progress.elapsed_seconds)}s elapsed
                  {progress.eta_seconds > 0 && ` · ~${Math.ceil(progress.eta_seconds)}s remaining`}
                </span>
              )}
            </div>

            {/* Progress Bar */}
            <div className="relative w-full h-3 bg-void rounded-full overflow-hidden mb-4 border border-border-dim">
              <motion.div
                className="h-full bg-gradient-to-r from-parasite-green/60 via-parasite-green to-parasite-green/60 rounded-full relative"
                initial={{ width: '0%' }}
                animate={{ width: progress ? `${Math.max(progress.percent, 2)}%` : '5%' }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
              </motion.div>
              {/* Scanning line effect */}
              {(!progress || progress.percent < 100) && (
                <motion.div
                  className="absolute top-0 h-full w-8 bg-gradient-to-r from-transparent via-parasite-green/40 to-transparent"
                  animate={{ left: ['-10%', '110%'] }}
                  transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                />
              )}
            </div>

            {/* Stats Grid */}
            {progress && progress.total_files > 0 && (
              <div className="grid grid-cols-4 gap-3 mb-4">
                <div className="bg-void/50 border border-border-dim rounded-sm p-3 text-center">
                  <div className="flex items-center justify-center mb-1">
                    <FileCode className="w-3.5 h-3.5 text-parasite-green/60 mr-1" />
                    <span className="text-[10px] text-text-dim tracking-wider">FILES</span>
                  </div>
                  <div className="text-parasite-green font-bold text-lg font-mono">
                    {progress.files_scanned}<span className="text-text-dim text-xs">/{progress.total_files}</span>
                  </div>
                </div>
                <div className="bg-void/50 border border-border-dim rounded-sm p-3 text-center">
                  <div className="flex items-center justify-center mb-1">
                    <Brain className="w-3.5 h-3.5 text-strain-blue/60 mr-1" />
                    <span className="text-[10px] text-text-dim tracking-wider">FUNCTIONS</span>
                  </div>
                  <div className="text-strain-blue font-bold text-lg font-mono">
                    {progress.functions_found}
                  </div>
                </div>
                <div className="bg-void/50 border border-border-dim rounded-sm p-3 text-center">
                  <div className="flex items-center justify-center mb-1">
                    <Shield className="w-3.5 h-3.5 text-warning-amber/60 mr-1" />
                    <span className="text-[10px] text-text-dim tracking-wider">PRIV_OPS</span>
                  </div>
                  <div className="text-warning-amber font-bold text-lg font-mono">
                    {progress.privilege_ops_found}
                  </div>
                </div>
                <div className="bg-void/50 border border-border-dim rounded-sm p-3 text-center">
                  <div className="flex items-center justify-center mb-1">
                    <Zap className="w-3.5 h-3.5 text-critical-red/60 mr-1" />
                    <span className="text-[10px] text-text-dim tracking-wider">PROGRESS</span>
                  </div>
                  <div className="text-critical-red font-bold text-lg font-mono">
                    {progress.percent.toFixed(0)}%
                  </div>
                </div>
              </div>
            )}

            {/* Current File */}
            <div className="bg-void border border-border-dim rounded-sm px-3 py-2 font-mono text-xs overflow-hidden">
              <span className="text-parasite-green/60 mr-2">{'>'}</span>
              <AnimatePresence mode="wait">
                <motion.span
                  key={progress?.current_file || 'init'}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  transition={{ duration: 0.2 }}
                  className="text-text-secondary"
                >
                  {progress?.current_file 
                    ? `Parsing ${progress.current_file}` 
                    : 'Initializing scan...'}
                </motion.span>
              </AnimatePresence>
              <span className="animate-pulse text-parasite-green ml-1">█</span>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.5 }}
        className="relative"
      >
        <form onSubmit={handleInject} className="flex flex-col items-center">
          <div className="w-full border-2 border-dashed border-border-glow bg-surface/50 p-12 rounded-sm relative overflow-hidden group hover:border-parasite-dim transition-colors duration-500">
            {/* Corner brackets */}
            <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-parasite-green/50 m-2"></div>
            <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-parasite-green/50 m-2"></div>
            <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-parasite-green/50 m-2"></div>
            <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-parasite-green/50 m-2"></div>
            
            <div className="flex flex-col items-center justify-center text-center space-y-6">
              <Upload className="w-12 h-12 text-parasite-green/50 group-hover:text-parasite-green transition-colors duration-500" />
              
              <div>
                <h3 className="text-xl font-bold tracking-widest text-text-primary mb-2">TARGET REPOSITORY</h3>
                <p className="text-text-dim text-sm">Paste a GitHub URL or local path</p>
              </div>

              <div className="w-full max-w-md relative">
                <Terminal className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-parasite-green/50" />
                <input
                  type="text"
                  value={repoPath}
                  onChange={(e) => setRepoPath(e.target.value)}
                  placeholder="https://github.com/user/repo  or  /path/to/repo"
                  className="w-full bg-void border border-border-dim rounded-sm py-3 pl-10 pr-4 text-parasite-green placeholder:text-text-dim focus:outline-none focus:border-parasite-green focus:ring-1 focus:ring-parasite-green/50 font-mono transition-all"
                  required
                />
              </div>

              {error && (
                <div className="text-critical-red text-sm bg-critical-glow px-4 py-2 border border-critical-red rounded-sm w-full max-w-md">
                  Error: {error}
                </div>
              )}
            </div>
          </div>

          <motion.button
            whileHover={{ scale: 1.02, boxShadow: '0 0 20px var(--parasite-glow)' }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            className="mt-8 bg-parasite-green text-black font-bold py-4 px-12 tracking-[0.2em] rounded-sm uppercase relative overflow-hidden group"
          >
            <span className="relative z-10">Inject Parasite</span>
            <div className="absolute inset-0 bg-white/20 transform -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out" />
          </motion.button>
        </form>
      </motion.div>
    </div>
  );
};
