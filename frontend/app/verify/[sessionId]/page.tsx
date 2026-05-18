'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Shield, CheckCircle, AlertTriangle } from 'lucide-react';
import { parasiteAPI } from '@/lib/api';

export default function VerifyPage() {
  const paramsObj = useParams();
  const sessionId = paramsObj.sessionId as string;
  
  const [loading, setLoading] = useState(true);
  const [artifacts, setArtifacts] = useState<any>(null);

  useEffect(() => {
    const fetchArtifacts = async () => {
      try {
        const res = await parasiteAPI.getArtifacts(sessionId);
        setArtifacts(res);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchArtifacts();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-void flex flex-col items-center justify-center font-mono">
        <Shield className="w-16 h-16 text-parasite-green animate-pulse mb-6 opacity-50" />
        <h1 className="text-xl text-parasite-green tracking-widest animate-pulse">VERIFYING BLOCKCHAIN RECORD...</h1>
      </div>
    );
  }

  if (!artifacts) {
    return (
      <div className="min-h-screen bg-void flex flex-col items-center justify-center font-mono p-8 text-center">
        <AlertTriangle className="w-16 h-16 text-critical-red mb-6" />
        <h1 className="text-2xl text-critical-red tracking-widest mb-4">RECORD NOT FOUND</h1>
        <p className="text-text-secondary max-w-md">The infection certificate for this session could not be verified on the blockchain.</p>
      </div>
    );
  }

  const cert = artifacts.certificate;
  const isOffline = !cert.minted;

  return (
    <div className="min-h-screen bg-void text-text-primary font-mono p-4 md:p-12">
      <div className="max-w-3xl mx-auto border border-border-dim bg-surface/50 p-8 rounded-sm">
        
        <div className="flex flex-col items-center justify-center text-center mb-12 pb-12 border-b border-border-dim">
          <Shield className="w-16 h-16 text-parasite-green mb-6" />
          <h1 className="text-3xl font-bold tracking-widest text-parasite-green mb-2">INFECTION VERIFIED</h1>
          <p className="text-text-secondary">Authentic PARASITE EVOLVED Post-Mortem Record</p>
        </div>

        <div className="space-y-8">
          <div>
            <h2 className="text-sm text-text-dim tracking-widest uppercase mb-4">Blockchain Status</h2>
            {isOffline ? (
              <div className="bg-warning-amber/10 border border-warning-amber p-4 rounded-sm flex items-start">
                <AlertTriangle className="w-5 h-5 text-warning-amber mr-3 mt-0.5" />
                <div>
                  <div className="text-warning-amber font-bold mb-1">OFFLINE FALLBACK RECORD</div>
                  <div className="text-sm text-warning-amber/80">Blockchain was unavailable during generation. This is a local cryptographic verification.</div>
                </div>
              </div>
            ) : (
              <div className="bg-parasite-green/10 border border-parasite-green p-4 rounded-sm flex items-start">
                <CheckCircle className="w-5 h-5 text-parasite-green mr-3 mt-0.5" />
                <div>
                  <div className="text-parasite-green font-bold mb-1">ON-CHAIN RECORD FOUND</div>
                  <div className="text-sm text-parasite-green/80">Verified on Polygon Mumbai Testnet</div>
                </div>
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-elevated p-4 border border-border-dim rounded-sm">
              <div className="text-xs text-text-dim mb-1">CASE ID</div>
              <div className="truncate text-sm">{cert.session_id}</div>
            </div>
            <div className="bg-elevated p-4 border border-border-dim rounded-sm">
              <div className="text-xs text-text-dim mb-1">TIMESTAMP</div>
              <div className="truncate text-sm">{cert.timestamp}</div>
            </div>
            <div className="bg-elevated p-4 border border-border-dim rounded-sm md:col-span-2">
              <div className="text-xs text-text-dim mb-1">TRANSACTION HASH</div>
              <div className="truncate text-sm text-parasite-green">{cert.tx_hash}</div>
            </div>
          </div>

          <div>
            <h2 className="text-sm text-text-dim tracking-widest uppercase mb-4 mt-8">Cryptographic Payload</h2>
            <div className="bg-void border border-border-dim p-4 rounded-sm overflow-x-auto text-xs text-text-secondary">
              <pre>{JSON.stringify(cert.certificate_data, null, 2)}</pre>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
