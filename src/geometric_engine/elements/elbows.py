"""
Elbow fitting elements (SMACNA).

Three types are provided:

* :class:`RectangularElbow`
    Smooth-radius rectangular elbow.  Loss coefficients follow SMACNA
    Figure 5-4 / Table 5-4 methodology (based on aspect ratio and radius
    ratio R/W).

* :class:`RoundElbow`
    Smooth-radius round elbow.  Loss coefficient from SMACNA Figure 5-1
    family (Idelchik, Diagram 6-1).

* :class:`MiteredElbow`
    Single-mitered (no turning vanes) elbow for both rectangular and round
    sections.  Loss coefficient from SMACNA Table 5-5.
"""

from __future__ import annotations

import math
from typing import Optional

from ..core.dimensions import Dimensions
from .base import (
    FittingElement,
    FittingType,
    _validate_positive,
    _clamp_angle,
)


# ---------------------------------------------------------------------------
# Smooth rectangular elbow
# ---------------------------------------------------------------------------

class RectangularElbow(FittingElement):
    """
    Smooth-radius rectangular elbow.

    Parameters
    ----------
    dimensions:
        Cross-sectional dimensions (``width`` and ``height`` required).
        *Width* is the dimension in the plane of the bend.
    angle:
        Deflection angle in degrees (0 < angle ≤ 180).  Defaults to 90°.
    radius_ratio:
        Centreline radius / width  (R/W).  SMACNA recommends R/W ≥ 1.5.
        Defaults to 1.5.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        angle: float = 90.0,
        radius_ratio: float = 1.5,
        tag: str = "",
    ) -> None:
        super().__init__(dimensions, FittingType.ELBOW, tag)
        if dimensions.width is None or dimensions.height is None:
            raise ValueError(
                "RectangularElbow requires 'width' and 'height' in dimensions."
            )
        self._angle_deg = _clamp_angle(angle, lo=1.0, hi=180.0)
        _validate_positive("radius_ratio", radius_ratio)
        self._radius_ratio = radius_ratio

    @property
    def angle_deg(self) -> float:
        """Deflection angle (degrees)."""
        return self._angle_deg

    @property
    def radius_ratio(self) -> float:
        """Centreline radius-to-width ratio (R/W)."""
        return self._radius_ratio

    # Centreline radius
    @property
    def _radius_m(self) -> float:
        return self._radius_ratio * self._inlet.width_m  # type: ignore[return-value]

    def surface_area(self) -> float:
        """
        Approximate lateral surface area of the elbow body (m²).

        Computed as the perimeter of the cross-section multiplied by the arc
        length along the centreline.
        """
        arc_length = self._radius_m * math.radians(self._angle_deg)
        return self._inlet.perimeter() * arc_length

    def volume(self) -> float:
        """Internal air-side volume (m³)."""
        arc_length = self._radius_m * math.radians(self._angle_deg)
        return self._inlet.cross_section_area() * arc_length

    def loss_coefficient(self) -> float:
        """
        Dimensionless loss coefficient *C* (SMACNA methodology).

        The base 90° coefficient is interpolated from the empirical table
        below (Idelchik, Handbook of Hydraulic Resistance, Table 6-5):

            R/W   :  0.5   0.75  1.0   1.5   2.0   3.0
            C_90  :  1.50  0.57  0.27  0.22  0.20  0.18

        For angles other than 90° a factor k(θ) = 0.031·θ + 0.57 (linearised
        fit for 30° ≤ θ ≤ 120°) is applied following SMACNA Figure 5-4.
        """
        rw_table = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
        c90_table = [1.50, 0.57, 0.27, 0.22, 0.20, 0.18]
        c90 = _interpolate(self._radius_ratio, rw_table, c90_table)
        theta = self._angle_deg
        if theta <= 90.0:
            k_theta = theta / 90.0 * 0.85 + 0.15
        else:
            k_theta = 1.0 + (theta - 90.0) / 90.0 * 0.4
        return c90 * k_theta

    def info(self):  # type: ignore[override]
        d = super().info()
        d["angle_deg"] = self._angle_deg
        d["radius_ratio"] = self._radius_ratio
        return d


# ---------------------------------------------------------------------------
# Smooth round elbow
# ---------------------------------------------------------------------------

class RoundElbow(FittingElement):
    """
    Smooth-radius round elbow.

    Parameters
    ----------
    dimensions:
        Cross-sectional dimensions (``diameter`` required).
    angle:
        Deflection angle in degrees (0 < angle ≤ 180).  Defaults to 90°.
    radius_ratio:
        Centreline radius / diameter  (R/D).  SMACNA recommends R/D ≥ 1.5.
        Defaults to 1.5.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        angle: float = 90.0,
        radius_ratio: float = 1.5,
        tag: str = "",
    ) -> None:
        super().__init__(dimensions, FittingType.ELBOW, tag)
        if dimensions.diameter is None:
            raise ValueError("RoundElbow requires 'diameter' in dimensions.")
        self._angle_deg = _clamp_angle(angle, lo=1.0, hi=180.0)
        _validate_positive("radius_ratio", radius_ratio)
        self._radius_ratio = radius_ratio

    @property
    def angle_deg(self) -> float:
        return self._angle_deg

    @property
    def radius_ratio(self) -> float:
        return self._radius_ratio

    @property
    def _radius_m(self) -> float:
        return self._radius_ratio * self._inlet.diameter_m  # type: ignore[return-value]

    def surface_area(self) -> float:
        """Lateral surface area of the elbow (m²)."""
        arc_length = self._radius_m * math.radians(self._angle_deg)
        return math.pi * self._inlet.diameter_m * arc_length  # type: ignore[operator]

    def volume(self) -> float:
        """Internal air-side volume (m³)."""
        arc_length = self._radius_m * math.radians(self._angle_deg)
        return self._inlet.cross_section_area() * arc_length

    def loss_coefficient(self) -> float:
        """
        Dimensionless loss coefficient *C* (SMACNA / Idelchik, Diagram 6-1).

        Base 90° values:

            R/D  :  0.5   0.75  1.0   1.5   2.0   3.0
            C_90 :  0.90  0.45  0.33  0.24  0.19  0.16

        Angle correction identical to :class:`RectangularElbow`.
        """
        rd_table = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
        c90_table = [0.90, 0.45, 0.33, 0.24, 0.19, 0.16]
        c90 = _interpolate(self._radius_ratio, rd_table, c90_table)
        theta = self._angle_deg
        if theta <= 90.0:
            k_theta = theta / 90.0 * 0.85 + 0.15
        else:
            k_theta = 1.0 + (theta - 90.0) / 90.0 * 0.4
        return c90 * k_theta

    def info(self):  # type: ignore[override]
        d = super().info()
        d["angle_deg"] = self._angle_deg
        d["radius_ratio"] = self._radius_ratio
        return d


