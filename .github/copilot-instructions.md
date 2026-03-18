# Copilot Instructions for WIZARD-FITTINGS-V1

## Project Overview
WIZARD-FITTINGS is a Python library implementing an industrial geometric engine for SMACNA HVAC duct fittings (v2.0.0). It provides geometry calculations, pressure-loss formulas, isometric rendering, and multi-format export for 87 standard fittings.

## Repository Structure
- `src/geometric_engine/` – Main package
  - `core/` – Geometric primitives (`Point2D`, `Point3D`, `Vector2D`, `Vector3D`) and `Dimensions` (unit conversion)
  - `elements/` – Fitting element classes (ducts, elbows, transitions, tees, caps, offsets, oval, special, supports)
  - `registry/` – 87-fitting SMACNA catalogue (`FittingRegistry`, `FittingEntry`)
  - `calculations/` – HVAC pressure-loss formulas (Darcy-Weisbach, Colebrook-White)
  - `renderer/` – Isometric projection engine and themes
  - `export/` – Multi-format export (PDF, STL, STEP, PNG)
- `tests/` – pytest test suite (188 tests)

## Build & Test
```bash
pip install -e ".[dev]"
pytest
```

## Code Conventions
- Python 3.9+, no runtime dependencies
- All public APIs use type hints with `from __future__ import annotations`
- Physical quantities are stored internally in SI units (metres, m², m³)
- Use `Dimensions._to_m()` to convert user-provided values to metres
- `_validate_positive(name, value)` for parameter validation
- Every `FittingElement` subclass must implement `surface_area()`, `volume()`, and `loss_coefficient()`
- Cross-section area for circles: `π·(D/2)²` (not `π·D²`)
- Volume for shape-changing transitions (rect→round, oval→round, etc.): use trapezoidal approximation `L/2·(A₁+A₂)`
- Volume for same-shape transitions (rect→rect, round→round): use prismatoid formula `L/6·(A₁+4·Aₘ+A₂)` with the actual mid-section dimensions
- Surface area of revolution (e.g., bell-mouth quarter-circle flare): use `2π·r·∫ R(φ) dφ` (Pappus' theorem), not full/half torus formulas

## Testing Practices
- Place element tests in `tests/test_elements.py` and `tests/test_new_elements.py`
- Test exact computed values (not just `> 0`) wherever a formula has a known closed-form result
- Use `math.isclose()` for floating-point comparisons
