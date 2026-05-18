'use client';

import React from 'react';
import { Shield, Zap, Target, ArrowRight } from 'lucide-react';

interface HardeningGuideProps {
  guide: any;
}

export const HardeningGuide: React.FC<HardeningGuideProps> = ({ guide }) => {
  const isGood = guide.risk_score < 50;

  return (
    <div className="space-y-8">
      {/* Exec Summary & Score */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 bg-surface/50 border border-border-dim rounded-sm p-6">
          <h3 className="text-sm font-bold text-text-dim tracking-widest uppercase flex items-center mb-4">
            <Shield className="w-4 h-4 mr-2" />
            Executive Summary
          </h3>
          <p className="text-lg text-text-primary leading-relaxed">
            {guide.executive_summary}
          </p>
        </div>
        
        <div className="bg-surface/50 border border-border-dim rounded-sm p-6 flex flex-col items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent to-parasite-green/5" />
          <h3 className="text-sm font-bold text-text-dim tracking-widest uppercase mb-4 relative z-10">
            System Risk Grade
          </h3>
          <div className={`text-6xl font-bold font-mono relative z-10 ${isGood ? 'text-parasite-green' : 'text-critical-red'}`}>
            {guide.risk_grade}
          </div>
          <div className="text-sm text-text-secondary mt-2 relative z-10">
            Score: {guide.risk_score}/100
          </div>
        </div>
      </div>

      {/* Quick Wins */}
      <div className="bg-surface/50 border border-border-dim rounded-sm p-6">
        <h3 className="text-sm font-bold text-text-dim tracking-widest uppercase flex items-center mb-6">
          <Zap className="w-4 h-4 mr-2 text-warning-amber" />
          Quick Wins (Do These Now)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {guide.quick_wins.map((win: string, i: number) => (
            <div key={i} className="flex items-center space-x-3 bg-elevated/30 border border-border-dim p-4 rounded-sm">
              <div className="w-5 h-5 rounded-sm border border-parasite-green/50 flex items-center justify-center">
                <span className="text-parasite-green text-xs"></span>
              </div>
              <span className="text-sm text-text-primary">{win}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Roadmap */}
      <div className="bg-surface/50 border border-border-dim rounded-sm p-6">
        <h3 className="text-sm font-bold text-text-dim tracking-widest uppercase flex items-center mb-6">
          <Target className="w-4 h-4 mr-2 text-parasite-green" />
          Implementation Roadmap
        </h3>
        <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border-dim before:to-transparent">
          {guide.implementation_roadmap.map((phase: any, i: number) => (
            <div key={i} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
              <div className="flex items-center justify-center w-10 h-10 rounded-full border border-parasite-green/50 bg-void text-parasite-green shadow-[0_0_10px_rgba(0,255,136,0.2)] shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 font-mono text-xs">
                {i + 1}
              </div>
              
              <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-elevated/30 border border-border-dim p-4 rounded-sm">
                <div className="flex items-center justify-between mb-2 border-b border-border-dim pb-2">
                  <span className="font-bold text-parasite-green font-mono">{phase.phase}</span>
                  <span className="text-xs text-text-dim uppercase">{phase.effort}</span>
                </div>
                <ul className="space-y-1 mb-3">
                  {phase.items.map((item: string, j: number) => (
                    <li key={j} className="text-sm text-text-primary flex items-start">
                      <ArrowRight className="w-3 h-3 mr-2 mt-1 text-text-dim flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
                <div className="text-xs text-text-secondary bg-surface p-2 rounded-sm italic">
                  Gain: {phase.security_gain}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
