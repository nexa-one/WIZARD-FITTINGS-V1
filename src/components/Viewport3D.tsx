import React, { useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Text } from '@react-three/drei';
import * as THREE from 'three';
import { useHVACStore } from '../store';

interface GeometryMeshProps {
  geometry: THREE.BufferGeometry;
  viewMode: string;
}

const GeometryMesh: React.FC<GeometryMeshProps> = ({ geometry, viewMode }) => {
  const meshRef = useRef<THREE.Mesh>(null);

  if (viewMode === 'X_RAY_TRANSPARENT') {
    return (
      <mesh ref={meshRef} geometry={geometry}>
        <meshStandardMaterial
          color="#4A90D9"
          transparent
          opacity={0.3}
          wireframe={false}
          side={THREE.DoubleSide}
        />
      </mesh>
    );
  }

  if (viewMode === 'CNC_FLAT_PATTERN') {
    return (
      <mesh ref={meshRef} geometry={geometry}>
        <meshBasicMaterial color="#00ff88" wireframe />
      </mesh>
    );
  }

  return (
    <mesh ref={meshRef} geometry={geometry} castShadow receiveShadow>
      <meshStandardMaterial
        color="#4A90D9"
        metalness={0.6}
        roughness={0.3}
        envMapIntensity={1}
      />
    </mesh>
  );
};

export const Viewport3D: React.FC = () => {
  const { builtGeometry, viewMode } = useHVACStore();

  return (
    <div className="w-full h-full bg-gray-950 relative">
      <Canvas
        camera={{ position: [30, 20, 30], fov: 45 }}
        shadows
        gl={{ antialias: true }}
      >
        <color attach="background" args={['#0a0a0f']} />
        <ambientLight intensity={0.5} />
        <directionalLight
          position={[50, 50, 50]}
          intensity={1}
          castShadow
          shadow-mapSize={[1024, 1024]}
        />
        <directionalLight position={[-30, 30, -30]} intensity={0.3} />

        {builtGeometry ? (
          <GeometryMesh geometry={builtGeometry} viewMode={viewMode} />
        ) : (
          <Text
            position={[0, 0, 0]}
            fontSize={2}
            color="#4B5563"
            anchorX="center"
            anchorY="middle"
          >
            No geometry built yet
          </Text>
        )}

        <Grid
          args={[100, 100]}
          position={[0, -15, 0]}
          cellColor="#1f2937"
          sectionColor="#374151"
          fadeDistance={80}
          cellSize={2}
          sectionSize={10}
        />

        <OrbitControls
          enablePan
          enableZoom
          enableRotate
          minDistance={5}
          maxDistance={200}
        />

        <axesHelper args={[10]} />
      </Canvas>

      <div className="absolute top-3 right-3 text-xs text-gray-600 bg-gray-900/50 px-2 py-1 rounded">
        {viewMode === '3D_VISUAL' ? '3D Visual' : viewMode === 'CNC_FLAT_PATTERN' ? 'CNC Pattern' : 'X-Ray'}
      </div>
    </div>
  );
};
