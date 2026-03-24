"""
Surface unwrapping algorithms for HVAC duct fittings.

Implements analytical flattening for ruled surfaces:
  - Cylinder  → rectangle
  - Cone (frustum) → radial sector
  - Elbow (segmented) → sinusoidal gore strips
  - Square-to-round / Transition → triangulated development

All measurements in mm.  Precision: 4 decimal places.
"""

from __future__ import annotations

import math
from typing import List, Tuple, Union

from .models import (
    FittingParameters,
    FittingType,
    FlatPattern,
    Vector2D,
    Vector3D,
)

# K-factor for bend-allowance calculations.
# A value of 0.44 corresponds to the neutral-axis position for typical
# cold-rolled sheet metal (SMACNA HVAC Duct Construction Standards).
# The neutral axis lies at radius R_neutral = R_inside + K * t from the
# inside face, where K ∈ (0, 1).
K_FACTOR: float = 0.44

# Number of polyline segments used to approximate circular arcs
_ARC_SEGMENTS: int = 64


# ---------------------------------------------------------------------------
# Helper geometry
# ---------------------------------------------------------------------------


def _dist3d(a: Vector3D, b: Vector3D) -> float:
    """Euclidean distance between two 3-D points."""
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def _trilaterate_2d(
    x1: float, y1: float, x2: float, y2: float, d1: float, d2: float
) -> Tuple[float, float]:
    """Compute 2-D apex given two base points and distances.

    Places the apex on the *positive-y* side of the directed baseline
    (x1,y1) → (x2,y2), using the law of cosines.

    Returns:
        (gx, gy) – global 2-D coordinates of the apex.
    """
    base = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    if base < 1e-9:
        return (x1, y1 + d1)

    # Local x of apex along the base
    lx = (d1 ** 2 - d2 ** 2 + base ** 2) / (2.0 * base)
    ly_sq = max(0.0, d1 ** 2 - lx ** 2)
    ly = math.sqrt(ly_sq)

    # Rotate back to global frame
    angle = math.atan2(y2 - y1, x2 - x1)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    gx = x1 + lx * cos_a - ly * sin_a
    gy = y1 + lx * sin_a + ly * cos_a
    return (gx, gy)


def _polygon_area_2d(pts: List[Vector2D]) -> float:
    """Signed area of a 2-D polygon via the shoelace formula."""
    n = len(pts)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += pts[i].x * pts[j].y
        area -= pts[j].x * pts[i].y
    return area / 2.0


# ---------------------------------------------------------------------------
# Bend-allowance / compensation
# ---------------------------------------------------------------------------


def compute_bend_allowance(
    bend_angle_deg: float,
    bend_radius_mm: float,
    thickness_mm: float,
    k_factor: float = K_FACTOR,
) -> float:
    """Return the bend allowance (arc length along the neutral axis).

    Formula:
        BA = angle_rad × (R + K × t)

    Args:
        bend_angle_deg: Included bend angle in degrees.
        bend_radius_mm: Inside bend radius in mm.
        thickness_mm:   Sheet thickness in mm.
        k_factor:       K-factor (default 0.44).

    Returns:
        Bend allowance in mm, rounded to 4 decimal places.
    """
    angle_rad = math.radians(bend_angle_deg)
    return round(angle_rad * (bend_radius_mm + k_factor * thickness_mm), 4)


def compute_bend_deduction(
    bend_angle_deg: float,
    bend_radius_mm: float,
    thickness_mm: float,
    k_factor: float = K_FACTOR,
) -> float:
    """Return the bend deduction (material consumed by the bend).

    Formula:
        OSSB = tan(angle/2) × (R + t)
        BD   = 2 × OSSB − BA

    Args:
        bend_angle_deg: Included bend angle in degrees.
        bend_radius_mm: Inside bend radius in mm.
        thickness_mm:   Sheet thickness in mm.
        k_factor:       K-factor (default 0.44).

    Returns:
        Bend deduction in mm, rounded to 4 decimal places.
    """
    angle_rad = math.radians(bend_angle_deg)
    ossb = math.tan(angle_rad / 2.0) * (bend_radius_mm + thickness_mm)
    ba = compute_bend_allowance(bend_angle_deg, bend_radius_mm, thickness_mm, k_factor)
    return round(2.0 * ossb - ba, 4)


