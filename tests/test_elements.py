"""Tests for all fitting element classes."""

import math
import pytest

from geometric_engine.core.dimensions import Dimensions, UnitSystem
from geometric_engine.elements.ducts import RectangularDuct, RoundDuct, OvalDuct
from geometric_engine.elements.elbows import RectangularElbow, RoundElbow, MiteredElbow
from geometric_engine.elements.transitions import (
    RectangularTransition,
    RoundTransition,
    RectangularToRoundTransition,
)
from geometric_engine.elements.tees import (
    RectangularTee,
    RoundTee,
    RectangularWye,
    RoundWye,
)
from geometric_engine.elements.caps import RectangularCap, RoundCap


# ---------------------------------------------------------------------------
# Straight duct sections
# ---------------------------------------------------------------------------

class TestRectangularDuct:
    def setup_method(self):
        self.dims = Dimensions(width=0.4, height=0.3)
        self.duct = RectangularDuct(self.dims, length=2.0, tag="D-001")

    def test_volume(self):
        assert math.isclose(self.duct.volume(), 0.4 * 0.3 * 2.0)

    def test_surface_area(self):
        assert math.isclose(self.duct.surface_area(), 2 * (0.4 + 0.3) * 2.0)

    def test_loss_coefficient(self):
        assert self.duct.loss_coefficient() == 0.0

    def test_info_keys(self):
        info = self.duct.info()
        assert "length_m" in info
        assert info["tag"] == "D-001"

    def test_requires_width_height(self):
        with pytest.raises(ValueError):
            RectangularDuct(Dimensions(diameter=0.5), length=1.0)

    def test_requires_positive_length(self):
        with pytest.raises(ValueError):
            RectangularDuct(Dimensions(width=0.4, height=0.3), length=0)


class TestRoundDuct:
    def setup_method(self):
        self.dims = Dimensions(diameter=0.5)
        self.duct = RoundDuct(self.dims, length=3.0)

    def test_volume(self):
        expected = math.pi * (0.25**2) * 3.0
        assert math.isclose(self.duct.volume(), expected)

    def test_surface_area(self):
        expected = math.pi * 0.5 * 3.0
        assert math.isclose(self.duct.surface_area(), expected)

    def test_requires_diameter(self):
        with pytest.raises(ValueError):
            RoundDuct(Dimensions(width=0.4, height=0.3), length=1.0)


class TestOvalDuct:
    def setup_method(self):
        self.dims = Dimensions(major_axis=0.6, minor_axis=0.3)
        self.duct = OvalDuct(self.dims, length=2.0)

    def test_volume_positive(self):
        assert self.duct.volume() > 0

    def test_major_gt_minor(self):
        with pytest.raises(ValueError):
            OvalDuct(Dimensions(major_axis=0.2, minor_axis=0.4), length=1.0)


# ---------------------------------------------------------------------------
# Elbows
# ---------------------------------------------------------------------------

class TestRectangularElbow:
    def setup_method(self):
        self.dims = Dimensions(width=0.4, height=0.3)
        self.elbow = RectangularElbow(self.dims, angle=90.0, radius_ratio=1.5)

    def test_loss_coefficient_positive(self):
        assert self.elbow.loss_coefficient() > 0

    def test_surface_area_positive(self):
        assert self.elbow.surface_area() > 0

    def test_volume_positive(self):
        assert self.elbow.volume() > 0

    def test_smaller_radius_higher_loss(self):
        c_large = RectangularElbow(self.dims, radius_ratio=3.0).loss_coefficient()
        c_small = RectangularElbow(self.dims, radius_ratio=0.5).loss_coefficient()
        assert c_small > c_large

    def test_larger_angle_higher_loss(self):
        c45 = RectangularElbow(self.dims, angle=45.0).loss_coefficient()
        c90 = RectangularElbow(self.dims, angle=90.0).loss_coefficient()
        assert c90 > c45

    def test_invalid_angle(self):
        with pytest.raises(ValueError):
            RectangularElbow(self.dims, angle=0.0)

    def test_requires_rect_dims(self):
        with pytest.raises(ValueError):
            RectangularElbow(Dimensions(diameter=0.5))


class TestRoundElbow:
    def setup_method(self):
        self.dims = Dimensions(diameter=0.5)
        self.elbow = RoundElbow(self.dims, angle=90.0, radius_ratio=1.5)

    def test_loss_coefficient_range(self):
        c = self.elbow.loss_coefficient()
        assert 0 < c < 2.0

    def test_requires_diameter(self):
        with pytest.raises(ValueError):
            RoundElbow(Dimensions(width=0.4, height=0.3))


class TestMiteredElbow:
    def setup_method(self):
        self.dims = Dimensions(width=0.4, height=0.3)

    def test_90deg_loss(self):
        c = MiteredElbow(self.dims, angle=90.0).loss_coefficient()
        assert math.isclose(c, 1.20)

    def test_45deg_loss(self):
        c = MiteredElbow(self.dims, angle=45.0).loss_coefficient()
        assert math.isclose(c, 0.26)

    def test_angle_over_90_raises(self):
        with pytest.raises(ValueError):
            MiteredElbow(self.dims, angle=91.0)


# ---------------------------------------------------------------------------
# Transitions
# ---------------------------------------------------------------------------

