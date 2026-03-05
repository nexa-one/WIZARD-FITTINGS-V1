# WIZARD-FITTINGS-V1

**Industrial Geometric Engine for SMACNA HVAC Duct Fittings**

A Python library that models, parameterises, and calculates geometric and
aerodynamic properties of HVAC ductwork fittings following the
[SMACNA](https://www.smacna.org/) standard (Sheet Metal and Air Conditioning
Contractors' National Association).

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
