# WIZARD-FITTINGS-V1  –  v2.0.0

**Industrial Geometric Engine for all 87 SMACNA HVAC Duct Fittings**

A Python library that models, parametrises, and calculates geometric and
aerodynamic properties of HVAC ductwork fittings following the
[SMACNA](https://www.smacna.org/) standard (Sheet Metal and Air Conditioning
Contractors' National Association).

Version 2.0.0 adds a full fitting registry (87 fittings), an isometric
Canvas2D renderer, three themes, and multi-format export (PDF/PNG/STL/STEP).

---

## What's new in v2.0.0

| Feature | Details |
|---|---|
| **87-fitting SMACNA registry** | All fittings in categories RE, RO, RT, RR, RC, CE, CT, CR, FO, SP, SU |
| **Isometric renderer** | Canvas2D projection: `screen_x = (x-z)·cos30°·scale + cx` |
| **9 draw primitives** | `isoBox`, `isoCylinder`, `isoCone`, `isoElbowArc`, `isoFlatOval`, `isoDimLine`, `isoCoordCube`, `isoTitleBlock`, `isoAnnotationBlock` |
| **3 themes** | `light_technical`, `dark_professional`, `blueprint` |
| **4 export formats** | PDF, PNG, STL, STEP |
| **New element classes** | Offsets (RO), Flat-oval (FO), Special/Accessory (SP), Supports (SU) |

---

## Features

| Module | Description |
|---|---|
| `core.primitives` | 2-D / 3-D point and vector types |
| `core.dimensions` | Cross-section dimensions with metric / imperial support |
| `elements.ducts` | Rectangular, round, and oval straight duct sections |
| `elements.elbows` | Smooth-radius rectangular, smooth-radius round, and mitered elbows |
| `elements.transitions` | Rectangular, round, and rect→round transition sections |
| `elements.tees` | Rectangular and round tee / wye fittings |
| `elements.caps` | Rectangular and round end-cap fittings |
| `elements.offsets` | Rectangular offset fittings (RO-1..5) |
| `elements.oval` | Flat-oval fittings (FO-1..8) |
| `elements.special` | Special / accessory fittings (SP-1..10) |
| `elements.supports` | Support and hanger fittings (SU-1..8) |
| `registry.fitting_registry` | Complete 87-fitting SMACNA catalogue |
| `renderer.isometric` | Isometric projection engine + 9 draw primitives |
| `renderer.theme` | Theme manager (3 themes) |
| `renderer.sketch` | `SketchGenerator` – fitting → sketch dict (draw_cmds JSON) |
| `export.exporter` | `FittingExporter` – PDF / PNG / STL / STEP |
| `calculations.pressure_loss` | Dynamic pressure, friction factor, duct ΔP, fitting ΔP |

---

## Quick Start

```python
from geometric_engine.registry.fitting_registry import get_fitting, registry_summary
from geometric_engine.renderer.sketch import SketchGenerator
from geometric_engine.export.exporter import FittingExporter

# --- Browse the registry ---
print(registry_summary())   # {'CE': 7, 'CR': 7, 'CT': 10, ...}

entry = get_fitting("RE-4")
print(entry.params)          # ['W', 'H', 'R']
print(entry.description)     # 'Smooth-radius rectangular 90° elbow'

# --- Generate an isometric sketch ---
gen = SketchGenerator(theme="light_technical")
sketch = gen.generate(
    fitting_id="RE-4",
    params={"W": 0.4, "H": 0.3, "R": 0.6},
    metadata={"project": "Site A", "prepared_by": "J. Smith"},
)
print(sketch["theme"])       # 'light_technical'
print(len(sketch["draw_cmds"]))  # number of draw commands

# --- Export to different formats ---
exp = FittingExporter()
pdf_manifest = exp.export(sketch, fmt="pdf")   # JSON manifest for ReportLab
png_data     = exp.export(sketch, fmt="png")   # JSON for Canvas2D renderer
stl_text     = exp.export(sketch, fmt="stl")   # ASCII STL
step_stub    = exp.export(sketch, fmt="step")  # STEP AP214 JSON manifest
```

### Physics calculations

```python
from geometric_engine.core.dimensions import Dimensions, UnitSystem
from geometric_engine.elements.elbows import RectangularElbow
from geometric_engine.calculations.pressure_loss import fitting_pressure_drop, velocity_from_flow

dims = Dimensions(width=0.4, height=0.3)
elbow = RectangularElbow(dims, angle=90.0, radius_ratio=1.5, tag="EL-01")

print(elbow.loss_coefficient())   # ~0.19
print(elbow.surface_area())       # m²
print(elbow.info())               # dict with all geometric props

velocity = velocity_from_flow(flow_rate=0.5, area=elbow.inlet_area())
dp = fitting_pressure_drop(elbow.loss_coefficient(), velocity)
print(f"ΔP = {dp:.2f} Pa")
```

---

## Installation

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest        # 188 tests
```

---

## Project Layout

```
src/
  geometric_engine/
    core/
      primitives.py       # Point2D/3D, Vector2D/3D
      dimensions.py       # Dimensions, UnitSystem
    elements/
      base.py             # FittingElement ABC, FittingType enum
      ducts.py            # RectangularDuct, RoundDuct, OvalDuct
      elbows.py           # RectangularElbow, RoundElbow, MiteredElbow
      transitions.py      # RectangularTransition, RoundTransition, …
      tees.py             # RectangularTee, RoundTee, RectangularWye, RoundWye
      caps.py             # RectangularCap, RoundCap
      offsets.py          # RectangularSingleOffset … RectangularLateralOffset
      oval.py             # OvalElbow90 … OvalOffset
      special.py          # VolumeControlDamper … DoubleWallSection
      supports.py         # StrapHanger … SeismicTransverse
    registry/
      fitting_registry.py # FITTING_REGISTRY – all 87 SMACNA fittings
    renderer/
      isometric.py        # IsometricProjection + 9 draw primitives
      theme.py            # ThemeManager (light_technical/dark_professional/blueprint)
      sketch.py           # SketchGenerator
    export/
      exporter.py         # FittingExporter (pdf/png/stl/step)
    calculations/
      pressure_loss.py    # dynamic_pressure, duct_pressure_drop, …
tests/
  test_primitives.py
  test_dimensions.py
  test_elements.py
  test_pressure_loss.py
  test_registry.py
  test_new_elements.py
  test_renderer_and_export.py
```


---

## Features

| Module | Description |
|---|---|
| `core.primitives` | 2-D / 3-D point and vector types |
| `core.dimensions` | Cross-section dimensions with metric / imperial support |
| `elements.ducts` | Rectangular, round, and oval straight duct sections |
| `elements.elbows` | Smooth-radius rectangular, smooth-radius round, and mitered elbows |
| `elements.transitions` | Rectangular, round, and rect→round transition sections |
| `elements.tees` | Rectangular and round 90° tee branch fittings |
| `elements.tees` | Rectangular and round symmetrical wye fittings |
| `elements.caps` | Rectangular and round end-cap fittings |
| `calculations.pressure_loss` | Dynamic pressure, friction factor, duct ΔP, fitting ΔP |

---

## Quick Start

```python
from geometric_engine.core.dimensions import Dimensions, UnitSystem
from geometric_engine.elements.elbows import RectangularElbow, RoundElbow
from geometric_engine.elements.ducts import RoundDuct
from geometric_engine.calculations.pressure_loss import (
    fitting_pressure_drop,
    duct_pressure_drop,
    velocity_from_flow,
)

# --- Rectangular 90° elbow (metric) ---
dims = Dimensions(width=0.4, height=0.3)          # 400 mm × 300 mm
elbow = RectangularElbow(dims, angle=90.0, radius_ratio=1.5, tag="EL-01")

print(elbow.loss_coefficient())   # e.g. 0.187
print(elbow.surface_area())       # m²
print(elbow.info())               # dict with all geometric props

# --- Round elbow (imperial) ---
dims_imp = Dimensions(diameter=12.0, unit_system=UnitSystem.IMPERIAL)  # 12-inch duct
round_elbow = RoundElbow(dims_imp, angle=90.0, radius_ratio=1.5)

# --- Pressure drop ---
flow_rate = 0.5  # m³/s
velocity = velocity_from_flow(flow_rate, elbow.inlet_area())
dp_fitting = fitting_pressure_drop(elbow.loss_coefficient(), velocity)  # Pa
print(f"Fitting ΔP: {dp_fitting:.2f} Pa")

# --- Straight duct friction loss ---
duct = RoundDuct(Dimensions(diameter=0.5), length=10.0)
dp_duct = duct_pressure_drop(
    velocity=5.0,
    length=duct.length_m,
    hydraulic_diameter=duct.inlet_hydraulic_diameter(),
)
print(f"Duct ΔP: {dp_duct:.2f} Pa")
```

---

## Installation

```bash
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

---

## Project Layout

```
src/
  geometric_engine/
    core/
      primitives.py     # Point2D, Point3D, Vector2D, Vector3D
      dimensions.py     # Dimensions, UnitSystem
    elements/
      base.py           # FittingElement ABC, FittingType enum
      ducts.py          # RectangularDuct, RoundDuct, OvalDuct
      elbows.py         # RectangularElbow, RoundElbow, MiteredElbow
      transitions.py    # RectangularTransition, RoundTransition,
                        #   RectangularToRoundTransition
      tees.py           # RectangularTee, RoundTee, RectangularWye, RoundWye
      caps.py           # RectangularCap, RoundCap
    calculations/
      pressure_loss.py  # dynamic_pressure, fitting_pressure_drop,
                        #   duct_pressure_drop, friction_factor, …
tests/
  test_primitives.py
  test_dimensions.py
  test_elements.py
  test_pressure_loss.py
```
