"""
Special and accessory fitting elements (SMACNA – category SP).

Covers volume-control dampers, fire/smoke dampers, access doors, flex
connectors, plenums, and similar accessories attached to ductwork.

* SP-1  :class:`VolumeControlDamper`   – Rect VCD.
* SP-2  :class:`FireDamper`            – Rect fire damper frame.
* SP-3  :class:`FireSmokeDamper`       – Rect fire–smoke damper (FSD).
* SP-4  :class:`AccessDoor`            – Rect access door panel.
* SP-5  :class:`FlexConnector`         – Rect flexible connector.
* SP-6  :class:`LinerThroat`           – Rect duct liner throat.
* SP-7  :class:`CircularBellMouth`     – Circular bell-mouth inlet.
* SP-8  :class:`PlenumTakeoff`         – Rect plenum with offset takeoff.
* SP-9  :class:`RegisterBoot`          – Rect register boot (floor/ceiling).
* SP-10 :class:`DoubleWallSection`     – Rect double-wall duct section.
"""

from __future__ import annotations

import math

from ..core.dimensions import Dimensions
from .base import FittingElement, FittingType, _validate_positive


class VolumeControlDamper(FittingElement):
    """
    Rectangular volume-control damper (SMACNA SP-1).

    Parameters
    ----------
    dimensions:
        Frame cross-section (``width`` and ``height`` required).
    length:
        Damper body depth (blade-to-blade, in duct axis direction).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        length: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError("VolumeControlDamper requires 'width' and 'height' in dimensions.")
        _validate_positive("length", length)
        super().__init__(dimensions, FittingType.SPECIAL, tag)
        self._length_m = dimensions._to_m(length)  # type: ignore[arg-type]

    def surface_area(self) -> float:
        """Frame outer surface area (4 sides)."""
        return self._inlet.perimeter() * self._length_m

    def volume(self) -> float:
        """Internal volume through the damper."""
        return self._inlet.cross_section_area() * self._length_m

    def loss_coefficient(self) -> float:
        """
        Fully-open VCD loss coefficient per SMACNA Table 5-1.

        For a multi-blade parallel damper fully open, C ≈ 0.52.
        """
        return 0.52


class FireDamper(FittingElement):
    """
    Rectangular fire damper frame (SMACNA SP-2).

    Parameters
    ----------
    dimensions:
        Frame cross-section (``width`` and ``height`` required).
    length:
        Frame depth in duct axis direction.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        length: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError("FireDamper requires 'width' and 'height' in dimensions.")
        _validate_positive("length", length)
        super().__init__(dimensions, FittingType.SPECIAL, tag)
        self._length_m = dimensions._to_m(length)  # type: ignore[arg-type]

    def surface_area(self) -> float:
        return self._inlet.perimeter() * self._length_m

    def volume(self) -> float:
        return self._inlet.cross_section_area() * self._length_m

    def loss_coefficient(self) -> float:
        """Fire damper fully open: C ≈ 1.0 (curtain-type) per SMACNA."""
        return 1.0


class FireSmokeDamper(FittingElement):
    """
    Rectangular fire–smoke damper (SMACNA SP-3).

    Parameters
    ----------
    dimensions:
        Frame cross-section (``width`` and ``height`` required).
    tag:
        Optional user-defined identifier.
    """

    def __init__(self, dimensions: Dimensions, tag: str = "") -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError("FireSmokeDamper requires 'width' and 'height' in dimensions.")
        super().__init__(dimensions, FittingType.SPECIAL, tag)

    def surface_area(self) -> float:
        return self._inlet.cross_section_area() * 2  # front + back face

    def volume(self) -> float:
        return 0.0  # negligible depth

    def loss_coefficient(self) -> float:
        """FSD fully open: C ≈ 1.5 (multi-blade + actuator)."""
        return 1.5


