"""
cnc_module.renderer
===================
3-D hollow-duct visualisation engine.

The key constraint from the problem statement:
  *"El ducto es un objeto hueco formado por una lámina de metal – no se
   debe ver como un sólido 3-D.  Se deben usar efectos de profundidad
   que permitan visualizar el ducto como tal."*

This renderer produces isometric SVG output where:
  • Outer faces use light fills (visible sheet-metal surface).
  • Inner cavity faces use darker fills (hollow interior).
  • End openings show the wall cross-section (ring/frame) so the viewer
    can see that the duct is hollow, not solid.
  • Edge-shading gradients simulate sheet-metal reflectivity.
  • Hidden-line removal is approximated by face sorting (painter's algo).
"""

from cnc_module.renderer.isometric import IsometricRenderer
from cnc_module.renderer.hollow_shell import (
    HollowShellEffect,
    Face,
    FaceType,
    RGBColor,
)

__all__ = [
    "IsometricRenderer",
    "HollowShellEffect",
    "Face",
    "FaceType",
    "RGBColor",
]
