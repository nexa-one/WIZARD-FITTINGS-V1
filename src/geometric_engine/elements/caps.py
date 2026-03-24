"""
End-cap (closure) fitting elements.

Caps seal the open end of a duct section.  They contribute negligible
airflow resistance but do have a sheet-metal area that matters for material
take-off.

* :class:`RectangularCap`  – Flat rectangular closure plate.
* :class:`RoundCap`        – Flat circular closure plate.
"""

from __future__ import annotations

import math

from ..core.dimensions import Dimensions
from .base import FittingElement, FittingType


class RectangularCap(FittingElement):
    """
    Flat rectangular end-cap.

    Parameters
    ----------
    dimensions:
        Cross-section to seal (``width`` and ``height`` required).
    tag:
        Optional user-defined identifier.
    """

    def __init__(self, dimensions: Dimensions, tag: str = "") -> None:
        if dimensions.width is None or dimensions.height is None:
            raise ValueError("RectangularCap requires 'width' and 'height' in dimensions.")
        super().__init__(dimensions, FittingType.CAP, tag)

    def surface_area(self) -> float:
        """Face area of the cap plate (m²)."""
        return self._inlet.cross_section_area()

    def volume(self) -> float:
        """
        Enclosed volume behind the cap.

        For a flat cap the enclosed volume is zero.
        """
        return 0.0

    def loss_coefficient(self) -> float:
        """
        Loss coefficient for a capped (dead-end) duct.

        A dead-end presents a loss coefficient of approximately **1.0**
        (all dynamic pressure is converted to static, then lost to
        turbulence upon reversal – SMACNA).
        """
        return 1.0


class RoundCap(FittingElement):
    """
    Flat circular end-cap.

    Parameters
    ----------
    dimensions:
        Cross-section to seal (``diameter`` required).
    tag:
        Optional user-defined identifier.
    """

    def __init__(self, dimensions: Dimensions, tag: str = "") -> None:
        if dimensions.diameter is None:
            raise ValueError("RoundCap requires 'diameter' in dimensions.")
        super().__init__(dimensions, FittingType.CAP, tag)

    def surface_area(self) -> float:
        """Face area of the cap plate (m²)."""
        return self._inlet.cross_section_area()

    def volume(self) -> float:
        """Enclosed volume behind the cap (0 for a flat plate)."""
        return 0.0

    def loss_coefficient(self) -> float:
        """Loss coefficient for a capped duct (1.0)."""
        return 1.0
