"""
Base class for all SMACNA fitting elements.

Every fitting in the WIZARD-FITTINGS engine inherits from
:class:`FittingElement`, which enforces a common interface for geometric
calculations and provides shared bookkeeping (fitting type, tag, etc.).
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any

from ..core.dimensions import Dimensions


class FittingType(Enum):
    """Catalogue of supported SMACNA fitting categories."""

    DUCT_STRAIGHT = "duct_straight"
    ELBOW = "elbow"
    TRANSITION = "transition"
    TEE = "tee"
    WYE = "wye"
    CAP = "cap"
    OFFSET = "offset"


class FittingElement(ABC):
    """
    Abstract base class for all industrial fitting elements.

    Parameters
    ----------
    inlet:
        :class:`~geometric_engine.core.dimensions.Dimensions` object
        describing the *inlet* (upstream) cross-section.
    fitting_type:
        Category of this fitting per :class:`FittingType`.
    tag:
        Optional user-defined identifier (e.g. ``"EL-001"``).
    """

    def __init__(
        self,
        inlet: Dimensions,
        fitting_type: FittingType,
        tag: str = "",
    ) -> None:
        if not isinstance(inlet, Dimensions):
            raise TypeError("inlet must be a Dimensions instance.")
        self._inlet = inlet
        self._fitting_type = fitting_type
        self._tag = tag

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def inlet(self) -> Dimensions:
        """Inlet (upstream) cross-section dimensions."""
        return self._inlet

    @property
    def fitting_type(self) -> FittingType:
        """Category of this fitting."""
        return self._fitting_type

    @property
    def tag(self) -> str:
        """User-defined fitting identifier."""
        return self._tag

    # ------------------------------------------------------------------
    # Abstract interface – subclasses must implement
    # ------------------------------------------------------------------

    @abstractmethod
    def surface_area(self) -> float:
        """Return the total external surface area of the fitting (m²)."""

    @abstractmethod
    def volume(self) -> float:
        """Return the internal (air-side) volume of the fitting (m³)."""

    @abstractmethod
    def loss_coefficient(self) -> float:
        """
        Return the dimensionless pressure-loss coefficient *C* (also called
        *ζ* or *K*) for the fitting.

        The total pressure drop is given by:

            ΔP = C · (ρ · v²) / 2

        where *ρ* is the air density and *v* is the mean velocity at the
        inlet cross-section.
        """

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def inlet_area(self) -> float:
        """Return the inlet cross-sectional area (m²)."""
        return self._inlet.cross_section_area()

    def inlet_hydraulic_diameter(self) -> float:
        """Return the inlet hydraulic diameter D_h (m)."""
        return self._inlet.hydraulic_diameter()

    def info(self) -> Dict[str, Any]:
        """
        Return a dictionary summarising the fitting's geometry and losses.

        Useful for serialisation, reporting, or debugging.
        """
        return {
            "tag": self._tag,
            "fitting_type": self._fitting_type.value,
            "inlet_area_m2": round(self.inlet_area(), 6),
            "inlet_hydraulic_diameter_m": round(self.inlet_hydraulic_diameter(), 6),
            "surface_area_m2": round(self.surface_area(), 6),
            "volume_m3": round(self.volume(), 6),
            "loss_coefficient": round(self.loss_coefficient(), 4),
        }

    def __repr__(self) -> str:
        cls = type(self).__name__
        tag_str = f", tag={self._tag!r}" if self._tag else ""
        return f"{cls}(inlet={self._inlet!r}{tag_str})"


def _validate_positive(name: str, value: float) -> None:
    """Raise ``ValueError`` when *value* is not strictly positive."""
    if value <= 0:
        raise ValueError(f"{name} must be a positive number; got {value}.")


def _clamp_angle(angle_deg: float, lo: float = 0.0, hi: float = 180.0) -> float:
    """Return *angle_deg* clamped to the valid range [*lo*, *hi*]."""
    if not (lo <= angle_deg <= hi):
        raise ValueError(
            f"Angle must be in [{lo}, {hi}] degrees; got {angle_deg}."
        )
    return float(angle_deg)
