import * as THREE from 'three';
import { ParametricSolidDefinition, FittingType, ShapeType } from '../types/hvac';
import { generateLoftPath } from './loftEngine';
import { Profile } from './wallConstruction';

function getInletProfile(psd: ParametricSolidDefinition): Profile {
  return {
    type: psd.shapeType,
    width: psd.inletWidth,
    height: psd.inletHeight,
    diameter: psd.inletDiameter,
  };
}

function getOutletProfile(psd: ParametricSolidDefinition): Profile {
  return {
    type: psd.shapeType,
    width: psd.outletWidth ?? psd.inletWidth,
    height: psd.outletHeight ?? psd.inletHeight,
    diameter: psd.outletDiameter ?? psd.inletDiameter,
  };
}

export function buildGeometry(psd: ParametricSolidDefinition): THREE.BufferGeometry | null {
  const inlet = getInletProfile(psd);
  const outlet = getOutletProfile(psd);

  switch (psd.fittingType) {
    case FittingType.STRAIGHT_DUCT: {
      return generateLoftPath(inlet, inlet, psd.length, psd.alignment);
    }

    case FittingType.ELBOW_90: {
      if (psd.shapeType === ShapeType.ROUND) {
        const r = (psd.inletDiameter ?? 12) / 2;
        const tubeRadius = r;
        const torusRadius = r * 1.5;
        const geo = new THREE.TorusGeometry(torusRadius, tubeRadius, 16, 32, Math.PI / 2);
        return geo;
      } else {
        const w = psd.inletWidth ?? 12;
        const h = psd.inletHeight ?? 12;
        const geo = new THREE.BoxGeometry(w, h, psd.neckLength + w);
        return geo;
      }
    }

    case FittingType.ELBOW_45: {
      if (psd.shapeType === ShapeType.ROUND) {
        const r = (psd.inletDiameter ?? 12) / 2;
        const tubeRadius = r;
        const torusRadius = r * 1.5;
        const geo = new THREE.TorusGeometry(torusRadius, tubeRadius, 16, 32, Math.PI / 4);
        return geo;
      } else {
        const w = psd.inletWidth ?? 12;
        const h = psd.inletHeight ?? 12;
        const geo = new THREE.BoxGeometry(w, h, psd.neckLength + w * 0.7);
        return geo;
      }
    }

    case FittingType.TRANSITION:
    case FittingType.REDUCER: {
      return generateLoftPath(inlet, outlet, psd.length, psd.alignment);
    }

    case FittingType.OFFSET: {
      const l = psd.length;
      return generateLoftPath(inlet, outlet, l, psd.alignment);
    }

    case FittingType.TEE: {
      const w = psd.inletWidth ?? 12;
      const h = psd.inletHeight ?? 12;
      const mainGeo = new THREE.BoxGeometry(psd.length, h, w);
      const branchGeo = new THREE.BoxGeometry(h, psd.length / 2, w);
      branchGeo.translate(0, psd.length / 4, 0);
      const merged = mergeGeometries([mainGeo, branchGeo]);
      return merged;
    }

    case FittingType.CROSS: {
      const w = psd.inletWidth ?? 12;
      const h = psd.inletHeight ?? 12;
      const mainGeo = new THREE.BoxGeometry(psd.length, h, w);
      const crossGeo = new THREE.BoxGeometry(h, psd.length, w);
      const merged = mergeGeometries([mainGeo, crossGeo]);
      return merged;
    }

    case FittingType.CAP: {
      if (psd.shapeType === ShapeType.ROUND) {
        const r = (psd.inletDiameter ?? 12) / 2;
        return new THREE.SphereGeometry(r, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2);
      } else {
        const w = psd.inletWidth ?? 12;
        const h = psd.inletHeight ?? 12;
        return new THREE.BoxGeometry(w, h, psd.neckLength);
      }
    }

    case FittingType.REGISTER_BOX: {
      const w = psd.inletWidth ?? 12;
      const h = psd.inletHeight ?? 12;
      return new THREE.BoxGeometry(w, h, psd.length);
    }

    default:
      return null;
  }
}

function mergeGeometries(geos: THREE.BufferGeometry[]): THREE.BufferGeometry {
  const merged = new THREE.BufferGeometry();
  const posArrays: Float32Array[] = [];
  let totalLen = 0;

  for (const g of geos) {
    const pos = g.attributes.position.array as Float32Array;
    posArrays.push(pos);
    totalLen += pos.length;
  }

  const combined = new Float32Array(totalLen);
  let offset = 0;
  for (const arr of posArrays) {
    combined.set(arr, offset);
    offset += arr.length;
  }

  merged.setAttribute('position', new THREE.Float32BufferAttribute(combined, 3));
  merged.computeVertexNormals();
  return merged;
}
