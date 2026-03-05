"""
Geometric calculation module.

Each fitting type returns a ``geometry`` dict that is compatible with the
``geometry_core`` downstream pipeline (spec: ``geometry_core_compatible``).

All calculations use **inches**.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from geometric_engine.models import (
    FittingParameters,
    FittingType,
    TRANSITIONS_DEFAULT_ALIGNMENT,
)
from geometric_engine.smacna import elbow_radius


# ---------------------------------------------------------------------------
# Weight estimation (galvanized steel)
# ---------------------------------------------------------------------------
# Approximate weight per square inch for common gauges (lb/in²).
# Source: standard sheet-steel density 0.2836 lb/in³, gauge thicknesses per
#         SMACNA Table 1-11.
_GAUGE_THICKNESS_IN: Dict[int, float] = {
    26: 0.0187,
    24: 0.0239,
    22: 0.0299,
    20: 0.0359,
    18: 0.0478,
    16: 0.0598,
    14: 0.0747,
}
_STEEL_DENSITY_LB_PER_IN3: float = 0.2836


def weight_per_sq_in(gauge: int) -> float:
    """Return material weight (lb) per square inch for *gauge*."""
    thickness = _GAUGE_THICKNESS_IN.get(gauge, 0.0299)  # default 22 ga
    return thickness * _STEEL_DENSITY_LB_PER_IN3


# ---------------------------------------------------------------------------
# Per-fitting geometry builders
# ---------------------------------------------------------------------------


def _geometry_straight(p: FittingParameters) -> Dict[str, Any]:
    length = p.length or 0.0
    perimeter = 2.0 * (p.width + p.height)
    surface_area = perimeter * length
    return {
        "type": "straight",
        "cross_section": {"width": p.width, "height": p.height},
        "length": length,
        "perimeter": round(perimeter, 4),
        "surface_area_sq_in": round(surface_area, 4),
    }


def _geometry_elbow(p: FittingParameters) -> Dict[str, Any]:
    angle_deg = p.angle or (90.0 if p.fitting_type == FittingType.ELBOW_90 else 45.0)
    radius = elbow_radius(p.width)
    arc_length = math.pi * radius * angle_deg / 180.0
    perimeter = 2.0 * (p.width + p.height)
    # Approximate surface area as the arc of the outer face + cheeks
    throat_radius = radius - p.width / 2.0
    heel_radius = radius + p.width / 2.0
    outer_arc = math.pi * heel_radius * angle_deg / 180.0
    inner_arc = math.pi * throat_radius * angle_deg / 180.0
    cheek_area = 2.0 * (math.pi * (heel_radius ** 2 - throat_radius ** 2) * angle_deg / 360.0)
    face_area = p.height * (outer_arc + inner_arc)
    surface_area = face_area + cheek_area
    return {
        "type": p.fitting_type.value,
        "cross_section": {"width": p.width, "height": p.height},
        "angle_deg": angle_deg,
        "centerline_radius": round(radius, 4),
        "throat_radius": round(throat_radius, 4),
        "heel_radius": round(heel_radius, 4),
        "arc_length_centerline": round(arc_length, 4),
        "turning_vanes": p.turning_vanes,
        "surface_area_sq_in": round(surface_area, 4),
    }


def _geometry_transition(p: FittingParameters) -> Dict[str, Any]:
    length = p.length or 0.0
    w_out = p.neck_out if p.neck_out is not None else p.width
    h_out = p.height  # height unchanged for a simple flat transition
    alignment = TRANSITIONS_DEFAULT_ALIGNMENT
    # Trapezoidal surface areas for each of the four faces
    top_bottom_area = 2.0 * 0.5 * (p.width + w_out) * length
    left_right_area = 2.0 * p.height * length
    surface_area = top_bottom_area + left_right_area
    return {
        "type": "transition",
        "inlet": {"width": p.width, "height": p.height},
        "outlet": {"width": w_out, "height": h_out},
        "length": length,
        "alignment": alignment,
        "surface_area_sq_in": round(surface_area, 4),
    }


def _geometry_reducer(p: FittingParameters) -> Dict[str, Any]:
    length = p.length or 0.0
    w_out = p.neck_out if p.neck_out is not None else p.width * 0.5
    h_out = p.height * 0.5 if p.neck_out is None else p.height
    top_bottom_area = 2.0 * 0.5 * (p.width + w_out) * length
    left_right_area = 2.0 * 0.5 * (p.height + h_out) * length
    surface_area = top_bottom_area + left_right_area
    return {
        "type": "reducer",
        "inlet": {"width": p.width, "height": p.height},
        "outlet": {"width": w_out, "height": h_out},
        "length": length,
        "surface_area_sq_in": round(surface_area, 4),
    }


def _geometry_square_to_round(p: FittingParameters) -> Dict[str, Any]:
    length = p.length or 0.0
    diameter_out = p.neck_out if p.neck_out is not None else min(p.width, p.height)
    # Lateral surface approximated as frustum
    r_out = diameter_out / 2.0
    square_perimeter = 2.0 * (p.width + p.height)
    round_perimeter = math.pi * diameter_out
    surface_area = 0.5 * (square_perimeter + round_perimeter) * length
    return {
        "type": "square_to_round",
        "inlet": {"width": p.width, "height": p.height},
        "outlet": {"diameter": diameter_out, "radius": round(r_out, 4)},
        "length": length,
        "surface_area_sq_in": round(surface_area, 4),
    }


def _geometry_offset_z(p: FittingParameters) -> Dict[str, Any]:
    length = p.length or 0.0
    offset = p.neck_out if p.neck_out is not None else p.width
    perimeter = 2.0 * (p.width + p.height)
    surface_area = perimeter * length
    return {
        "type": "offset_z",
        "cross_section": {"width": p.width, "height": p.height},
        "length": length,
        "offset": offset,
        "surface_area_sq_in": round(surface_area, 4),
    }


def _geometry_tee(p: FittingParameters) -> Dict[str, Any]:
    main_length = p.length or 0.0
    branch_width = p.neck_out if p.neck_out is not None else p.width * 0.5
    branch_height = p.height
    perimeter_main = 2.0 * (p.width + p.height)
    perimeter_branch = 2.0 * (branch_width + branch_height)
    surface_area = perimeter_main * main_length + perimeter_branch * main_length * 0.5
    return {
        "type": "tee",
        "main": {"width": p.width, "height": p.height, "length": main_length},
        "branch": {"width": branch_width, "height": branch_height},
        "surface_area_sq_in": round(surface_area, 4),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_GEOMETRY_BUILDERS = {
    FittingType.STRAIGHT: _geometry_straight,
    FittingType.ELBOW_90: _geometry_elbow,
    FittingType.ELBOW_45: _geometry_elbow,
    FittingType.TRANSITION: _geometry_transition,
    FittingType.REDUCER: _geometry_reducer,
    FittingType.SQUARE_TO_ROUND: _geometry_square_to_round,
    FittingType.OFFSET_Z: _geometry_offset_z,
    FittingType.TEE: _geometry_tee,
}


def compute_geometry(params: FittingParameters) -> Dict[str, Any]:
    """
    Compute the geometry dict for *params*.

    Returns a ``geometry_core_compatible`` dict containing all dimensional
    data and the surface area in square inches.
    """
    builder = _GEOMETRY_BUILDERS.get(params.fitting_type)
    if builder is None:
        raise ValueError(f"Unsupported fitting type: {params.fitting_type}")
    return builder(params)


def compute_surface_area(geometry: Dict[str, Any]) -> float:
    """Extract the surface area (sq-in) from a geometry dict."""
    return float(geometry.get("surface_area_sq_in", 0.0))


def compute_weight(surface_area_sq_in: float, gauge: int) -> float:
    """Return estimated material weight in pounds."""
    return round(surface_area_sq_in * weight_per_sq_in(gauge), 4)
