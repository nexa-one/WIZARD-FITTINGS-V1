"""
cnc_module.models.fittings
==========================
SMACNA-based HVAC duct fitting definitions.

Each fitting holds:
  • inlet / outlet duct geometries
  • dimensional parameters (length, angle, offset, …)
  • a reference to the :class:`SheetMetal` blank

All linear dimensions are in **millimetres**; angles are in **degrees**.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Union

from cnc_module.models.duct import RectangularDuct, RoundDuct, FlatOvalDuct
from cnc_module.models.material import SheetMetal

DuctType = Union[RectangularDuct, RoundDuct, FlatOvalDuct]


class FittingType(Enum):
    STRAIGHT = auto()
    ELBOW = auto()
    TRANSITION = auto()
    TEE = auto()
    WYE = auto()
    REDUCER = auto()
    END_CAP = auto()
    OFFSET = auto()


# ------------------------------------------------------------------ #
# Base class                                                           #
# ------------------------------------------------------------------ #
@dataclass
class Fitting:
    """Abstract base for all duct fittings."""

    fitting_type: FittingType
    metal: SheetMetal
    label: str = ""

    def surface_area(self) -> float:
        """Return total outer surface area (mm²) – to be overridden."""
        raise NotImplementedError

    def flat_panel_count(self) -> int:
        """Number of individual flat panels the fitting unfolds into."""
        raise NotImplementedError


# ------------------------------------------------------------------ #
# Straight Section                                                     #
# ------------------------------------------------------------------ #
@dataclass
class StraightSection(Fitting):
    """A plain straight length of duct.

    Parameters
    ----------
    duct:   Cross-section geometry.
    length: Duct run length (mm).
    """

    duct: DuctType = field(default=None)
    length: float = 1000.0

    fitting_type: FittingType = field(init=False, default=FittingType.STRAIGHT)

    def __post_init__(self) -> None:
        if self.duct is None:
            raise ValueError("duct must be provided")
        if self.length <= 0:
            raise ValueError(f"length must be positive, got {self.length}")

    def surface_area(self) -> float:
        return self.duct.perimeter * self.length

    def flat_panel_count(self) -> int:
        if isinstance(self.duct, RectangularDuct):
            return 4   # top, bottom, left side, right side
        return 1       # round/oval: single rolled panel


# ------------------------------------------------------------------ #
# Elbows                                                               #
# ------------------------------------------------------------------ #
@dataclass
class RectangularElbow(Fitting):
    """Rectangular duct elbow (mitered or radiused).

    Parameters
    ----------
    duct:        Cross-section geometry.
    angle:       Bend angle in degrees (typically 90 or 45).
    throat_radius: Inner bend radius (mm).  0 = fully mitered.
    """

    duct: RectangularDuct = field(default=None)
    angle: float = 90.0
    throat_radius: float = 0.0

    fitting_type: FittingType = field(init=False, default=FittingType.ELBOW)

    def __post_init__(self) -> None:
        if self.duct is None:
            raise ValueError("duct must be provided")
        if not (0 < self.angle <= 180):
            raise ValueError(f"angle must be in (0, 180], got {self.angle}")

    @property
    def heel_radius(self) -> float:
        """Outer (heel) radius of the elbow (mm)."""
        return self.throat_radius + self.duct.width

    def surface_area(self) -> float:
        """Approximate outer surface area for a radiused elbow."""
        theta = math.radians(self.angle)
        # mean radius of the bend
        r_mean = self.throat_radius + self.duct.width / 2.0
        arc_len = r_mean * theta
        return self.duct.perimeter * arc_len

    def flat_panel_count(self) -> int:
        return 4   # cheeks + top + bottom gores


@dataclass
class RoundElbow(Fitting):
    """Round duct elbow (segmented or stamped).

    Parameters
    ----------
    duct:       Cross-section geometry.
    angle:      Bend angle in degrees.
    radius:     Centreline bend radius (mm).  SMACNA recommends ≥ 1.5×D.
    segments:   Number of gore segments (typically 4–7).
    """

    duct: RoundDuct = field(default=None)
    angle: float = 90.0
    radius: float = None  # set to 1.5×D if not provided
    segments: int = 5

    fitting_type: FittingType = field(init=False, default=FittingType.ELBOW)

    def __post_init__(self) -> None:
        if self.duct is None:
            raise ValueError("duct must be provided")
        if not (0 < self.angle <= 180):
            raise ValueError(f"angle must be in (0, 180], got {self.angle}")
        if self.radius is None:
            self.radius = 1.5 * self.duct.diameter
        if self.segments < 2:
            raise ValueError(f"segments must be >= 2, got {self.segments}")

    def surface_area(self) -> float:
        theta = math.radians(self.angle)
        arc_len = self.radius * theta
        return self.duct.perimeter * arc_len

    def flat_panel_count(self) -> int:
        return self.segments + 1   # N gore panels + 2 end caps − 1 shared = segments+1


# ------------------------------------------------------------------ #
# Transitions                                                          #
# ------------------------------------------------------------------ #
@dataclass
class RectangularTransition(Fitting):
    """Rectangular to rectangular (offset) transition.

    Parameters
    ----------
    inlet:   Inlet cross-section.
    outlet:  Outlet cross-section.
    length:  Axial length of the transition (mm).
    offset_x, offset_y: Lateral offsets of the outlet centreline (mm).
    """

    inlet: RectangularDuct = field(default=None)
    outlet: RectangularDuct = field(default=None)
    length: float = 300.0
    offset_x: float = 0.0
    offset_y: float = 0.0

    fitting_type: FittingType = field(init=False, default=FittingType.TRANSITION)

    def __post_init__(self) -> None:
        if self.inlet is None or self.outlet is None:
            raise ValueError("Both inlet and outlet must be provided")
        if self.length <= 0:
            raise ValueError(f"length must be positive, got {self.length}")

    def surface_area(self) -> float:
        p_in = self.inlet.perimeter
        p_out = self.outlet.perimeter
        return (p_in + p_out) / 2.0 * self.length

    def flat_panel_count(self) -> int:
        return 4


@dataclass
class RoundToRectTransition(Fitting):
    """Round-to-rectangular transition (boot / square-to-round).

    Parameters
    ----------
    round_end:  Round duct cross-section.
    rect_end:   Rectangular duct cross-section.
    length:     Axial length (mm).
    """

    round_end: RoundDuct = field(default=None)
    rect_end: RectangularDuct = field(default=None)
    length: float = 250.0

    fitting_type: FittingType = field(init=False, default=FittingType.TRANSITION)

    def __post_init__(self) -> None:
        if self.round_end is None or self.rect_end is None:
            raise ValueError("Both round_end and rect_end must be provided")
        if self.length <= 0:
            raise ValueError(f"length must be positive, got {self.length}")

    def surface_area(self) -> float:
        p_r = self.round_end.perimeter
        p_rect = self.rect_end.perimeter
        return (p_r + p_rect) / 2.0 * self.length

    def flat_panel_count(self) -> int:
        return 4   # four triangular / trapezoidal panels


# ------------------------------------------------------------------ #
# Tee / Wye                                                            #
# ------------------------------------------------------------------ #
@dataclass
class RectangularTee(Fitting):
    """Rectangular duct tee (straight-through + 90° branch).

    Parameters
    ----------
    main:    Main-duct cross-section.
    branch:  Branch cross-section.
    length:  Length of main-duct trunk (mm).
    """

    main: RectangularDuct = field(default=None)
    branch: RectangularDuct = field(default=None)
    length: float = 600.0

    fitting_type: FittingType = field(init=False, default=FittingType.TEE)

    def __post_init__(self) -> None:
        if self.main is None or self.branch is None:
            raise ValueError("Both main and branch must be provided")
        if self.length <= 0:
            raise ValueError(f"length must be positive, got {self.length}")

    def surface_area(self) -> float:
        # main trunk + branch collar (minus the hole)
        main_area = self.main.perimeter * self.length
        branch_area = self.branch.perimeter * self.branch.width  # stub height ≈ width
        return main_area + branch_area

    def flat_panel_count(self) -> int:
        return 6   # 4 main panels + 2 branch stub panels


@dataclass
class RoundTee(Fitting):
    """Round duct tee."""

    main: RoundDuct = field(default=None)
    branch: RoundDuct = field(default=None)
    length: float = 600.0

    fitting_type: FittingType = field(init=False, default=FittingType.TEE)

    def __post_init__(self) -> None:
        if self.main is None or self.branch is None:
            raise ValueError("Both main and branch must be provided")
        if self.length <= 0:
            raise ValueError(f"length must be positive, got {self.length}")

    def surface_area(self) -> float:
        main_area = self.main.perimeter * self.length
        branch_area = self.branch.perimeter * self.branch.diameter
        return main_area + branch_area

    def flat_panel_count(self) -> int:
        return 2   # main body + branch stub


# ------------------------------------------------------------------ #
# Reducer                                                              #
# ------------------------------------------------------------------ #
@dataclass
class RectangularReducer(Fitting):
    """Concentric or eccentric rectangular reducer.

    Parameters
    ----------
    large:     Larger cross-section (inlet).
    small:     Smaller cross-section (outlet).
    length:    Axial length (mm).
    eccentric: If True the bottom face stays flat (eccentric reducer).
    """

    large: RectangularDuct = field(default=None)
    small: RectangularDuct = field(default=None)
    length: float = 200.0
    eccentric: bool = False

    fitting_type: FittingType = field(init=False, default=FittingType.REDUCER)

    def __post_init__(self) -> None:
        if self.large is None or self.small is None:
            raise ValueError("Both large and small must be provided")
        if self.length <= 0:
            raise ValueError(f"length must be positive, got {self.length}")

    def surface_area(self) -> float:
        p_in = self.large.perimeter
        p_out = self.small.perimeter
        return (p_in + p_out) / 2.0 * self.length

    def flat_panel_count(self) -> int:
        return 4


# ------------------------------------------------------------------ #
# End Cap                                                              #
# ------------------------------------------------------------------ #
@dataclass
class EndCap(Fitting):
    """Flat or dished end cap for a duct opening."""

    duct: DuctType = field(default=None)
    dished: bool = False

    fitting_type: FittingType = field(init=False, default=FittingType.END_CAP)

    def __post_init__(self) -> None:
        if self.duct is None:
            raise ValueError("duct must be provided")

    def surface_area(self) -> float:
        if isinstance(self.duct, RectangularDuct):
            return self.duct.external_width * self.duct.external_height
        if isinstance(self.duct, RoundDuct):
            return math.pi * (self.duct.external_diameter / 2.0) ** 2
        return self.duct.area

    def flat_panel_count(self) -> int:
        return 1
