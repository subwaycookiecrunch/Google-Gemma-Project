'use client';

import React from 'react';
import { Canvas } from '@react-three/fiber';
import * as THREE from 'three';
import { GraphData, FeedingPoint, Strain } from '@/lib/types';
import { CodeGraph } from './CodeGraph';
import { ParticleField } from './ParticleField';
import { CameraController } from './CameraController';
import { TendrilSystem } from './TendrilSystem';

export type Phase = 'IDLE' | 'INFILTRATING' | 'EVOLVING' | 'REVEALING' | 'COMPLETE';

interface ParasiteCanvasProps {
  graphData: GraphData | null;
  phase: Phase;
  feedingPoints: FeedingPoint[];
  dominantStrain?: Strain;
  strains?: Strain[];
  compromisedNodeIds?: string[];
  focusTarget: THREE.Vector3 | null;
  onNodeClick: (nodeId: string, position: THREE.Vector3) => void;
  isSymbiotic?: boolean;
}

export const ParasiteCanvas: React.FC<ParasiteCanvasProps> = ({
  graphData,
  phase,
  feedingPoints,
  dominantStrain,
  strains,
  compromisedNodeIds,
  focusTarget,
  onNodeClick,
  isSymbiotic,
}) => {
  return (
    <div className="w-full h-full bg-void">
      <Canvas
        camera={{ position: [0, 0, 80], fov: 60 }}
        gl={{ antialias: true, alpha: true }}
      >
        <fog attach="fog" args={['#020204', 60, 200]} />
        <ambientLight intensity={0.2} />
        <pointLight position={[0, 0, 0]} intensity={2} color="#00ff88" distance={100} />
        <pointLight position={[50, 50, 50]} intensity={1} color="#4488ff" distance={150} />
        
        <CameraController phase={phase} focusTarget={focusTarget} />
        <ParticleField phase={phase} />
        <CodeGraph 
          data={graphData} 
          phase={phase} 
          feedingPoints={feedingPoints}
          dominantTargetId={dominantStrain?.target_feeding_point?.node_id}
          compromisedNodeIds={compromisedNodeIds}
          onNodeClick={onNodeClick}
          isSymbiotic={isSymbiotic}
        />
        <TendrilSystem 
          feedingPoints={feedingPoints}
          activeStrain={dominantStrain}
          strains={strains}
          phase={phase}
        />
      </Canvas>
    </div>
  );
};
