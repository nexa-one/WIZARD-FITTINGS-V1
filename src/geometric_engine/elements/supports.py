"""
Duct support and hanger elements (SMACNA – category SU).

Supports are primarily structural; they have material (fabrication) geometry
but contribute negligible aerodynamic losses.  The ``loss_coefficient``
method returns 0.0 for all support types.

* SU-1 :class:`StrapHanger`          – Single strap / clevis hanger.
* SU-2 :class:`TrapezeBracket`       – Trapeze hanger with threaded rods.
* SU-3 :class:`ClevisHanger`         – Clevis hanger for round duct.
* SU-4 :class:`BandHanger`           – Band hanger for round duct.
* SU-5 :class:`BeamClamp`            – Beam-clamp attachment.
* SU-6 :class:`TieRod`               – Tie-rod lateral support.
* SU-7 :class:`SeismicLongitudinal`  – Seismic bracing, longitudinal.
* SU-8 :class:`SeismicTransverse`    – Seismic bracing, transverse.
"""

from __future__ import annotations

import math

from ..core.dimensions import Dimensions
from .base import FittingElement, FittingType, _validate_positive


class StrapHanger(FittingElement):
    """
    Single strap hanger (SMACNA SU-1).

    Parameters
    ----------
    dimensions:
        Duct cross-section being supported (``width`` required).
    strap_width:
        Width of the hanger strap (same unit as *dimensions*).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        strap_width: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None:
            raise ValueError("StrapHanger requires 'width' in dimensions.")
        _validate_positive("strap_width", strap_width)
        super().__init__(dimensions, FittingType.SUPPORT, tag)
        self._strap_width_m = dimensions._to_m(strap_width)  # type: ignore[arg-type]

    @property
    def strap_width_m(self) -> float:
        return self._strap_width_m

    def surface_area(self) -> float:
        """Strap contact area on the duct bottom (m²)."""
        return self._inlet.width_m * self._strap_width_m  # type: ignore[return-value, operator]

    def volume(self) -> float:
        return 0.0

    def loss_coefficient(self) -> float:
        return 0.0


class TrapezeBracket(FittingElement):
    """
    Trapeze hanger with two threaded rods (SMACNA SU-2).

    Parameters
    ----------
    dimensions:
        Duct cross-section being supported (``width`` required).
    span:
        Distance between the two vertical rods (same unit as *dimensions*).
    rod_dia:
        Diameter of the threaded rods (same unit as *dimensions*).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        span: float,
        rod_dia: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None:
            raise ValueError("TrapezeBracket requires 'width' in dimensions.")
        _validate_positive("span", span)
        _validate_positive("rod_dia", rod_dia)
        super().__init__(dimensions, FittingType.SUPPORT, tag)
        self._span_m = dimensions._to_m(span)  # type: ignore[arg-type]
        self._rod_dia_m = dimensions._to_m(rod_dia)  # type: ignore[arg-type]

    @property
    def span_m(self) -> float:
        return self._span_m

    @property
    def rod_dia_m(self) -> float:
        return self._rod_dia_m

    def surface_area(self) -> float:
        """Approximate strut surface area (bottom bar + 2 short rods assumed 300 mm)."""
        rod_length = 0.3  # m, stub assumption
        return self._span_m * self._rod_dia_m * 2 + 2 * rod_length * self._rod_dia_m

    def volume(self) -> float:
        return 0.0

    def loss_coefficient(self) -> float:
        return 0.0


class ClevisHanger(FittingElement):
    """
    Clevis hanger for round duct (SMACNA SU-3).

    Parameters
    ----------
    dimensions:
        Round duct cross-section (``diameter`` required).
    tag:
        Optional user-defined identifier.
    """

    def __init__(self, dimensions: Dimensions, tag: str = "") -> None:
        if dimensions.diameter is None:
            raise ValueError("ClevisHanger requires 'diameter' in dimensions.")
        super().__init__(dimensions, FittingType.SUPPORT, tag)

    def surface_area(self) -> float:
        """U-bolt contact footprint approximation."""
        d = self._inlet.diameter_m  # type: ignore[assignment]
        return math.pi * d * 0.1  # type: ignore[operator]

    def volume(self) -> float:
        return 0.0

    def loss_coefficient(self) -> float:
        return 0.0


