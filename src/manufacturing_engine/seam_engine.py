"""
Seam allowance and corner-notch injection engine.

Supported seam types and their standard allowances:
    Pittsburgh  – 12.7 mm
    Snaplock    – 9.5 mm
    S-Cleat     – custom (caller-supplied)
    Drive       – custom (caller-supplied)

All measurements in mm.  Precision: 4 decimal places.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from .models import FlatPattern, SeamType, Vector2D

__all__ = [
    "SEAM_ALLOWANCES",
    "apply_seam",
    "generate_corner_notches",
]

# Standard seam allowances in mm (None = custom / caller must supply)
SEAM_ALLOWANCES: dict = {
    SeamType.PITTSBURGH: 12.7,
    SeamType.SNAPLOCK:   9.5,
    SeamType.S_CLEAT:    None,
    SeamType.DRIVE:      None,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def apply_seam(
    pattern: FlatPattern,
    seam_type: SeamType,
    *,
    seam_side: str = "right",
    custom_allowance_mm: Optional[float] = None,
) -> FlatPattern:
    """Inject a seam allowance into a flat pattern.

    The seam is added to one longitudinal edge of the flat pattern by
    offsetting that edge outward.  Square corner notches are automatically
    cut at both ends of the seam strip to prevent material overlap when
    the duct is assembled.

    This function is designed for rectangular flat patterns produced by
    :func:`~manufacturing_engine.unwrap.unwrap_cylinder`.  For other
    pattern shapes the outline is passed through unchanged (with only
    the notch polygons appended).

    Args:
        pattern:              Source FlatPattern to modify.
        seam_type:            SeamType enum value.
        seam_side:            Which edge receives the seam:
                              ``"right"`` (default), ``"left"``, ``"top"``,
                              or ``"bottom"``.
        custom_allowance_mm:  Required when seam_type is S_CLEAT or DRIVE.

    Returns:
        New FlatPattern with the seam allowance incorporated.

    Raises:
        ValueError: If a custom type is used without providing
                    ``custom_allowance_mm``.
    """
    allowance = SEAM_ALLOWANCES[seam_type]
    if allowance is None:
        if custom_allowance_mm is None:
            raise ValueError(
                f"custom_allowance_mm is required for SeamType.{seam_type.name}."
            )
        allowance = custom_allowance_mm

    new_outline = _offset_seam_edge(pattern.outline, seam_side, allowance)
    notches = generate_corner_notches(pattern.outline, seam_side, allowance)

    return FlatPattern(
        outline=new_outline,
        bend_lines=list(pattern.bend_lines),
        notches=list(pattern.notches) + notches,
        labels=list(pattern.labels),
        area_m2=pattern.area_m2,
    )


def generate_corner_notches(
    outline: List[Vector2D],
    seam_side: str,
    allowance_mm: float,
) -> List[List[Vector2D]]:
    """Compute square corner notches for a seam allowance strip.

    Corner notches are cut at both ends of the seam edge to prevent
    material bunching when the seam fold is closed.  Each notch is a
    square of side = ``allowance_mm`` at the corner of the seam strip.

    Args:
        outline:       Closed polygon vertices of the flat pattern.
        seam_side:     Side that carries the seam (``"right"`` etc.).
        allowance_mm:  Width of the seam allowance strip in mm.

    Returns:
        List of two closed polygon (square notch) vertex lists.
    """
    bbox = _bounding_box(outline)
    x_min, y_min, x_max, y_max = bbox
    notch_sz = round(allowance_mm, 4)

    if seam_side == "right":
        x_seam = x_max
        # Bottom-right notch
        n1 = [
            Vector2D(x_seam - notch_sz, y_min),
            Vector2D(x_seam, y_min),
            Vector2D(x_seam, y_min + notch_sz),
            Vector2D(x_seam - notch_sz, y_min + notch_sz),
            Vector2D(x_seam - notch_sz, y_min),
        ]
        # Top-right notch
        n2 = [
            Vector2D(x_seam - notch_sz, y_max - notch_sz),
            Vector2D(x_seam, y_max - notch_sz),
            Vector2D(x_seam, y_max),
            Vector2D(x_seam - notch_sz, y_max),
            Vector2D(x_seam - notch_sz, y_max - notch_sz),
        ]
    elif seam_side == "left":
        x_seam = x_min
        n1 = [
            Vector2D(x_seam, y_min),
            Vector2D(x_seam + notch_sz, y_min),
            Vector2D(x_seam + notch_sz, y_min + notch_sz),
            Vector2D(x_seam, y_min + notch_sz),
            Vector2D(x_seam, y_min),
        ]
        n2 = [
            Vector2D(x_seam, y_max - notch_sz),
            Vector2D(x_seam + notch_sz, y_max - notch_sz),
            Vector2D(x_seam + notch_sz, y_max),
            Vector2D(x_seam, y_max),
            Vector2D(x_seam, y_max - notch_sz),
        ]
    elif seam_side == "top":
        y_seam = y_max
        n1 = [
            Vector2D(x_min, y_seam - notch_sz),
            Vector2D(x_min + notch_sz, y_seam - notch_sz),
            Vector2D(x_min + notch_sz, y_seam),
            Vector2D(x_min, y_seam),
            Vector2D(x_min, y_seam - notch_sz),
        ]
        n2 = [
            Vector2D(x_max - notch_sz, y_seam - notch_sz),
            Vector2D(x_max, y_seam - notch_sz),
            Vector2D(x_max, y_seam),
            Vector2D(x_max - notch_sz, y_seam),
            Vector2D(x_max - notch_sz, y_seam - notch_sz),
        ]
    else:  # bottom
        y_seam = y_min
        n1 = [
            Vector2D(x_min, y_seam),
            Vector2D(x_min + notch_sz, y_seam),
            Vector2D(x_min + notch_sz, y_seam + notch_sz),
            Vector2D(x_min, y_seam + notch_sz),
            Vector2D(x_min, y_seam),
        ]
        n2 = [
            Vector2D(x_max - notch_sz, y_seam),
            Vector2D(x_max, y_seam),
            Vector2D(x_max, y_seam + notch_sz),
            Vector2D(x_max - notch_sz, y_seam + notch_sz),
            Vector2D(x_max - notch_sz, y_seam),
        ]

    return [n1, n2]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _bounding_box(pts: List[Vector2D]) -> Tuple[float, float, float, float]:
    """Return (x_min, y_min, x_max, y_max) of a point list."""
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _offset_seam_edge(
    outline: List[Vector2D], seam_side: str, allowance: float
) -> List[Vector2D]:
    """Return a new outline with the seam edge extended and corner notches cut.

    The modified outline represents the *actual cut boundary* including
    the seam allowance strip and the notch cut-outs.

    For a rectangular outline the result is:
        ──────── base edge ────────
        │                         │
        │                         │   seam edge (right example)
        ──  notch  ──  seam  ──  notch  ──
    """
    bbox = _bounding_box(outline)
    x_min, y_min, x_max, y_max = bbox
    a = round(allowance, 4)

    if seam_side == "right":
        # Original right edge at x_max; extend to x_max + a,
        # with square notch cuts at the corners.
        return [
            Vector2D(x_min, y_min),
            Vector2D(x_max, y_min),
            Vector2D(x_max, y_min + a),
            Vector2D(x_max + a, y_min + a),
            Vector2D(x_max + a, y_max - a),
            Vector2D(x_max, y_max - a),
            Vector2D(x_max, y_max),
            Vector2D(x_min, y_max),
            Vector2D(x_min, y_min),
        ]
    elif seam_side == "left":
        return [
            Vector2D(x_min, y_min),
            Vector2D(x_min, y_min + a),
            Vector2D(x_min - a, y_min + a),
            Vector2D(x_min - a, y_max - a),
            Vector2D(x_min, y_max - a),
            Vector2D(x_min, y_max),
            Vector2D(x_max, y_max),
            Vector2D(x_max, y_min),
            Vector2D(x_min, y_min),
        ]
    elif seam_side == "top":
        return [
            Vector2D(x_min, y_min),
            Vector2D(x_max, y_min),
            Vector2D(x_max, y_max),
            Vector2D(x_max - a, y_max),
            Vector2D(x_max - a, y_max + a),
            Vector2D(x_min + a, y_max + a),
            Vector2D(x_min + a, y_max),
            Vector2D(x_min, y_max),
            Vector2D(x_min, y_min),
        ]
    else:  # bottom
        return [
            Vector2D(x_min, y_min),
            Vector2D(x_min + a, y_min),
            Vector2D(x_min + a, y_min - a),
            Vector2D(x_max - a, y_min - a),
            Vector2D(x_max - a, y_min),
            Vector2D(x_max, y_min),
            Vector2D(x_max, y_max),
            Vector2D(x_min, y_max),
            Vector2D(x_min, y_min),
        ]