class AccessDoor(FittingElement):
    """
    Rectangular access door panel (SMACNA SP-4).

    Parameters
    ----------
    dimensions:
        Duct cross-section at the door location (``width`` and ``height``
        required).  The door panel itself is sized separately by
        *panel_width* and *panel_height*.
    panel_width:
        Door panel width (same unit as *dimensions*).
    panel_height:
        Door panel height (same unit as *dimensions*).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        panel_width: float,
        panel_height: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError("AccessDoor requires 'width' and 'height' in dimensions.")
        _validate_positive("panel_width", panel_width)
        _validate_positive("panel_height", panel_height)
        super().__init__(dimensions, FittingType.SPECIAL, tag)
        self._pw_m = dimensions._to_m(panel_width)  # type: ignore[arg-type]
        self._ph_m = dimensions._to_m(panel_height)  # type: ignore[arg-type]

    @property
    def panel_area_m2(self) -> float:
        """Area of the access panel (m²)."""
        return self._pw_m * self._ph_m

    def surface_area(self) -> float:
        return self.panel_area_m2

    def volume(self) -> float:
        return 0.0

    def loss_coefficient(self) -> float:
        """Access doors do not contribute an aerodynamic loss coefficient (0.0)."""
        return 0.0


class FlexConnector(FittingElement):
    """
    Rectangular flexible connector (SMACNA SP-5).

    Parameters
    ----------
    dimensions:
        Cross-section (``width`` and ``height`` required).
    length:
        Connector length (typically 100–300 mm).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        length: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError("FlexConnector requires 'width' and 'height' in dimensions.")
        _validate_positive("length", length)
        super().__init__(dimensions, FittingType.SPECIAL, tag)
        self._length_m = dimensions._to_m(length)  # type: ignore[arg-type]

    def surface_area(self) -> float:
        return self._inlet.perimeter() * self._length_m

    def volume(self) -> float:
        return self._inlet.cross_section_area() * self._length_m

    def loss_coefficient(self) -> float:
        """Flex connector: C ≈ 0.05 (negligible when straight)."""
        return 0.05


class LinerThroat(FittingElement):
    """
    Rectangular duct liner throat section (SMACNA SP-6).

    Parameters
    ----------
    dimensions:
        External cross-section (``width`` and ``height`` required).
    liner_thickness:
        Acoustic liner thickness (same unit as *dimensions*).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        liner_thickness: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError("LinerThroat requires 'width' and 'height' in dimensions.")
        _validate_positive("liner_thickness", liner_thickness)
        super().__init__(dimensions, FittingType.SPECIAL, tag)
        self._liner_m = dimensions._to_m(liner_thickness)  # type: ignore[arg-type]

    @property
    def net_width_m(self) -> float:
        """Internal clear width after liner (m)."""
        return self._inlet.width_m - 2 * self._liner_m  # type: ignore[operator]

    @property
    def net_height_m(self) -> float:
        """Internal clear height after liner (m)."""
        return self._inlet.height_m - 2 * self._liner_m  # type: ignore[operator]

    @property
    def net_area_m2(self) -> float:
        """Net internal cross-section area (m²)."""
        return max(0.0, self.net_width_m * self.net_height_m)

    def surface_area(self) -> float:
        return self._inlet.cross_section_area()

    def volume(self) -> float:
        return 0.0

    def loss_coefficient(self) -> float:
        """
        Additional loss due to liner reducing free area.

        C = (A_gross/A_net - 1)²
        """
        a_g = self._inlet.cross_section_area()
        a_n = self.net_area_m2
        if a_n <= 0:
            return float("inf")
        return (a_g / a_n - 1.0) ** 2


class CircularBellMouth(FittingElement):
    """
    Circular bell-mouth inlet fitting (SMACNA SP-7).

    Parameters
    ----------
    dimensions:
        Round outlet cross-section (``diameter`` required).
    bell_radius:
        Radius of the bell-mouth curve (same unit as *dimensions*).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        bell_radius: float,
        tag: str = "",
    ) -> None:
        if dimensions.diameter is None:
            raise ValueError("CircularBellMouth requires 'diameter' in dimensions.")
        _validate_positive("bell_radius", bell_radius)
        super().__init__(dimensions, FittingType.SPECIAL, tag)
        self._bell_radius_m = dimensions._to_m(bell_radius)  # type: ignore[arg-type]

    def surface_area(self) -> float:
        """Lateral surface area of the bell-mouth flare (quarter-circle profile of revolution)."""
        d = self._inlet.diameter_m  # type: ignore[assignment]
        r = self._bell_radius_m
        return 2 * math.pi * r * (math.pi * d / 4 + r)  # type: ignore[operator]

    def volume(self) -> float:
        """Volume swept by the bell-mouth profile (torus quadrant approximation)."""
        d = self._inlet.diameter_m  # type: ignore[assignment]
        r = self._bell_radius_m
        return math.pi**2 * r**2 * (d / 2 + r / 3) / 2  # type: ignore[operator]

    def loss_coefficient(self) -> float:
        """
        Bell-mouth inlet loss coefficient.

        Per Idelchik Diagram 5-22: C ≈ 0.04 for r/D > 0.2.
        """
        r_over_d = self._bell_radius_m / self._inlet.diameter_m  # type: ignore[operator]
        if r_over_d >= 0.2:
            return 0.04
        return 0.5 - 2.0 * r_over_d


