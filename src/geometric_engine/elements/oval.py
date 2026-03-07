"""
Flat-oval (racetrack) fitting elements (SMACNA – category FO).

* FO-1 :class:`OvalElbow90`       – 90° flat-oval elbow.
* FO-2 :class:`OvalElbow45`       – 45° flat-oval elbow.
* FO-3 :class:`OvalTee90`         – Flat-oval main with round branch tee.
* FO-4 :class:`OvalWye45`         – 45° flat-oval wye.
* FO-5 :class:`OvalReducer`       – Flat-oval to flat-oval reducer.
* FO-6 :class:`OvalToRound`       – Flat-oval to round transition.
* FO-7 :class:`OvalToRect`        – Flat-oval to rectangular transition.
* FO-8 :class:`OvalOffset`        – Flat-oval single-plane offset.
"""

from __future__ import annotations

import math

from ..core.dimensions import Dimensions
from .base import FittingElement, FittingType, _validate_positive, _clamp_angle
from .elbows import _interpolate


class OvalElbow90(FittingElement):
    """
    90° flat-oval elbow (SMACNA FO-1).

    Parameters
    ----------
    dimensions:
        Oval cross-section (``major_axis`` and ``minor_axis`` required).
    radius_ratio:
        Centreline radius / major_axis  (R/Wo).  Defaults to 1.5.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        radius_ratio: float = 1.5,
        tag: str = "",
    ) -> None:
        if dimensions.major_axis is None or dimensions.minor_axis is None:
            raise ValueError("OvalElbow90 requires 'major_axis' and 'minor_axis' in dimensions.")
        _validate_positive("radius_ratio", radius_ratio)
        super().__init__(dimensions, FittingType.ELBOW, tag)
        self._radius_ratio = radius_ratio

    @property
    def _radius_m(self) -> float:
        return self._radius_ratio * self._inlet.major_axis_m  # type: ignore[return-value]

    def surface_area(self) -> float:
        arc = self._radius_m * math.pi / 2
        return self._inlet.perimeter() * arc

    def volume(self) -> float:
        arc = self._radius_m * math.pi / 2
        return self._inlet.cross_section_area() * arc

    def loss_coefficient(self) -> float:
        """Oval 90° elbow – interpolated from SMACNA data (same table as round)."""
        rd_table = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
        c90_table = [0.90, 0.45, 0.33, 0.24, 0.19, 0.16]
        return _interpolate(self._radius_ratio, rd_table, c90_table) * 1.05  # oval penalty


class OvalElbow45(FittingElement):
    """
    45° flat-oval elbow (SMACNA FO-2).

    Parameters
    ----------
    dimensions:
        Oval cross-section.
    radius_ratio:
        Centreline radius / major_axis (R/Wo).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        radius_ratio: float = 1.5,
        tag: str = "",
    ) -> None:
        if dimensions.major_axis is None or dimensions.minor_axis is None:
            raise ValueError("OvalElbow45 requires 'major_axis' and 'minor_axis' in dimensions.")
        _validate_positive("radius_ratio", radius_ratio)
        super().__init__(dimensions, FittingType.ELBOW, tag)
        self._radius_ratio = radius_ratio

    @property
    def _radius_m(self) -> float:
        return self._radius_ratio * self._inlet.major_axis_m  # type: ignore[return-value]

    def surface_area(self) -> float:
        arc = self._radius_m * math.pi / 4
        return self._inlet.perimeter() * arc

    def volume(self) -> float:
        arc = self._radius_m * math.pi / 4
        return self._inlet.cross_section_area() * arc

    def loss_coefficient(self) -> float:
        rd_table = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
        c90_table = [0.90, 0.45, 0.33, 0.24, 0.19, 0.16]
        c90 = _interpolate(self._radius_ratio, rd_table, c90_table) * 1.05
        return c90 * 0.55  # 45° factor