# ---------------------------------------------------------------------------
# Cylinder development
# ---------------------------------------------------------------------------


def unwrap_cylinder(params: FittingParameters) -> FlatPattern:
    """Unroll a right circular cylinder into a flat rectangle.

    Developed dimensions:
        Width  = π × D  (full circumference)
        Height = L      (axial length)

    The seam line is placed at the right edge (x = circumference).

    Args:
        params: FittingParameters with diameter_mm and length_mm set.

    Returns:
        FlatPattern whose outline is a closed rectangle.
    """
    r = params.diameter_mm / 2.0
    circumference = round(2.0 * math.pi * r, 4)
    height = params.length_mm

    outline: List[Vector2D] = [
        Vector2D(0.0, 0.0),
        Vector2D(circumference, 0.0),
        Vector2D(circumference, height),
        Vector2D(0.0, height),
        Vector2D(0.0, 0.0),  # close
    ]

    # Seam line: right-hand edge
    seam_start = Vector2D(circumference, 0.0)
    seam_end = Vector2D(circumference, height)

    # Lateral surface area (m²)
    area_m2 = round(circumference * height / 1_000_000.0, 4)

    return FlatPattern(
        outline=outline,
        bend_lines=[(seam_start, seam_end)],
        notches=[],
        labels=[(Vector2D(round(circumference / 2, 4), round(height / 2, 4)),
                 params.item_id)],
        area_m2=area_m2,
    )


# ---------------------------------------------------------------------------
# Cone (frustum) development
# ---------------------------------------------------------------------------


def unwrap_cone(params: FittingParameters) -> FlatPattern:
    """Develop a truncated cone (frustum) into a flat radial sector.

    Uses the standard radial-line development for right circular cones:
        L0  = R × slant / (R − r)   [development radius, large end]
        L1  = r × slant / (R − r)   [development radius, small end]
        θ   = 2π × R / L0            [sector angle, radians]

    When top and bottom radii are equal (cylinder) the function delegates
    to :func:`unwrap_cylinder`.

    Args:
        params: FittingParameters with diameter_mm (large end),
                top_diameter_mm (small end), and length_mm (axial height).

    Returns:
        FlatPattern containing the sector outline and the seam line.
    """
    big_r = params.diameter_mm / 2.0
    small_r = params.top_diameter_mm / 2.0
    height = params.length_mm

    if abs(big_r - small_r) < 1e-6:
        return unwrap_cylinder(params)

    # Slant height of the frustum
    slant = math.sqrt(height ** 2 + (big_r - small_r) ** 2)

    # Radial development dimensions
    L0 = big_r * slant / (big_r - small_r)   # outer arc radius
    L1 = small_r * slant / (big_r - small_r)  # inner arc radius

    # Sector angle (in radians)
    sector_angle = 2.0 * math.pi * big_r / L0

    n = _ARC_SEGMENTS
    outline: List[Vector2D] = []

    # Outer arc (large end) from 0 → sector_angle
    for i in range(n + 1):
        ang = i * sector_angle / n
        outline.append(
            Vector2D(round(L0 * math.cos(ang), 4), round(L0 * math.sin(ang), 4))
        )

    # Inner arc (small end) reversed: from sector_angle → 0
    for i in range(n, -1, -1):
        ang = i * sector_angle / n
        outline.append(
            Vector2D(round(L1 * math.cos(ang), 4), round(L1 * math.sin(ang), 4))
        )

    # Close the polygon
    outline.append(outline[0])

    # Seam line at angle = 0
    seam_start = Vector2D(round(L1, 4), 0.0)
    seam_end = Vector2D(round(L0, 4), 0.0)

    # Lateral surface area of frustum
    area_m2 = round(math.pi * (big_r + small_r) * slant / 1_000_000.0, 4)

    # Label at the mid-arc, outer radius
    half_ang = sector_angle / 2.0
    label_pos = Vector2D(
        round(L0 * math.cos(half_ang), 4), round(L0 * math.sin(half_ang), 4)
    )

    return FlatPattern(
        outline=outline,
        bend_lines=[(seam_start, seam_end)],
        notches=[],
        labels=[(label_pos, params.item_id)],
        area_m2=area_m2,
    )


# ---------------------------------------------------------------------------
# Elbow development (segmented gore method)
# ---------------------------------------------------------------------------


