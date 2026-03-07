"""
Transition (reducer / expander) fitting elements (SMACNA).

Covers:

* :class:`RectangularTransition`
    Symmetric rectangular (or square) concentric transition.  Loss
    coefficients follow SMACNA Figure 5-18 (contracting) and Figure 5-19
    (expanding) methodology.

* :class:`RoundTransition`
    Concentric conical transition for round ducts.  Loss coefficient from
    Idelchik Diagram 5-23 (contracting) / Diagram 5-24 (expanding).

* :class:`RectangularToRoundTransition`
    Rectangular-to-round (or reverse) transformation section.
"""

from __future__ import annotations

import math

from ..core.dimensions import Dimensions
from .base import (
    FittingElement,
    FittingType,
    _validate_positive,
    _clamp_angle,
)
from .elbows import _interpolate


class RectangularTransition(FittingElement):
    """
    Symmetric concentric rectangular transition.

    Parameters
    ----------
    inlet:
        Inlet cross-section (``width`` and ``height`` required).
    outlet:
        Outlet cross-section (``width`` and ``height`` required).
    length:
        Axial length of the transition in the same unit as *inlet*.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        inlet: Dimensions,
        outlet: Dimensions,
        length: float,
        tag: str = "",
    ) -> None:
        super().__init__(inlet, FittingType.TRANSITION, tag)
        if inlet.width is None or inlet.height is None:
            raise ValueError(
                "RectangularTransition: inlet requires 'width' and 'height'."
            )
        if outlet.width is None or outlet.height is None:
            raise ValueError(
                "RectangularTransition: outlet requires 'width' and 'height'."
            )
        _validate_positive("length", length)
        self._outlet = outlet
        self._length_m = inlet._to_m(length)  # type: ignore[arg-type]

    @property
    def outlet(self) -> Dimensions:
        """Outlet cross-section dimensions."""
        return self._outlet

    @property
    def length_m(self) -> float:
        """Axial length in metres."""
        return self._length_m

    def _half_angle_deg(self) -> float:
        """Half-angle of the taper (degrees)."""
        inlet_w = self._inlet.width_m  # type: ignore[assignment]
        outlet_w = self._outlet.width_m  # type: ignore[assignment]
        delta = abs(inlet_w - outlet_w) / 2.0  # type: ignore[operator]
        return math.degrees(math.atan2(delta, self._length_m))

    def surface_area(self) -> float:
        """
        Approximate lateral surface area by treating each face as a trapezoid.
        """
        w1, h1 = self._inlet.width_m, self._inlet.height_m  # type: ignore[assignment]
        w2, h2 = self._outlet.width_m, self._outlet.height_m  # type: ignore[assignment]
        slant_w = math.hypot((w2 - w1) / 2, self._length_m)  # type: ignore[operator]
        slant_h = math.hypot((h2 - h1) / 2, self._length_m)  # type: ignore[operator]
        area_w_faces = 2 * 0.5 * (w1 + w2) * slant_w  # type: ignore[operator]
        area_h_faces = 2 * 0.5 * (h1 + h2) * slant_h  # type: ignore[operator]
        return area_w_faces + area_h_faces

    def volume(self) -> float:
        """
        Internal volume using the prismatoid formula:

            V = L/6 · (A₁ + 4·A_m + A₂)
        """
        a1 = self._inlet.cross_section_area()
        a2 = self._outlet.cross_section_area()
        mid = Dimensions(
            width=(self._inlet.width + self._outlet.width) / 2,  # type: ignore[operator]
            height=(self._inlet.height + self._outlet.height) / 2,  # type: ignore[operator]
            unit_system=self._inlet.unit_system,
        )
        a_m = mid.cross_section_area()
        return self._length_m / 6 * (a1 + 4 * a_m + a2)

    def loss_coefficient(self) -> float:
        """
        Loss coefficient (SMACNA).

        * **Contraction**: C = 0.5 · (1 - A2/A1)² using Borda–Carnot with a
          contraction factor of 0.5.
        * **Expansion**: C = (1 - A1/A2)² · K_angle, where K_angle accounts
          for the taper angle (Idelchik Diagram 5-24).
        """
        a1 = self._inlet.cross_section_area()
        a2 = self._outlet.cross_section_area()
        if a2 <= a1:
            # Contraction
            return 0.5 * (1.0 - a2 / a1) ** 2
        # Expansion – Borda-Carnot with angle correction
        theta = self._half_angle_deg()
        theta_table = [0, 5, 10, 15, 20, 30, 45, 60, 90]
        k_table = [0.0, 0.17, 0.28, 0.45, 0.60, 0.81, 0.96, 1.00, 1.00]
        k_angle = _interpolate(theta, theta_table, k_table)
        return (1.0 - a1 / a2) ** 2 * k_angle

    def info(self):  # type: ignore[override]
        d = super().info()
        d["outlet_area_m2"] = round(self._outlet.cross_section_area(), 6)
        d["length_m"] = round(self._length_m, 6)
        d["half_angle_deg"] = round(self._half_angle_deg(), 2)
        return d


class RoundTransition(FittingElement):
    """
    Concentric conical transition for round ducts.

    Parameters
    ----------
    inlet:
        Inlet dimensions (``diameter`` required).
    outlet:
        Outlet dimensions (``diameter`` required).
    length:
        Axial length in the same unit as *inlet*.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        inlet: Dimensions,
        outlet: Dimensions,
        length: float,
        tag: str = "",
    ) -> None:
        super().__init__(inlet, FittingType.TRANSITION, tag)
        if inlet.diameter is None:
            raise ValueError("RoundTransition: inlet requires 'diameter'.")
        if outlet.diameter is None:
            raise ValueError("RoundTransition: outlet requires 'diameter'.")
        _validate_positive("length", length)
        self._outlet = outlet
        self._length_m = inlet._to_m(length)  # type: ignore[arg-type]

    @property
    def outlet(self) -> Dimensions:
        return self._outlet

    @property
    def length_m(self) -> float:
        return self._length_m

    def _half_angle_deg(self) -> float:
        delta = abs(self._inlet.diameter_m - self._outlet.diameter_m) / 2  # type: ignore[operator]
        return math.degrees(math.atan2(delta, self._length_m))

    def surface_area(self) -> float:
        """Lateral surface area of the cone frustum (m²)."""
        r1 = self._inlet.diameter_m / 2  # type: ignore[operator]
        r2 = self._outlet.diameter_m / 2  # type: ignore[operator]
        slant = math.hypot(abs(r1 - r2), self._length_m)
        return math.pi * (r1 + r2) * slant

    def volume(self) -> float:
        """Internal volume of the cone frustum (m³)."""
        r1 = self._inlet.diameter_m / 2  # type: ignore[operator]
        r2 = self._outlet.diameter_m / 2  # type: ignore[operator]
        return math.pi * self._length_m / 3 * (r1**2 + r1 * r2 + r2**2)

    def loss_coefficient(self) -> float:
        """Loss coefficient (same methodology as RectangularTransition)."""
        a1 = self._inlet.cross_section_area()
        a2 = self._outlet.cross_section_area()
        if a2 <= a1:
            return 0.5 * (1.0 - a2 / a1) ** 2
        theta = self._half_angle_deg()
        theta_table = [0, 5, 10, 15, 20, 30, 45, 60, 90]
        k_table = [0.0, 0.17, 0.28, 0.45, 0.60, 0.81, 0.96, 1.00, 1.00]
        k_angle = _interpolate(theta, theta_table, k_table)
        return (1.0 - a1 / a2) ** 2 * k_angle

    def info(self):  # type: ignore[override]
        d = super().info()
        d["outlet_area_m2"] = round(self._outlet.cross_section_area(), 6)
        d["length_m"] = round(self._length_m, 6)
        d["half_angle_deg"] = round(self._half_angle_deg(), 2)
        return d


