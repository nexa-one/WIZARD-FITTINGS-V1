import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Grid, Environment } from '@react-three/drei'
import * as THREE from 'three'
import type { FittingType } from '@/types'

interface FittingViewer3DProps {
  fittingType: FittingType
  geometryData?: Record<string, unknown> | null
}

function ElbowMesh() {
  const meshRef = useRef<THREE.Mesh>(null!)
  useFrame((_, delta) => { meshRef.current.rotation.y += delta * 0.3 })

  const geometry = useMemo(() => {
    const path = new THREE.CatmullRomCurve3([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(0, 0.5, 0),
      new THREE.Vector3(0.5, 1, 0),
      new THREE.Vector3(1, 1, 0),
    ])
    return new THREE.TubeGeometry(path, 20, 0.25, 8, false)
  }, [])

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial color="#4a90d9" metalness={0.6} roughness={0.3} />
    </mesh>
  )
}

function TeeMesh() {
  const groupRef = useRef<THREE.Group>(null!)
  useFrame((_, delta) => { groupRef.current.rotation.y += delta * 0.3 })
  return (
    <group ref={groupRef}>
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[2, 0.5, 0.5]} />
        <meshStandardMaterial color="#4a90d9" metalness={0.6} roughness={0.3} />
      </mesh>
      <mesh position={[0, 0.6, 0]}>
        <boxGeometry args={[0.4, 0.7, 0.4]} />
        <meshStandardMaterial color="#4a90d9" metalness={0.6} roughness={0.3} />
      </mesh>
    </group>
  )
}

function ReducerMesh() {
  const meshRef = useRef<THREE.Mesh>(null!)
  useFrame((_, delta) => { meshRef.current.rotation.y += delta * 0.3 })
  const geometry = useMemo(() => {
    const geo = new THREE.CylinderGeometry(0.6, 0.3, 1.2, 16)
    return geo
  }, [])
  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial color="#4a90d9" metalness={0.6} roughness={0.3} />
    </mesh>
  )
}

function DuctMesh() {
  const meshRef = useRef<THREE.Mesh>(null!)
  useFrame((_, delta) => { meshRef.current.rotation.y += delta * 0.3 })
  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[0.8, 0.6, 2]} />
      <meshStandardMaterial color="#4a90d9" metalness={0.6} roughness={0.3} />
    </mesh>
  )
}

function CapMesh() {
  const meshRef = useRef<THREE.Mesh>(null!)
  useFrame((_, delta) => { meshRef.current.rotation.y += delta * 0.3 })
  return (
    <group ref={meshRef}>
      <mesh>
        <boxGeometry args={[0.8, 0.6, 0.4]} />
        <meshStandardMaterial color="#4a90d9" metalness={0.6} roughness={0.3} />
      </mesh>
      <mesh position={[0, 0, -0.25]}>
        <planeGeometry args={[0.8, 0.6]} />
        <meshStandardMaterial color="#2a5fa8" metalness={0.5} roughness={0.4} side={THREE.DoubleSide} />
      </mesh>
    </group>
  )
}

function FittingMeshSelector({ type }: { type: FittingType }) {
  switch (type) {
    case 'elbow': return <ElbowMesh />
    case 'tee': return <TeeMesh />
    case 'reducer':
    case 'transition': return <ReducerMesh />
    case 'cap': return <CapMesh />
    default: return <DuctMesh />
  }
}

export function FittingViewer3D({ fittingType }: FittingViewer3DProps) {
  return (
    <Canvas
      camera={{ position: [3, 2.5, 3], fov: 50 }}
      style={{ background: 'transparent' }}
    >
      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 8, 5]} intensity={1} castShadow />
      <pointLight position={[-3, 3, -3]} intensity={0.5} color="#4a90d9" />

      <FittingMeshSelector type={fittingType} />

      <Grid
        position={[0, -1, 0]}
        args={[10, 10]}
        cellSize={0.5}
        cellThickness={0.5}
        cellColor="#21262d"
        sectionSize={2}
        sectionThickness={1}
        sectionColor="#30363d"
        fadeDistance={8}
        fadeStrength={1}
      />

      <OrbitControls
        enablePan
        enableZoom
        enableRotate
        minDistance={1.5}
        maxDistance={10}
      />
    </Canvas>
  )
}
