"""
Core geometric primitives for the WIZARD-FITTINGS geometric engine.

Provides 2-D and 3-D point and vector types used throughout the engine to
describe fitting geometry, centroids, normals, and directional quantities.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Point2D:
    """A point in a 2-D Cartesian plane (e.g. a duct cross-section)."""

    x: float
    y: float

    def distance_to(self, other: "Point2D") -> float:
        """Return the Euclidean distance to *other*."""
        return math.hypot(self.x - other.x, self.y - other.y)

    def midpoint(self, other: "Point2D") -> "Point2D":
        """Return the midpoint between *self* and *other*."""
        return Point2D((self.x + other.x) / 2, (self.y + other.y) / 2)

    def translate(self, dx: float, dy: float) -> "Point2D":
        """Return a new point translated by (*dx*, *dy*)."""
        return Point2D(self.x + dx, self.y + dy)

    def __add__(self, vector: "Vector2D") -> "Point2D":
        return Point2D(self.x + vector.x, self.y + vector.y)

    def __sub__(self, other: "Point2D") -> "Vector2D":
        return Vector2D(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        return f"Point2D(x={self.x}, y={self.y})"


@dataclass
class Point3D:
    """A point in 3-D space (e.g. a fitting origin or end-point)."""

    x: float
    y: float
    z: float

    def distance_to(self, other: "Point3D") -> float:
        """Return the Euclidean distance to *other*."""
        return math.sqrt(
            (self.x - other.x) ** 2
            + (self.y - other.y) ** 2
            + (self.z - other.z) ** 2
        )

    def midpoint(self, other: "Point3D") -> "Point3D":
        """Return the midpoint between *self* and *other*."""
        return Point3D(
            (self.x + other.x) / 2,
            (self.y + other.y) / 2,
            (self.z + other.z) / 2,
        )

    def translate(self, dx: float, dy: float, dz: float) -> "Point3D":
        """Return a new point translated by (*dx*, *dy*, *dz*)."""
        return Point3D(self.x + dx, self.y + dy, self.z + dz)

    def __add__(self, vector: "Vector3D") -> "Point3D":
        return Point3D(self.x + vector.x, self.y + vector.y, self.z + vector.z)

    def __sub__(self, other: "Point3D") -> "Vector3D":
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __repr__(self) -> str:
        return f"Point3D(x={self.x}, y={self.y}, z={self.z})"


@dataclass
class Vector2D:
    """A 2-D direction/displacement vector."""

    x: float
    y: float

    @property
    def magnitude(self) -> float:
        """Length of the vector."""
        return math.hypot(self.x, self.y)

    def normalize(self) -> "Vector2D":
        """Return a unit vector in the same direction."""
        mag = self.magnitude
        if mag == 0:
            raise ValueError("Cannot normalize a zero-length vector.")
        return Vector2D(self.x / mag, self.y / mag)

    def dot(self, other: "Vector2D") -> float:
        """Dot product with *other*."""
        return self.x * other.x + self.y * other.y

    def angle_to(self, other: "Vector2D") -> float:
        """Angle in radians between *self* and *other*."""
        cos_theta = self.dot(other) / (self.magnitude * other.magnitude)
        cos_theta = max(-1.0, min(1.0, cos_theta))
        return math.acos(cos_theta)

    def rotate(self, angle_rad: float) -> "Vector2D":
        """Return a new vector rotated by *angle_rad* radians (counter-clockwise)."""
        c, s = math.cos(angle_rad), math.sin(angle_rad)
        return Vector2D(c * self.x - s * self.y, s * self.x + c * self.y)

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2D":
        return Vector2D(self.x * scalar, self.y * scalar)

    def __repr__(self) -> str:
        return f"Vector2D(x={self.x}, y={self.y})"


@dataclass
class Vector3D:
    """A 3-D direction/displacement vector."""

    x: float
    y: float
    z: float

    @property
    def magnitude(self) -> float:
        """Length of the vector."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> "Vector3D":
        """Return a unit vector in the same direction."""
        mag = self.magnitude
        if mag == 0:
            raise ValueError("Cannot normalize a zero-length vector.")
        return Vector3D(self.x / mag, self.y / mag, self.z / mag)

    def dot(self, other: "Vector3D") -> float:
        """Dot product with *other*."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vector3D") -> "Vector3D":
        """Cross product with *other*."""
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def angle_to(self, other: "Vector3D") -> float:
        """Angle in radians between *self* and *other*."""
        cos_theta = self.dot(other) / (self.magnitude * other.magnitude)
        cos_theta = max(-1.0, min(1.0, cos_theta))
        return math.acos(cos_theta)

    def __add__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vector3D":
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __repr__(self) -> str:
        return f"Vector3D(x={self.x}, y={self.y}, z={self.z})"