# ---------------------------------------------------------------------------
# Mitered elbow (no turning vanes)
# ---------------------------------------------------------------------------

class MiteredElbow(FittingElement):
    """
    Single-mitered elbow (no turning vanes) for rectangular or round ducts.

    Parameters
    ----------
    dimensions:
        Cross-sectional dimensions.  Rectangular or round sections are
        both accepted.
    angle:
        Deflection angle in degrees (0 < angle ≤ 90).  Defaults to 90°.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        angle: float = 90.0,
        tag: str = "",
    ) -> None:
        super().__init__(dimensions, FittingType.ELBOW, tag)
        self._angle_deg = _clamp_angle(angle, lo=1.0, hi=90.0)

    @property
    def angle_deg(self) -> float:
        return self._angle_deg

    def surface_area(self) -> float:
        """
        Approximate lateral surface area.

        For a mitered elbow the fitting depth is proportional to the
        hydraulic diameter and the tangent of half the deflection angle.
        """
        d_h = self._inlet.hydraulic_diameter()
        depth = d_h * math.tan(math.radians(self._angle_deg / 2))
        return self._inlet.perimeter() * depth

    def volume(self) -> float:
        """Internal air-side volume (m³)."""
        d_h = self._inlet.hydraulic_diameter()
        depth = d_h * math.tan(math.radians(self._angle_deg / 2))
        return self._inlet.cross_section_area() * depth

    def loss_coefficient(self) -> float:
        """
        Dimensionless loss coefficient (SMACNA Table 5-5).

        For a sharp mitered bend (no turning vanes):

            θ (°)  :  15    30    45    60    75    90
            C      :  0.05  0.11  0.26  0.47  0.72  1.20
        """
        theta_table = [15.0, 30.0, 45.0, 60.0, 75.0, 90.0]
        c_table = [0.05, 0.11, 0.26, 0.47, 0.72, 1.20]
        return _interpolate(self._angle_deg, theta_table, c_table)

    def info(self):  # type: ignore[override]
        d = super().info()
        d["angle_deg"] = self._angle_deg
        return d


# ---------------------------------------------------------------------------
# Interpolation helper
# ---------------------------------------------------------------------------

def _interpolate(x: float, xs: list, ys: list) -> float:
    """
    Linear interpolation / extrapolation over a sorted (xs, ys) table.

    Values outside the range are clamped to the boundary value.
    """
    if x <= xs[0]:
        return ys[0]
    if x >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            t = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + t * (ys[i + 1] - ys[i])
    return ys[-1]  # unreachable but satisfies type checker
