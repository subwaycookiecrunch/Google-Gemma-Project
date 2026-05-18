import React from 'react';
import { UploadZone } from '@/components/parasite/UploadZone';
import { Header } from '@/components/parasite/Header';

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-void flex flex-col relative overflow-hidden font-mono">
      <Header />
      
      {/* Background drifting particles via CSS */}
      <div className="absolute inset-0 pointer-events-none opacity-20">
        <div className="absolute top-1/4 left-1/4 w-1 h-1 bg-parasite-green rounded-full shadow-[0_0_10px_#00ff88] animate-[drift_20s_linear_infinite]" />
        <div className="absolute top-1/2 right-1/3 w-1.5 h-1.5 bg-parasite-green rounded-full shadow-[0_0_10px_#00ff88] animate-[drift_25s_linear_infinite_reverse]" />
        <div className="absolute bottom-1/4 left-1/3 w-2 h-2 bg-parasite-green rounded-full shadow-[0_0_10px_#00ff88] opacity-50 animate-[drift_30s_linear_infinite]" />
        <div className="absolute top-1/3 right-1/4 w-1 h-1 bg-critical-red rounded-full shadow-[0_0_10px_#ff2244] animate-[drift_15s_linear_infinite_reverse]" />
      </div>

      <div className="flex-1 flex flex-col">
        {/* TOP SECTION */}
        <div className="h-[60vh] flex flex-col items-center justify-center text-center z-10 px-4 pt-16">
          <div className="space-y-4 max-w-3xl">
            <p className="text-text-secondary text-xl md:text-2xl tracking-widest animate-[fadeIn_1s_ease-out_0.5s_both]">
              I don't scan your code.
            </p>
            <p className="text-parasite-green text-3xl md:text-5xl font-bold tracking-widest animate-[fadeIn_1s_ease-out_1.5s_both] filter drop-shadow-[0_0_10px_rgba(0,255,136,0.3)]">
              I become it.
            </p>
            <p className="text-text-secondary text-xl md:text-2xl tracking-widest animate-[fadeIn_1s_ease-out_2.5s_both] mt-8">
              I evolve inside it.
            </p>
            <div className="pt-8 space-y-2 animate-[fadeIn_1s_ease-out_3.5s_both]">
              <p className="text-text-secondary text-lg md:text-xl tracking-wider">
                Then I show you exactly
              </p>
              <p className="text-text-secondary text-lg md:text-xl tracking-wider">
                how I would have
              </p>
              <p className="text-critical-red text-4xl md:text-6xl font-bold tracking-widest pt-2 filter drop-shadow-[0_0_15px_rgba(255,34,68,0.4)]">
                destroyed it.
              </p>
            </div>
          </div>
        </div>

        {/* BOTTOM SECTION */}
        <div className="h-[40vh] flex items-center justify-center z-10 bg-gradient-to-t from-black/50 to-transparent">
          <UploadZone />
        </div>
      </div>

      {/* Adding custom keyframes globally for this page */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes drift {
          0% { transform: translate(0, 0) rotate(0deg); }
          50% { transform: translate(100px, 50px) rotate(180deg); opacity: 0.5; }
          100% { transform: translate(0, 0) rotate(360deg); }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}} />
    </main>
  );
}
