"""Tests for geometry calculation module."""
import math
import pytest

from geometric_engine.geometry import (
    compute_geometry,
    compute_surface_area,
    compute_weight,
    weight_per_sq_in,
)
from geometric_engine.models import FittingParameters, FittingType, PressureClass
from geometric_engine.smacna import apply_defaults


def _make(ft: str, width: float, height: float, **kw) -> FittingParameters:
    p = FittingParameters(fitting_type=FittingType(ft), width=width, height=height, **kw)
    apply_defaults(p)
    return p


class TestStraightGeometry:
    def test_surface_area(self):
        p = _make("straight", 24, 12, length=60)
        g = compute_geometry(p)
        perimeter = 2 * (24 + 12)
        assert g["surface_area_sq_in"] == pytest.approx(perimeter * 60, rel=1e-4)

    def test_required_keys(self):
        p = _make("straight", 24, 12)
        g = compute_geometry(p)
        assert "cross_section" in g
        assert "length" in g
        assert "surface_area_sq_in" in g

    def test_default_length_used(self):
        p = _make("straight", 24, 12)
        g = compute_geometry(p)
        assert g["length"] == 56.0


class TestElbowGeometry:
    def test_90_radius(self):
        p = _make("elbow_90", 24, 12)
        g = compute_geometry(p)
        assert g["centerline_radius"] == pytest.approx(24 * 1.5, rel=1e-4)

    def test_45_angle(self):
        p = _make("elbow_45", 12, 8)
        g = compute_geometry(p)
        assert g["angle_deg"] == 45.0

    def test_surface_area_positive(self):
        p = _make("elbow_90", 24, 12)
        g = compute_geometry(p)
        assert g["surface_area_sq_in"] > 0

    def test_throat_less_than_heel(self):
        p = _make("elbow_90", 24, 12)
        g = compute_geometry(p)
        assert g["throat_radius"] < g["heel_radius"]


class TestTransitionGeometry:
    def test_keys_present(self):
        p = _make("transition", 24, 12, neck_out=12.0, length=30.0)
        g = compute_geometry(p)
        assert "inlet" in g
        assert "outlet" in g

    def test_surface_area_positive(self):
        p = _make("transition", 24, 12, neck_out=12.0, length=30.0)
        g = compute_geometry(p)
        assert g["surface_area_sq_in"] > 0


class TestReducerGeometry:
    def test_outlet_smaller_than_inlet(self):
        p = _make("reducer", 24, 12, neck_out=12.0, length=20.0)
        g = compute_geometry(p)
        assert g["outlet"]["width"] < g["inlet"]["width"]


class TestSquareToRoundGeometry:
    def test_outlet_has_diameter(self):
        p = _make("square_to_round", 24, 12)
        g = compute_geometry(p)
        assert "diameter" in g["outlet"]


class TestOffsetZGeometry:
    def test_offset_present(self):
        p = _make("offset_z", 12, 8)
        g = compute_geometry(p)
        assert "offset" in g


class TestTeeGeometry:
    def test_main_and_branch_present(self):
        p = _make("tee", 24, 12)
        g = compute_geometry(p)
        assert "main" in g
        assert "branch" in g


class TestComputeWeight:
    def test_weight_positive(self):
        p = _make("straight", 24, 12)
        g = compute_geometry(p)
        sa = compute_surface_area(g)
        w = compute_weight(sa, 24)
        assert w > 0

    def test_thicker_gauge_heavier(self):
        p = _make("straight", 24, 12)
        g = compute_geometry(p)
        sa = compute_surface_area(g)
        w_thick = compute_weight(sa, 18)
        w_thin = compute_weight(sa, 26)
        assert w_thick > w_thin


class TestUnsupportedFitting:
    def test_raises_for_unknown_type(self):
        p = FittingParameters(fitting_type=FittingType.STRAIGHT, width=10, height=8)
        # Manually corrupt the type to force the error path
        p.fitting_type = "nonexistent"  # type: ignore[assignment]
        with pytest.raises((ValueError, KeyError)):
            compute_geometry(p)
