"""
Tests for cnc_module.models – duct geometry and material data models.
"""

import math
import pytest

from cnc_module.models.duct import RectangularDuct, RoundDuct, FlatOvalDuct, DuctShape
from cnc_module.models.material import SheetMetal, GaugeTable
from cnc_module.models.fittings import (
    StraightSection,
    RectangularElbow,
    RoundElbow,
    RectangularTransition,
    RoundToRectTransition,
    RectangularTee,
    RoundTee,
    RectangularReducer,
    EndCap,
)


# ================================================================== #
# RectangularDuct                                                      #
# ================================================================== #
class TestRectangularDuct:
    def test_shape_enum(self):
        d = RectangularDuct(400, 200)
        assert d.shape == DuctShape.RECTANGULAR

    def test_perimeter(self):
        d = RectangularDuct(400, 200)
        assert d.perimeter == pytest.approx(1200.0)

    def test_area(self):
        d = RectangularDuct(400, 200)
        assert d.area == pytest.approx(80_000.0)

    def test_hydraulic_diameter(self):
        d = RectangularDuct(400, 200)
        # (2 × 400 × 200) / (400 + 200) = 266.67
        assert d.hydraulic_diameter == pytest.approx(266.667, rel=1e-3)

    def test_external_dimensions(self):
        d = RectangularDuct(400, 200, thickness=1.0)
        assert d.external_width == pytest.approx(402.0)
        assert d.external_height == pytest.approx(202.0)

    def test_aspect_ratio(self):
        d = RectangularDuct(400, 200)
        assert d.aspect_ratio == pytest.approx(2.0)

    def test_outer_corners_count(self):
        d = RectangularDuct(400, 200)
        corners = d.outer_corners(z=0.0)
        assert len(corners) == 4

    def test_inner_corners_count(self):
        d = RectangularDuct(400, 200)
        corners = d.inner_corners(z=0.0)
        assert len(corners) == 4

    def test_invalid_width(self):
        with pytest.raises(ValueError):
            RectangularDuct(-100, 200)

    def test_invalid_height(self):
        with pytest.raises(ValueError):
            RectangularDuct(400, 0)

    def test_invalid_thickness(self):
        with pytest.raises(ValueError):
            RectangularDuct(400, 200, thickness=-1)


# ================================================================== #
# RoundDuct                                                            #
# ================================================================== #
class TestRoundDuct:
    def test_shape_enum(self):
        d = RoundDuct(300)
        assert d.shape == DuctShape.ROUND

    def test_perimeter(self):
        d = RoundDuct(300)
        assert d.perimeter == pytest.approx(math.pi * 300)

    def test_area(self):
        d = RoundDuct(300)
        assert d.area == pytest.approx(math.pi * 150 ** 2)

    def test_hydraulic_diameter(self):
        d = RoundDuct(300)
        assert d.hydraulic_diameter == pytest.approx(300.0)

    def test_external_diameter(self):
        d = RoundDuct(300, thickness=1.5)
        assert d.external_diameter == pytest.approx(303.0)

    def test_circle_points_count(self):
        d = RoundDuct(300)
        pts = d.circle_points(segments=36)
        assert len(pts) == 36

    def test_invalid_diameter(self):
        with pytest.raises(ValueError):
            RoundDuct(0)

    def test_invalid_thickness(self):
        with pytest.raises(ValueError):
            RoundDuct(300, thickness=0)


# ================================================================== #
# FlatOvalDuct                                                         #
# ================================================================== #
class TestFlatOvalDuct:
    def test_shape_enum(self):
        d = FlatOvalDuct(500, 200)
        assert d.shape == DuctShape.FLAT_OVAL

    def test_straight_length(self):
        d = FlatOvalDuct(500, 200)
        assert d.straight_length == pytest.approx(300.0)

    def test_perimeter(self):
        d = FlatOvalDuct(500, 200)
        expected = math.pi * 200 + 2 * 300
        assert d.perimeter == pytest.approx(expected)

    def test_area(self):
        d = FlatOvalDuct(500, 200)
        expected = math.pi * 100 ** 2 + 200 * 300
        assert d.area == pytest.approx(expected)

    def test_major_equals_minor_is_round(self):
        d = FlatOvalDuct(200, 200)
        assert d.straight_length == pytest.approx(0.0)

    def test_invalid_major_less_than_minor(self):
        with pytest.raises(ValueError):
            FlatOvalDuct(100, 200)

    def test_invalid_major(self):
        with pytest.raises(ValueError):
            FlatOvalDuct(0, 200)


