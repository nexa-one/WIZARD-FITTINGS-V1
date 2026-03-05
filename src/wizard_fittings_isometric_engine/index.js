/**
 * WIZARD_FITTINGS_ISOMETRIC_ENGINE – Public module entry point
 *
 * Re-exports all public classes and utilities so consumers can import from
 * a single path:
 *
 *   import {
 *     WizardFittingsEngine,
 *     IsometricSketchRenderer,
 *     generateGeometry,
 *     IsometricProjection,
 *     DEFAULT_CONFIG,
 *     ENGINE_VERSION,
 *   } from "./src/wizard_fittings_isometric_engine/index.js";
 */

export { WizardFittingsEngine }         from "./WizardFittingsEngine.js";
export { IsometricSketchRenderer }      from "./renderers/IsometricSketchRenderer.js";
export { CoordinateCube }               from "./ui/CoordinateCube.js";
export { ViewportController }           from "./ui/ViewportController.js";
export { ThemeManager }                 from "./ui/ThemeManager.js";
export { ExportManager }                from "./export/ExportManager.js";
export { generateGeometry, SUPPORTED_TYPES } from "./geometry/FittingGeometry.js";
export { IsometricProjection }          from "./geometry/IsometricProjection.js";
export { DEFAULT_CONFIG, ENGINE_NAME, ENGINE_VERSION } from "./config.js";
