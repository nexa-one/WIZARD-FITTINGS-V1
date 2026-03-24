"""
cnc_module.flat_pattern
=======================
2-D flat-metal (sheet-metal development) template generator.
Produces cut-ready panels with:
  • body lines (outer cut boundary)
  • bend lines (fold lines for press-brake)
  • seam allowances (Pittsburgh, snap-lock, or butt seams)
  • tab and slot geometry for transverse joints
"""

from cnc_module.flat_pattern.pattern import FlatPattern, Panel, LineType
from cnc_module.flat_pattern.generator import FlatPatternGenerator
from cnc_module.flat_pattern.seam import SeamType, SeamAllowance

__all__ = [
    "FlatPattern",
    "Panel",
    "LineType",
    "FlatPatternGenerator",
    "SeamType",
    "SeamAllowance",
]