# ================================================================== #
# SheetMetal / GaugeTable                                              #
# ================================================================== #
class TestSheetMetal:
    def test_from_gauge_22(self):
        m = SheetMetal.from_gauge(22)
        assert m.thickness == pytest.approx(0.759)
        assert m.gauge == 22

    def test_from_gauge_20(self):
        m = SheetMetal.from_gauge(20)
        assert m.thickness == pytest.approx(0.912)

    def test_unknown_gauge(self):
        with pytest.raises(KeyError):
            GaugeTable.thickness_mm(99)

    def test_bend_deduction_positive(self):
        m = SheetMetal(thickness=1.0, bend_radius=1.0)
        bd = m.bend_deduction(90.0)
        assert bd > 0

    def test_bend_radius_default(self):
        m = SheetMetal(thickness=1.5)
        assert m.bend_radius == pytest.approx(1.5)

    def test_invalid_thickness(self):
        with pytest.raises(ValueError):
            SheetMetal(thickness=0)


# ================================================================== #
# Fittings                                                             #
# ================================================================== #
@pytest.fixture
def metal():
    return SheetMetal(thickness=0.8)


@pytest.fixture
def rect_duct():
    return RectangularDuct(400, 200)


@pytest.fixture
def round_duct():
    return RoundDuct(300)


class TestStraightSection:
    def test_surface_area_rect(self, metal, rect_duct):
        s = StraightSection(duct=rect_duct, length=1000, metal=metal)
        assert s.surface_area() == pytest.approx(rect_duct.perimeter * 1000)

    def test_surface_area_round(self, metal, round_duct):
        s = StraightSection(duct=round_duct, length=500, metal=metal)
        assert s.surface_area() == pytest.approx(round_duct.perimeter * 500)

    def test_flat_panel_count_rect(self, metal, rect_duct):
        s = StraightSection(duct=rect_duct, length=1000, metal=metal)
        assert s.flat_panel_count() == 4

    def test_flat_panel_count_round(self, metal, round_duct):
        s = StraightSection(duct=round_duct, length=500, metal=metal)
        assert s.flat_panel_count() == 1

    def test_invalid_length(self, metal, rect_duct):
        with pytest.raises(ValueError):
            StraightSection(duct=rect_duct, length=0, metal=metal)

    def test_missing_duct(self, metal):
        with pytest.raises((ValueError, TypeError)):
            StraightSection(duct=None, length=500, metal=metal)


class TestRectangularElbow:
    def test_heel_radius(self, metal, rect_duct):
        e = RectangularElbow(duct=rect_duct, angle=90, throat_radius=100, metal=metal)
        assert e.heel_radius == pytest.approx(500.0)

    def test_surface_area_positive(self, metal, rect_duct):
        e = RectangularElbow(duct=rect_duct, angle=90, throat_radius=100, metal=metal)
        assert e.surface_area() > 0

    def test_invalid_angle(self, metal, rect_duct):
        with pytest.raises(ValueError):
            RectangularElbow(duct=rect_duct, angle=200, metal=metal)


class TestRoundElbow:
    def test_default_radius(self, metal, round_duct):
        e = RoundElbow(duct=round_duct, angle=90, metal=metal)
        assert e.radius == pytest.approx(1.5 * round_duct.diameter)

    def test_surface_area_positive(self, metal, round_duct):
        e = RoundElbow(duct=round_duct, angle=90, metal=metal)
        assert e.surface_area() > 0


class TestRectangularTransition:
    def test_surface_area(self, metal):
        inlet = RectangularDuct(400, 300)
        outlet = RectangularDuct(200, 150)
        t = RectangularTransition(inlet=inlet, outlet=outlet, length=300, metal=metal)
        assert t.surface_area() > 0

    def test_flat_panel_count(self, metal):
        t = RectangularTransition(
            inlet=RectangularDuct(400, 300),
            outlet=RectangularDuct(200, 150),
            length=300,
            metal=metal,
        )
        assert t.flat_panel_count() == 4


class TestRectangularTee:
    def test_flat_panel_count(self, metal, rect_duct):
        tee = RectangularTee(
            main=rect_duct,
            branch=RectangularDuct(200, 200),
            length=600,
            metal=metal,
        )
        assert tee.flat_panel_count() == 6


class TestEndCap:
    def test_surface_area_rect(self, metal, rect_duct):
        cap = EndCap(duct=rect_duct, metal=metal)
        expected = rect_duct.external_width * rect_duct.external_height
        assert cap.surface_area() == pytest.approx(expected)

    def test_surface_area_round(self, metal, round_duct):
        cap = EndCap(duct=round_duct, metal=metal)
        expected = math.pi * (round_duct.external_diameter / 2.0) ** 2
        assert cap.surface_area() == pytest.approx(expected)
