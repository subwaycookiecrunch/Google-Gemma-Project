'use client';

import React, { useEffect, useState } from 'react';
import { parasiteAPI } from '@/lib/api';
import { FeedingPoint } from '@/lib/types';
import { FeedingPointCard } from '@/components/parasite/FeedingPointCard';
import { useRouter, useParams } from 'next/navigation';
import { motion } from 'framer-motion';

export default function InfiltrationDashboard() {
  const [feedingPoints, setFeedingPoints] = useState<FeedingPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const paramsObj = useParams();
  const sessionId = paramsObj.sessionId as string;

  useEffect(() => {
    const fetchFeedingPoints = async () => {
      try {
        const result = await parasiteAPI.getFeedingPoints(sessionId);
        setFeedingPoints(result.feeding_points);
      } catch (err) {
        console.error('Failed to fetch feeding points', err);
      } finally {
        setLoading(false);
      }
    };
    fetchFeedingPoints();
  }, [sessionId]);

  const handleEvolve = async () => {
    try {
      setLoading(true);
      await parasiteAPI.evolve(sessionId);
      router.push(`/session/${sessionId}/evolve`);
    } catch (err) {
      console.error('Failed to evolve', err);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <span className="text-parasite-green animate-pulse">Processing...</span>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-7xl mx-auto flex flex-col h-full">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-parasite-green tracking-widest mb-2">
          FEEDING POINTS DETECTED
        </h1>
        <p className="text-text-secondary tracking-wider">
          Critical infiltration nodes identified. Host is fully mapped and vulnerable.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-12">
        {feedingPoints.map((point, idx) => (
          <motion.div
            key={point.node_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
          >
            <FeedingPointCard point={point} />
          </motion.div>
        ))}
      </div>

      <div className="mt-auto pt-8 border-t border-border-dim flex justify-center pb-8">
        <motion.button
          onClick={handleEvolve}
          whileHover={{ scale: 1.02, boxShadow: '0 0 20px var(--parasite-glow)' }}
          whileTap={{ scale: 0.98 }}
          className="bg-parasite-green text-black font-bold py-4 px-12 tracking-[0.2em] rounded-sm uppercase flex items-center justify-center min-w-[300px]"
        >
          BEGIN EVOLUTION <span className="ml-2">→</span>
        </motion.button>
      </div>
    </div>
  );
}
