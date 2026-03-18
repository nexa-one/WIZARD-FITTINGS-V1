"""
Data models for the HVAC Manufacturing Engine.

All measurements are in millimetres unless otherwise noted.
Precision target: 4 decimal places for geometric quantities.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class FittingType(Enum):
    """Supported HVAC duct fitting types."""

    CYLINDER = "cylinder"
    CONE = "cone"
    ELBOW = "elbow"
    OFFSET = "offset"
    TRANSITION = "transition"         # alias kept for backward compat
    SQUARE_TO_ROUND = "square_to_round"


class Material(Enum):
    """Sheet metal materials with associated densities."""

    GALVANIZED_STEEL = "galvanized_steel"
    STAINLESS_STEEL = "stainless_steel"


class SeamType(Enum):
    """Seam joint types used in HVAC duct fabrication."""

    PITTSBURGH = "pittsburgh"
    SNAPLOCK = "snaplock"
    S_CLEAT = "s_cleat"
    DRIVE = "drive"


# ---------------------------------------------------------------------------
# Geometry primitives
# ---------------------------------------------------------------------------


@dataclass
class Vector2D:
    """2-D point / vector (x, y) in mm."""

    x: float
    y: float

    def __add__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2D") -> "Vector2D":
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2D":
        return Vector2D(self.x * scalar, self.y * scalar)

    def length(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def distance_to(self, other: "Vector2D") -> float:
        return (self - other).length()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2D):
            return NotImplemented
        return math.isclose(self.x, other.x, abs_tol=1e-4) and math.isclose(
            self.y, other.y, abs_tol=1e-4
        )

    def __repr__(self) -> str:
        return f"Vector2D({self.x:.4f}, {self.y:.4f})"


@dataclass
class Vector3D:
    """3-D point / vector (x, y, z) in mm."""

    x: float
    y: float
    z: float

    def __add__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vector3D":
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def length(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def distance_to(self, other: "Vector3D") -> float:
        return (self - other).length()

    def normalize(self) -> "Vector3D":
        lng = self.length()
        if lng < 1e-12:
            return Vector3D(0.0, 0.0, 0.0)
        return Vector3D(self.x / lng, self.y / lng, self.z / lng)

    def dot(self, other: "Vector3D") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def __repr__(self) -> str:
        return f"Vector3D({self.x:.4f}, {self.y:.4f}, {self.z:.4f})"


# ---------------------------------------------------------------------------
# Flat pattern
# ---------------------------------------------------------------------------


@dataclass
class FlatPattern:
    """2-D flat pattern produced by the surface-unwrapping engine.

    Attributes:
        outline:    Closed polyline (first == last) representing the outer cut
                    boundary in the CUT_OUTLINE DXF layer.
        bend_lines: List of (start, end) segments for the BEND_LINES layer.
        notches:    List of closed polygons (triangular or square corner cuts)
                    for the NOTCHES layer.
        labels:     List of (position, text) tuples for the MARKING_TEXT layer.
        area_m2:    Developed surface area in square metres (4 d.p.).
    """

    outline: List[Vector2D]
    bend_lines: List[Tuple[Vector2D, Vector2D]] = field(default_factory=list)
    notches: List[List[Vector2D]] = field(default_factory=list)
    labels: List[Tuple[Vector2D, str]] = field(default_factory=list)
    area_m2: float = 0.0


# ---------------------------------------------------------------------------
# Fitting parameters
# ---------------------------------------------------------------------------


@dataclass
class FittingParameters:
    """Complete parameter set describing an HVAC fitting.

    All linear dimensions in mm, all angles in degrees.
    """

    fitting_type: FittingType
    material: Material
    thickness_mm: float
    seam_type: SeamType
    item_id: str
    system_name: str
    quantity: int = 1

    # --- Cylinder / cone / elbow ---
    diameter_mm: float = 0.0
    length_mm: float = 0.0

    # --- Cone ---
    top_diameter_mm: float = 0.0

    # --- Elbow / offset ---
    elbow_angle_deg: float = 90.0
    radius_mm: float = 0.0     # elbow centreline radius
    num_pieces: int = 5        # total gore segments (incl. end halves)

    # --- Square-to-round / transition ---
    rect_width_mm: float = 0.0
    rect_height_mm: float = 0.0
    round_diameter_mm: float = 0.0
    offset_x_mm: float = 0.0   # offset of circle centre from rect centre
    offset_y_mm: float = 0.0


# ---------------------------------------------------------------------------
# Bill of Materials
# ---------------------------------------------------------------------------


@dataclass
class BOMItem:
    """Single row in a Bill of Materials report.

    Fields match the export specification:
    ID, System, Material, Thickness, Area_m2, Weight_kg, Quantity.
    """

    item_id: str
    system: str
    material: str
    thickness_mm: float
    area_m2: float
    weight_kg: float
    quantity: int

    def to_dict(self) -> dict:
        return {
            "ID": self.item_id,
            "System": self.system,
            "Material": self.material,
            "Thickness": self.thickness_mm,
            "Area_m2": self.area_m2,
            "Weight_kg": self.weight_kg,
            "Quantity": self.quantity,
        }
