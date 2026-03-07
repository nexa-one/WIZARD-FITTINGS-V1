"""Tests for core geometric primitives."""

import math
import pytest
from geometric_engine.core.primitives import Point2D, Point3D, Vector2D, Vector3D


class TestPoint2D:
    def test_distance(self):
        p1, p2 = Point2D(0, 0), Point2D(3, 4)
        assert math.isclose(p1.distance_to(p2), 5.0)

    def test_midpoint(self):
        p1, p2 = Point2D(0, 0), Point2D(4, 6)
        mid = p1.midpoint(p2)
        assert mid.x == 2.0 and mid.y == 3.0

    def test_translate(self):
        p = Point2D(1, 2).translate(3, -1)
        assert p.x == 4.0 and p.y == 1.0

    def test_add_vector(self):
        p = Point2D(1, 2) + Vector2D(3, 4)
        assert p.x == 4 and p.y == 6

    def test_sub_point_gives_vector(self):
        v = Point2D(4, 5) - Point2D(1, 2)
        assert isinstance(v, Vector2D)
        assert v.x == 3 and v.y == 3


class TestPoint3D:
    def test_distance(self):
        p1, p2 = Point3D(0, 0, 0), Point3D(1, 1, 1)
        assert math.isclose(p1.distance_to(p2), math.sqrt(3))

    def test_midpoint(self):
        m = Point3D(0, 0, 0).midpoint(Point3D(2, 4, 6))
        assert m.x == 1 and m.y == 2 and m.z == 3

    def test_translate(self):
        p = Point3D(1, 2, 3).translate(1, 1, 1)
        assert p.x == 2 and p.y == 3 and p.z == 4

    def test_cross_via_sub(self):
        v = Point3D(3, 3, 3) - Point3D(1, 1, 1)
        assert isinstance(v, Vector3D)
        assert v.x == 2 and v.y == 2 and v.z == 2


class TestVector2D:
    def test_magnitude(self):
        assert math.isclose(Vector2D(3, 4).magnitude, 5.0)

    def test_normalize(self):
        v = Vector2D(3, 4).normalize()
        assert math.isclose(v.magnitude, 1.0)

    def test_normalize_zero_raises(self):
        with pytest.raises(ValueError):
            Vector2D(0, 0).normalize()

    def test_dot(self):
        assert Vector2D(1, 0).dot(Vector2D(0, 1)) == 0.0
        assert Vector2D(2, 0).dot(Vector2D(3, 0)) == 6.0

    def test_rotate_90(self):
        v = Vector2D(1, 0).rotate(math.pi / 2)
        assert math.isclose(v.x, 0.0, abs_tol=1e-9)
        assert math.isclose(v.y, 1.0, abs_tol=1e-9)

    def test_add_sub_mul(self):
        a, b = Vector2D(1, 2), Vector2D(3, 4)
        assert (a + b) == Vector2D(4, 6)
        assert (b - a) == Vector2D(2, 2)
        assert (a * 3) == Vector2D(3, 6)


class TestVector3D:
    def test_magnitude(self):
        assert math.isclose(Vector3D(1, 1, 1).magnitude, math.sqrt(3))

    def test_cross_product(self):
        v = Vector3D(1, 0, 0).cross(Vector3D(0, 1, 0))
        assert math.isclose(v.x, 0) and math.isclose(v.y, 0) and math.isclose(v.z, 1)

    def test_angle_to(self):
        angle = Vector3D(1, 0, 0).angle_to(Vector3D(0, 1, 0))
        assert math.isclose(angle, math.pi / 2)

    def test_normalize_zero_raises(self):
        with pytest.raises(ValueError):
            Vector3D(0, 0, 0).normalize()