class RectangularToRoundTransition(FittingElement):
    """
    Rectangular-inlet to round-outlet transformation section.

    Parameters
    ----------
    inlet:
        Rectangular inlet (``width`` and ``height`` required).
    outlet:
        Round outlet (``diameter`` required).
    length:
        Axial length in the same unit as *inlet*.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        inlet: Dimensions,
        outlet: Dimensions,
        length: float,
        tag: str = "",
    ) -> None:
        super().__init__(inlet, FittingType.TRANSITION, tag)
        if inlet.width is None or inlet.height is None:
            raise ValueError(
                "RectangularToRoundTransition: inlet requires 'width' and 'height'."
            )
        if outlet.diameter is None:
            raise ValueError(
                "RectangularToRoundTransition: outlet requires 'diameter'."
            )
        _validate_positive("length", length)
        self._outlet = outlet
        self._length_m = inlet._to_m(length)  # type: ignore[arg-type]

    @property
    def outlet(self) -> Dimensions:
        return self._outlet

    @property
    def length_m(self) -> float:
        return self._length_m

    def surface_area(self) -> float:
        """
        Approximate surface area as the average perimeter × length.

        A more precise calculation would require a parametric surface
        representation; this linear interpolation is a standard engineering
        approximation.
        """
        p1 = self._inlet.perimeter()
        p2 = self._outlet.perimeter()
        return (p1 + p2) / 2 * self._length_m

    def volume(self) -> float:
        """
        Internal volume using the prismatoid formula (A_mid = average of
        inlet and outlet areas).
        """
        a1 = self._inlet.cross_section_area()
        a2 = self._outlet.cross_section_area()
        a_m = (a1 + a2) / 2
        return self._length_m / 6 * (a1 + 4 * a_m + a2)

    def loss_coefficient(self) -> float:
        """
        Loss coefficient based on area ratio (same as :class:`RoundTransition`).
        """
        a1 = self._inlet.cross_section_area()
        a2 = self._outlet.cross_section_area()
        if a2 <= a1:
            return 0.5 * (1.0 - a2 / a1) ** 2
        return (1.0 - a1 / a2) ** 2

    def info(self):  # type: ignore[override]
        d = super().info()
        d["outlet_area_m2"] = round(self._outlet.cross_section_area(), 6)
        d["length_m"] = round(self._length_m, 6)
        return d