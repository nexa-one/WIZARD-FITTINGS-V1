import { ParametricSolidDefinition, DimensionMode } from '../types/hvac';

export const GAUGE_THICKNESS: Record<number, number> = {
  14: 0.0747,
  16: 0.0598,
  18: 0.0478,
  20: 0.0359,
  22: 0.0299,
  24: 0.0239,
  26: 0.0179,
  28: 0.0149,
};

export function resolveDimensions(psd: ParametricSolidDefinition): ParametricSolidDefinition {
  if (psd.dimensionMode === DimensionMode.INTERNAL_ID) {
    const thickness = GAUGE_THICKNESS[psd.wallGauge] ?? 0.0179;
    const doubled = thickness * 2;
    return {
      ...psd,
      inletWidth: psd.inletWidth !== undefined ? psd.inletWidth + doubled : undefined,
      inletHeight: psd.inletHeight !== undefined ? psd.inletHeight + doubled : undefined,
      inletDiameter: psd.inletDiameter !== undefined ? psd.inletDiameter + doubled : undefined,
      outletWidth: psd.outletWidth !== undefined ? psd.outletWidth + doubled : undefined,
      outletHeight: psd.outletHeight !== undefined ? psd.outletHeight + doubled : undefined,
      outletDiameter: psd.outletDiameter !== undefined ? psd.outletDiameter + doubled : undefined,
    };
  }
  return psd;
}
