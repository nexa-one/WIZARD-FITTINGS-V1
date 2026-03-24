"""
cnc_module.models.material
==========================
Sheet-metal gauge / material definitions used in HVAC ductwork.
Thickness values follow the SMACNA *HVAC Duct Construction Standards*
(US-gauge steel).  All dimensions are in millimetres.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


# SMACNA Table 1-1 – galvanised steel gauges (decimal inches → mm)
# gauge: thickness_mm
_STEEL_GAUGE_MM: Dict[int, float] = {
    10: 3.416,
    12: 2.753,
    14: 1.994,
    16: 1.613,
    18: 1.270,
    20: 0.912,
    22: 0.759,
    24: 0.607,
    26: 0.455,
    28: 0.378,
}


class GaugeTable:
    """Look-up table for sheet-metal gauge thicknesses."""

    STEEL = _STEEL_GAUGE_MM

    @staticmethod
    def thickness_mm(gauge: int, material: str = "steel") -> float:
        """Return the wall thickness in mm for a given gauge number.

        Parameters
        ----------
        gauge:    US gauge number (e.g. 22 for standard residential).
        material: Currently only ``"steel"`` is supported.

        Raises
        ------
        KeyError: if the gauge number is not in the table.
        """
        if material.lower() == "steel":
            if gauge not in _STEEL_GAUGE_MM:
                raise KeyError(
                    f"Gauge {gauge} not found in steel table. "
                    f"Available: {sorted(_STEEL_GAUGE_MM)}"
                )
            return _STEEL_GAUGE_MM[gauge]
        raise NotImplementedError(f"Material '{material}' is not yet supported.")


@dataclass
class SheetMetal:
    """Properties of the sheet-metal blank used for a duct fitting.

    Parameters
    ----------
    thickness:    Wall thickness (mm).
    gauge:        US gauge number – automatically filled when ``thickness``
                  is derived from :class:`GaugeTable`.
    material:     Material description (default = "Galvanised Steel").
    bend_radius:  Minimum inside bend radius (mm).  SMACNA recommends
                  ≥ 1× thickness for 90° bends in galvanised steel.
    seam_allowance: Extra flat width added for Pittsburgh / snap lock seams (mm).
    tab_allowance:  Extra width added for connecting tabs (mm).
    """

    thickness: float
    gauge: Optional[int] = None
    material: str = "Galvanised Steel"
    bend_radius: Optional[float] = None
    seam_allowance: float = 6.0    # 6 mm is a common Pittsburgh allowance
    tab_allowance: float = 12.0    # 12 mm tab for transverse joints

    def __post_init__(self) -> None:
        if self.thickness <= 0:
            raise ValueError(f"thickness must be positive, got {self.thickness}")
        if self.bend_radius is None:
            self.bend_radius = max(self.thickness, 1.0)

    # ------------------------------------------------------------------ #
    # Convenience constructors                                            #
    # ------------------------------------------------------------------ #
    @classmethod
    def from_gauge(cls, gauge: int, material: str = "steel", **kwargs) -> "SheetMetal":
        """Create a :class:`SheetMetal` from a US gauge number."""
        thickness = GaugeTable.thickness_mm(gauge, material)
        return cls(thickness=thickness, gauge=gauge, **kwargs)

    # ------------------------------------------------------------------ #
    # Bend deduction helpers                                              #
    # ------------------------------------------------------------------ #
    @property
    def k_factor(self) -> float:
        """Sheet-metal K-factor for flat-pattern bend compensation.
        Typical value for air-duct grade steel = 0.33."""
        return 0.33

    def bend_deduction(self, angle_deg: float = 90.0) -> float:
        """Flat-pattern bend deduction for a given bend angle (degrees).

        Formula: BD = 2 × tan(θ/2) × (R + T) − BA
        where BA = (π/180) × θ × (R + K×T)
        """
        import math
        theta = math.radians(angle_deg)
        r, t, k = self.bend_radius, self.thickness, self.k_factor
        ba = theta * (r + k * t)
        bd = 2.0 * math.tan(theta / 2.0) * (r + t) - ba
        return bd

    def __repr__(self) -> str:
        g = f", gauge={self.gauge}" if self.gauge is not None else ""
        return f"SheetMetal(thickness={self.thickness}{g}, material='{self.material}')"
