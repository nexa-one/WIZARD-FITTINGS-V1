"""
WIZARD-FITTINGS CNC Module – Flat Metal Template Engine
=======================================================
Generates 2-D flat-metal (sheet-metal) cutting templates and
3-D hollow-duct visualisations for HVAC rectangular / round /
flat-oval ductwork following SMACNA standards.

Sub-packages
------------
models       – Duct cross-sections, fittings, sheet-metal properties
flat_pattern – 2-D development / unfolding of duct surfaces
renderer     – Isometric 3-D renderer with hollow-shell depth effects
export       – DXF / SVG / G-code export for CNC machines
"""

from cnc_module.models import (
    DuctShape,
    RectangularDuct,
    RoundDuct,
    FlatOvalDuct,
    SheetMetal,
)
from cnc_module.flat_pattern import FlatPatternGenerator, FlatPattern
from cnc_module.renderer import IsometricRenderer
from cnc_module.export import DXFExporter, SVGExporter

__version__ = "1.0.0"
__all__ = [
    "DuctShape",
    "RectangularDuct",
    "RoundDuct",
    "FlatOvalDuct",
    "SheetMetal",
    "FlatPatternGenerator",
    "FlatPattern",
    "IsometricRenderer",
    "DXFExporter",
    "SVGExporter",
]
