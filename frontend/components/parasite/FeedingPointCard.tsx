'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FeedingPoint } from '@/lib/types';
import { ShieldAlert, Crosshair, ChevronDown, ChevronUp } from 'lucide-react';

interface Props {
  point: FeedingPoint;
}

const ScoreBar = ({ label, score }: { label: string; score: number }) => {
  const filled = Math.round(score);
  const empty = 10 - filled;
  return (
    <div className="flex items-center text-xs font-mono mb-1">
      <span className="w-20 text-text-secondary">{label}</span>
      <span className="text-parasite-dim tracking-tighter">
        {'█'.repeat(filled)}
      </span>
      <span className="text-border-dim tracking-tighter">
        {'█'.repeat(empty)}
      </span>
      <span className="ml-2 w-8 text-right text-parasite-green">{score.toFixed(1)}</span>
    </div>
  );
};

export const FeedingPointCard: React.FC<Props> = ({ point }) => {
  const [expanded, setExpanded] = useState(false);

  const badgeClass = 
    point.danger_level === 'CRITICAL' ? 'danger-critical' :
    point.danger_level === 'HIGH' ? 'danger-high' : 'danger-medium';

  return (
    <div 
      className="parasite-card flex flex-col cursor-pointer group"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex justify-between items-start mb-2">
        <div className="text-xs text-text-dim break-all">
          {point.file}:{point.line}
        </div>
        <div className={`danger-badge ${badgeClass}`}>
          {point.danger_level}
        </div>
      </div>

      <div className="text-xl font-bold text-parasite-green mb-4 truncate group-hover:text-white transition-colors">
        {point.name}()
      </div>

      <div className="bg-void p-3 rounded-sm border border-border-dim mb-4">
        <ScoreBar label="BLAST" score={point.blast_radius_score} />
        <ScoreBar label="STEALTH" score={point.stealth_score} />
        <ScoreBar label="PERSIST" score={point.persistence_score} />
      </div>

      <p className="text-sm text-text-secondary line-clamp-2 mb-4 flex-1">
        {point.explanation}
      </p>

      <div className="flex flex-wrap gap-2 mb-4">
        {point.attack_surfaces.slice(0, 3).map((surface, i) => (
          <span key={i} className="text-[10px] px-2 py-1 bg-elevated text-text-dim border border-border-dim rounded-sm">
            {surface}
          </span>
        ))}
        {point.attack_surfaces.length > 3 && (
          <span className="text-[10px] px-2 py-1 text-text-dim">
            +{point.attack_surfaces.length - 3} more
          </span>
        )}
      </div>

      <div className="flex justify-center border-t border-border-dim pt-2 text-text-dim group-hover:text-parasite-green transition-colors">
        {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="pt-4 mt-2 border-t border-border-dim">
              <h4 className="text-xs font-bold text-warning-amber mb-2 flex items-center">
                <Crosshair size={14} className="mr-1" /> ATTACK APPROACH
              </h4>
              <p className="text-xs text-text-primary bg-elevated p-3 rounded-sm border border-border-dim whitespace-pre-wrap leading-relaxed">
                {point.attack_approach}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