class TestRectangularTransition:
    def setup_method(self):
        self.inlet = Dimensions(width=0.6, height=0.4)
        self.outlet_small = Dimensions(width=0.3, height=0.2)
        self.outlet_large = Dimensions(width=0.8, height=0.5)

    def test_contraction_loss(self):
        t = RectangularTransition(self.inlet, self.outlet_small, length=0.5)
        c = t.loss_coefficient()
        assert 0 < c < 1

    def test_expansion_loss(self):
        t = RectangularTransition(self.inlet, self.outlet_large, length=0.5)
        c = t.loss_coefficient()
        assert c > 0

    def test_volume_positive(self):
        t = RectangularTransition(self.inlet, self.outlet_small, length=1.0)
        assert t.volume() > 0

    def test_surface_area_positive(self):
        t = RectangularTransition(self.inlet, self.outlet_small, length=1.0)
        assert t.surface_area() > 0


class TestRoundTransition:
    def setup_method(self):
        self.inlet = Dimensions(diameter=0.5)
        self.outlet_small = Dimensions(diameter=0.3)
        self.outlet_large = Dimensions(diameter=0.7)

    def test_contraction_loss(self):
        t = RoundTransition(self.inlet, self.outlet_small, length=0.5)
        assert t.loss_coefficient() > 0

    def test_volume_cone_frustum(self):
        t = RoundTransition(self.inlet, self.outlet_small, length=1.0)
        r1, r2 = 0.25, 0.15
        expected = math.pi * 1.0 / 3 * (r1**2 + r1 * r2 + r2**2)
        assert math.isclose(t.volume(), expected)


class TestRectangularToRoundTransition:
    def test_basic(self):
        inlet = Dimensions(width=0.5, height=0.4)
        outlet = Dimensions(diameter=0.4)
        t = RectangularToRoundTransition(inlet, outlet, length=0.4)
        assert t.surface_area() > 0
        assert t.volume() > 0
        assert t.loss_coefficient() >= 0


# ---------------------------------------------------------------------------
# Tees and Wyes
# ---------------------------------------------------------------------------

class TestRectangularTee:
    def setup_method(self):
        self.inlet = Dimensions(width=0.6, height=0.4)
        self.main_out = Dimensions(width=0.4, height=0.4)
        self.branch = Dimensions(width=0.3, height=0.3)
        self.tee = RectangularTee(self.inlet, self.main_out, self.branch)

    def test_branch_loss_greater_than_main(self):
        assert self.tee.loss_coefficient_branch() > self.tee.loss_coefficient_main()

    def test_volume_positive(self):
        assert self.tee.volume() > 0

    def test_info_keys(self):
        info = self.tee.info()
        assert "loss_coefficient_main" in info
        assert "loss_coefficient_branch" in info


class TestRoundTee:
    def setup_method(self):
        self.inlet = Dimensions(diameter=0.5)
        self.main_out = Dimensions(diameter=0.4)
        self.branch = Dimensions(diameter=0.3)
        self.tee = RoundTee(self.inlet, self.main_out, self.branch)

    def test_loss_positive(self):
        assert self.tee.loss_coefficient() > 0


class TestRectangularWye:
    def setup_method(self):
        self.inlet = Dimensions(width=0.6, height=0.4)
        self.b_a = Dimensions(width=0.3, height=0.4)
        self.b_b = Dimensions(width=0.3, height=0.4)
        self.wye = RectangularWye(self.inlet, self.b_a, self.b_b, branch_angle=45.0)

    def test_loss_positive(self):
        assert self.wye.loss_coefficient() > 0

    def test_bad_angle(self):
        with pytest.raises(ValueError):
            RectangularWye(self.inlet, self.b_a, self.b_b, branch_angle=0.0)


class TestRoundWye:
    def test_loss(self):
        inlet = Dimensions(diameter=0.5)
        b = Dimensions(diameter=0.3)
        wye = RoundWye(inlet, b, b, branch_angle=30.0)
        assert wye.loss_coefficient() > 0


# ---------------------------------------------------------------------------
# Caps
# ---------------------------------------------------------------------------

class TestCaps:
    def test_rectangular_cap_area(self):
        cap = RectangularCap(Dimensions(width=0.4, height=0.3))
        assert math.isclose(cap.surface_area(), 0.12)
        assert cap.volume() == 0.0
        assert cap.loss_coefficient() == 1.0

    def test_round_cap_area(self):
        cap = RoundCap(Dimensions(diameter=0.5))
        assert math.isclose(cap.surface_area(), math.pi * 0.25**2)
        assert cap.volume() == 0.0
        assert cap.loss_coefficient() == 1.0

    def test_rectangular_cap_requires_dims(self):
        with pytest.raises(ValueError):
            RectangularCap(Dimensions(diameter=0.5))

    def test_round_cap_requires_diameter(self):
        with pytest.raises(ValueError):
            RoundCap(Dimensions(width=0.4, height=0.3))


# ---------------------------------------------------------------------------
# Imperial unit system integration test
# ---------------------------------------------------------------------------

class TestImperialUnits:
    def test_round_duct_imperial(self):
        dims = Dimensions(diameter=12.0, unit_system=UnitSystem.IMPERIAL)  # 12 inches = ~0.3048 m
        duct = RoundDuct(dims, length=120.0)  # 120 inches = 3.048 m
        expected_vol = math.pi * (0.1524**2) * 3.048
        assert math.isclose(duct.volume(), expected_vol, rel_tol=1e-5)
