import { ParametricSolidDefinition, ValidationResult } from '../types/hvac';
import { applyIndustrialDefaults } from './industrialDefaults';
import { resolveDimensions } from './dimensionResolver';
import { validatePSD } from './validationEngine';
import { computeWallConstruction, WallConstructionResult } from './wallConstruction';
import { buildGeometry } from './geometryEngine';
import * as THREE from 'three';

export { applyIndustrialDefaults } from './industrialDefaults';
export { resolveDimensions, GAUGE_THICKNESS } from './dimensionResolver';
export { validatePSD } from './validationEngine';
export { computeWallConstruction } from './wallConstruction';
export { buildGeometry } from './geometryEngine';
export { generateLoftPath } from './loftEngine';
export type { Profile, WallConstructionResult } from './wallConstruction';

export interface PSDPipelineResult {
  psd: ParametricSolidDefinition;
  validation: ValidationResult;
  wallConstruction: WallConstructionResult;
  geometry: THREE.BufferGeometry | null;
}

export function processPSD(partial: Partial<ParametricSolidDefinition>): PSDPipelineResult {
  const withDefaults = applyIndustrialDefaults(partial);
  const resolved = resolveDimensions(withDefaults);
  const validation = validatePSD(resolved);
  const wallConstruction = computeWallConstruction(resolved);
  const geometry = validation.valid ? buildGeometry(resolved) : null;

  return {
    psd: resolved,
    validation,
    wallConstruction,
    geometry,
  };
}
