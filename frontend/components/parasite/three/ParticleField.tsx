import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface ParticleFieldProps {
  phase: string;
}

export const ParticleField: React.FC<ParticleFieldProps> = ({ phase }) => {
  const pointsRef = useRef<THREE.Points>(null);
  
  // Create static buffer data
  const { positions, velocities, colors } = useMemo(() => {
    const isComplete = phase === 'COMPLETE';
    const count = isComplete ? 2500 : 2000;
    
    const pos = new Float32Array(count * 3);
    const vel = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    
    const colorA = new THREE.Color('#003322');
    const colorB = new THREE.Color('#001133');
    const colorBright = new THREE.Color('#00ff88');

    for (let i = 0; i < count; i++) {
      // Random position in sphere radius 120
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = Math.cbrt(Math.random()) * 120;
      
      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);
      
      // Velocities
      vel[i * 3] = (Math.random() - 0.5) * 0.05;
      vel[i * 3 + 1] = (Math.random() - 0.5) * 0.05;
      vel[i * 3 + 2] = (Math.random() - 0.5) * 0.05;
      
      // Colors
      const isBright = isComplete && i > 2000;
      const particleColor = isBright ? colorBright : (Math.random() > 0.5 ? colorA : colorB);
      
      col[i * 3] = particleColor.r;
      col[i * 3 + 1] = particleColor.g;
      col[i * 3 + 2] = particleColor.b;
    }
    return { positions: pos, velocities: vel, colors: col };
  }, [phase]);

  useFrame(() => {
    if (!pointsRef.current) return;
    const isComplete = phase === 'COMPLETE';
    
    const positionsAttr = pointsRef.current.geometry.attributes.position;
    const positionsArray = positionsAttr.array as Float32Array;
    
    for (let i = 0; i < positionsArray.length / 3; i++) {
      const idx = i * 3;
      
      if (isComplete && i > 2000) {
        // Bright particles flow toward center
        const x = positionsArray[idx];
        const y = positionsArray[idx + 1];
        const z = positionsArray[idx + 2];
        const dist = Math.sqrt(x*x + y*y + z*z);
        
        if (dist > 5) {
          positionsArray[idx] -= (x / dist) * 0.5;
          positionsArray[idx + 1] -= (y / dist) * 0.5;
          positionsArray[idx + 2] -= (z / dist) * 0.5;
        } else {
          // Reset to edge
          const theta = Math.random() * Math.PI * 2;
          const phi = Math.acos(2 * Math.random() - 1);
          const r = 120;
          positionsArray[idx] = r * Math.sin(phi) * Math.cos(theta);
          positionsArray[idx + 1] = r * Math.sin(phi) * Math.sin(theta);
          positionsArray[idx + 2] = r * Math.cos(phi);
        }
      } else {
        // Drift
        positionsArray[idx] += velocities[idx];
        positionsArray[idx + 1] += velocities[idx + 1];
        positionsArray[idx + 2] += velocities[idx + 2];
        
        // Wrap around
        if (Math.abs(positionsArray[idx]) > 120) positionsArray[idx] *= -0.99;
        if (Math.abs(positionsArray[idx + 1]) > 120) positionsArray[idx + 1] *= -0.99;
        if (Math.abs(positionsArray[idx + 2]) > 120) positionsArray[idx + 2] *= -0.99;
      }
    }
    
    positionsAttr.needsUpdate = true;
    
    // Slight rotation of entire field
    pointsRef.current.rotation.y += 0.0005;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={colors.length / 3}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.15}
        vertexColors
        transparent
        opacity={0.8}
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  );
};
