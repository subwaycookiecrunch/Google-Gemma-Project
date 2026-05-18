import React from 'react';
import { InfectionVisualization } from '@/components/parasite/InfectionVisualization';

export default async function VisualizationPage({
  params,
}: {
  params: Promise<{ sessionId: string }>;
}) {
  // In Next.js 15, route parameters are promises
  const { sessionId } = await params;

  return <InfectionVisualization sessionId={sessionId} />;
}
