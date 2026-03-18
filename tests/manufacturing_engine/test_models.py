"""
Unit tests – data models (models.py)

Covers Vector2D/3D arithmetic, BOMItem.to_dict, and
geometry helpers in unwrap.py that aren't exercised by
the fitting-specific tests.
"""

import math
import pytest

from manufacturing_engine.models import BOMItem, Vector2D, Vector3D
from manufacturing_engine.unwrap import (
    _polygon_area_2d,
    _trilaterate_2d,
    unwrap_fitting,
)
from manufacturing_engine.models import (
    FittingParameters,
    FittingType,
    Material,
    SeamType,
)


# ---------------------------------------------------------------------------
# Vector2D
# ---------------------------------------------------------------------------


class TestVector2D:
    def test_add(self):
        v = Vector2D(1.0, 2.0) + Vector2D(3.0, 4.0)
        assert v == Vector2D(4.0, 6.0)

    def test_sub(self):
        v = Vector2D(5.0, 3.0) - Vector2D(2.0, 1.0)
        assert v == Vector2D(3.0, 2.0)

    def test_mul(self):
        v = Vector2D(2.0, 3.0) * 2.0
        assert v == Vector2D(4.0, 6.0)

    def test_length(self):
        v = Vector2D(3.0, 4.0)
        assert math.isclose(v.length(), 5.0, rel_tol=1e-6)

    def test_distance_to(self):
        a = Vector2D(0.0, 0.0)
        b = Vector2D(3.0, 4.0)
        assert math.isclose(a.distance_to(b), 5.0, rel_tol=1e-6)

    def test_eq_non_vector(self):
        v = Vector2D(1.0, 2.0)
        assert v.__eq__("not a vector") is NotImplemented

    def test_repr(self):
        r = repr(Vector2D(1.5, 2.75))
        assert "1.5000" in r and "2.7500" in r


# ---------------------------------------------------------------------------
# Vector3D
# ---------------------------------------------------------------------------


class TestVector3D:
    def test_add(self):
        v = Vector3D(1, 2, 3) + Vector3D(4, 5, 6)
        assert v == Vector3D(5, 7, 9)

    def test_sub(self):
        v = Vector3D(5, 7, 9) - Vector3D(1, 2, 3)
        assert v == Vector3D(4, 5, 6)

    def test_mul(self):
        v = Vector3D(1, 2, 3) * 3.0
        assert v == Vector3D(3, 6, 9)

    def test_length(self):
        v = Vector3D(1, 0, 0)
        assert math.isclose(v.length(), 1.0, rel_tol=1e-6)

    def test_distance_to(self):
        a = Vector3D(0, 0, 0)
        b = Vector3D(1, 2, 2)
        assert math.isclose(a.distance_to(b), 3.0, rel_tol=1e-6)

    def test_normalize_unit_vector(self):
        v = Vector3D(3.0, 0.0, 0.0).normalize()
        assert math.isclose(v.x, 1.0, rel_tol=1e-6)
        assert math.isclose(v.y, 0.0, abs_tol=1e-9)

    def test_normalize_zero_vector(self):
        v = Vector3D(0.0, 0.0, 0.0).normalize()
        assert v == Vector3D(0.0, 0.0, 0.0)

    def test_dot(self):
        a = Vector3D(1, 0, 0)
        b = Vector3D(0, 1, 0)
        assert a.dot(b) == 0.0
        assert a.dot(a) == 1.0

    def test_cross(self):
        i = Vector3D(1, 0, 0)
        j = Vector3D(0, 1, 0)
        k = i.cross(j)
        assert math.isclose(k.x, 0.0, abs_tol=1e-9)
        assert math.isclose(k.y, 0.0, abs_tol=1e-9)
        assert math.isclose(k.z, 1.0, rel_tol=1e-6)

    def test_repr(self):
        r = repr(Vector3D(1.0, 2.5, 3.75))
        assert "1.0000" in r and "2.5000" in r and "3.7500" in r


# ---------------------------------------------------------------------------
# _polygon_area_2d (shoelace formula)
# ---------------------------------------------------------------------------


class TestPolygonArea2D:
    def test_unit_square(self):
        pts = [Vector2D(0, 0), Vector2D(1, 0), Vector2D(1, 1), Vector2D(0, 1)]
        assert math.isclose(abs(_polygon_area_2d(pts)), 1.0, rel_tol=1e-6)

    def test_rectangle(self):
        pts = [
            Vector2D(0, 0), Vector2D(10, 0),
            Vector2D(10, 5), Vector2D(0, 5),
        ]
        assert math.isclose(abs(_polygon_area_2d(pts)), 50.0, rel_tol=1e-6)

    def test_winding_determines_sign(self):
        cw = [Vector2D(0, 0), Vector2D(0, 1), Vector2D(1, 1), Vector2D(1, 0)]
        ccw = list(reversed(cw))
        assert _polygon_area_2d(cw) * _polygon_area_2d(ccw) < 0


# ---------------------------------------------------------------------------
# _trilaterate_2d degenerate case
# ---------------------------------------------------------------------------


class TestTrilaterate2D:
    def test_degenerate_zero_base(self):
        """When both reference points coincide, apex is placed above p1."""
        gx, gy = _trilaterate_2d(5.0, 5.0, 5.0, 5.0, 3.0, 3.0)
        assert math.isclose(gx, 5.0, abs_tol=1e-6)
        assert math.isclose(gy, 8.0, abs_tol=1e-6)

    def test_normal_case_equilateral(self):
        """Equilateral triangle: apex at (0.5, sqrt(3)/2) from base (0,0)–(1,0)."""
        gx, gy = _trilaterate_2d(0.0, 0.0, 1.0, 0.0, 1.0, 1.0)
        assert math.isclose(gx, 0.5, abs_tol=1e-4)
        assert math.isclose(gy, math.sqrt(3) / 2.0, abs_tol=1e-4)


# ---------------------------------------------------------------------------
# unwrap_fitting ValueError for unknown type
# ---------------------------------------------------------------------------


class TestUnwrapFittingErrors:
    def test_invalid_fitting_type_raises(self):
        """unwrap_fitting must raise ValueError for unsupported types.

        FittingType is an enum so we cannot create an invalid value directly.
        We patch the attribute to simulate a future enum extension that has no
        handler registered in the dispatcher.
        """
        params = FittingParameters(
            fitting_type=FittingType.CYLINDER,   # will be patched below
            material=Material.GALVANIZED_STEEL,
            thickness_mm=0.8,
            seam_type=SeamType.PITTSBURGH,
            item_id="ERR",
            system_name="SYS",
        )
        import unittest.mock as mock
        with mock.patch.object(params, "fitting_type", new="UNSUPPORTED"):
            with pytest.raises(ValueError, match="Unsupported fitting type"):
                unwrap_fitting(params)
