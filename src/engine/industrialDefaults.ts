import { ParametricSolidDefinition, FittingType, ShapeType, ConnectionType, WallType, DimensionMode } from '../types/hvac';

export const INDUSTRIAL_DEFAULTS = {
  STRAIGHT_DUCT_LENGTH: 56,
  NECK_LENGTH: 6,
  TRANSITIONS_ALIGNMENT: 'CENTERED' as const,
  REDUCERS_ALIGNMENT: 'CENTERLINE' as const,
  OFFSET_ALIGNMENT: 'CENTERLINE' as const,
  ELBOWS_NECK_LENGTH: 6,
  DIMENSION_MODE: 'EXTERNAL_OD' as const,
  WALL_GAUGE: 26,
};

let idCounter = 0;

export function applyIndustrialDefaults(psd: Partial<ParametricSolidDefinition>): ParametricSolidDefinition {
  const fittingType = psd.fittingType ?? FittingType.STRAIGHT_DUCT;
  
  let alignment: ParametricSolidDefinition['alignment'] = 'CENTERED';
  if (fittingType === FittingType.REDUCER) alignment = 'CENTERLINE';
  if (fittingType === FittingType.OFFSET) alignment = 'CENTERLINE';
  if (psd.alignment) alignment = psd.alignment;

  return {
    id: psd.id ?? `psd-${++idCounter}-${Date.now()}`,
    fittingType,
    shapeType: psd.shapeType ?? ShapeType.RECTANGULAR,
    inletWidth: psd.inletWidth ?? 12,
    inletHeight: psd.inletHeight ?? 12,
    inletDiameter: psd.inletDiameter ?? 12,
    outletWidth: psd.outletWidth ?? psd.inletWidth ?? 12,
    outletHeight: psd.outletHeight ?? psd.inletHeight ?? 12,
    outletDiameter: psd.outletDiameter ?? psd.inletDiameter ?? 12,
    length: psd.length ?? INDUSTRIAL_DEFAULTS.STRAIGHT_DUCT_LENGTH,
    neckLength: psd.neckLength ?? INDUSTRIAL_DEFAULTS.NECK_LENGTH,
    wallType: psd.wallType ?? WallType.SINGLE_WALL,
    wallGauge: psd.wallGauge ?? INDUSTRIAL_DEFAULTS.WALL_GAUGE,
    insulation: psd.insulation,
    linerPerforation: psd.linerPerforation,
    connectionType: psd.connectionType ?? ConnectionType.TDC,
    dimensionMode: psd.dimensionMode ?? DimensionMode.EXTERNAL_OD,
    alignment,
    orderId: psd.orderId,
    notes: psd.notes,
    elevationCode: psd.elevationCode,
    planCode: psd.planCode,
  };
}
