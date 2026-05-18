import React, { useMemo } from 'react';
import * as THREE from 'three';

interface EdgeMeshProps {
  source: THREE.Vector3;
  target: THREE.Vector3;
  type: string;
  isInfected: boolean;
  isSymbiotic?: boolean;
}

export const EdgeMesh: React.FC<EdgeMeshProps> = ({ source, target, type, isInfected, isSymbiotic }) => {
  const lineGeometry = useMemo(() => {
    const geo = new THREE.BufferGeometry().setFromPoints([source, target]);
    return geo;
  }, [source, target]);

  let color = '#1a2a3a';
  if (isInfected) color = isSymbiotic ? '#00ff88' : '#ff2244';
  else if (type === 'data_flow') color = '#2a4a6a';
  else if (type === 'privilege_escalation') color = '#3a1a1a';

  return (
    <line geometry={lineGeometry}>
      <lineBasicMaterial 
        color={color} 
        transparent 
        opacity={isInfected ? 0.6 : 0.3} 
        linewidth={1} 
      />
    </line>
  );
};
