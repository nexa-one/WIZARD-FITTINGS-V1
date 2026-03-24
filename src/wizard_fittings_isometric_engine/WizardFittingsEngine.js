/**
 * WizardFittingsEngine – main façade for the WIZARD_FITTINGS_ISOMETRIC_ENGINE.
 *
 * Integrates:
 *   • IsometricSketchRenderer  (sketch_isometric mode)
 *   • CoordinateCube           (XYZ orientation widget)
 *   • ViewportController       (zoom / pan / rotate)
 *   • ThemeManager             (theme switching + persistence)
 *   • ExportManager            (PDF / PNG / STL / STEP)
 *   • FittingGeometry          (parametric geometry generators)
 *
 * Usage (browser ES-module):
 *   import { WizardFittingsEngine } from "./index.js";
 *   const engine = new WizardFittingsEngine({ canvas, cubeCanvas });
 *   engine.render(fittingJSON);
 */

import { DEFAULT_CONFIG }            from "./config.js";
import { generateGeometry }          from "./geometry/FittingGeometry.js";
import { IsometricSketchRenderer }   from "./renderers/IsometricSketchRenderer.js";
import { CoordinateCube }            from "./ui/CoordinateCube.js";
import { ViewportController }        from "./ui/ViewportController.js";
import { ThemeManager }              from "./ui/ThemeManager.js";
import { ExportManager }             from "./export/ExportManager.js";

export class WizardFittingsEngine {
  /**
   * @param {object} opts
   * @param {HTMLCanvasElement}  opts.canvas       – main drawing canvas
   * @param {HTMLCanvasElement}  [opts.cubeCanvas] – coordinate-cube mini canvas
   * @param {object}             [opts.config]     – optional config overrides (deep-merged)
   */
  constructor({ canvas, cubeCanvas = null, config = {} } = {}) {
    this.canvas      = canvas;
    this.cubeCanvas  = cubeCanvas;
    this.config      = this._mergeConfig(DEFAULT_CONFIG, config);

    // Sub-modules
    this.themeManager = new ThemeManager(this.config.theming);
    this.renderer     = new IsometricSketchRenderer(canvas, this.config);
    this.exportMgr    = new ExportManager(canvas, this.config.export);

    if (cubeCanvas) {
      this.cube = new CoordinateCube(cubeCanvas, this.config);
    }

    // Viewport controller – updates renderer state on interaction
    this.viewport = new ViewportController(
      canvas,
      this.config.viewport_controls,
      {
        onUpdate: ({ scale, panX, panY, rotDeg }) => {
          this.renderer.setScale(scale);
          this.renderer.setPan(panX, panY);
          if (this.cube) this.cube.draw(rotDeg, this.themeManager.currentKey);
          if (this._lastFitting && this._lastGeometry) {
            this.renderer.render(this._lastFitting, this._lastGeometry);
          }
        },
      }
    );

    // Current mode: 'sketch_isometric' | '3d_visual'
    this._mode        = this.config.output_mode.default;
    this._lastFitting  = null;
    this._lastGeometry = null;

    // Propagate theme changes to renderer
    this.themeManager.onChange((key) => {
      this.renderer.setTheme(key);
      if (this._lastFitting && this._lastGeometry) {
        this.renderer.render(this._lastFitting, this._lastGeometry);
      }
      if (this.cube) this.cube.draw(0, key);
    });
  }

  // ── render ────────────────────────────────────────────────────────────────

  /**
   * Render a fitting from its JSON definition.
   *
   * @param {object} fittingJSON  – fitting object matching the fitting_schema
   * @returns {WizardFittingsEngine} this (chainable)
   */
  render(fittingJSON) {
    const type = fittingJSON.type;
    const dims = fittingJSON.dimensions || {};

    // Apply render_options.theme if specified
    const ro = fittingJSON.render_options || {};
    if (ro.theme && ro.theme !== this.themeManager.currentKey) {
      this.themeManager.setTheme(ro.theme);
    }
    if (ro.mode) {
      this._mode = ro.mode;
    }

    const geometry = generateGeometry(type, dims);

    this._lastFitting  = fittingJSON;
    this._lastGeometry = geometry;

    if (this._mode === "sketch_isometric") {
      this.renderer.setTheme(this.themeManager.currentKey);
      this.renderer.render(fittingJSON, geometry);
    }
    // 3d_visual mode: delegate to a WebGL renderer (future expansion)

    if (this.cube) this.cube.draw(0, this.themeManager.currentKey);

    return this;
  }

  // ── parametric update ────────────────────────────────────────────────────

  /**
   * Update a single dimension field and re-render immediately.
   * Designed for real-time parametric module integration.
   *
   * @param {string} key    – dimension key, e.g. 'width'
   * @param {number} value  – new value in mm
   * @returns {WizardFittingsEngine} this
   */
  updateParameter(key, value) {
    if (!this._lastFitting) return this;
    this._lastFitting = {
      ...this._lastFitting,
      dimensions: { ...this._lastFitting.dimensions, [key]: value },
    };
    return this.render(this._lastFitting);
  }

  // ── mode ─────────────────────────────────────────────────────────────────

  /**
   * Switch between 'sketch_isometric' and '3d_visual'.
   * @param {'sketch_isometric'|'3d_visual'} mode
   */
  setMode(mode) {
    if (!this.config.output_mode.available_modes.includes(mode)) {
      throw new Error(`Invalid mode "${mode}"`);
    }
    this._mode = mode;
    if (this._lastFitting) this.render(this._lastFitting);
    return this;
  }

  get currentMode() { return this._mode; }

  // ── theme ─────────────────────────────────────────────────────────────────

  /**
   * Switch the active theme.
   * @param {'light_technical'|'dark_professional'|'blueprint'} theme
   */
  setTheme(theme) {
    this.themeManager.setTheme(theme);
    return this;
  }

  // ── export ────────────────────────────────────────────────────────────────

  /**
   * Export the current view.
   * @param {'png'|'pdf'|'stl'|'step'} format
   * @param {object} [opts]  – format-specific options
   */
  export(format, opts = {}) {
    switch (format) {
      case "png":
        return this.exportMgr.exportPNG(opts.filename, opts);
      case "pdf":
        return this.exportMgr.exportPDF(opts.filename, opts);
      case "stl":
        if (!this._lastGeometry) throw new Error("No geometry to export. Call render() first.");
        return this.exportMgr.exportSTL(this._lastGeometry, opts.filename);
      case "step":
        if (!this._lastGeometry) throw new Error("No geometry to export. Call render() first.");
        return this.exportMgr.exportSTEP(this._lastGeometry, opts.filename);
      default:
        throw new Error(`Unknown export format "${format}"`);
    }
  }

  // ── viewport ──────────────────────────────────────────────────────────────

  resetView() {
    this.viewport.reset();
    return this;
  }

  // ── utility ───────────────────────────────────────────────────────────────

  /**
   * Populate a theme <select> element.
   * @param {HTMLSelectElement} el
   */
  populateThemeSelect(el) {
    this.themeManager.populateSelect(el);
    return this;
  }

  // ── deep-merge config ─────────────────────────────────────────────────────

  _mergeConfig(defaults, overrides) {
    const result = { ...defaults };
    for (const key of Object.keys(overrides)) {
      if (
        overrides[key] !== null &&
        typeof overrides[key] === "object" &&
        !Array.isArray(overrides[key]) &&
        typeof defaults[key] === "object"
      ) {
        result[key] = this._mergeConfig(defaults[key], overrides[key]);
      } else {
        result[key] = overrides[key];
      }
    }
    return result;
  }
}
