import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { GraphData, FeedingPoint } from '@/lib/types';
import { NodeMesh } from './NodeMesh';
import { EdgeMesh } from './EdgeMesh';

interface CodeGraphProps {
  data: GraphData | null;
  phase: string;
  feedingPoints: FeedingPoint[];
  dominantTargetId?: string;
  compromisedNodeIds?: string[];
  onNodeClick: (nodeId: string, position: THREE.Vector3) => void;
  isSymbiotic?: boolean;
}

export const CodeGraph: React.FC<CodeGraphProps> = ({
  data,
  phase,
  feedingPoints,
  dominantTargetId,
  compromisedNodeIds = [],
  onNodeClick,
  isSymbiotic
}) => {
  const [positions, setPositions] = useState<Record<string, THREE.Vector3>>({});
  const velocities = useRef<Record<string, THREE.Vector3>>({});
  const initialized = useRef(false);

  // Initialize random positions on a sphere
  useEffect(() => {
    if (!data || initialized.current) return;
    
    const initialPos: Record<string, THREE.Vector3> = {};
    const initialVel: Record<string, THREE.Vector3> = {};
    
    data.nodes.forEach(node => {
      // Files outer ring, functions inner
      const radius = node.type === 'file' ? 40 : 20;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      
      initialPos[node.id] = new THREE.Vector3(
        radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.sin(phi) * Math.sin(theta),
        radius * Math.cos(phi)
      );
      initialVel[node.id] = new THREE.Vector3();
    });
    
    setPositions(initialPos);
    velocities.current = initialVel;
    initialized.current = true;
  }, [data]);

  // Force simulation loop — runs until graph stabilizes
  const stabilized = useRef(false);
  useFrame(() => {
    if (!data || !initialized.current || stabilized.current) return;
    
    const damping = 0.85;
    const repulsion = 150;
    const springLen = 15;
    const springK = 0.05;
    const centerPull = 0.01;

    const newPositions = { ...positions };
    const newVelocities = { ...velocities.current };
    
    // Calculate forces
    data.nodes.forEach(nodeA => {
      const posA = newPositions[nodeA.id];
      if (!posA) return;
      let force = new THREE.Vector3();

      // Repulsion
      data.nodes.forEach(nodeB => {
        if (nodeA.id === nodeB.id) return;
        const posB = newPositions[nodeB.id];
        if (!posB) return;
        
        const diff = posA.clone().sub(posB);
        const distSq = diff.lengthSq();
        if (distSq > 0 && distSq < 1000) {
          force.add(diff.normalize().multiplyScalar(repulsion / distSq));
        }
      });

      // Attraction to center
      force.add(posA.clone().multiplyScalar(-centerPull));
      
      newVelocities[nodeA.id].add(force);
    });

    // Spring forces (edges)
    data.edges.forEach(edge => {
      const posA = newPositions[edge.source];
      const posB = newPositions[edge.target];
      if (!posA || !posB) return;

      const diff = posB.clone().sub(posA);
      const dist = diff.length();
      const forceMag = (dist - springLen) * springK;
      const forceVec = diff.normalize().multiplyScalar(forceMag);

      newVelocities[edge.source].add(forceVec);
      newVelocities[edge.target].sub(forceVec);
    });

    // Update positions
    let moved = false;
    data.nodes.forEach(node => {
      const vel = newVelocities[node.id];
      vel.multiplyScalar(damping);
      if (vel.lengthSq() > 0.001) {
        newPositions[node.id].add(vel);
        moved = true;
      }
    });

    if (moved) {
      setPositions(newPositions);
    } else {
      // Graph has stabilized
      stabilized.current = true;
    }
  });

  const fpIds = useMemo(() => new Set(feedingPoints.map(f => f.node_id)), [feedingPoints]);
  const compIds = useMemo(() => new Set(compromisedNodeIds), [compromisedNodeIds]);

  if (!data || !initialized.current) return null;

  return (
    <group>
      {/* Render Edges */}
      {data.edges.map((edge, i) => {
        const sourcePos = positions[edge.source];
        const targetPos = positions[edge.target];
        if (!sourcePos || !targetPos) return null;
        
        const isInfected = compIds.has(edge.source) && compIds.has(edge.target);
        
        return (
          <EdgeMesh 
            key={`edge-${i}`}
            source={sourcePos}
            target={targetPos}
            type={edge.type}
            isInfected={isInfected}
            isSymbiotic={isSymbiotic}
          />
        );
      })}

      {/* Render Nodes */}
      {data.nodes.map(node => {
        const pos = positions[node.id];
        if (!pos) return null;
        
        return (
          <NodeMesh
            key={node.id}
            id={node.id}
            type={node.type}
            label={node.label}
            position={pos}
            isFeedingPoint={fpIds.has(node.id)}
            isDominantTarget={node.id === dominantTargetId}
            isCompromised={compIds.has(node.id)}
            isSymbiotic={isSymbiotic}
            onClick={() => onNodeClick(node.id, pos)}
          />
        );
      })}
    </group>
  );
};
