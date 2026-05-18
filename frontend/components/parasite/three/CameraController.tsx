import React, { useRef, useEffect } from 'react';
import { useFrame, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

interface CameraControllerProps {
  phase: string;
  focusTarget: THREE.Vector3 | null;
}

export const CameraController: React.FC<CameraControllerProps> = ({ phase, focusTarget }) => {
  const controlsRef = useRef<any>(null);
  const { camera } = useThree();
  const targetPos = useRef(new THREE.Vector3(0, 0, 0));
  const cameraPos = useRef(new THREE.Vector3(0, 0, 80));

  useEffect(() => {
    if (focusTarget) {
      // Offset camera slightly from target
      cameraPos.current.copy(focusTarget).add(new THREE.Vector3(15, 10, 25));
      targetPos.current.copy(focusTarget);
    } else {
      switch (phase) {
        case 'IDLE':
          cameraPos.current.set(0, 0, 80);
          targetPos.current.set(0, 0, 0);
          break;
        case 'INFILTRATING':
          cameraPos.current.set(0, 20, 100);
          targetPos.current.set(0, 0, 0);
          break;
        case 'EVOLVING':
          cameraPos.current.set(0, 30, 70);
          break;
        case 'REVEALING':
          cameraPos.current.set(40, 20, 60);
          break;
        case 'COMPLETE':
          cameraPos.current.set(0, 0, 120);
          targetPos.current.set(0, 0, 0);
          break;
      }
    }
  }, [phase, focusTarget]);

  useFrame(() => {
    if (!controlsRef.current) return;
    
    // Smoothly interpolate camera position and target
    camera.position.lerp(cameraPos.current, 0.05);
    controlsRef.current.target.lerp(targetPos.current, 0.05);
    controlsRef.current.update();
  });

  return (
    <OrbitControls 
      ref={controlsRef}
      autoRotate={phase === 'IDLE'}
      autoRotateSpeed={0.5}
      enableDamping
      dampingFactor={0.05}
      maxDistance={200}
      minDistance={10}
    />
  );
};
