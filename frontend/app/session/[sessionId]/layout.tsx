'use client';

import React, { useEffect, useState } from 'react';
import { parasiteAPI } from '@/lib/api';
import { InfiltrationStats, InfiltrationResult } from '@/lib/types';
import { Header } from '@/components/parasite/Header';
import { usePathname, useRouter, useParams } from 'next/navigation';
import { Shield, Activity, Skull, TerminalSquare, Eye } from 'lucide-react';
import { LoadingParasite } from '@/components/parasite/LoadingParasite';

export default function SessionLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ sessionId: string }>;
}) {
  const [stats, setStats] = useState<InfiltrationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const pathname = usePathname();
  const router = useRouter();

  const paramsObj = useParams();
  const sessionId = paramsObj.sessionId as string;

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const result = await parasiteAPI.getStats(sessionId);
        setStats(result.stats);
      } catch (err) {
        console.error('Failed to fetch session stats', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, [sessionId]);

  const navItems = [
    { name: 'INFILTRATION', path: `/session/${sessionId}`, icon: TerminalSquare },
    { name: 'EVOLUTION', path: `/session/${sessionId}/evolve`, icon: Activity },
    { name: 'REVELATION', path: `/session/${sessionId}/reveal`, icon: Skull },
    { name: 'VISUALIZATION', path: `/session/${sessionId}/visualization`, icon: Eye },
  ];

  if (loading) return <LoadingParasite />;

  const isEvolving = pathname.includes('/evolve');
  const isRevealing = pathname.includes('/reveal');
  const status = isRevealing ? 'REVEALING' : isEvolving ? 'EVOLVING' : 'INFILTRATING';

  return (
    <div className="min-h-screen bg-void flex flex-col font-mono text-text-primary">
      <Header sessionId={sessionId} status={status} />
      
      <div className="flex flex-1 pt-[56px] h-[calc(100vh-56px)] overflow-hidden">
        {/* Left Sidebar */}
        <aside className="w-[280px] border-r border-border-dim bg-surface/50 flex flex-col h-full overflow-y-auto">
          <div className="p-6 border-b border-border-dim">
            <h2 className="text-xs text-text-dim font-bold tracking-widest mb-4">SESSION DATA</h2>
            <div className="text-sm text-text-secondary space-y-2">
              <div className="flex justify-between">
                <span className="text-text-dim">ID:</span>
                <span className="text-parasite-green truncate ml-2">{sessionId.substring(0, 8)}...</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-dim">TARGET:</span>
                <span className="truncate ml-2 text-right">local_repo</span>
              </div>
            </div>
          </div>

          <nav className="p-4 border-b border-border-dim space-y-2">
            <h2 className="text-xs text-text-dim font-bold tracking-widest mb-4 px-2">SEQUENCE</h2>
            {navItems.map((item) => {
              const isActive = pathname === item.path;
              return (
                <button
                  key={item.name}
                  onClick={() => router.push(item.path)}
                  className={`w-full flex items-center px-4 py-3 text-sm tracking-wider rounded-sm transition-colors ${
                    isActive 
                      ? 'bg-parasite-green/10 text-parasite-green border border-parasite-green/30' 
                      : 'text-text-secondary hover:text-text-primary hover:bg-elevated'
                  }`}
                >
                  <item.icon className="w-4 h-4 mr-3" />
                  {item.name}
                </button>
              );
            })}
          </nav>

          {stats && (
            <div className="p-6 flex-1">
              <h2 className="text-xs text-text-dim font-bold tracking-widest mb-4">STATISTICS</h2>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-text-dim">FILES_SCANNED</span>
                  <span className="text-parasite-green">{stats.files}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-text-dim">FUNCTIONS</span>
                  <span className="text-parasite-green">{stats.functions}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-text-dim">GRAPH_EDGES</span>
                  <span className="text-parasite-green">{stats.edges}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-text-dim">PRIVILEGE_OPS</span>
                  <span className="text-parasite-green">{stats.privilege_ops}</span>
                </div>
                <div className="flex justify-between items-center mt-4 pt-4 border-t border-border-dim">
                  <span className="text-warning-amber">CRITICAL_FLAWS</span>
                  <span className="text-critical-red font-bold animate-pulse">{stats.critical_ops}</span>
                </div>
              </div>
            </div>
          )}
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto relative bg-gradient-to-br from-void via-void to-surface/20">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />
          <div className="relative z-10 min-h-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
