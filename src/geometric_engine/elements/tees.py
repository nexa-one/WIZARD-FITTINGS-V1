"""
Tee and Wye branch fitting elements (SMACNA).

Branch fittings split or combine airflow at a junction.  Four classes are
provided:

* :class:`RectangularTee`  – 90° rectangular branch tee (main continues straight).
* :class:`RoundTee`        – 90° round branch tee.
* :class:`RectangularWye`  – Symmetrical rectangular wye (45° branch each side).
* :class:`RoundWye`        – Symmetrical round wye (45° branch each side).

Loss coefficients are given for the **straight (main) run** and the
**branch** leg separately.  Velocity is referenced to the *common* (inlet
or outlet) cross-section.
"""

from __future__ import annotations

import math
from typing import Tuple

from ..core.dimensions import Dimensions
from .base import (
    FittingElement,
    FittingType,
    _validate_positive,
)
from .elbows import _interpolate


class RectangularTee(FittingElement):
    """
    Rectangular 90° tee fitting (main + one side branch).

    Parameters
    ----------
    main_inlet:
        Common (upstream) rectangular cross-section.
    main_outlet:
        Straight-through (downstream) rectangular cross-section.
    branch:
        Branch (90°) rectangular cross-section.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        main_inlet: Dimensions,
        main_outlet: Dimensions,
        branch: Dimensions,
        tag: str = "",
    ) -> None:
        for name, dims in [
            ("main_inlet", main_inlet),
            ("main_outlet", main_outlet),
            ("branch", branch),
        ]:
            if dims.width is None or dims.height is None:
                raise ValueError(f"RectangularTee: '{name}' requires 'width' and 'height'.")
        super().__init__(main_inlet, FittingType.TEE, tag)
        self._main_outlet = main_outlet
        self._branch = branch

    @property
    def main_outlet(self) -> Dimensions:
        return self._main_outlet

    @property
    def branch(self) -> Dimensions:
        return self._branch

    def surface_area(self) -> float:
        """Approximate outer surface area (sum of three duct openings × 0.5)."""
        return (
            self._inlet.cross_section_area()
            + self._main_outlet.cross_section_area()
            + self._branch.cross_section_area()
        ) * 0.5

    def volume(self) -> float:
        """Approximate internal volume (main run + branch stub)."""
        dh = self._inlet.hydraulic_diameter()
        main_vol = self._inlet.cross_section_area() * dh
        branch_vol = self._branch.cross_section_area() * (dh / 2)
        return main_vol + branch_vol

    def loss_coefficient_main(self) -> float:
        """
        Loss coefficient for the straight-through (main) leg.

        Based on velocity-pressure ratio at the common inlet using SMACNA
        simplified formula:

            C_main = 0.5 · (1 – Q_b / Q_c)²

        where Q_b / Q_c ≈ A_b / A_c (equal-velocity assumption).
        """
        a_c = self._inlet.cross_section_area()
        a_b = self._branch.cross_section_area()
        ratio = min(a_b / a_c, 1.0)
        return 0.5 * (1.0 - ratio) ** 2

    def loss_coefficient_branch(self) -> float:
        """
        Loss coefficient for the branch leg (SMACNA Table 5-14).

        C_branch = 1.0 · (A_c/A_b – 1)  (minimum 0.5)
        """
        a_c = self._inlet.cross_section_area()
        a_b = self._branch.cross_section_area()
        c = (a_c / a_b - 1.0)
        return max(c, 0.5)

    def loss_coefficient(self) -> float:
        """Return the *branch* loss coefficient (the larger of the two legs)."""
        return self.loss_coefficient_branch()

    def info(self):  # type: ignore[override]
        d = super().info()
        d["loss_coefficient_main"] = round(self.loss_coefficient_main(), 4)
        d["loss_coefficient_branch"] = round(self.loss_coefficient_branch(), 4)
        d["main_outlet_area_m2"] = round(self._main_outlet.cross_section_area(), 6)
        d["branch_area_m2"] = round(self._branch.cross_section_area(), 6)
        return d


class RoundTee(FittingElement):
    """
    Round 90° tee fitting.

    Parameters
    ----------
    main_inlet:
        Common (upstream) round cross-section (``diameter`` required).
    main_outlet:
        Straight-through round cross-section (``diameter`` required).
    branch:
        Branch round cross-section (``diameter`` required).
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        main_inlet: Dimensions,
        main_outlet: Dimensions,
        branch: Dimensions,
        tag: str = "",
    ) -> None:
        for name, dims in [
            ("main_inlet", main_inlet),
            ("main_outlet", main_outlet),
            ("branch", branch),
        ]:
            if dims.diameter is None:
                raise ValueError(f"RoundTee: '{name}' requires 'diameter'.")
        super().__init__(main_inlet, FittingType.TEE, tag)
        self._main_outlet = main_outlet
        self._branch = branch

    @property
    def main_outlet(self) -> Dimensions:
        return self._main_outlet

    @property
    def branch(self) -> Dimensions:
        return self._branch

    def surface_area(self) -> float:
        dh = self._inlet.diameter_m  # type: ignore[assignment]
        main_area = math.pi * dh * dh  # type: ignore[operator]
        branch_area = (
            math.pi
            * self._branch.diameter_m  # type: ignore[operator]
            * self._branch.diameter_m  # type: ignore[operator]
        )
        return (main_area + branch_area) * 0.5

    def volume(self) -> float:
        dh = self._inlet.diameter_m  # type: ignore[assignment]
        main_vol = self._inlet.cross_section_area() * dh  # type: ignore[operator]
        branch_vol = self._branch.cross_section_area() * (dh / 2)  # type: ignore[operator]
        return main_vol + branch_vol

    def loss_coefficient_main(self) -> float:
        a_c = self._inlet.cross_section_area()
        a_b = self._branch.cross_section_area()
        ratio = min(a_b / a_c, 1.0)
        return 0.5 * (1.0 - ratio) ** 2

    def loss_coefficient_branch(self) -> float:
        a_c = self._inlet.cross_section_area()
        a_b = self._branch.cross_section_area()
        return max(a_c / a_b - 1.0, 0.5)

    def loss_coefficient(self) -> float:
        return self.loss_coefficient_branch()

    def info(self):  # type: ignore[override]
        d = super().info()
        d["loss_coefficient_main"] = round(self.loss_coefficient_main(), 4)
        d["loss_coefficient_branch"] = round(self.loss_coefficient_branch(), 4)
        d["main_outlet_area_m2"] = round(self._main_outlet.cross_section_area(), 6)
        d["branch_area_m2"] = round(self._branch.cross_section_area(), 6)
        return d