class BandHanger(FittingElement):
    """
    Band hanger for round duct (SMACNA SU-4).

    Parameters
    ----------
    dimensions:
        Round duct cross-section (``diameter`` required).
    band_width:
        Width of the hanger band (same unit as *dimensions*).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        band_width: float,
        tag: str = "",
    ) -> None:
        if dimensions.diameter is None:
            raise ValueError("BandHanger requires 'diameter' in dimensions.")
        _validate_positive("band_width", band_width)
        super().__init__(dimensions, FittingType.SUPPORT, tag)
        self._band_width_m = dimensions._to_m(band_width)  # type: ignore[arg-type]

    @property
    def band_width_m(self) -> float:
        return self._band_width_m

    def surface_area(self) -> float:
        """Hanger band contact area (m²)."""
        return math.pi * self._inlet.diameter_m * self._band_width_m  # type: ignore[operator]

    def volume(self) -> float:
        return 0.0

    def loss_coefficient(self) -> float:
        return 0.0


class BeamClamp(FittingElement):
    """
    Beam-clamp attachment for duct hanger rods (SMACNA SU-5).

    Parameters
    ----------
    dimensions:
        Duct cross-section being supported (``width`` required for reference).
    flange_size:
        Beam flange width the clamp grips (same unit as *dimensions*).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        flange_size: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None:
            raise ValueError("BeamClamp requires 'width' in dimensions.")
        _validate_positive("flange_size", flange_size)
        super().__init__(dimensions, FittingType.SUPPORT, tag)
        self._flange_m = dimensions._to_m(flange_size)  # type: ignore[arg-type]

    def surface_area(self) -> float:
        """Clamp jaw contact area (m²)."""
        return self._flange_m * 0.05  # 50 mm jaw depth approximation

    def volume(self) -> float:
        return 0.0

    def loss_coefficient(self) -> float:
        return 0.0


class TieRod(FittingElement):
    """
    Tie-rod lateral support for rectangular duct (SMACNA SU-6).

    Parameters
    ----------
    dimensions:
        Duct cross-section (``width`` required).
    rod_dia:
        Tie-rod diameter (same unit as *dimensions*).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        rod_dia: float,
        tag: str = "",
    ) -> None:
        if dimensions.width is None:
            raise ValueError("TieRod requires 'width' in dimensions.")
        _validate_positive("rod_dia", rod_dia)
        super().__init__(dimensions, FittingType.SUPPORT, tag)
        self._rod_dia_m = dimensions._to_m(rod_dia)  # type: ignore[arg-type]

    def surface_area(self) -> float:
        """Rod cross-section area × duct width (fabrication ref)."""
        return math.pi * (self._rod_dia_m / 2) ** 2 + self._inlet.width_m * self._rod_dia_m  # type: ignore[operator]

    def volume(self) -> float:
        return 0.0

    def loss_coefficient(self) -> float:
        return 0.0


class SeismicBrace(FittingElement):
    """
    Seismic bracing for ductwork (base class for SU-7/8).

    Parameters
    ----------
    dimensions:
        Duct cross-section (``width`` or ``diameter`` required).
    duct_size:
        Largest duct dimension for brace-size selection (same unit).
    splay_angle:
        Brace splay angle from vertical (degrees).
    brace_type:
        ``"longitudinal"`` (SU-7) or ``"transverse"`` (SU-8).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        dimensions: Dimensions,
        duct_size: float,
        splay_angle: float,
        brace_type: str,
        tag: str = "",
    ) -> None:
        if dimensions.width is None and dimensions.diameter is None:
            raise ValueError("SeismicBrace requires 'width' or 'diameter' in dimensions.")
        _validate_positive("duct_size", duct_size)
        if not (0.0 < splay_angle < 90.0):
            raise ValueError("splay_angle must be in (0, 90) degrees.")
        if brace_type not in ("longitudinal", "transverse"):
            raise ValueError("brace_type must be 'longitudinal' or 'transverse'.")
        super().__init__(dimensions, FittingType.SUPPORT, tag)
        self._duct_size_m = dimensions._to_m(duct_size)  # type: ignore[arg-type]
        self._splay_angle = splay_angle
        self._brace_type = brace_type

    @property
    def splay_angle(self) -> float:
        return self._splay_angle

    @property
    def brace_type(self) -> str:
        return self._brace_type

    def _brace_length_m(self) -> float:
        """Approximate brace rod length based on splay angle and duct size."""
        return self._duct_size_m / math.sin(math.radians(self._splay_angle))

    def surface_area(self) -> float:
        """Brace rod surface area (approximated as 25 mm round rod)."""
        rod_dia = 0.025  # m
        return math.pi * rod_dia * self._brace_length_m()

    def volume(self) -> float:
        return 0.0

    def loss_coefficient(self) -> float:
        return 0.0

    def info(self):  # type: ignore[override]
        d = super().info()
        d["brace_type"] = self._brace_type
        d["splay_angle_deg"] = self._splay_angle
        d["brace_length_m"] = round(self._brace_length_m(), 4)
        return d


class SeismicLongitudinal(SeismicBrace):
    """Seismic longitudinal brace (SMACNA SU-7)."""

    def __init__(
        self,
        dimensions: Dimensions,
        duct_size: float,
        splay_angle: float = 45.0,
        tag: str = "",
    ) -> None:
        super().__init__(dimensions, duct_size, splay_angle, "longitudinal", tag)


class SeismicTransverse(SeismicBrace):
    """Seismic transverse brace (SMACNA SU-8)."""

    def __init__(
        self,
        dimensions: Dimensions,
        duct_size: float,
        splay_angle: float = 45.0,
        tag: str = "",
    ) -> None:
        super().__init__(dimensions, duct_size, splay_angle, "transverse", tag)