def unwrap_elbow(params: FittingParameters) -> List[FlatPattern]:
    """Develop an elbow as a list of sinusoidal gore flat patterns.

    Each gore is the development of a cylinder segment cut by two angled
    planes.  The axial height at circumferential position θ is:

        h(θ) = (R_cl + r × cos θ) × β

    where R_cl is the elbow centreline radius, r is the duct radius,
    β = total_angle / n_pieces is the angle subtended by one gore, and
    θ is measured from the *outer* side (θ = 0 → outer, θ = π → inner).

    Args:
        params: FittingParameters with diameter_mm, radius_mm (centreline),
                elbow_angle_deg, and num_pieces.

    Returns:
        List of FlatPattern objects (one per gore piece).
    """
    r = params.diameter_mm / 2.0
    R_cl = params.radius_mm
    n = params.num_pieces
    total_angle = math.radians(params.elbow_angle_deg)
    beta = total_angle / n          # angle per gore
    circumference = 2.0 * math.pi * r

    patterns: List[FlatPattern] = []
    n_pts = _ARC_SEGMENTS

    for piece_idx in range(n):
        bottom_pts: List[Vector2D] = []
        top_pts: List[Vector2D] = []

        for i in range(n_pts + 1):
            # θ goes 0 → 2π; x goes 0 → circumference
            theta = 2.0 * math.pi * i / n_pts
            x = round(circumference * i / n_pts, 4)

            h = round((R_cl + r * math.cos(theta)) * beta, 4)

            bottom_pts.append(Vector2D(x, 0.0))
            top_pts.append(Vector2D(x, h))

        # Closed outline: bottom L→R, then top R→L
        outline: List[Vector2D] = (
            bottom_pts + list(reversed(top_pts)) + [bottom_pts[0]]
        )

        # Area via trapezoidal integration
        dx = circumference / n_pts
        area_mm2 = sum(
            (top_pts[i].y + top_pts[(i + 1) % (n_pts + 1)].y) / 2.0 * dx
            for i in range(n_pts)
        )
        area_m2 = round(area_mm2 / 1_000_000.0, 4)

        L_center = round(R_cl * beta, 4)
        label_pos = Vector2D(round(circumference / 2.0, 4), L_center)

        patterns.append(
            FlatPattern(
                outline=outline,
                bend_lines=[],
                notches=[],
                labels=[(label_pos, f"{params.item_id}-G{piece_idx + 1:02d}")],
                area_m2=area_m2,
            )
        )

    return patterns


# ---------------------------------------------------------------------------
# Square-to-round (transition) development
# ---------------------------------------------------------------------------


