"""
Dimension and unit-system helpers for the WIZARD-FITTINGS geometric engine.

All fitting elements operate internally in SI units (metres, m², m³).
When a ``UnitSystem.IMPERIAL`` context is used the ``Dimensions`` dataclass
transparently converts inch/feet inputs to metres so the rest of the engine
is always unit-consistent.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class UnitSystem(Enum):
    """Supported unit systems."""

    METRIC = "metric"
    IMPERIAL = "imperial"


# Conversion constants
_IN_TO_M = 0.0254          # 1 inch → metres
_FT_TO_M = 0.3048          # 1 foot → metres
_M_TO_IN = 1 / _IN_TO_M
_M_TO_FT = 1 / _FT_TO_M


def inches_to_metres(value: float) -> float:
    """Convert inches to metres."""
    return value * _IN_TO_M


def metres_to_inches(value: float) -> float:
    """Convert metres to inches."""
    return value * _M_TO_IN


def feet_to_metres(value: float) -> float:
    """Convert feet to metres."""
    return value * _FT_TO_M


def metres_to_feet(value: float) -> float:
    """Convert metres to feet."""
    return value * _M_TO_FT


@dataclass
class Dimensions:
    """
    Cross-sectional dimensions for a duct fitting.

    All public attributes are stored in the *native* unit provided by the
    caller (metres for METRIC, inches for IMPERIAL) so that numeric values
    remain legible.  Internal calculations always work in metres via the
    ``*_m`` properties.

    Parameters
    ----------
    width:
        Cross-sectional width (m for METRIC, in for IMPERIAL).  For round
        sections this is the diameter.
    height:
        Cross-sectional height (m for METRIC, in for IMPERIAL).  Should be
        ``None`` for round and oval sections when ``diameter`` is supplied.
    diameter:
        Diameter for round sections (m for METRIC, in for IMPERIAL).
    major_axis:
        Major axis of an oval section (m / in).
    minor_axis:
        Minor axis of an oval section (m / in).
    unit_system:
        Whether *width*, *height* etc. are supplied in metric or imperial
        units.  Defaults to :attr:`UnitSystem.METRIC`.
    """

    width: Optional[float] = None
    height: Optional[float] = None
    diameter: Optional[float] = None
    major_axis: Optional[float] = None
    minor_axis: Optional[float] = None
    unit_system: UnitSystem = field(default=UnitSystem.METRIC)

    # ------------------------------------------------------------------
    # Internal helpers – always return SI (metres)
    # ------------------------------------------------------------------

    def _to_m(self, value: Optional[float]) -> Optional[float]:
        """Convert a native-unit value to metres."""
        if value is None:
            return None
        if self.unit_system == UnitSystem.IMPERIAL:
            return inches_to_metres(value)
        return value

    @property
    def width_m(self) -> Optional[float]:
        """Width in metres."""
        return self._to_m(self.width)

    @property
    def height_m(self) -> Optional[float]:
        """Height in metres."""
        return self._to_m(self.height)

    @property
    def diameter_m(self) -> Optional[float]:
        """Diameter in metres."""
        return self._to_m(self.diameter)

    @property
    def major_axis_m(self) -> Optional[float]:
        """Major axis in metres (oval sections)."""
        return self._to_m(self.major_axis)

    @property
    def minor_axis_m(self) -> Optional[float]:
        """Minor axis in metres (oval sections)."""
        return self._to_m(self.minor_axis)

    # ------------------------------------------------------------------
    # Derived geometric quantities
    # ------------------------------------------------------------------

    def cross_section_area(self) -> float:
        """
        Return the cross-sectional area in m².

        Supports rectangular, round, and oval sections.
        """
        if self.diameter_m is not None:
            return math.pi * (self.diameter_m / 2) ** 2

        if self.major_axis_m is not None and self.minor_axis_m is not None:
            return math.pi * (self.major_axis_m / 2) * (self.minor_axis_m / 2)

        if self.width_m is not None and self.height_m is not None:
            return self.width_m * self.height_m

        raise ValueError(
            "Insufficient dimensions to compute cross-sectional area.  "
            "Provide (width, height), diameter, or (major_axis, minor_axis)."
        )

    def perimeter(self) -> float:
        """
        Return the cross-sectional perimeter in metres.

        For oval sections the Ramanujan approximation is used.
        """
        if self.diameter_m is not None:
            return math.pi * self.diameter_m

        if self.major_axis_m is not None and self.minor_axis_m is not None:
            a, b = self.major_axis_m / 2, self.minor_axis_m / 2
            h = ((a - b) / (a + b)) ** 2
            return math.pi * (a + b) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))

        if self.width_m is not None and self.height_m is not None:
            return 2 * (self.width_m + self.height_m)

        raise ValueError(
            "Insufficient dimensions to compute perimeter.  "
            "Provide (width, height), diameter, or (major_axis, minor_axis)."
        )

    def hydraulic_diameter(self) -> float:
        """
        Return the hydraulic (equivalent) diameter D_h = 4A / P in metres.

        For circular sections this equals the actual diameter.
        """
        return 4 * self.cross_section_area() / self.perimeter()

    def aspect_ratio(self) -> float:
        """
        Return the aspect ratio (width / height) for rectangular sections.

        Raises ``ValueError`` for non-rectangular sections.
        """
        if self.width_m is None or self.height_m is None:
            raise ValueError("Aspect ratio is only defined for rectangular sections.")
        return self.width_m / self.height_m

    def __repr__(self) -> str:
        parts = []
        if self.diameter is not None:
            parts.append(f"diameter={self.diameter}")
        if self.width is not None:
            parts.append(f"width={self.width}")
        if self.height is not None:
            parts.append(f"height={self.height}")
        if self.major_axis is not None:
            parts.append(f"major_axis={self.major_axis}")
        if self.minor_axis is not None:
            parts.append(f"minor_axis={self.minor_axis}")
        parts.append(f"unit_system={self.unit_system.value}")
        return f"Dimensions({', '.join(parts)})"