'use client';

import React from 'react';
import { usePersonality } from '@/lib/PersonalityContext';
import { motion } from 'framer-motion';

export const PersonalityToggle: React.FC<{ size?: 'sm' | 'lg' }> = ({ size = 'sm' }) => {
  const { personality, togglePersonality } = usePersonality();

  const isParasitic = personality === 'PARASITIC';

  const w = size === 'lg' ? 'w-64' : 'w-48';
  const h = size === 'lg' ? 'h-12' : 'h-8';
  const textSize = size === 'lg' ? 'text-sm' : 'text-[10px]';

  return (
    <div 
      className={`relative ${w} ${h} flex bg-surface/80 border border-border-dim rounded-full p-1 cursor-pointer overflow-hidden backdrop-blur z-50 transition-colors duration-500`}
      onClick={togglePersonality}
      style={{
        boxShadow: isParasitic ? '0 0 15px rgba(255, 34, 68, 0.1)' : '0 0 15px rgba(0, 255, 136, 0.1)'
      }}
    >
      {/* Sliding background */}
      <motion.div
        className="absolute top-1 bottom-1 rounded-full pointer-events-none"
        initial={false}
        animate={{
          left: isParasitic ? '4px' : '50%',
          width: 'calc(50% - 4px)',
          backgroundColor: isParasitic ? '#ff2244' : '#00ff88',
        }}
        transition={{ type: "spring", stiffness: 300, damping: 25 }}
      />
      
      {/* Labels */}
      <div className={`relative flex-1 flex items-center justify-center font-bold tracking-widest ${textSize} transition-colors duration-300 z-10 ${isParasitic ? 'text-black' : 'text-text-secondary'}`}>
        ☠️ PARASITIC
      </div>
      
      <div className={`relative flex-1 flex items-center justify-center font-bold tracking-widest ${textSize} transition-colors duration-300 z-10 ${!isParasitic ? 'text-black' : 'text-text-secondary'}`}>
        💚 SYMBIOTIC
      </div>
    </div>
  );
};
