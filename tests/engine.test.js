/**
 * Engine unit tests
 *
 * Run with:  node --experimental-vm-modules node_modules/.bin/jest tests/engine.test.js
 * Or simpler: node tests/engine.test.js  (self-contained, no test runner needed)
 *
 * These tests cover:
 *   • IsometricProjection – projection math
 *   • FittingGeometry     – geometry generation for every fitting type
 *   • WizardFittingsEngine – public API contract (headless, no DOM)
 *   • DEFAULT_CONFIG       – structural integrity
 */

// ── Minimal test harness (no external dependencies) ──────────────────────────

let _passed = 0;
let _failed = 0;
const _failures = [];

function describe(name, fn) {
  console.log(`\n── ${name}`);
  fn();
}

function it(name, fn) {
  try {
    fn();
    console.log(`  ✓ ${name}`);
    _passed++;
  } catch (err) {
    console.error(`  ✗ ${name}`);
    console.error(`    ${err.message}`);
    _failed++;
    _failures.push({ name, err });
  }
}

function expect(actual) {
  return {
    toBe:          (v) => { if (actual !== v) throw new Error(`Expected ${JSON.stringify(v)}, got ${JSON.stringify(actual)}`); },
    toEqual:       (v) => { if (JSON.stringify(actual) !== JSON.stringify(v)) throw new Error(`Expected ${JSON.stringify(v)}, got ${JSON.stringify(actual)}`); },
    toBeCloseTo:   (v, p=2) => { const d = Math.abs(actual - v); if (d > Math.pow(10, -p)) throw new Error(`Expected ~${v}, got ${actual}`); },
    toBeGreaterThan: (v) => { if (!(actual > v)) throw new Error(`Expected > ${v}, got ${actual}`); },
    toBeLessThan:    (v) => { if (!(actual < v)) throw new Error(`Expected < ${v}, got ${actual}`); },
    toBeInstanceOf: (Cls) => { if (!(actual instanceof Cls)) throw new Error(`Expected instance of ${Cls.name}`); },
    toBeTruthy:   () => { if (!actual) throw new Error(`Expected truthy, got ${actual}`); },
    toBeFalsy:    () => { if (actual) throw new Error(`Expected falsy, got ${actual}`); },
    toContain:    (v) => { if (!actual.includes(v)) throw new Error(`Expected array/string to contain ${v}`); },
    toHaveLength: (n) => { if (actual.length !== n) throw new Error(`Expected length ${n}, got ${actual.length}`); },
    toThrow:      ()  => {
      if (typeof actual !== "function") throw new Error("toThrow requires a function");
      try { actual(); throw new Error("Did not throw"); }
      catch (e) { if (e.message === "Did not throw") throw e; }
    },
  };
}

// ── Import modules (CommonJS-compatible dynamic import via createRequire) ─────
// We test the ES-module source via Node's native ESM loader.
// This file is run with:  node --input-type=module < tests/engine.test.js
// Or: node tests/engine.test.js  (with "type":"module" in package.json)

import { IsometricProjection }
  from "../src/wizard_fittings_isometric_engine/geometry/IsometricProjection.js";
import { generateGeometry, SUPPORTED_TYPES }
  from "../src/wizard_fittings_isometric_engine/geometry/FittingGeometry.js";
import { DEFAULT_CONFIG, ENGINE_VERSION, ENGINE_NAME }
  from "../src/wizard_fittings_isometric_engine/config.js";

// ─────────────────────────────────────────────────────────────────────────────

