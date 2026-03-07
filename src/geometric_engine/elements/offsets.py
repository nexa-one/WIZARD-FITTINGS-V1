"""
Rectangular offset fitting elements (SMACNA – category RO).

Offsets route airflow around an obstacle or change elevation/lateral
position while maintaining the same duct cross-section.

* RO-1 :class:`RectangularSingleOffset`   – Single-plane offset (S-curve).
* RO-2 :class:`RectangularDoubleOffset`   – Double-plane offset (X and Y).
* RO-3 :class:`RectangularSymmetricOffset`– Symmetric S-curve offset.
* RO-4 :class:`RectangularVerticalOffset` – Vertical rise offset.
* RO-5 :class:`RectangularLateralOffset`  – Lateral (horizontal) offset.
"""

from __future__ import annotations

import math

from ..core.dimensions import Dimensions
from .base import FittingElement, FittingType, _validate_positive


class RectangularSingleOffset(FittingElement):
    """
    Single-plane S-curve offset (SMACNA RO-1).

    Parameters
    ----------
    dimensions:
        Cross-section (``width`` and ``height`` required).
    length:
        Total axial length of the offset run (same unit as *dimensions*).
    offset:
        Perpendicular displacement between inlet and outlet centrelines.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        length: float,
        offset: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError(
                "RectangularSingleOffset requires 'width' and 'height' in dimensions."
            )
        _validate_positive("length", length)
        _validate_positive("offset", offset)
        super().__init__(dimensions, FittingType.OFFSET, tag)
        self._length_m = dimensions._to_m(length)  # type: ignore[arg-type]
        self._offset_m = dimensions._to_m(offset)  # type: ignore[arg-type]

    @property
    def length_m(self) -> float:
        return self._length_m

    @property
    def offset_m(self) -> float:
        return self._offset_m

    def surface_area(self) -> float:
        """Lateral surface area approximated as two straight sections of length L/2."""
        return self._inlet.perimeter() * self._length_m

    def volume(self) -> float:
        """Internal volume (axial path length ≈ L for small offsets)."""
        return self._inlet.cross_section_area() * self._length_m

    def loss_coefficient(self) -> float:
        """
        Loss coefficient based on offset-to-length ratio (SMACNA Fig 5-22).

            C = 0.9 · (Δ / L)²
        """
        return 0.9 * (self._offset_m / self._length_m) ** 2

    def info(self):  # type: ignore[override]
        d = super().info()
        d["length_m"] = round(self._length_m, 6)
        d["offset_m"] = round(self._offset_m, 6)
        return d


class RectangularDoubleOffset(FittingElement):
    """
    Double-plane offset with independent X and Y displacements (SMACNA RO-2).

    Parameters
    ----------
    dimensions:
        Cross-section (``width`` and ``height`` required).
    length_x:
        Axial length used for the horizontal offset section.
    length_y:
        Axial length used for the vertical offset section.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        length_x: float,
        length_y: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError(
                "RectangularDoubleOffset requires 'width' and 'height' in dimensions."
            )
        _validate_positive("length_x", length_x)
        _validate_positive("length_y", length_y)
        super().__init__(dimensions, FittingType.OFFSET, tag)
        self._lx_m = dimensions._to_m(length_x)  # type: ignore[arg-type]
        self._ly_m = dimensions._to_m(length_y)  # type: ignore[arg-type]

    def surface_area(self) -> float:
        return self._inlet.perimeter() * (self._lx_m + self._ly_m)

    def volume(self) -> float:
        return self._inlet.cross_section_area() * (self._lx_m + self._ly_m)

    def loss_coefficient(self) -> float:
        """Sum of losses for horizontal and vertical offset sections."""
        c_x = 0.9 * (self._inlet.width_m / self._lx_m) ** 2  # type: ignore[operator]
        c_y = 0.9 * (self._inlet.height_m / self._ly_m) ** 2  # type: ignore[operator]
        return c_x + c_y


class RectangularSymmetricOffset(FittingElement):
    """
    Symmetric S-curve offset with equal tapers on both sides (SMACNA RO-3).

    Parameters
    ----------
    dimensions:
        Cross-section (``width`` and ``height`` required).
    length:
        Total axial length.
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
            raise ValueError(
                "RectangularSymmetricOffset requires 'width' and 'height' in dimensions."
            )
        _validate_positive("length", length)
        super().__init__(dimensions, FittingType.OFFSET, tag)
        self._length_m = dimensions._to_m(length)  # type: ignore[arg-type]

    def surface_area(self) -> float:
        return self._inlet.perimeter() * self._length_m

    def volume(self) -> float:
        return self._inlet.cross_section_area() * self._length_m

    def loss_coefficient(self) -> float:
        """Symmetric offset – loss coefficient ~0.4 (SMACNA)."""
        return 0.4


class RectangularVerticalOffset(FittingElement):
    """
    Vertical rise offset (SMACNA RO-4).

    Parameters
    ----------
    dimensions:
        Cross-section (``width`` and ``height`` required).
    rise:
        Vertical displacement between inlet and outlet centrelines.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        rise: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError(
                "RectangularVerticalOffset requires 'width' and 'height' in dimensions."
            )
        _validate_positive("rise", rise)
        super().__init__(dimensions, FittingType.OFFSET, tag)
        self._rise_m = dimensions._to_m(rise)  # type: ignore[arg-type]

    @property
    def rise_m(self) -> float:
        return self._rise_m

    def surface_area(self) -> float:
        dh = self._inlet.hydraulic_diameter()
        total_length = math.hypot(self._rise_m, dh * 2)
        return self._inlet.perimeter() * total_length

    def volume(self) -> float:
        dh = self._inlet.hydraulic_diameter()
        total_length = math.hypot(self._rise_m, dh * 2)
        return self._inlet.cross_section_area() * total_length

    def loss_coefficient(self) -> float:
        """Rise offset – loss coefficient based on SMACNA 2 × elbow method."""
        return 0.6


class RectangularLateralOffset(FittingElement):
    """
    Lateral (horizontal) offset (SMACNA RO-5).

    Parameters
    ----------
    dimensions:
        Cross-section (``width`` and ``height`` required).
    lateral:
        Horizontal displacement between inlet and outlet centrelines.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        lateral: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError(
                "RectangularLateralOffset requires 'width' and 'height' in dimensions."
            )
        _validate_positive("lateral", lateral)
        super().__init__(dimensions, FittingType.OFFSET, tag)
        self._lateral_m = dimensions._to_m(lateral)  # type: ignore[arg-type]

    @property
    def lateral_m(self) -> float:
        return self._lateral_m

    def surface_area(self) -> float:
        dh = self._inlet.hydraulic_diameter()
        total_length = math.hypot(self._lateral_m, dh * 2)
        return self._inlet.perimeter() * total_length

    def volume(self) -> float:
        dh = self._inlet.hydraulic_diameter()
        total_length = math.hypot(self._lateral_m, dh * 2)
        return self._inlet.cross_section_area() * total_length

    def loss_coefficient(self) -> float:
        """Lateral offset – loss coefficient ≈ 0.6 (SMACNA 2 × elbow method)."""
        return 0.6