'use client';

import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

interface StatusTerminalProps {
  logs: string[];
  title: string;
  height?: string;
}

export const StatusTerminal: React.FC<StatusTerminalProps> = ({ 
  logs, 
  title, 
  height = 'h-64' 
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className={`parasite-card flex flex-col p-0 overflow-hidden ${height}`}>
      {/* Title bar */}
      <div className="bg-elevated px-4 py-2 border-b border-border-dim flex items-center justify-between">
        <div className="flex space-x-2">
          <div className="w-3 h-3 rounded-full bg-critical-dim"></div>
          <div className="w-3 h-3 rounded-full bg-warning-amber/50"></div>
          <div className="w-3 h-3 rounded-full bg-parasite-dim"></div>
        </div>
        <div className="text-xs text-text-dim font-bold tracking-widest">{title}</div>
        <div className="w-8"></div> {/* Spacer for balance */}
      </div>

      {/* Terminal Content */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 bg-void text-parasite-green text-xs md:text-sm space-y-1"
      >
        {logs.map((log, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className="font-mono break-all"
          >
            {log.startsWith('[') ? (
              <>
                <span className="text-text-dim">{log.substring(0, log.indexOf(']') + 1)}</span>
                <span className="ml-2">{log.substring(log.indexOf(']') + 1)}</span>
              </>
            ) : (
              log
            )}
          </motion.div>
        ))}
        <div className="flex items-center text-parasite-green mt-2">
          <span>&gt;</span>
          <span className="w-2 h-4 bg-parasite-green ml-2 animate-pulse"></span>
        </div>
      </div>
    </div>
  );
};
