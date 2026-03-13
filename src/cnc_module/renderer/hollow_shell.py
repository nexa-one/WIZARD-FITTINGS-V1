"""
cnc_module.renderer.hollow_shell
==================================
Depth / shading model for hollow sheet-metal duct rendering.

Key concepts
------------
FaceType.OUTER_FACE   – Visible exterior surfaces of the duct.
FaceType.INNER_FACE   – Interior cavity surfaces visible through an open end.
FaceType.END_RING     – The annular cross-section at each duct opening (shows
                        wall thickness – this is what communicates "hollow").
FaceType.HIDDEN       – Back-facing or occluded surfaces (not rendered).

Lighting model
--------------
Ambient + directional Lambertian shading is applied:
  • Light direction = normalised (1, 2, 3) in world space (upper-right).
  • Outer faces:  L_ambient=0.25, L_diffuse=0.75
  • Inner faces:  L_ambient=0.05, L_diffuse=0.20  (dark cavity effect)
  • End rings:    L_ambient=0.35, L_diffuse=0.45  (visible edge highlight)

The resulting colour is blended with a configurable material base colour.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple, Optional

# Type aliases
Vec3 = Tuple[float, float, float]
RGBColor = Tuple[int, int, int]   # 0-255 per channel


class FaceType(Enum):
    OUTER_FACE = auto()
    INNER_FACE = auto()
    END_RING = auto()
    HIDDEN = auto()


@dataclass
class Face:
    """A 3-D polygon (face of the duct mesh).

    Attributes
    ----------
    vertices:   List of 3-D points in world space (mm).
    face_type:  Semantic classification.
    normal:     Outward-facing unit normal vector.
    base_color: Material base colour (RGB 0-255).
    label:      Debug / annotation string.
    """

    vertices: List[Vec3]
    face_type: FaceType
    normal: Optional[Vec3] = None
    base_color: RGBColor = (180, 180, 180)   # galvanised steel grey
    label: str = ""

    def __post_init__(self) -> None:
        if self.normal is None:
            self.normal = _compute_normal(self.vertices)

    @property
    def centroid(self) -> Vec3:
        n = len(self.vertices)
        cx = sum(v[0] for v in self.vertices) / n
        cy = sum(v[1] for v in self.vertices) / n
        cz = sum(v[2] for v in self.vertices) / n
        return (cx, cy, cz)


@dataclass
class HollowShellEffect:
    """Compute shaded face colours for a hollow sheet-metal duct.

    Parameters
    ----------
    outer_color:    Base colour for exterior faces (R, G, B).
    inner_color:    Base colour for interior cavity faces (R, G, B).
    ring_color:     Base colour for end-ring (wall cross-section) faces (R, G, B).
    light_dir:      World-space light direction vector (will be normalised).
    ambient:        Global ambient coefficient (0-1).
    """

    outer_color: RGBColor = (195, 200, 205)   # light galvanised grey
    inner_color: RGBColor = (50, 55, 60)      # dark interior shadow
    ring_color: RGBColor = (220, 225, 230)    # bright edge highlight
    light_dir: Vec3 = (1.0, 2.0, 3.0)
    ambient: float = 0.25

    _light_norm: Vec3 = field(init=False)

    def __post_init__(self) -> None:
        self._light_norm = _normalise(self.light_dir)

    # ------------------------------------------------------------------ #
    # Shading                                                             #
    # ------------------------------------------------------------------ #
    def shade(self, face: Face) -> RGBColor:
        """Return the shaded fill colour for *face*.

        Inner faces are rendered much darker than outer faces to give the
        visual impression of looking into a hollow tube.
        End-ring faces receive a bright highlight so the viewer can clearly
        see the sheet-metal wall thickness.
        """
        if face.face_type == FaceType.HIDDEN:
            return (0, 0, 0)   # never actually drawn

        # Lambertian dot product
        n = _normalise(face.normal) if face.normal else (0.0, 0.0, 1.0)
        dot = max(0.0, _dot(n, self._light_norm))

        if face.face_type == FaceType.OUTER_FACE:
            k_amb = self.ambient
            k_diff = 0.75
            base = self.outer_color
        elif face.face_type == FaceType.INNER_FACE:
            # Dark interior – heavily reduced ambient + diffuse
            k_amb = 0.05
            k_diff = 0.20
            base = self.inner_color
        else:  # END_RING
            k_amb = 0.35
            k_diff = 0.55
            base = self.ring_color

        intensity = min(1.0, k_amb + k_diff * dot)
        r = min(255, int(base[0] * intensity))
        g = min(255, int(base[1] * intensity))
        b = min(255, int(base[2] * intensity))
        return (r, g, b)

    def opacity(self, face: Face) -> float:
        """Return the SVG fill opacity for *face*."""
        if face.face_type == FaceType.INNER_FACE:
            return 0.85   # slight transparency lets the outer surface show through
        return 1.0

    def stroke_color(self, face: Face) -> RGBColor:
        """Return the SVG stroke colour for face outlines."""
        if face.face_type == FaceType.INNER_FACE:
            return (30, 30, 30)
        if face.face_type == FaceType.END_RING:
            return (80, 90, 100)
        return (60, 65, 70)

    def stroke_width(self, face: Face) -> float:
        if face.face_type == FaceType.END_RING:
            return 1.5   # emphasise the wall-thickness ring
        return 0.5


# ------------------------------------------------------------------ #
# Linear-algebra helpers                                              #
# ------------------------------------------------------------------ #
def _dot(a: Vec3, b: Vec3) -> float:
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0],
    )


def _normalise(v: Vec3) -> Vec3:
    mag = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if mag < 1e-12:
        return (0.0, 0.0, 1.0)
    return (v[0]/mag, v[1]/mag, v[2]/mag)


def _compute_normal(vertices: List[Vec3]) -> Vec3:
    """Compute polygon face normal using Newell's method."""
    n = len(vertices)
    nx = ny = nz = 0.0
    for i in range(n):
        cur = vertices[i]
        nxt = vertices[(i + 1) % n]
        nx += (cur[1] - nxt[1]) * (cur[2] + nxt[2])
        ny += (cur[2] - nxt[2]) * (cur[0] + nxt[0])
        nz += (cur[0] - nxt[0]) * (cur[1] + nxt[1])
    return _normalise((nx, ny, nz))