describe("IsometricProjection", () => {
  const proj = new IsometricProjection({ scale: 1, originX: 0, originY: 0 });

  it("projects world +X to right-and-down", () => {
    const p = proj.project(1, 0, 0);
    expect(p.x).toBeGreaterThan(0);   // rightward
    expect(p.y).toBeGreaterThan(0);   // downward in canvas coords
  });

  it("projects world +Y to left-and-down", () => {
    const p = proj.project(0, 1, 0);
    expect(p.x).toBeLessThan(0);      // leftward
    expect(p.y).toBeGreaterThan(0);   // downward
  });

  it("projects world +Z upward", () => {
    const p = proj.project(0, 0, 1);
    expect(p.x).toBeCloseTo(0, 5);    // straight up (no horizontal shift)
    expect(p.y).toBeLessThan(0);      // upward in canvas coords
  });

  it("origin stays at canvas origin when scale=1 and origin=0,0", () => {
    const p = proj.project(0, 0, 0);
    expect(p.x).toBeCloseTo(0, 10);
    expect(p.y).toBeCloseTo(0, 10);
  });

  it("origin offset is applied correctly", () => {
    const p2 = new IsometricProjection({ scale: 1, originX: 100, originY: 50 });
    const p  = p2.project(0, 0, 0);
    expect(p.x).toBeCloseTo(100, 10);
    expect(p.y).toBeCloseTo(50,  10);
  });

  it("scale doubles the projected distance", () => {
    const p1 = proj.project(10, 0, 0);
    const p2 = proj.withScale(2).project(10, 0, 0);
    expect(p2.x).toBeCloseTo(p1.x * 2, 5);
    expect(p2.y).toBeCloseTo(p1.y * 2, 5);
  });

  it("projectArray works for [x,y,z] tuple", () => {
    const p  = proj.projectArray([1, 0, 0]);
    const p2 = proj.project(1, 0, 0);
    expect(p.x).toBeCloseTo(p2.x, 10);
    expect(p.y).toBeCloseTo(p2.y, 10);
  });

  it("projectAll projects every vertex", () => {
    const verts  = [[0,0,0],[1,0,0],[0,1,0],[0,0,1]];
    const result = proj.projectAll(verts);
    expect(result).toHaveLength(4);
  });

  it("axisVectors returns dx/dy for x, y, z axes", () => {
    const av = proj.axisVectors;
    expect(typeof av.x.dx).toBe("number");
    expect(typeof av.y.dy).toBe("number");
    expect(typeof av.z.dy).toBe("number");
  });
});

// ─────────────────────────────────────────────────────────────────────────────

describe("FittingGeometry – SUPPORTED_TYPES", () => {
  it("exports array of type strings", () => {
    expect(Array.isArray(SUPPORTED_TYPES)).toBe(true);
    expect(SUPPORTED_TYPES.length).toBeGreaterThan(0);
  });

  it("includes all 8 canonical fitting types", () => {
    const required = ["elbow_90","elbow_45","tee","reducer","offset","cap","wye","transition"];
    required.forEach(t => expect(SUPPORTED_TYPES).toContain(t));
  });

  it("throws for unknown fitting type", () => {
    expect(() => generateGeometry("banana", {})).toThrow();
  });
});

// ── Per-type geometry contract ───────────────────────────────────────────────

const DIMS = {
  width: 300, height: 200, depth: 300,
  centerline_radius: 150, angle_deg: 45,
  inlet_width: 300, inlet_height: 200,
  outlet_width: 200, outlet_height: 150,
};

function checkGeometry(geo, label) {
  it(`${label} returns vertices array`, () => {
    expect(Array.isArray(geo.vertices)).toBe(true);
    expect(geo.vertices.length).toBeGreaterThan(0);
  });
  it(`${label} every vertex has 3 coords`, () => {
    geo.vertices.forEach(v => {
      if (v.length !== 3) throw new Error(`Vertex has ${v.length} coords: ${v}`);
    });
  });
  it(`${label} returns edges array`, () => {
    expect(Array.isArray(geo.edges)).toBe(true);
    expect(geo.edges.length).toBeGreaterThan(0);
  });
  it(`${label} each edge has v1, v2, type`, () => {
    geo.edges.forEach(e => {
      if (typeof e.v1 !== "number") throw new Error("edge.v1 not a number");
      if (typeof e.v2 !== "number") throw new Error("edge.v2 not a number");
      if (!["visible","hidden","silhouette"].includes(e.type))
        throw new Error(`Unknown edge type: ${e.type}`);
    });
  });
  it(`${label} edge vertex indices are in range`, () => {
    const n = geo.vertices.length;
    geo.edges.forEach(e => {
      if (e.v1 < 0 || e.v1 >= n) throw new Error(`edge.v1=${e.v1} out of range [0,${n})`);
      if (e.v2 < 0 || e.v2 >= n) throw new Error(`edge.v2=${e.v2} out of range [0,${n})`);
    });
  });
  it(`${label} returns faces array`, () => {
    expect(Array.isArray(geo.faces)).toBe(true);
    expect(geo.faces.length).toBeGreaterThan(0);
  });
  it(`${label} returns dimensions array`, () => {
    expect(Array.isArray(geo.dimensions)).toBe(true);
    expect(geo.dimensions.length).toBeGreaterThan(0);
  });
}

