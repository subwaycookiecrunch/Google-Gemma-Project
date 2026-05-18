import React, { useRef, useMemo } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Strain, FeedingPoint } from '@/lib/types';

interface TendrilSystemProps {
  feedingPoints: FeedingPoint[];
  activeStrain?: Strain;
  strains?: Strain[];
  phase: string;
}

const STRAIN_COLORS = [
  '#ff2244', // Red
  '#ff8800', // Orange
  '#ff22aa', // Pink
  '#4488ff', // Blue
  '#88ff22', // Lime
];

export const TendrilSystem: React.FC<TendrilSystemProps> = ({ feedingPoints, activeStrain, strains, phase }) => {
  const groupRef = useRef<THREE.Group>(null);

  const tendrils = useMemo(() => {
    if (!strains || strains.length === 0) return [];
    
    return strains.map((strain, idx) => {
      const isDominant = activeStrain?.strain_id === strain.strain_id;
      // Deterministic pseudo-random generation for curves
      const points = [];
      const numPoints = 20;
      const radius = 20 + strain.fitness_score * 30; // higher fitness = reaches further
      const angleOffsets = [0.1, -0.2, 0.3, -0.1, 0.4];
      const baseAngle = (idx / strains.length) * Math.PI * 2;

      for (let i = 0; i <= numPoints; i++) {
        const t = i / numPoints;
        const dist = t * radius;
        const wobble = Math.sin(t * Math.PI * 4 + idx) * 5;
        const x = Math.cos(baseAngle + angleOffsets[idx % angleOffsets.length] * t) * dist + wobble;
        const y = Math.sin(baseAngle + angleOffsets[idx % angleOffsets.length] * t) * dist + wobble;
        const z = Math.sin(t * Math.PI * 2 + idx) * 10;
        points.push(new THREE.Vector3(x, y, z));
      }

      const curve = new THREE.CatmullRomCurve3(points);
      const color = new THREE.Color(STRAIN_COLORS[idx % STRAIN_COLORS.length]);
      
      // Dominant strain gets the brightest color
      if (isDominant) {
        color.setHex(0xff2244); // Critical red for dominant
      }

      return {
        curve,
        color,
        isDominant,
        fitness: strain.fitness_score
      };
    });
  }, [strains, activeStrain]);

  useFrame(({ clock }) => {
    if (groupRef.current && (phase === 'EVOLVING' || phase === 'REVEALING' || phase === 'COMPLETE')) {
      groupRef.current.rotation.y = Math.sin(clock.elapsedTime * 0.1) * 0.2;
      groupRef.current.rotation.z = Math.cos(clock.elapsedTime * 0.1) * 0.2;
    }
  });

  if (phase === 'IDLE' || phase === 'INFILTRATING' || tendrils.length === 0) return null;

  return (
    <group ref={groupRef}>
      {tendrils.map((t, idx) => (
        <mesh key={idx}>
          <tubeGeometry args={[t.curve, 64, t.isDominant ? 0.6 : 0.2, 8, false]} />
          <meshStandardMaterial 
            color={t.color} 
            emissive={t.color}
            emissiveIntensity={t.isDominant ? 2.5 : 0.5}
            transparent
            opacity={t.isDominant ? 0.9 : 0.4}
          />
        </mesh>
      ))}
    </group>
  );
};