class OvalTee90(FittingElement):
    """
    Flat-oval main duct with a round branch tee (SMACNA FO-3).

    Parameters
    ----------
    main_inlet:
        Oval main inlet (``major_axis`` and ``minor_axis`` required).
    branch:
        Round branch (``diameter`` required).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        main_inlet: Dimensions,
        branch: Dimensions,
        tag: str = "",
    ) -> None:
        if main_inlet.major_axis is None or main_inlet.minor_axis is None:
            raise ValueError("OvalTee90: 'main_inlet' requires 'major_axis' and 'minor_axis'.")
        if branch.diameter is None:
            raise ValueError("OvalTee90: 'branch' requires 'diameter'.")
        super().__init__(main_inlet, FittingType.TEE, tag)
        self._branch = branch

    @property
    def branch(self) -> Dimensions:
        return self._branch

    def surface_area(self) -> float:
        dh = self._inlet.hydraulic_diameter()
        return self._inlet.cross_section_area() + self._branch.cross_section_area() * 0.5 * dh

    def volume(self) -> float:
        dh = self._inlet.hydraulic_diameter()
        return (
            self._inlet.cross_section_area() * dh
            + self._branch.cross_section_area() * dh / 2
        )

    def loss_coefficient(self) -> float:
        a_c = self._inlet.cross_section_area()
        a_b = self._branch.cross_section_area()
        return max(a_c / a_b - 1.0, 0.5)


class OvalWye45(FittingElement):
    """
    45° flat-oval wye (SMACNA FO-4).

    Parameters
    ----------
    main_inlet:
        Oval main inlet.
    branch_a:
        First oval branch.
    branch_b:
        Second oval branch.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        main_inlet: Dimensions,
        branch_a: Dimensions,
        branch_b: Dimensions,
        tag: str = "",
    ) -> None:
        for name, dims in [("main_inlet", main_inlet), ("branch_a", branch_a), ("branch_b", branch_b)]:
            if dims.major_axis is None or dims.minor_axis is None:
                raise ValueError(f"OvalWye45: '{name}' requires 'major_axis' and 'minor_axis'.")
        super().__init__(main_inlet, FittingType.WYE, tag)
        self._branch_a = branch_a
        self._branch_b = branch_b

    def surface_area(self) -> float:
        return (
            self._inlet.cross_section_area()
            + self._branch_a.cross_section_area()
            + self._branch_b.cross_section_area()
        ) * 0.6

    def volume(self) -> float:
        dh = self._inlet.hydraulic_diameter()
        return self._inlet.cross_section_area() * dh * 0.75

    def loss_coefficient(self) -> float:
        return 0.45 / math.sin(math.radians(45.0))


class OvalReducer(FittingElement):
    """
    Flat-oval to flat-oval reducer (SMACNA FO-5).

    Parameters
    ----------
    inlet:
        Larger oval inlet.
    outlet:
        Smaller oval outlet.
    length:
        Axial length.
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
        for name, dims in [("inlet", inlet), ("outlet", outlet)]:
            if dims.major_axis is None or dims.minor_axis is None:
                raise ValueError(f"OvalReducer: '{name}' requires 'major_axis' and 'minor_axis'.")
        _validate_positive("length", length)
        super().__init__(inlet, FittingType.TRANSITION, tag)
        self._outlet = outlet
        self._length_m = inlet._to_m(length)  # type: ignore[arg-type]

    def surface_area(self) -> float:
        p1, p2 = self._inlet.perimeter(), self._outlet.perimeter()
        return (p1 + p2) / 2 * self._length_m

    def volume(self) -> float:
        a1 = self._inlet.cross_section_area()
        a2 = self._outlet.cross_section_area()
        return self._length_m / 6 * (a1 + 4 * (a1 + a2) / 2 + a2)

    def loss_coefficient(self) -> float:
        a1 = self._inlet.cross_section_area()
        a2 = self._outlet.cross_section_area()
        if a2 <= a1:
            return 0.5 * (1.0 - a2 / a1) ** 2
        return (1.0 - a1 / a2) ** 2


class OvalToRound(FittingElement):
    """
    Flat-oval to round transition (SMACNA FO-6).

    Parameters
    ----------
    inlet:
        Oval inlet.
    outlet:
        Round outlet (``diameter`` required).
    length:
        Axial length.
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
        if inlet.major_axis is None or inlet.minor_axis is None:
            raise ValueError("OvalToRound: 'inlet' requires 'major_axis' and 'minor_axis'.")
        if outlet.diameter is None:
            raise ValueError("OvalToRound: 'outlet' requires 'diameter'.")
        _validate_positive("length", length)
        super().__init__(inlet, FittingType.TRANSITION, tag)
        self._outlet = outlet
        self._length_m = inlet._to_m(length)  # type: ignore[arg-type]

    def surface_area(self) -> float:
        p1, p2 = self._inlet.perimeter(), self._outlet.perimeter()
        return (p1 + p2) / 2 * self._length_m

    def volume(self) -> float:
        a1 = self._inlet.cross_section_area()
        a2 = self._outlet.cross_section_area()
        return self._length_m / 6 * (a1 + 4 * (a1 + a2) / 2 + a2)

    def loss_coefficient(self) -> float:
        a1 = self._inlet.cross_section_area()
        a2 = self._outlet.cross_section_area()
        if a2 <= a1:
            return 0.5 * (1.0 - a2 / a1) ** 2
        return (1.0 - a1 / a2) ** 2