SUPPORTED_TYPES.forEach(type => {
  describe(`FittingGeometry – ${type}`, () => {
    const geo = generateGeometry(type, DIMS);
    checkGeometry(geo, type);
  });
});

// ─────────────────────────────────────────────────────────────────────────────

describe("DEFAULT_CONFIG structure", () => {
  it("has ENGINE_NAME and ENGINE_VERSION exports", () => {
    expect(ENGINE_NAME).toBe("WIZARD_FITTINGS_ISOMETRIC_ENGINE");
    expect(ENGINE_VERSION).toBe("1.0.0");
  });

  it("default output mode is sketch_isometric", () => {
    expect(DEFAULT_CONFIG.output_mode.default).toBe("sketch_isometric");
  });

  it("available_modes includes both modes", () => {
    expect(DEFAULT_CONFIG.output_mode.available_modes).toContain("sketch_isometric");
    expect(DEFAULT_CONFIG.output_mode.available_modes).toContain("3d_visual");
  });

  it("sketch_isometric has object_lines config", () => {
    const ol = DEFAULT_CONFIG.output_mode.sketch_isometric.object_lines;
    expect(typeof ol.visible_edges.color).toBe("string");
    expect(typeof ol.hidden_edges.color).toBe("string");
    expect(typeof ol.silhouette.color).toBe("string");
  });

  it("dimension_lines config has blue color", () => {
    const dl = DEFAULT_CONFIG.output_mode.sketch_isometric.dimension_lines;
    expect(dl.color).toBe("#1A56DB");
    expect(dl.text_color).toBe("#1A56DB");
  });

  it("sketch_isometric background is white", () => {
    expect(DEFAULT_CONFIG.output_mode.sketch_isometric.background).toBe("#FFFFFF");
  });

  it("theming has three themes", () => {
    const themes = DEFAULT_CONFIG.theming.available_themes;
    expect(typeof themes.light_technical).toBe("object");
    expect(typeof themes.dark_professional).toBe("object");
    expect(typeof themes.blueprint).toBe("object");
  });

  it("export formats include pdf, stl, step, png", () => {
    const fmt = DEFAULT_CONFIG.export.formats;
    expect(fmt.pdf.enabled).toBe(true);
    expect(fmt.stl.enabled).toBe(true);
    expect(fmt.step.enabled).toBe(true);
    expect(fmt.png.enabled).toBe(true);
  });

  it("annotations_panel has required fields", () => {
    const required = DEFAULT_CONFIG.annotations_panel.fields.filter(f => f.required);
    expect(required.length).toBeGreaterThan(0);
  });

  it("coordinate_cube config is present", () => {
    expect(DEFAULT_CONFIG.coordinate_cube.enabled).toBe(true);
    expect(DEFAULT_CONFIG.coordinate_cube.size_px).toBe(80);
  });

  it("viewport_controls.zoom has min/max scale", () => {
    const z = DEFAULT_CONFIG.viewport_controls.zoom;
    expect(z.min_scale).toBeLessThan(z.max_scale);
  });
});

// ── Dimension fields ──────────────────────────────────────────────────────────

describe("DEFAULT_CONFIG.dimensions.fields", () => {
  const fields = DEFAULT_CONFIG.dimensions.fields;

  it("width field has label W and blue color", () => {
    expect(fields.width.label).toBe("W");
    expect(fields.width.color).toBe("#1A56DB");
  });

  it("angle field has correct label", () => {
    expect(fields.angle.label).toBe("∠");
  });

  it("inlet_diameter has Ø IN label", () => {
    expect(fields.inlet_diameter.label).toBe("Ø IN");
  });
});

// ── Summary ───────────────────────────────────────────────────────────────────

console.log(`\n${"─".repeat(50)}`);
console.log(`Results: ${_passed} passed, ${_failed} failed`);
if (_failures.length) {
  console.log("\nFailures:");
  _failures.forEach(({ name }) => console.log(`  ✗ ${name}`));
  process.exit(1);
} else {
  console.log("All tests passed ✓");
}
