'use client';

import React from 'react';
import { Shield, Clock, AlertTriangle, CheckCircle } from 'lucide-react';
import { CodeDiff } from './CodeDiff';

interface HealingPlanCardProps {
  plan: any;
}

export const HealingPlanCard: React.FC<HealingPlanCardProps> = ({ plan }) => {
  return (
    <div className="bg-surface/50 border border-border-dim rounded-sm p-6 space-y-6 hover:border-parasite-green/50 transition-colors">
      <div className="flex justify-between items-start border-b border-border-dim pb-4">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <span className="bg-parasite-green/20 text-parasite-green px-2 py-0.5 rounded-sm text-xs font-bold font-mono">
              P{plan.priority}
            </span>
            <h3 className="text-xl font-bold text-text-primary">{plan.vulnerability_name}</h3>
          </div>
          <p className="text-sm text-text-secondary">{plan.root_cause}</p>
        </div>
        <div className="flex items-center space-x-2 text-parasite-green bg-parasite-green/10 px-3 py-1 rounded-sm border border-parasite-green/30">
          <Clock className="w-4 h-4" />
          <span className="text-sm font-bold font-mono">{plan.effort_estimate}</span>
        </div>
      </div>

      <div className="space-y-2">
        <h4 className="text-xs font-bold text-text-dim tracking-widest uppercase">The Cure</h4>
        <p className="text-sm text-text-secondary italic">"{plan.explanation}"</p>
      </div>

      <div className="space-y-2">
        <h4 className="text-xs font-bold text-text-dim tracking-widest uppercase flex items-center">
          <Shield className="w-4 h-4 mr-2" /> 
          Immediate Fix
        </h4>
        <CodeDiff 
          filename={plan.immediate_fix?.file || 'unknown'} 
          beforeCode={plan.before_code} 
          afterCode={plan.after_code} 
        />
      </div>

      {plan.test_cases && plan.test_cases.length > 0 && (
        <div className="pt-4 border-t border-border-dim space-y-2">
          <h4 className="text-xs font-bold text-text-dim tracking-widest uppercase">Verification</h4>
          <ul className="space-y-2">
            {plan.test_cases.map((tc: string, i: number) => (
              <li key={i} className="flex items-start text-sm text-text-secondary">
                <CheckCircle className="w-4 h-4 text-parasite-green mr-2 mt-0.5 flex-shrink-0" />
                {tc}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