class PlenumTakeoff(FittingElement):
    """
    Rectangular plenum with offset takeoff (SMACNA SP-8).

    Parameters
    ----------
    dimensions:
        Plenum cross-section (``width`` and ``height`` required).
    outlet_width:
        Takeoff outlet width.
    outlet_height:
        Takeoff outlet height.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        outlet_width: float,
        outlet_height: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError("PlenumTakeoff requires 'width' and 'height' in dimensions.")
        _validate_positive("outlet_width", outlet_width)
        _validate_positive("outlet_height", outlet_height)
        super().__init__(dimensions, FittingType.SPECIAL, tag)
        self._ow_m = dimensions._to_m(outlet_width)  # type: ignore[arg-type]
        self._oh_m = dimensions._to_m(outlet_height)  # type: ignore[arg-type]

    @property
    def outlet_area_m2(self) -> float:
        return self._ow_m * self._oh_m

    def surface_area(self) -> float:
        return self._inlet.cross_section_area() + self.outlet_area_m2

    def volume(self) -> float:
        dh = self._inlet.hydraulic_diameter()
        return self._inlet.cross_section_area() * dh

    def loss_coefficient(self) -> float:
        """
        Plenum takeoff – C based on area ratio (SMACNA SP-8).

            C = 1.0 · (A_plenum/A_outlet - 1)  (min 0.5)
        """
        return max(self._inlet.cross_section_area() / self.outlet_area_m2 - 1.0, 0.5)


class RegisterBoot(FittingElement):
    """
    Rectangular register boot fitting (floor/ceiling outlet – SMACNA SP-9).

    Parameters
    ----------
    dimensions:
        Duct inlet cross-section (``width`` and ``height`` required).
    neck_diameter:
        Neck (round outlet) diameter (same unit as *dimensions*).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        neck_diameter: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError("RegisterBoot requires 'width' and 'height' in dimensions.")
        _validate_positive("neck_diameter", neck_diameter)
        super().__init__(dimensions, FittingType.SPECIAL, tag)
        self._neck_m = dimensions._to_m(neck_diameter)  # type: ignore[arg-type]

    @property
    def neck_area_m2(self) -> float:
        return math.pi * (self._neck_m / 2) ** 2

    def surface_area(self) -> float:
        return self._inlet.cross_section_area() + self.neck_area_m2

    def volume(self) -> float:
        dh = self._inlet.hydraulic_diameter()
        return self._inlet.cross_section_area() * dh * 0.75

    def loss_coefficient(self) -> float:
        """Boot fitting: C ≈ 1.0 (90° turn + area change)."""
        return 1.0


class DoubleWallSection(FittingElement):
    """
    Rectangular double-wall duct section (SMACNA SP-10).

    Parameters
    ----------
    dimensions:
        External cross-section (``width`` and ``height`` required).
    liner_thickness:
        Insulation / liner thickness on each side.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        liner_thickness: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError("DoubleWallSection requires 'width' and 'height' in dimensions.")
        _validate_positive("liner_thickness", liner_thickness)
        super().__init__(dimensions, FittingType.SPECIAL, tag)
        self._liner_m = dimensions._to_m(liner_thickness)  # type: ignore[arg-type]

    @property
    def inner_area_m2(self) -> float:
        iw = self._inlet.width_m - 2 * self._liner_m  # type: ignore[operator]
        ih = self._inlet.height_m - 2 * self._liner_m  # type: ignore[operator]
        return max(0.0, iw * ih)

    def surface_area(self) -> float:
        """Outer shell surface area (m²)."""
        return self._inlet.cross_section_area()

    def volume(self) -> float:
        """Volume of liner material = outer area − inner area (per unit length)."""
        return self._inlet.cross_section_area() - self.inner_area_m2

    def loss_coefficient(self) -> float:
        """Liner adds minor friction; negligible fitting loss (0.0)."""
        return 0.0
