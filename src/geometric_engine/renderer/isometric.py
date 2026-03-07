"""
Isometric projection engine for WIZARD-FITTINGS v2.0.0.

Implements the Canvas2D isometric renderer described in the engine spec:

    screen_x = (x - z) * cos(30°) * scale + offset_cx
    screen_y = (x + z) * sin(30°) * scale - y * scale + offset_cy

All drawing commands are returned as plain Python dicts so they can be
serialised to JSON and consumed by a front-end canvas renderer.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# Isometric constants
_COS30 = math.cos(math.radians(30))   # ≈ 0.866
_SIN30 = math.sin(math.radians(30))   # = 0.500


# ---------------------------------------------------------------------------
# Screen coordinate
# ---------------------------------------------------------------------------

@dataclass
class ScreenPoint:
    """A 2-D screen position (pixels)."""
    sx: float
    sy: float

    def as_tuple(self) -> Tuple[float, float]:
        return (self.sx, self.sy)


# ---------------------------------------------------------------------------
# Draw commands – each is a plain dict with a "type" key
# ---------------------------------------------------------------------------

def _cmd(type_: str, **kwargs: Any) -> Dict[str, Any]:
    return {"type": type_, **kwargs}


# ---------------------------------------------------------------------------
# Isometric projection
# ---------------------------------------------------------------------------

class IsometricProjection:
    """
    Projects 3-D world coordinates to 2-D isometric screen coordinates.

    Parameters
    ----------
    scale:
        Pixels per metre (default: 200).
    offset_cx:
        Horizontal centre offset in pixels (default: 400).
    offset_cy:
        Vertical centre offset in pixels (default: 300).
    """

    def __init__(
        self,
        scale: float = 200.0,
        offset_cx: float = 400.0,
        offset_cy: float = 300.0,
    ) -> None:
        if scale <= 0:
            raise ValueError(f"scale must be positive; got {scale}.")
        self.scale = scale
        self.offset_cx = offset_cx
        self.offset_cy = offset_cy

    def project(self, x: float, y: float, z: float) -> ScreenPoint:
        """
        Project 3-D world point (x, y, z) to 2-D screen point.

        Convention:
        * *x* – depth axis (into page)
        * *y* – vertical axis (up)
        * *z* – horizontal axis (right)
        """
        sx = (x - z) * _COS30 * self.scale + self.offset_cx
        sy = (x + z) * _SIN30 * self.scale - y * self.scale + self.offset_cy
        return ScreenPoint(sx, sy)

    def project_all(self, points: List[Tuple[float, float, float]]) -> List[ScreenPoint]:
        """Project a list of (x, y, z) tuples."""
        return [self.project(*p) for p in points]


# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------

def iso_box(
    proj: IsometricProjection,
    x: float, y: float, z: float,
    W: float, H: float, D: float,
    theme_colors: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Generate draw commands for an isometric box (rectangular prism).

    Parameters
    ----------
    proj:
        :class:`IsometricProjection` instance.
    x, y, z:
        World origin of the box (bottom-front-left corner).
    W:
        Width (along Z axis).
    H:
        Height (along Y axis).
    D:
        Depth (along X axis).
    theme_colors:
        Optional dict with keys ``"top"``, ``"left"``, ``"right"`` for face
        shading and ``"outline"`` for edge colour.
    """
    colors = {
        "top":     "#F9F9F9",
        "left":    "#ECECEC",
        "right":   "#E0E0E0",
        "outline": "#111111",
    }
    if theme_colors:
        colors.update(theme_colors)

    # 8 corners of the box
    corners_3d = [
        (x,     y,     z),      # 0 front-bottom-left
        (x,     y,     z + W),  # 1 front-bottom-right
        (x,     y + H, z),      # 2 front-top-left
        (x,     y + H, z + W),  # 3 front-top-right
        (x + D, y,     z),      # 4 back-bottom-left
        (x + D, y,     z + W),  # 5 back-bottom-right
        (x + D, y + H, z),      # 6 back-top-left
        (x + D, y + H, z + W),  # 7 back-top-right
    ]
    c = [proj.project(*p).as_tuple() for p in corners_3d]

    cmds: List[Dict[str, Any]] = []

    # Top face (y+H plane) – corners [front-top-left, front-top-right, back-top-right, back-top-left]
    cmds.append(_cmd("polygon",
                     points=[c[2], c[3], c[7], c[6]],
                     fill=colors["top"], stroke=colors["outline"], stroke_width=1.8))
    # Left face (z plane)
    cmds.append(_cmd("polygon",
                     points=[c[0], c[2], c[6], c[4]],
                     fill=colors["left"], stroke=colors["outline"], stroke_width=1.8))
    # Right face (z+W plane)
    cmds.append(_cmd("polygon",
                     points=[c[1], c[3], c[7], c[5]],
                     fill=colors["right"], stroke=colors["outline"], stroke_width=1.8))

    return cmds


