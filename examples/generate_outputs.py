#!/usr/bin/env python3
"""
examples/generate_outputs.py
==============================
Generate sample flat-pattern SVGs, 3-D isometric SVGs, and DXF files
for all standard HVAC duct fittings.

Run from the repository root:
    python examples/generate_outputs.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from cnc_module.models.duct import RectangularDuct, RoundDuct, FlatOvalDuct
from cnc_module.models.material import SheetMetal
from cnc_module.models.fittings import (
    StraightSection, RectangularElbow, RoundElbow,
    RectangularTransition, RoundToRectTransition,
    RectangularTee, RoundTee, RectangularReducer, EndCap,
)
from cnc_module.flat_pattern import FlatPatternGenerator
from cnc_module.flat_pattern.seam import SeamType
from cnc_module.renderer import IsometricRenderer
from cnc_module.export import DXFExporter, SVGExporter

OUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT, exist_ok=True)

metal = SheetMetal.from_gauge(22)
gen = FlatPatternGenerator(seam_type=SeamType.PITTSBURGH)
renderer = IsometricRenderer(circle_segments=36)
dxf_exp = DXFExporter()
svg_exp = SVGExporter()

fittings = [
    StraightSection(
        label="400×200 Straight – 1000 mm",
        duct=RectangularDuct(400, 200),
        length=1000,
        metal=metal,
    ),
    StraightSection(
        label="Ø300 Round Straight – 1000 mm",
        duct=RoundDuct(300),
        length=1000,
        metal=metal,
    ),
    StraightSection(
        label="500×200 Flat-Oval Straight – 1000 mm",
        duct=FlatOvalDuct(500, 200),
        length=1000,
        metal=metal,
    ),
    RectangularElbow(
        label="400×200 Rect Elbow 90°",
        duct=RectangularDuct(400, 200),
        angle=90,
        throat_radius=100,
        metal=metal,
    ),
    RoundElbow(
        label="Ø300 Round Elbow 90°",
        duct=RoundDuct(300),
        angle=90,
        metal=metal,
    ),
    RectangularTransition(
        label="600×400 → 300×200 Transition",
        inlet=RectangularDuct(600, 400),
        outlet=RectangularDuct(300, 200),
        length=300,
        metal=metal,
    ),
    RoundToRectTransition(
        label="Ø250 → 300×200 Round-to-Rect",
        round_end=RoundDuct(250),
        rect_end=RectangularDuct(300, 200),
        length=250,
        metal=metal,
    ),
    RectangularTee(
        label="600×300 Rect Tee (branch 300×200)",
        main=RectangularDuct(600, 300),
        branch=RectangularDuct(300, 200),
        length=600,
        metal=metal,
    ),
    RoundTee(
        label="Ø350 Round Tee (branch Ø200)",
        main=RoundDuct(350),
        branch=RoundDuct(200),
        length=600,
        metal=metal,
    ),
    RectangularReducer(
        label="400×300 → 200×150 Reducer",
        large=RectangularDuct(400, 300),
        small=RectangularDuct(200, 150),
        length=200,
        metal=metal,
    ),
    EndCap(
        label="400×200 End Cap",
        duct=RectangularDuct(400, 200),
        metal=metal,
    ),
]

for fitting in fittings:
    slug = fitting.label.replace(" ", "_").replace("×", "x").replace("→", "to").replace("/", "-").replace("°", "deg")

    # Flat pattern
    try:
        fp = gen.generate(fitting)
        flat_svg = os.path.join(OUT, f"{slug}__flat.svg")
        svg_exp.export_flat_pattern(fp, flat_svg)
        dxf_file = os.path.join(OUT, f"{slug}__flat.dxf")
        dxf_exp.export(fp, dxf_file)
        print(f"✓ Flat pattern: {slug} ({fp.panel_count} panels)")
    except Exception as e:
        print(f"✗ Flat pattern ERROR for {slug}: {e}")

    # 3D isometric render
    try:
        svg_3d = renderer.render(fitting, width=900, height=680)
        view_file = os.path.join(OUT, f"{slug}__3d.svg")
        svg_exp.export_3d_view(svg_3d, view_file)
        print(f"✓ 3D view:      {slug}")
    except Exception as e:
        print(f"✗ 3D view ERROR for {slug}: {e}")

print(f"\nAll outputs written to: {OUT}")
