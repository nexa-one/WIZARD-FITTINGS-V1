# WIZARD-FITTINGS-V1

A comprehensive HVAC/SMACNA industrial platform for designing, analysing and fabricating sheet-metal ductwork fittings.  
The repository brings together four main modules:

| Module | Tech | Description |
|--------|------|-------------|
| **HVAC Parametric Engine** (React app) | TypeScript / React / Vite / Three.js | Interactive CAD frontend — 3D viewport, AI generator, wizard workflow |
| **Geometric Engine** (Python) | Python 3.9+ | 87-fitting SMACNA registry, isometric renderer, pressure-loss calculations |
| **CNC Flat-Metal Module** (Python) | Python 3.9+ | Flat-pattern development, hollow-duct 3D renderer, DXF + SVG export |
| **Manufacturing Engine** (Python) | Python 3.9+ | Surface unwrap, seam engine, DXF export, bill-of-materials |
| **Isometric Sketch Engine** (JS ESM) | Pure JavaScript (ESM) | Browser-ready hollow-duct isometric renderer for all 87 SMACNA fittings |

---

## React HVAC Parametric Engine (Frontend)

### Features
- **3D Viewport** — Real-time Three.js rendering; 3D Visual, CNC Flat Pattern, X-Ray modes
- **10 Fitting Types** — Straight Duct, Elbow 90°/45°, Transition, Reducer, Offset, Tee, Cross, Cap, Register Box
- **Three Input Modes**: AI Generator (NLP), Parametric Builder, 6-step Wizard Fittings
- **ID/OD Dimension Mode** — gauge-based wall thickness applied automatically
- **Order Management** — draft / submit workflow
- **Validation Engine** — real-time errors + warnings
- **Plugin Registry** — extensible geometry, export, analysis, UI plugins
- **i18n** — English (USA) / Spanish (LATAM)

### Quick Start
```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # TypeScript check + Vite production build
```

---

## Python Modules

### Install (all modules)
```bash
pip install -e ".[dev]"
```

### Run Tests
```bash
pytest                       # all Python test suites
pytest tests/geometric_engine
pytest tests/cnc_module
pytest tests/manufacturing_engine
```

### Geometric Engine (`src/geometric_engine/`)
Full 87-fitting SMACNA registry with isometric renderer, themes, pressure-loss calculations,
and DXF/SVG export.  195 tests.

### CNC Flat-Metal Module (`src/cnc_module/`)
Flat-pattern development (2D unfolding), hollow-duct 3D renderer, DXF R2010 + SVG export.
123 tests.

### Manufacturing Engine (`src/manufacturing_engine/`)
Surface unwrapping, flat-pattern generation, seam layout, DXF export, bill-of-materials.

---

## Isometric Sketch Engine (JavaScript/ESM)

A pure ES-module browser library that renders all 87 SMACNA duct fittings as isometric
hollow-shell SVGs with configurable themes and export (SVG/PDF/PNG).

```bash
# From the engine directory
cd src/wizard_fittings_isometric_engine
node ../../tests/engine.test.js   # run 82 tests
```

Or from the repo root:
```bash
node tests/engine.test.js
```

---

## Project Structure

```
.
├── src/
│   ├── App.tsx                          # React app entry
│   ├── components/                      # React UI components
│   ├── engine/                          # HVAC parametric engine (TS)
│   ├── i18n/                            # Translations (EN/ES)
│   ├── modules/ai, parametric, wizard/  # Input mode modules
│   ├── plugins/                         # Plugin registry
│   ├── store/                           # Zustand state
│   ├── styles/                          # CSS for isometric sketch
│   ├── types/                           # TypeScript types
│   ├── geometric_engine/                # Python geometric engine
│   ├── cnc_module/                      # Python CNC flat-metal module
│   ├── manufacturing_engine/            # Python manufacturing engine
│   └── wizard_fittings_isometric_engine/ # JS isometric engine
├── tests/
│   ├── geometric_engine/                # 195 Python tests
│   ├── cnc_module/                      # 123 Python tests
│   ├── manufacturing_engine/            # Python tests
│   └── engine.test.js                   # 82 JS tests
├── demo/                                # HTML demo for isometric engine
├── examples/                            # Python usage examples
├── pyproject.toml                       # Python package config
├── package.json                         # Node/React app config
└── README.md
```
