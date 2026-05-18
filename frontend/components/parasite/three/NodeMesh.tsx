import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';

interface NodeMeshProps {
  id: string;
  type: string;
  label: string;
  position: THREE.Vector3;
  isFeedingPoint: boolean;
  isDominantTarget: boolean;
  isCompromised: boolean;
  isSymbiotic?: boolean;
  onClick: () => void;
}

export const NodeMesh: React.FC<NodeMeshProps> = ({
  type,
  label,
  position,
  isFeedingPoint,
  isDominantTarget,
  isCompromised,
  isSymbiotic,
  onClick
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  // Styling based on node type and status
  const isFile = type === 'file';
  const isPrivilege = type === 'privilege_op';
  
  const baseRadius = isFile ? 1.5 : (isPrivilege ? 1.2 : 0.8);
  const targetScale = hovered ? 1.5 : 1.0;

  // Colors
  let color = isFile ? '#334455' : '#223344';
  if (isCompromised) color = isSymbiotic ? '#00ff88' : '#ff8800'; // Green if healed, Amber if compromised
  else if (isDominantTarget) color = isSymbiotic ? '#00ff88' : '#ff2244';
  else if (isFeedingPoint) color = isSymbiotic ? '#00cc66' : '#ff2244'; // Healing nodes vs Feeding nodes
  else if (isPrivilege) color = '#aa2244';

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    
    // Smooth scaling on hover
    meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);
    
    // Pulsing effect for special nodes
    if (isFeedingPoint || isDominantTarget || isCompromised) {
      const pulse = 1 + Math.sin(clock.elapsedTime * 3) * 0.15;
      meshRef.current.scale.x = targetScale * pulse;
      meshRef.current.scale.y = targetScale * pulse;
      meshRef.current.scale.z = targetScale * pulse;
    }
  });

  return (
    <mesh
      ref={meshRef}
      position={position}
      onClick={(e) => { e.stopPropagation(); onClick(); }}
      onPointerOver={(e) => { e.stopPropagation(); setHovered(true); document.body.style.cursor = 'pointer'; }}
      onPointerOut={() => { setHovered(false); document.body.style.cursor = 'default'; }}
    >
      {isPrivilege ? (
        <octahedronGeometry args={[baseRadius, 0]} />
      ) : (
        <sphereGeometry args={[baseRadius, 16, 16]} />
      )}
      
      <meshStandardMaterial 
        color={color} 
        emissive={color}
        emissiveIntensity={isFeedingPoint || isDominantTarget || isCompromised ? 0.8 : 0.2}
        roughness={0.4}
        metalness={0.8}
      />
      
      {hovered && (
        <Html distanceFactor={15} center>
          <div className="px-2 py-1 bg-surface/90 border border-border-dim rounded-sm text-xs font-mono text-text-primary whitespace-nowrap pointer-events-none">
            {label}
          </div>
        </Html>
      )}
    </mesh>
  );
};
