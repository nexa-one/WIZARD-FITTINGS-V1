"""
cnc_module.models.duct
======================
Duct cross-section geometry following SMACNA dimensional standards.
All linear dimensions are in **millimetres** unless noted otherwise.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Tuple


class DuctShape(Enum):
    """Enumeration of supported duct cross-section shapes."""
    RECTANGULAR = auto()
    ROUND = auto()
    FLAT_OVAL = auto()


@dataclass
class RectangularDuct:
    """Rectangular duct cross-section.

    Parameters
    ----------
    width:     Internal duct width  (mm) – the longer dimension.
    height:    Internal duct height (mm) – the shorter dimension.
    thickness: Sheet-metal wall thickness (mm).  Default = 0.8 mm (20 gauge).
    """

    width: float
    height: float
    thickness: float = 0.8

    shape: DuctShape = field(init=False, default=DuctShape.RECTANGULAR)

    # ------------------------------------------------------------------ #
    # Validation                                                           #
    # ------------------------------------------------------------------ #
    def __post_init__(self) -> None:
        if self.width <= 0:
            raise ValueError(f"width must be positive, got {self.width}")
        if self.height <= 0:
            raise ValueError(f"height must be positive, got {self.height}")
        if self.thickness <= 0:
            raise ValueError(f"thickness must be positive, got {self.thickness}")

    # ------------------------------------------------------------------ #
    # Geometry helpers                                                     #
    # ------------------------------------------------------------------ #
    @property
    def perimeter(self) -> float:
        """Internal perimeter of the cross-section (mm)."""
        return 2.0 * (self.width + self.height)

    @property
    def external_width(self) -> float:
        return self.width + 2.0 * self.thickness

    @property
    def external_height(self) -> float:
        return self.height + 2.0 * self.thickness

    @property
    def area(self) -> float:
        """Internal cross-sectional area (mm²)."""
        return self.width * self.height

    @property
    def hydraulic_diameter(self) -> float:
        """Hydraulic diameter for circular-equivalent calculations (mm)."""
        return (2.0 * self.width * self.height) / (self.width + self.height)

    @property
    def aspect_ratio(self) -> float:
        """Width-to-height aspect ratio (always ≥ 1.0)."""
        return max(self.width, self.height) / min(self.width, self.height)

    # 3-D corner points of the **outer** box at z = 0 (bottom face)
    def outer_corners(self, z: float = 0.0) -> list[Tuple[float, float, float]]:
        """Eight outer corners of the duct cross-section at elevation ``z``."""
        hw = self.external_width / 2.0
        hh = self.external_height / 2.0
        return [
            (-hw, -hh, z), (hw, -hh, z),
            (hw,  hh, z), (-hw,  hh, z),
        ]

    # 3-D corner points of the **inner** box at z = 0 (hollow cavity)
    def inner_corners(self, z: float = 0.0) -> list[Tuple[float, float, float]]:
        hw = self.width / 2.0
        hh = self.height / 2.0
        return [
            (-hw, -hh, z), (hw, -hh, z),
            (hw,  hh, z), (-hw,  hh, z),
        ]

    def __repr__(self) -> str:
        return (
            f"RectangularDuct(width={self.width}, height={self.height}, "
            f"thickness={self.thickness})"
        )


@dataclass
class RoundDuct:
    """Round / circular duct cross-section.

    Parameters
    ----------
    diameter:  Internal diameter (mm).
    thickness: Sheet-metal wall thickness (mm).  Default = 0.8 mm.
    """

    diameter: float
    thickness: float = 0.8

    shape: DuctShape = field(init=False, default=DuctShape.ROUND)

    def __post_init__(self) -> None:
        if self.diameter <= 0:
            raise ValueError(f"diameter must be positive, got {self.diameter}")
        if self.thickness <= 0:
            raise ValueError(f"thickness must be positive, got {self.thickness}")

    @property
    def radius(self) -> float:
        return self.diameter / 2.0

    @property
    def external_diameter(self) -> float:
        return self.diameter + 2.0 * self.thickness

    @property
    def perimeter(self) -> float:
        """Internal circumference (mm)."""
        return math.pi * self.diameter

    @property
    def area(self) -> float:
        """Internal cross-sectional area (mm²)."""
        return math.pi * self.radius ** 2

    @property
    def hydraulic_diameter(self) -> float:
        return self.diameter

    def circle_points(
        self, segments: int = 36, z: float = 0.0, use_external: bool = False
    ) -> list[Tuple[float, float, float]]:
        """Return evenly-spaced points on the inner (or outer) circle."""
        r = (self.external_diameter if use_external else self.diameter) / 2.0
        pts = []
        for i in range(segments):
            angle = 2.0 * math.pi * i / segments
            pts.append((r * math.cos(angle), r * math.sin(angle), z))
        return pts

    def __repr__(self) -> str:
        return f"RoundDuct(diameter={self.diameter}, thickness={self.thickness})"


@dataclass
class FlatOvalDuct:
    """Flat-oval duct cross-section (semi-circular ends + flat sides).

    Parameters
    ----------
    major:     Total major dimension (mm) – the long axis.
    minor:     Total minor dimension (mm) – the short axis.
    thickness: Sheet-metal wall thickness (mm).  Default = 0.8 mm.

    Geometry
    --------
    The shape is formed by two semi-circles of radius = minor/2 joined
    by two straight sections of length = (major - minor).
    """

    major: float
    minor: float
    thickness: float = 0.8

    shape: DuctShape = field(init=False, default=DuctShape.FLAT_OVAL)

    def __post_init__(self) -> None:
        if self.major <= 0:
            raise ValueError(f"major must be positive, got {self.major}")
        if self.minor <= 0:
            raise ValueError(f"minor must be positive, got {self.minor}")
        if self.major < self.minor:
            raise ValueError(
                f"major ({self.major}) must be >= minor ({self.minor})"
            )
        if self.thickness <= 0:
            raise ValueError(f"thickness must be positive, got {self.thickness}")

    @property
    def radius(self) -> float:
        """Radius of the semi-circular ends (mm)."""
        return self.minor / 2.0

    @property
    def straight_length(self) -> float:
        """Length of the flat sides (mm)."""
        return self.major - self.minor

    @property
    def perimeter(self) -> float:
        """Internal perimeter: full circle + 2× straight sections."""
        return math.pi * self.minor + 2.0 * self.straight_length

    @property
    def area(self) -> float:
        """Internal cross-sectional area (mm²)."""
        return math.pi * self.radius ** 2 + self.minor * self.straight_length

    @property
    def hydraulic_diameter(self) -> float:
        return (4.0 * self.area) / self.perimeter

    def __repr__(self) -> str:
        return (
            f"FlatOvalDuct(major={self.major}, minor={self.minor}, "
            f"thickness={self.thickness})"
        )