def iso_cylinder(
    proj: IsometricProjection,
    x: float, y: float, z: float,
    r: float, h: float,
    axis: str = "Y",
    n_segments: int = 16,
    theme_colors: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Generate draw commands for an isometric cylinder.

    Parameters
    ----------
    proj:
        :class:`IsometricProjection` instance.
    x, y, z:
        World origin (centre of one circular face).
    r:
        Radius.
    h:
        Height (length along *axis*).
    axis:
        Principal axis: ``"X"``, ``"Y"``, or ``"Z"``.
    n_segments:
        Number of polygon segments approximating the circles.
    theme_colors:
        Optional face-colour overrides.
    """
    colors = {
        "side":    "#ECECEC",
        "cap":     "#F0F0F0",
        "outline": "#111111",
    }
    if theme_colors:
        colors.update(theme_colors)

    def _circle_pts(cx: float, cy: float, cz: float, radius: float, ax: str) -> List[tuple]:
        pts = []
        for i in range(n_segments):
            angle = 2 * math.pi * i / n_segments
            cos_a = math.cos(angle) * radius
            sin_a = math.sin(angle) * radius
            if ax == "Y":
                pts.append((cx + cos_a, cy, cz + sin_a))
            elif ax == "X":
                pts.append((cx, cy + cos_a, cz + sin_a))
            else:  # Z
                pts.append((cx + cos_a, cy + sin_a, cz))
        return pts

    def _offset_pts(pts: List[tuple], ax: str, dist: float) -> List[tuple]:
        if ax == "Y":
            return [(p[0], p[1] + dist, p[2]) for p in pts]
        if ax == "X":
            return [(p[0] + dist, p[1], p[2]) for p in pts]
        return [(p[0], p[1], p[2] + dist) for p in pts]

    pts_bottom = _circle_pts(x, y, z, r, axis)
    pts_top = _offset_pts(pts_bottom, axis, h)

    sp_b = [proj.project(*p).as_tuple() for p in pts_bottom]
    sp_t = [proj.project(*p).as_tuple() for p in pts_top]

    cmds: List[Dict[str, Any]] = []

    # Side quads
    for i in range(n_segments):
        j = (i + 1) % n_segments
        quad = [sp_b[i], sp_b[j], sp_t[j], sp_t[i]]
        cmds.append(_cmd("polygon", points=quad,
                         fill=colors["side"], stroke=colors["outline"], stroke_width=0.8))

    # Bottom cap
    cmds.append(_cmd("polygon", points=sp_b,
                     fill=colors["cap"], stroke=colors["outline"], stroke_width=1.8))
    # Top cap
    cmds.append(_cmd("polygon", points=sp_t,
                     fill=colors["cap"], stroke=colors["outline"], stroke_width=1.8))

    return cmds


def iso_cone(
    proj: IsometricProjection,
    x: float, y: float, z: float,
    r1: float, r2: float, h: float,
    axis: str = "Y",
    n_segments: int = 16,
    theme_colors: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Generate draw commands for an isometric cone frustum.

    Parameters
    ----------
    proj:
        :class:`IsometricProjection` instance.
    x, y, z:
        World origin (centre of base face).
    r1:
        Base radius.
    r2:
        Top radius (0 = sharp cone).
    h:
        Height.
    axis:
        Principal axis (``"X"``, ``"Y"``, ``"Z"``).
    n_segments:
        Polygon approximation segments.
    theme_colors:
        Optional colour overrides.
    """
    colors = {
        "side":    "#E8E8E8",
        "cap":     "#F0F0F0",
        "outline": "#111111",
    }
    if theme_colors:
        colors.update(theme_colors)

    def _circle(cx: float, cy: float, cz: float, radius: float, ax: str) -> List[tuple]:
        pts = []
        for i in range(n_segments):
            angle = 2 * math.pi * i / n_segments
            ca, sa = math.cos(angle) * radius, math.sin(angle) * radius
            if ax == "Y":
                pts.append((cx + ca, cy, cz + sa))
            elif ax == "X":
                pts.append((cx, cy + ca, cz + sa))
            else:
                pts.append((cx + ca, cy + sa, cz))
        return pts

    def _offset(pts: List[tuple], ax: str, dist: float) -> List[tuple]:
        if ax == "Y":
            return [(p[0], p[1] + dist, p[2]) for p in pts]
        if ax == "X":
            return [(p[0] + dist, p[1], p[2]) for p in pts]
        return [(p[0], p[1], p[2] + dist) for p in pts]

    base_pts = _circle(x, y, z, r1, axis)
    # Top is offset along axis and has radius r2
    top_raw = _circle(x, y, z, r2, axis)
    top_pts = _offset(top_raw, axis, h)

    sp_base = [proj.project(*p).as_tuple() for p in base_pts]
    sp_top = [proj.project(*p).as_tuple() for p in top_pts]

    cmds: List[Dict[str, Any]] = []
    for i in range(n_segments):
        j = (i + 1) % n_segments
        quad = [sp_base[i], sp_base[j], sp_top[j], sp_top[i]]
        cmds.append(_cmd("polygon", points=quad,
                         fill=colors["side"], stroke=colors["outline"], stroke_width=0.8))

    cmds.append(_cmd("polygon", points=sp_base,
                     fill=colors["cap"], stroke=colors["outline"], stroke_width=1.8))
    if r2 > 0:
        cmds.append(_cmd("polygon", points=sp_top,
                         fill=colors["cap"], stroke=colors["outline"], stroke_width=1.8))
    return cmds


def iso_elbow_arc(
    proj: IsometricProjection,
    cx: float, cy: float, cz: float,
    r: float,
    W_or_D: float,
    start_angle_deg: float,
    end_angle_deg: float,
    axis: str = "Y",
    n_segments: int = 16,
    theme_colors: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Generate draw commands for an elbow arc (swept tube along a circular path).

    Parameters
    ----------
    proj:
        :class:`IsometricProjection` instance.
    cx, cy, cz:
        Centre of the bend arc in world space.
    r:
        Centreline bend radius.
    W_or_D:
        Duct width or diameter (for tube cross-section half-width).
    start_angle_deg, end_angle_deg:
        Arc sweep angles in degrees (e.g. 0 → 90 for a 90° elbow).
    axis:
        Rotation axis of the bend (``"X"``, ``"Y"``, ``"Z"``).
    n_segments:
        Number of arc segments.
    theme_colors:
        Optional colour overrides.
    """
    colors = {
        "side":    "#E8E8E8",
        "outline": "#111111",
    }
    if theme_colors:
        colors.update(theme_colors)

    half = W_or_D / 2
    start_r = math.radians(start_angle_deg)
    end_r = math.radians(end_angle_deg)
    angles = [start_r + (end_r - start_r) * i / n_segments for i in range(n_segments + 1)]

    # Build centreline points along the arc
    def _arc_pt(angle: float) -> tuple:
        ca, sa = math.cos(angle), math.sin(angle)
        if axis == "Y":
            return (cx + r * ca, cy, cz + r * sa)
        if axis == "X":
            return (cx, cy + r * ca, cz + r * sa)
        return (cx + r * ca, cy + r * sa, cz)

    cmds: List[Dict[str, Any]] = []

    for i in range(n_segments):
        p0 = _arc_pt(angles[i])
        p1 = _arc_pt(angles[i + 1])
        sp0 = proj.project(*p0).as_tuple()
        sp1 = proj.project(*p1).as_tuple()
        cmds.append(_cmd("line", x1=sp0[0], y1=sp0[1], x2=sp1[0], y2=sp1[1],
                         stroke=colors["outline"], stroke_width=W_or_D * proj.scale * 0.1))

    return cmds


def iso_flat_oval(
    proj: IsometricProjection,
    x: float, y: float, z: float,
    Wo: float, Ho: float, h: float,
    axis: str = "Y",
    n_cap_segments: int = 8,
    theme_colors: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Generate draw commands for a flat-oval (racetrack) duct section.

    Parameters
    ----------
    proj:
        :class:`IsometricProjection` instance.
    x, y, z:
        World origin.
    Wo:
        Major axis (overall width) of the oval.
    Ho:
        Minor axis (overall height) of the oval.
    h:
        Duct length along *axis*.
    axis:
        Principal axis (``"X"``, ``"Y"``, ``"Z"``).
    n_cap_segments:
        Number of arc segments for each semicircular end.
    theme_colors:
        Optional colour overrides.
    """
    colors = {
        "side":    "#ECECEC",
        "cap":     "#F0F0F0",
        "outline": "#111111",
    }
    if theme_colors:
        colors.update(theme_colors)

    # Build a flat-oval outline in the XZ plane (if axis=Y)
    r_end = Ho / 2
    straight = (Wo - Ho) / 2

    def _oval_pts(ox: float, oy: float, oz: float) -> List[tuple]:
        pts: List[tuple] = []
        # Left semicircle  (centre at (ox, oy, oz - straight))
        for i in range(n_cap_segments + 1):
            ang = math.pi / 2 + math.pi * i / n_cap_segments
            if axis == "Y":
                pts.append((ox + r_end * math.cos(ang), oy, oz - straight + r_end * math.sin(ang)))
            elif axis == "X":
                pts.append((ox - straight + r_end * math.sin(ang), oy + r_end * math.cos(ang), oz))
            else:
                pts.append((ox + r_end * math.cos(ang), oy + r_end * math.sin(ang), oz - straight))
        # Right semicircle
        for i in range(n_cap_segments + 1):
            ang = -math.pi / 2 + math.pi * i / n_cap_segments
            if axis == "Y":
                pts.append((ox + r_end * math.cos(ang), oy, oz + straight + r_end * math.sin(ang)))
            elif axis == "X":
                pts.append((ox + straight + r_end * math.sin(ang), oy + r_end * math.cos(ang), oz))
            else:
                pts.append((ox + r_end * math.cos(ang), oy + r_end * math.sin(ang), oz + straight))
        return pts

    def _offset_pts(pts: List[tuple], ax: str, dist: float) -> List[tuple]:
        if ax == "Y":
            return [(p[0], p[1] + dist, p[2]) for p in pts]
        if ax == "X":
            return [(p[0] + dist, p[1], p[2]) for p in pts]
        return [(p[0], p[1], p[2] + dist) for p in pts]

    pts_b = _oval_pts(x, y, z)
    pts_t = _offset_pts(pts_b, axis, h)

    sp_b = [proj.project(*p).as_tuple() for p in pts_b]
    sp_t = [proj.project(*p).as_tuple() for p in pts_t]

    cmds: List[Dict[str, Any]] = []
    n = len(pts_b)
    for i in range(n):
        j = (i + 1) % n
        quad = [sp_b[i], sp_b[j], sp_t[j], sp_t[i]]
        cmds.append(_cmd("polygon", points=quad,
                         fill=colors["side"], stroke=colors["outline"], stroke_width=0.6))
    cmds.append(_cmd("polygon", points=sp_b,
                     fill=colors["cap"], stroke=colors["outline"], stroke_width=1.8))
    cmds.append(_cmd("polygon", points=sp_t,
                     fill=colors["cap"], stroke=colors["outline"], stroke_width=1.8))
    return cmds


def iso_dim_line(
    proj: IsometricProjection,
    p1: Tuple[float, float, float],
    p2: Tuple[float, float, float],
    label: str,
    offset: float = 0.05,
    color: str = "#1A56DB",
) -> List[Dict[str, Any]]:
    """
    Generate draw commands for an isometric dimension line.

    Parameters
    ----------
    proj:
        :class:`IsometricProjection` instance.
    p1, p2:
        World endpoints of the measured dimension.
    label:
        Dimension text (e.g. ``"W=400mm"``).
    offset:
        Perpendicular offset distance (world units).
    color:
        Stroke and text colour.
    """
    sp1 = proj.project(*p1)
    sp2 = proj.project(*p2)

    dx = sp2.sx - sp1.sx
    dy = sp2.sy - sp1.sy
    length = math.hypot(dx, dy) or 1.0
    perp_x = -dy / length * offset * proj.scale
    perp_y =  dx / length * offset * proj.scale

    o1x, o1y = sp1.sx + perp_x, sp1.sy + perp_y
    o2x, o2y = sp2.sx + perp_x, sp2.sy + perp_y
    mid_x, mid_y = (o1x + o2x) / 2, (o1y + o2y) / 2

    return [
        _cmd("line", x1=o1x, y1=o1y, x2=o2x, y2=o2y,
             stroke=color, stroke_width=1.0, dash=[4, 3]),
        _cmd("line", x1=sp1.sx, y1=sp1.sy, x2=o1x, y2=o1y,
             stroke=color, stroke_width=0.8),
        _cmd("line", x1=sp2.sx, y1=sp2.sy, x2=o2x, y2=o2y,
             stroke=color, stroke_width=0.8),
        _cmd("text", x=mid_x, y=mid_y, text=label,
             fill=color, font="Courier New", font_size=11, align="center"),
    ]


def iso_coord_cube(
    position: str = "top_right",
    size_px: int = 80,
    viewport_w: float = 800.0,
    viewport_h: float = 600.0,
) -> List[Dict[str, Any]]:
    """
    Generate draw commands for the coordinate cube orientation indicator
    (Fusion-360 style), placed at *position* in the viewport.

    Parameters
    ----------
    position:
        ``"top_right"`` (default) or ``"top_left"`` / ``"bottom_right"``.
    size_px:
        Cube size in pixels.
    viewport_w, viewport_h:
        Viewport dimensions for placement.
    """
    margin = 10
    if position == "top_right":
        cx, cy = viewport_w - margin - size_px / 2, margin + size_px / 2
    elif position == "top_left":
        cx, cy = margin + size_px / 2, margin + size_px / 2
    else:  # bottom_right
        cx, cy = viewport_w - margin - size_px / 2, viewport_h - margin - size_px / 2

    s = size_px / 4
    colors = {"X": "#E74C3C", "Y": "#2ECC71", "Z": "#3498DB"}

    def _axis(dx: float, dy: float, label: str) -> List[Dict[str, Any]]:
        return [
            _cmd("line", x1=cx, y1=cy, x2=cx + dx * s, y2=cy + dy * s,
                 stroke=colors[label], stroke_width=2.0),
            _cmd("text", x=cx + dx * s * 1.2, y=cy + dy * s * 1.2,
                 text=label, fill=colors[label], font="Courier New", font_size=10, align="center"),
        ]

    cmds: List[Dict[str, Any]] = [
        _cmd("circle", cx=cx, cy=cy, r=s * 0.2, fill="#CCCCCC", stroke="#666666", stroke_width=1),
    ]
    cmds.extend(_axis(_COS30, -_SIN30, "X"))     # right-forward
    cmds.extend(_axis(-_COS30, -_SIN30, "Z"))    # left-forward
    cmds.extend(_axis(0, -1, "Y"))               # up
    return cmds


def iso_title_block(
    fields: Dict[str, str],
    position: str = "bottom_right",
    viewport_w: float = 800.0,
    viewport_h: float = 600.0,
) -> List[Dict[str, Any]]:
    """
    Generate draw commands for the title block (annotation panel).

    Parameters
    ----------
    fields:
        Mapping of field name → value (e.g. ``{"project": "Site A", ...}``).
    position:
        ``"bottom_right"`` (default) or ``"bottom_left"``.
    viewport_w, viewport_h:
        Viewport dimensions.
    """
    row_h = 18
    col_w = 200
    margin = 12
    n = len(fields)
    block_h = row_h * n + margin
    block_w = col_w

    if position == "bottom_right":
        bx = viewport_w - block_w - margin
    else:
        bx = margin
    by = viewport_h - block_h - margin

    cmds: List[Dict[str, Any]] = [
        _cmd("rect", x=bx, y=by, w=block_w, h=block_h,
             fill="#FFFFFF", stroke="#111111", stroke_width=1.0),
    ]
    for i, (k, v) in enumerate(fields.items()):
        row_y = by + margin // 2 + i * row_h
        cmds.append(_cmd("text", x=bx + 6, y=row_y + 12,
                         text=f"{k}:", fill="#555555", font="Courier New",
                         font_size=10, align="left"))
        cmds.append(_cmd("text", x=bx + 90, y=row_y + 12,
                         text=str(v), fill="#111111", font="Courier New",
                         font_size=10, align="left"))
    return cmds


def iso_annotation_block(
    fields: Dict[str, str],
    position: str = "bottom_left",
    viewport_w: float = 800.0,
    viewport_h: float = 600.0,
) -> List[Dict[str, Any]]:
    """
    Generate draw commands for the annotation block (engineering metadata).

    Same structure as :func:`iso_title_block` but positioned at
    *bottom_left* by default with a slightly different text style.
    """
    return iso_title_block(
        fields=fields,
        position=position,
        viewport_w=viewport_w,
        viewport_h=viewport_h,
    )
