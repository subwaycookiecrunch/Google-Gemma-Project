'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const messages = [
  "Infiltrating host...",
  "Mapping privilege flows...",
  "Analyzing dependency graphs...",
  "Evolving attack vectors...",
  "Calculating time to death...",
  "You will never know I was here...",
];

export const LoadingParasite = () => {
  const [msgIndex, setMsgIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMsgIndex((prev) => (prev + 1) % messages.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-void flex flex-col items-center justify-center z-50 font-mono"
    >
      <div className="relative mb-12 flex flex-col items-center justify-center">
        {/* Core */}
        <motion.div 
          animate={{ scale: [1, 1.2, 1], rotate: [0, 180, 360] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          className="text-6xl z-10 filter drop-shadow-[0_0_15px_rgba(0,255,136,0.8)]"
        >
          🦠
        </motion.div>
        
        {/* Orbiting particles */}
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-parasite-green rounded-full opacity-50"
            animate={{
              x: [0, Math.cos((i * Math.PI) / 4) * 60, 0],
              y: [0, Math.sin((i * Math.PI) / 4) * 60, 0],
              scale: [0, 1, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              delay: i * 0.2,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      <div className="h-8 relative overflow-hidden flex items-center justify-center">
        <AnimatePresence mode="wait">
          <motion.div
            key={msgIndex}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -20, opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="text-parasite-green tracking-widest text-sm"
          >
            {messages[msgIndex]}
          </motion.div>
        </AnimatePresence>
      </div>
      
      {/* Loading bar */}
      <div className="w-64 h-1 bg-surface mt-8 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-parasite-green"
          animate={{ x: ['-100%', '100%'] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
        />
      </div>
    </motion.div>
  );
};
