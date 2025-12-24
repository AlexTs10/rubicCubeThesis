'use client';

import { useRef, useState, useEffect, useMemo } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { CubeState, FaceColor } from '@/types/cube';
import { COLOR_MAP, SOLVED_STATE } from '@/lib/constants';

interface CubieFaceProps {
  position: [number, number, number];
  rotation: [number, number, number];
  color: string;
}

function CubieFace({ position, rotation, color }: CubieFaceProps) {
  return (
    <mesh position={position} rotation={rotation}>
      <planeGeometry args={[0.9, 0.9]} />
      <meshStandardMaterial color={color} side={THREE.DoubleSide} />
    </mesh>
  );
}

interface CubieProps {
  position: [number, number, number];
  colors: {
    right?: string;
    left?: string;
    top?: string;
    bottom?: string;
    front?: string;
    back?: string;
  };
}

function Cubie({ position, colors }: CubieProps) {
  const [x, y, z] = position;
  const offset = 0.501;

  return (
    <group position={position}>
      {/* Black cube body */}
      <mesh>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>

      {/* Colored faces */}
      {colors.right && (
        <CubieFace
          position={[offset, 0, 0]}
          rotation={[0, Math.PI / 2, 0]}
          color={colors.right}
        />
      )}
      {colors.left && (
        <CubieFace
          position={[-offset, 0, 0]}
          rotation={[0, -Math.PI / 2, 0]}
          color={colors.left}
        />
      )}
      {colors.top && (
        <CubieFace
          position={[0, offset, 0]}
          rotation={[-Math.PI / 2, 0, 0]}
          color={colors.top}
        />
      )}
      {colors.bottom && (
        <CubieFace
          position={[0, -offset, 0]}
          rotation={[Math.PI / 2, 0, 0]}
          color={colors.bottom}
        />
      )}
      {colors.front && (
        <CubieFace
          position={[0, 0, offset]}
          rotation={[0, 0, 0]}
          color={colors.front}
        />
      )}
      {colors.back && (
        <CubieFace
          position={[0, 0, -offset]}
          rotation={[0, Math.PI, 0]}
          color={colors.back}
        />
      )}
    </group>
  );
}

interface RubiksCubeProps {
  state: CubeState;
  autoRotate?: boolean;
}

function RubiksCube({ state, autoRotate = false }: RubiksCubeProps) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (autoRotate && groupRef.current) {
      groupRef.current.rotation.y += delta * 0.3;
    }
  });

  // Generate cubies from state
  const cubies = useMemo(() => {
    const result: { position: [number, number, number]; colors: CubieProps['colors'] }[] = [];

    // Position mapping for faces (0-8 index to x,y,z offset on that face)
    const getPositionOnFace = (index: number): [number, number] => {
      const row = Math.floor(index / 3);
      const col = index % 3;
      return [col - 1, 1 - row]; // Convert to -1, 0, 1 coordinates
    };

    // Helper to get color from state
    const getColor = (face: keyof CubeState, index: number): string => {
      return COLOR_MAP[state[face][index]];
    };

    // Generate all 27 positions (-1, 0, 1 for each axis)
    for (let x = -1; x <= 1; x++) {
      for (let y = -1; y <= 1; y++) {
        for (let z = -1; z <= 1; z++) {
          // Skip center (not visible)
          if (x === 0 && y === 0 && z === 0) continue;

          const colors: CubieProps['colors'] = {};

          // Right face (R): x = 1
          if (x === 1) {
            const idx = (1 - y) * 3 + (1 - z);
            colors.right = getColor('R', idx);
          }

          // Left face (L): x = -1
          if (x === -1) {
            const idx = (1 - y) * 3 + (z + 1);
            colors.left = getColor('L', idx);
          }

          // Up face (U): y = 1
          if (y === 1) {
            const idx = (1 - z) * 3 + (x + 1);
            colors.top = getColor('U', idx);
          }

          // Down face (D): y = -1
          if (y === -1) {
            const idx = (z + 1) * 3 + (x + 1);
            colors.bottom = getColor('D', idx);
          }

          // Front face (F): z = 1
          if (z === 1) {
            const idx = (1 - y) * 3 + (x + 1);
            colors.front = getColor('F', idx);
          }

          // Back face (B): z = -1
          if (z === -1) {
            const idx = (1 - y) * 3 + (1 - x);
            colors.back = getColor('B', idx);
          }

          result.push({
            position: [x, y, z],
            colors,
          });
        }
      }
    }

    return result;
  }, [state]);

  return (
    <group ref={groupRef} rotation={[0.5, -0.7, 0]}>
      {cubies.map((cubie, index) => (
        <Cubie key={index} position={cubie.position} colors={cubie.colors} />
      ))}
    </group>
  );
}

function Scene({ state, autoRotate }: RubiksCubeProps) {
  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />
      <RubiksCube state={state} autoRotate={autoRotate} />
      <OrbitControls
        enablePan={false}
        enableZoom={true}
        minDistance={5}
        maxDistance={15}
      />
    </>
  );
}

interface RubiksCube3DProps {
  state?: CubeState;
  autoRotate?: boolean;
  className?: string;
}

export default function RubiksCube3D({
  state = SOLVED_STATE,
  autoRotate = false,
  className = '',
}: RubiksCube3DProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className={`flex items-center justify-center bg-slate-800/50 rounded-lg ${className}`}>
        <div className="text-slate-400">Loading 3D Cube...</div>
      </div>
    );
  }

  return (
    <div className={`bg-slate-900/50 rounded-lg overflow-hidden ${className}`}>
      <Canvas
        camera={{ position: [6, 6, 6], fov: 45 }}
        style={{ background: 'transparent' }}
      >
        <Scene state={state} autoRotate={autoRotate} />
      </Canvas>
    </div>
  );
}