class OvalToRect(FittingElement):
    """
    Flat-oval to rectangular transition (SMACNA FO-7).

    Parameters
    ----------
    inlet:
        Oval inlet.
    outlet:
        Rectangular outlet (``width`` and ``height`` required).
    length:
        Axial length.
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
        if inlet.major_axis is None or inlet.minor_axis is None:
            raise ValueError("OvalToRect: 'inlet' requires 'major_axis' and 'minor_axis'.")
        if outlet.width is None or outlet.height is None:
            raise ValueError("OvalToRect: 'outlet' requires 'width' and 'height'.")
        _validate_positive("length", length)
        super().__init__(inlet, FittingType.TRANSITION, tag)
        self._outlet = outlet
        self._length_m = inlet._to_m(length)  # type: ignore[arg-type]

    def surface_area(self) -> float:
        p1, p2 = self._inlet.perimeter(), self._outlet.perimeter()
        return (p1 + p2) / 2 * self._length_m

    def volume(self) -> float:
        a1 = self._inlet.cross_section_area()
        a2 = self._outlet.cross_section_area()
        return self._length_m / 6 * (a1 + 4 * (a1 + a2) / 2 + a2)

    def loss_coefficient(self) -> float:
        a1 = self._inlet.cross_section_area()
        a2 = self._outlet.cross_section_area()
        if a2 <= a1:
            return 0.5 * (1.0 - a2 / a1) ** 2
        return (1.0 - a1 / a2) ** 2


class OvalOffset(FittingElement):
    """
    Flat-oval single-plane offset (SMACNA FO-8).

    Parameters
    ----------
    dimensions:
        Oval cross-section.
    offset:
        Perpendicular displacement.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        offset: float,
        tag: str = "",
    ) -> None:
        if dimensions.major_axis is None or dimensions.minor_axis is None:
            raise ValueError("OvalOffset requires 'major_axis' and 'minor_axis' in dimensions.")
        _validate_positive("offset", offset)
        super().__init__(dimensions, FittingType.OFFSET, tag)
        self._offset_m = dimensions._to_m(offset)  # type: ignore[arg-type]

    def surface_area(self) -> float:
        dh = self._inlet.hydraulic_diameter()
        path = math.hypot(self._offset_m, dh * 2)
        return self._inlet.perimeter() * path

    def volume(self) -> float:
        dh = self._inlet.hydraulic_diameter()
        path = math.hypot(self._offset_m, dh * 2)
        return self._inlet.cross_section_area() * path

    def loss_coefficient(self) -> float:
        """Oval offset – loss coefficient ≈ 0.7 (two elbows + oval penalty)."""
        return 0.7
