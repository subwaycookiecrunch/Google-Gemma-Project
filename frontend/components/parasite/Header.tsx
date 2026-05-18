import React from 'react';
import { PersonalityToggle } from './PersonalityToggle';

type StatusType = 'INFILTRATING' | 'EVOLVING' | 'REVEALING' | 'COMPLETE' | null;

interface HeaderProps {
  sessionId?: string;
  status?: StatusType;
}

export const Header: React.FC<HeaderProps> = ({ sessionId, status }) => {
  const getStatusColor = (status: StatusType) => {
    switch (status) {
      case 'INFILTRATING': return 'text-warning-amber bg-warning-amber/10 border-warning-amber';
      case 'EVOLVING': return 'text-strain-blue bg-strain-blue/10 border-strain-blue';
      case 'REVEALING': return 'text-critical-red bg-critical-red/10 border-critical-red';
      case 'COMPLETE': return 'text-parasite-green bg-parasite-green/10 border-parasite-green';
      default: return 'text-text-dim border-border-dim';
    }
  };

  const getDotColor = (status: StatusType) => {
    switch (status) {
      case 'INFILTRATING': return 'bg-warning-amber';
      case 'EVOLVING': return 'bg-strain-blue';
      case 'REVEALING': return 'bg-critical-red';
      case 'COMPLETE': return 'bg-parasite-green';
      default: return 'bg-transparent';
    }
  };

  return (
    <header className="fixed top-0 w-full h-[56px] border-b border-border-dim bg-void/80 backdrop-blur-md z-50 flex items-center justify-between px-6 font-mono">
      <div className="flex items-baseline space-x-2">
        <span className="text-xl font-bold text-parasite-green tracking-widest">
          🦠 PARASITE
        </span>
        <span className="text-sm text-text-dim tracking-wider">
          EVOLVED
        </span>
        <span className="w-2 h-4 bg-parasite-green animate-pulse ml-1 opacity-80" />
      </div>

      {sessionId && status && (
        <div className="flex items-center space-x-4">
          <PersonalityToggle size="sm" />
          <div className="text-sm text-text-secondary">
            <span className="text-text-dim mr-2">SESSION:</span>
            {sessionId.substring(0, 12)}
          </div>
          
          <div className={`flex items-center px-3 py-1 text-xs border rounded-sm font-bold tracking-widest ${getStatusColor(status)}`}>
            {status !== 'COMPLETE' && (
              <span className={`w-2 h-2 rounded-full mr-2 animate-ping ${getDotColor(status)}`} />
            )}
            {status === 'COMPLETE' && (
              <span className={`w-2 h-2 rounded-full mr-2 ${getDotColor(status)}`} />
            )}
            {status}
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;