def unwrap_square_to_round(params: FittingParameters) -> List[FlatPattern]:
    """Develop a square-to-round transition into four triangulated gore panels.

    Uses the triangulation method:
    1. The circle at the top (radius r, centred at (ox, oy, L)) is divided
       into four quadrant arcs, one per rectangle side.
    2. For each panel the rectangle edge is the base and the circle arc is
       the top.  True lengths in 3-D are computed then each triangle is
       unfolded into 2-D using trilateration.

    Args:
        params: FittingParameters with rect_width_mm, rect_height_mm,
                round_diameter_mm, length_mm, and optional offset_x/y_mm.

    Returns:
        List of four FlatPattern objects (one per rectangle side).
    """
    W = params.rect_width_mm
    H = params.rect_height_mm
    r = params.round_diameter_mm / 2.0
    L = params.length_mm
    ox = params.offset_x_mm
    oy = params.offset_y_mm

    # Rectangle corners at z = 0 (counter-clockwise)
    rect_corners: List[Vector3D] = [
        Vector3D(-W / 2.0, -H / 2.0, 0.0),
        Vector3D( W / 2.0, -H / 2.0, 0.0),
        Vector3D( W / 2.0,  H / 2.0, 0.0),
        Vector3D(-W / 2.0,  H / 2.0, 0.0),
    ]

    # Circle divided into 4 × n_seg points at z = L
    n_seg = 16  # per quadrant
    n_total = 4 * n_seg
    circle_pts: List[Vector3D] = [
        Vector3D(
            ox + r * math.cos(2.0 * math.pi * i / n_total),
            oy + r * math.sin(2.0 * math.pi * i / n_total),
            L,
        )
        for i in range(n_total)
    ]

    def _closest_circle_idx(corner: Vector3D) -> int:
        """Return circle-point index closest to *corner* in plan (xy)."""
        ang = math.atan2(corner.y - oy, corner.x - ox)
        idx = round(ang / (2.0 * math.pi) * n_total) % n_total
        return int(idx)

    corner_circ_idx = [_closest_circle_idx(c) for c in rect_corners]

    patterns: List[FlatPattern] = []

    for side in range(4):
        c_start = rect_corners[side]
        c_end = rect_corners[(side + 1) % 4]
        base_len = _dist3d(c_start, c_end)

        # Arc indices for this panel
        start_idx = corner_circ_idx[side]
        end_idx = corner_circ_idx[(side + 1) % 4]
        arc_idxs: List[int] = []
        idx = start_idx
        steps = 0
        while idx != end_idx and steps < n_total:
            arc_idxs.append(idx)
            idx = (idx + 1) % n_total
            steps += 1
        arc_idxs.append(end_idx)

        # 2-D positions of the two base corners
        b1x, b1y = 0.0, 0.0
        b2x, b2y = base_len, 0.0

        # Trilaterate each arc point above the baseline
        top_pts_2d: List[Vector2D] = []
        for arc_idx in arc_idxs:
            cp = circle_pts[arc_idx]
            d1 = _dist3d(c_start, cp)
            d2 = _dist3d(c_end, cp)
            gx, gy = _trilaterate_2d(b1x, b1y, b2x, b2y, d1, d2)
            top_pts_2d.append(Vector2D(round(gx, 4), round(gy, 4)))

        # Outline: base (L→R), then arc top (R→L), close
        bottom_pts = [Vector2D(b1x, b1y), Vector2D(b2x, b2y)]
        outline: List[Vector2D] = (
            bottom_pts + list(reversed(top_pts_2d)) + [Vector2D(b1x, b1y)]
        )

        # Surface area of this panel (sum of triangle areas in 3-D)
        area_mm2 = 0.0
        for i in range(len(arc_idxs) - 1):
            # Triangle: c_start, arc[i], arc[i+1]
            a = circle_pts[arc_idxs[i]]
            b = circle_pts[arc_idxs[i + 1]]
            ab = b - a
            ac = c_start - a
            cross = ab.cross(ac)
            area_mm2 += cross.length() / 2.0
            # Triangle: c_end, arc[i], arc[i+1]
            ac2 = c_end - a
            cross2 = ab.cross(ac2)
            area_mm2 += cross2.length() / 2.0
        # Deduplicate (each triangle counted once per side):
        area_mm2 /= 2.0
        area_m2 = round(area_mm2 / 1_000_000.0, 4)

        # Label at centroid of top arc
        if top_pts_2d:
            lx = round(sum(p.x for p in top_pts_2d) / len(top_pts_2d), 4)
            ly = round(sum(p.y for p in top_pts_2d) / len(top_pts_2d), 4)
        else:
            lx, ly = base_len / 2.0, 0.0

        patterns.append(
            FlatPattern(
                outline=outline,
                bend_lines=[],
                notches=[],
                labels=[
                    (Vector2D(lx, ly), f"{params.item_id}-S{side + 1}")
                ],
                area_m2=area_m2,
            )
        )

    return patterns


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


def unwrap_fitting(
    params: FittingParameters,
) -> Union[FlatPattern, List[FlatPattern]]:
    """Dispatch to the correct unwrap function for the given fitting type.

    Args:
        params: Fully populated FittingParameters instance.

    Returns:
        A single FlatPattern (cylinder, cone) or a list of FlatPatterns
        (elbow, offset, square-to-round / transition).

    Raises:
        ValueError: If the fitting type is not supported.
    """
    ft = params.fitting_type
    if ft == FittingType.CYLINDER:
        return unwrap_cylinder(params)
    elif ft == FittingType.CONE:
        return unwrap_cone(params)
    elif ft in (FittingType.ELBOW, FittingType.OFFSET):
        return unwrap_elbow(params)
    elif ft in (FittingType.SQUARE_TO_ROUND, FittingType.TRANSITION):
        return unwrap_square_to_round(params)
    else:
        raise ValueError(f"Unsupported fitting type: {ft}")
