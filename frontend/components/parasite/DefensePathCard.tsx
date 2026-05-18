'use client';

import React from 'react';
import { Shield, Clock, ShieldCheck, FileCode2 } from 'lucide-react';

interface DefensePathCardProps {
  path: any;
}

export const DefensePathCard: React.FC<DefensePathCardProps> = ({ path }) => {
  return (
    <div className="bg-surface/50 border border-border-dim rounded-sm p-6 hover:border-parasite-green/50 transition-colors">
      <div className="flex justify-between items-start border-b border-border-dim pb-4 mb-6">
        <div>
          <h3 className="text-xl font-bold text-text-primary mb-1">{path.defense_name}</h3>
          <p className="text-sm text-text-secondary">Counters: <span className="text-text-primary line-through decoration-critical-red">{path.attack_path_name}</span></p>
        </div>
        <div className="flex flex-col items-end">
          <div className="flex items-center space-x-2 text-parasite-green bg-parasite-green/10 px-3 py-1 rounded-sm border border-parasite-green/30 mb-2">
            <Clock className="w-4 h-4" />
            <span className="text-sm font-bold font-mono">{path.total_effort}</span>
          </div>
          <span className="text-xs text-text-dim uppercase tracking-widest">{path.implementation_order}</span>
        </div>
      </div>

      <div className="bg-parasite-green/5 border border-parasite-green/20 p-4 rounded-sm mb-6 flex items-start">
        <ShieldCheck className="w-5 h-5 text-parasite-green mr-3 flex-shrink-0 mt-0.5" />
        <div>
          <h4 className="text-sm font-bold text-parasite-green mb-1">Security Gain</h4>
          <p className="text-sm text-text-secondary">{path.security_gain}</p>
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="text-xs font-bold text-text-dim tracking-widest uppercase">Defense Blueprint</h4>
        
        {path.steps.map((step: any, i: number) => (
          <div key={i} className="flex border border-border-dim rounded-sm bg-elevated/30 overflow-hidden">
            <div className="bg-border-dim/20 w-10 flex items-center justify-center font-mono text-text-dim border-r border-border-dim">
              {step.step_number}
            </div>
            <div className="p-4 flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-bold text-text-primary">{step.defense}</span>
                <span className="text-xs text-text-dim font-mono">{step.effort}</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="block text-text-dim mb-1 font-bold">Neutralizes:</span>
                  <span className="text-text-secondary">{step.threat}</span>
                </div>
                <div>
                  <span className="block text-text-dim mb-1 font-bold flex items-center">
                    <FileCode2 className="w-3 h-3 mr-1" /> Implementation ({step.file}):
                  </span>
                  <span className="text-text-secondary">{step.implementation}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
