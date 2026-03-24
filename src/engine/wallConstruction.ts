import { ParametricSolidDefinition, WallType, ShapeType } from '../types/hvac';
import { GAUGE_THICKNESS } from './dimensionResolver';

export interface Profile {
  type: ShapeType;
  width?: number;
  height?: number;
  diameter?: number;
}

export interface WallConstructionResult {
  outerProfile: Profile;
  innerProfile?: Profile;
  insulationThickness?: number;
  totalThickness: number;
}

export function computeWallConstruction(psd: ParametricSolidDefinition): WallConstructionResult {
  const gaugeThickness = GAUGE_THICKNESS[psd.wallGauge] ?? 0.0179;
  
  const outerProfile: Profile = {
    type: psd.shapeType,
    width: psd.inletWidth,
    height: psd.inletHeight,
    diameter: psd.inletDiameter,
  };

  if (psd.wallType === WallType.SINGLE_WALL) {
    return {
      outerProfile,
      totalThickness: gaugeThickness,
    };
  }

  // Double wall
  const insulationThickness = psd.insulation ?? 1.0;
  const totalThickness = gaugeThickness * 2 + insulationThickness;
  const innerReduction = totalThickness * 2;

  const innerProfile: Profile = {
    type: psd.shapeType,
    width: psd.inletWidth !== undefined ? psd.inletWidth - innerReduction : undefined,
    height: psd.inletHeight !== undefined ? psd.inletHeight - innerReduction : undefined,
    diameter: psd.inletDiameter !== undefined ? psd.inletDiameter - innerReduction : undefined,
  };

  return {
    outerProfile,
    innerProfile,
    insulationThickness,
    totalThickness,
  };
}
