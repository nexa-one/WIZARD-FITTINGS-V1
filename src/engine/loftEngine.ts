import * as THREE from 'three';
import { ShapeType } from '../types/hvac';
import { Profile } from './wallConstruction';

export type { Profile };

function createRectShape(w: number, h: number): THREE.Shape {
  const shape = new THREE.Shape();
  const hw = w / 2;
  const hh = h / 2;
  shape.moveTo(-hw, -hh);
  shape.lineTo(hw, -hh);
  shape.lineTo(hw, hh);
  shape.lineTo(-hw, hh);
  shape.closePath();
  return shape;
}

function createCircleShape(r: number): THREE.Shape {
  const shape = new THREE.Shape();
  shape.absarc(0, 0, r, 0, Math.PI * 2, false);
  return shape;
}

function profileToShape(profile: Profile): THREE.Shape {
  if (profile.type === ShapeType.ROUND) {
    const r = (profile.diameter ?? 12) / 2;
    return createCircleShape(r);
  } else if (profile.type === ShapeType.OVAL) {
    const w = profile.width ?? 12;
    const h = profile.height ?? 8;
    const shape = new THREE.Shape();
    const rx = w / 2;
    const ry = h / 2;
    shape.absellipse(0, 0, rx, ry, 0, Math.PI * 2, false, 0);
    return shape;
  } else {
    const w = profile.width ?? 12;
    const h = profile.height ?? 12;
    return createRectShape(w, h);
  }
}

export function generateLoftPath(
  inlet: Profile,
  outlet: Profile,
  length: number,
  _alignment: string // reserved for future offset/centerline alignment logic
): THREE.BufferGeometry {
  const inletShape = profileToShape(inlet);
  
  const path = new THREE.LineCurve3(
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, 0, length)
  );

  const extrudeSettings: THREE.ExtrudeGeometryOptions = {
    steps: 1,
    extrudePath: path,
  };

  const inletSame = 
    inlet.type === outlet.type &&
    inlet.width === outlet.width &&
    inlet.height === outlet.height &&
    inlet.diameter === outlet.diameter;

  if (inletSame) {
    return new THREE.ExtrudeGeometry(inletShape, extrudeSettings);
  }

  if (inlet.type === ShapeType.ROUND && outlet.type === ShapeType.ROUND) {
    const rIn = (inlet.diameter ?? 12) / 2;
    const rOut = (outlet.diameter ?? 8) / 2;
    const geo = new THREE.CylinderGeometry(rOut, rIn, length, 32, 1, false);
    geo.rotateX(Math.PI / 2);
    return geo;
  }

  const wIn = inlet.width ?? 12;
  const hIn = inlet.height ?? 12;
  const wOut = outlet.width ?? 8;
  const hOut = outlet.height ?? 8;
  
  const vertices: number[] = [];
  const indices: number[] = [];
  
  const hw1 = wIn / 2, hh1 = hIn / 2;
  const hw2 = wOut / 2, hh2 = hOut / 2;
  
  vertices.push(-hw1, -hh1, 0);
  vertices.push(hw1, -hh1, 0);
  vertices.push(hw1, hh1, 0);
  vertices.push(-hw1, hh1, 0);
  vertices.push(-hw2, -hh2, length);
  vertices.push(hw2, -hh2, length);
  vertices.push(hw2, hh2, length);
  vertices.push(-hw2, hh2, length);
  
  indices.push(0, 1, 5, 0, 5, 4);
  indices.push(1, 2, 6, 1, 6, 5);
  indices.push(2, 3, 7, 2, 7, 6);
  indices.push(3, 0, 4, 3, 4, 7);
  indices.push(0, 3, 2, 0, 2, 1);
  indices.push(4, 5, 6, 4, 6, 7);
  
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
  geo.setIndex(indices);
  geo.computeVertexNormals();
  return geo;
}
