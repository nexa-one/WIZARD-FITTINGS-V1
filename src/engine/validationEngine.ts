import { ParametricSolidDefinition, ValidationResult, WallType } from '../types/hvac';
import { GAUGE_THICKNESS } from './dimensionResolver';

export function validatePSD(psd: ParametricSolidDefinition): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (psd.inletWidth !== undefined && psd.inletWidth <= 0) errors.push('Inlet width must be positive');
  if (psd.inletHeight !== undefined && psd.inletHeight <= 0) errors.push('Inlet height must be positive');
  if (psd.inletDiameter !== undefined && psd.inletDiameter <= 0) errors.push('Inlet diameter must be positive');
  if (psd.outletWidth !== undefined && psd.outletWidth <= 0) errors.push('Outlet width must be positive');
  if (psd.outletHeight !== undefined && psd.outletHeight <= 0) errors.push('Outlet height must be positive');
  if (psd.outletDiameter !== undefined && psd.outletDiameter <= 0) errors.push('Outlet diameter must be positive');
  if (psd.length <= 0) errors.push('Length must be positive');
  if (psd.neckLength < 0) errors.push('Neck length cannot be negative');

  const thickness = GAUGE_THICKNESS[psd.wallGauge];
  if (!thickness) warnings.push(`Non-standard gauge ${psd.wallGauge} - using estimated thickness`);
  
  if (thickness === 0) errors.push('Wall gauge produces zero thickness');

  if (psd.wallType === WallType.DOUBLE_WALL) {
    if (!psd.insulation || psd.insulation <= 0) {
      warnings.push('Double wall should specify insulation thickness');
    }
    const t = thickness ?? 0.0179;
    const ins = psd.insulation ?? 1.0;
    const totalReduction = (t * 2 + ins) * 2;
    if (psd.inletDiameter !== undefined && psd.inletDiameter - totalReduction <= 0) {
      errors.push('Double wall inner diameter collapses - increase diameter or reduce insulation');
    }
    if (psd.inletWidth !== undefined && psd.inletWidth - totalReduction <= 0) {
      errors.push('Double wall inner width collapses - increase width or reduce insulation');
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}