class RectangularWye(FittingElement):
    """
    Symmetric rectangular wye (two 45° branches leaving a common inlet).

    Parameters
    ----------
    main_inlet:
        Common rectangular cross-section.
    branch_a:
        First branch rectangular cross-section.
    branch_b:
        Second branch rectangular cross-section.
    branch_angle:
        Half-angle of the branch from the main axis (degrees).  Defaults to 45°.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        main_inlet: Dimensions,
        branch_a: Dimensions,
        branch_b: Dimensions,
        branch_angle: float = 45.0,
        tag: str = "",
    ) -> None:
        for name, dims in [
            ("main_inlet", main_inlet),
            ("branch_a", branch_a),
            ("branch_b", branch_b),
        ]:
            if dims.width is None or dims.height is None:
                raise ValueError(f"RectangularWye: '{name}' requires 'width' and 'height'.")
        if not (0.0 < branch_angle < 90.0):
            raise ValueError("branch_angle must be in (0, 90) degrees.")
        super().__init__(main_inlet, FittingType.WYE, tag)
        self._branch_a = branch_a
        self._branch_b = branch_b
        self._branch_angle = branch_angle

    @property
    def branch_a(self) -> Dimensions:
        return self._branch_a

    @property
    def branch_b(self) -> Dimensions:
        return self._branch_b

    @property
    def branch_angle(self) -> float:
        return self._branch_angle

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
        """
        Loss coefficient for one branch (symmetric assumed, SMACNA Table 5-17).

        C = 0.45 / sin(θ)  where θ is the branch angle.
        """
        theta_rad = math.radians(self._branch_angle)
        return 0.45 / math.sin(theta_rad)

    def info(self):  # type: ignore[override]
        d = super().info()
        d["branch_angle_deg"] = self._branch_angle
        d["branch_a_area_m2"] = round(self._branch_a.cross_section_area(), 6)
        d["branch_b_area_m2"] = round(self._branch_b.cross_section_area(), 6)
        return d


class RoundWye(FittingElement):
    """
    Symmetric round wye fitting.

    Parameters
    ----------
    main_inlet:
        Common round cross-section (``diameter`` required).
    branch_a:
        First branch round cross-section (``diameter`` required).
    branch_b:
        Second branch round cross-section (``diameter`` required).
    branch_angle:
        Half-angle of the branch from the main axis (degrees).  Defaults to 45°.
    tag:
        Optional user-defined identifier.
    """

    def __init__(
        self,
        main_inlet: Dimensions,
        branch_a: Dimensions,
        branch_b: Dimensions,
        branch_angle: float = 45.0,
        tag: str = "",
    ) -> None:
        for name, dims in [
            ("main_inlet", main_inlet),
            ("branch_a", branch_a),
            ("branch_b", branch_b),
        ]:
            if dims.diameter is None:
                raise ValueError(f"RoundWye: '{name}' requires 'diameter'.")
        if not (0.0 < branch_angle < 90.0):
            raise ValueError("branch_angle must be in (0, 90) degrees.")
        super().__init__(main_inlet, FittingType.WYE, tag)
        self._branch_a = branch_a
        self._branch_b = branch_b
        self._branch_angle = branch_angle

    @property
    def branch_a(self) -> Dimensions:
        return self._branch_a

    @property
    def branch_b(self) -> Dimensions:
        return self._branch_b

    @property
    def branch_angle(self) -> float:
        return self._branch_angle

    def surface_area(self) -> float:
        d = self._inlet.diameter_m  # type: ignore[assignment]
        return math.pi * d * d * 0.6  # type: ignore[operator]

    def volume(self) -> float:
        d = self._inlet.diameter_m  # type: ignore[assignment]
        return self._inlet.cross_section_area() * d * 0.75  # type: ignore[operator]

    def loss_coefficient(self) -> float:
        theta_rad = math.radians(self._branch_angle)
        return 0.45 / math.sin(theta_rad)

    def info(self):  # type: ignore[override]
        d = super().info()
        d["branch_angle_deg"] = self._branch_angle
        d["branch_a_area_m2"] = round(self._branch_a.cross_section_area(), 6)
        d["branch_b_area_m2"] = round(self._branch_b.cross_section_area(), 6)
        return d
