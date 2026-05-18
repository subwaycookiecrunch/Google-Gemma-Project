'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

export type Personality = 'PARASITIC' | 'SYMBIOTIC';

interface PersonalityContextType {
  personality: Personality;
  togglePersonality: () => void;
  tokens: {
    primary: string;
    primaryGlow: string;
    badge: string;
    terminalColor: string;
  };
}

const PARASITIC_TOKENS = {
  primary: '#ff2244',
  primaryGlow: '#ff224422',
  badge: 'CRITICAL',
  terminalColor: '#ff6688',
};

const SYMBIOTIC_TOKENS = {
  primary: '#00ff88',
  primaryGlow: '#00ff8822',
  badge: 'FIXABLE',
  terminalColor: '#00ff88',
};

const PersonalityContext = createContext<PersonalityContextType | undefined>(undefined);

export const PersonalityProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [personality, setPersonality] = useState<Personality>('PARASITIC');

  const togglePersonality = () => {
    setPersonality(prev => (prev === 'PARASITIC' ? 'SYMBIOTIC' : 'PARASITIC'));
  };

  useEffect(() => {
    const root = document.documentElement;
    const tokens = personality === 'PARASITIC' ? PARASITIC_TOKENS : SYMBIOTIC_TOKENS;
    
    // Smooth transition
    root.style.setProperty('--mode-primary', tokens.primary);
    root.style.setProperty('--mode-primary-glow', tokens.primaryGlow);
    root.style.setProperty('--mode-terminal', tokens.terminalColor);
    
    // We update class on body to allow Tailwind variants to easily hook in
    if (personality === 'SYMBIOTIC') {
      root.classList.add('symbiotic-mode');
      root.classList.remove('parasitic-mode');
    } else {
      root.classList.add('parasitic-mode');
      root.classList.remove('symbiotic-mode');
    }
  }, [personality]);

  const value = {
    personality,
    togglePersonality,
    tokens: personality === 'PARASITIC' ? PARASITIC_TOKENS : SYMBIOTIC_TOKENS,
  };

  return (
    <PersonalityContext.Provider value={value}>
      {children}
    </PersonalityContext.Provider>
  );
};

export const usePersonality = () => {
  const context = useContext(PersonalityContext);
  if (context === undefined) {
    throw new Error('usePersonality must be used within a PersonalityProvider');
  }
  return context;
};
