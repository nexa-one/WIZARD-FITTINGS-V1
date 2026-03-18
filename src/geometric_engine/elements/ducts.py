"""
Straight duct section elements.

Covers three cross-section shapes commonly encountered in SMACNA ductwork:

* :class:`RectangularDuct`  – four-sided rectangular cross-section.
* :class:`RoundDuct`        – circular cross-section.
* :class:`OvalDuct`         – flat-oval (racetrack) cross-section.

All lengths are stored and returned in metres (m).
Surface areas are in m², volumes in m³.
"""

from __future__ import annotations

import math

from ..core.dimensions import Dimensions
from .base import FittingElement, FittingType, _validate_positive


class RectangularDuct(FittingElement):
    """
    A straight rectangular duct section.

    Parameters
    ----------
    dimensions:
        Cross-sectional dimensions (``width`` and ``height`` required).
    length:
        Duct length in the same unit system as *dimensions*.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        length: float,
        tag: str = "",
    ) -> None:
        super().__init__(dimensions, FittingType.DUCT_STRAIGHT, tag)
        _validate_positive("length", length)
        if dimensions.width is None or dimensions.height is None:
            raise ValueError(
                "RectangularDuct requires both 'width' and 'height' in dimensions."
            )
        self._length_m = dimensions._to_m(length)  # type: ignore[arg-type]

    @property
    def length_m(self) -> float:
        """Duct length in metres."""
        return self._length_m

    def surface_area(self) -> float:
        """Total external surface area (4 walls) in m²."""
        return self._inlet.perimeter() * self._length_m

    def volume(self) -> float:
        """Internal air-side volume in m³."""
        return self._inlet.cross_section_area() * self._length_m

    def loss_coefficient(self) -> float:
        """
        Loss coefficient for a straight duct section.

        For a straight run without fittings the dynamic pressure loss is
        captured separately by the friction factor; the *fitting* loss
        coefficient is effectively **0**.
        """
        return 0.0

    def info(self):  # type: ignore[override]
        d = super().info()
        d["length_m"] = round(self._length_m, 6)
        return d


class RoundDuct(FittingElement):
    """
    A straight round (circular) duct section.

    Parameters
    ----------
    dimensions:
        Cross-sectional dimensions (``diameter`` required).
    length:
        Duct length in the same unit system as *dimensions*.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        length: float,
        tag: str = "",
    ) -> None:
        super().__init__(dimensions, FittingType.DUCT_STRAIGHT, tag)
        _validate_positive("length", length)
        if dimensions.diameter is None:
            raise ValueError("RoundDuct requires 'diameter' in dimensions.")
        self._length_m = dimensions._to_m(length)  # type: ignore[arg-type]

    @property
    def length_m(self) -> float:
        """Duct length in metres."""
        return self._length_m

    def surface_area(self) -> float:
        """Lateral surface area (cylindrical wall) in m²."""
        return math.pi * self._inlet.diameter_m * self._length_m  # type: ignore[operator]

    def volume(self) -> float:
        """Internal air-side volume in m³."""
        return self._inlet.cross_section_area() * self._length_m

    def loss_coefficient(self) -> float:
        """Fitting loss coefficient for a straight run (0.0)."""
        return 0.0

    def info(self):  # type: ignore[override]
        d = super().info()
        d["length_m"] = round(self._length_m, 6)
        return d


class OvalDuct(FittingElement):
    """
    A straight flat-oval duct section.

    Parameters
    ----------
    dimensions:
        Cross-sectional dimensions (``major_axis`` and ``minor_axis``
        required).
    length:
        Duct length in the same unit system as *dimensions*.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        length: float,
        tag: str = "",
    ) -> None:
        super().__init__(dimensions, FittingType.DUCT_STRAIGHT, tag)
        _validate_positive("length", length)
        if dimensions.major_axis is None or dimensions.minor_axis is None:
            raise ValueError(
                "OvalDuct requires both 'major_axis' and 'minor_axis' in dimensions."
            )
        if dimensions.major_axis_m < dimensions.minor_axis_m:  # type: ignore[operator]
            raise ValueError("major_axis must be ≥ minor_axis.")
        self._length_m = dimensions._to_m(length)  # type: ignore[arg-type]

    @property
    def length_m(self) -> float:
        """Duct length in metres."""
        return self._length_m

    def surface_area(self) -> float:
        """Lateral surface area in m²."""
        return self._inlet.perimeter() * self._length_m

    def volume(self) -> float:
        """Internal air-side volume in m³."""
        return self._inlet.cross_section_area() * self._length_m

    def loss_coefficient(self) -> float:
        """Fitting loss coefficient for a straight run (0.0)."""
        return 0.0

    def info(self):  # type: ignore[override]
        d = super().info()
        d["length_m"] = round(self._length_m, 6)
        return d
