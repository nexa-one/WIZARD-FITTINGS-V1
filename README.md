# HVAC Parametric Engine v7.0

A professional HVAC Parametric CAD Platform for designing and ordering sheet-metal ductwork fittings. Built with React + TypeScript + Vite + Three.js + Tailwind CSS.

## Features

- **3D Viewport** — Real-time Three.js rendering with OrbitControls; three view modes: 3D Visual, CNC Flat Pattern, X-Ray Transparent
- **10 Fitting Types** — Straight Duct, Elbow 90°/45°, Transition, Reducer, Offset, Tee, Cross, Cap, Register Box
- **Three Input Modes**
  - 🤖 **AI Generator** — Describe a fitting in plain English; NLP parser extracts geometry, dimensions, and shape
  - ⚙️ **Parametric Builder** — Full manual form with all parameters
  - 🧙 **Wizard Fittings** — 6-step guided workflow with elevation and plan codes
- **ID/OD Dimension Mode** — Toggle between external (OD) and internal (ID) dimensions; wall gauge thickness applied automatically
- **Wall Construction** — Single wall and double wall (with insulation); liner perforation parameters
- **Order Management** — Create draft orders, add items, track status
- **Validation Engine** — Real-time error and warning reporting
- **Plugin Registry** — Extensible architecture for geometry, export, analysis, and UI plugins
- **Language Toggle** — English (USA) / Spanish (LATAM)
- **Dark / Light Theme**

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI Framework | React 18 + TypeScript |
| Build | Vite 5 |
| 3D Rendering | Three.js + @react-three/fiber + @react-three/drei |
| State | Zustand |
| Styling | Tailwind CSS + clsx |

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## Build

```bash
npm run build   # TypeScript check + Vite production build
npm run preview # Preview production build locally
```

## Project Structure

```
src/
├── types/hvac.ts          # Enums and interfaces (PSD, Order, etc.)
├── engine/
│   ├── industrialDefaults.ts  # SMACNA defaults
│   ├── dimensionResolver.ts   # ID/OD conversion using gauge thickness
│   ├── wallConstruction.ts    # Single/double wall profile computation
│   ├── validationEngine.ts    # PSD validation (errors + warnings)
│   ├── loftEngine.ts          # Profile-to-geometry loft generation
│   ├── geometryEngine.ts      # Per-fitting-type Three.js geometry
│   └── index.ts               # processPSD() pipeline export
├── store/index.ts             # Zustand global store
├── plugins/pluginRegistry.ts  # Plugin architecture
├── components/
│   ├── Viewport3D.tsx          # @react-three/fiber canvas
│   ├── toolbar/GlobalToolbar.tsx
│   ├── panels/DockablePanel.tsx
│   ├── panels/OrderPanel.tsx
│   └── ui/                    # IDODToggle, ThemeToggle
└── modules/
    ├── ai/AIGenerator.tsx
    ├── parametric/ParametricBuilder.tsx
    └── wizard/                # 6-step WizardFittings + step components
```
