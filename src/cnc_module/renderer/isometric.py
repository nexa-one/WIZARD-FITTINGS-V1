"""
cnc_module.renderer.isometric
==============================
SVG isometric renderer for hollow sheet-metal ducts.

Produces an SVG file (or SVG string) showing the duct fitting in a
dimetric/isometric projection where:

  • Back faces are discarded (back-face culling).
  • Faces are depth-sorted using the painter's algorithm.
  • Exterior faces are shaded with a light Lambertian model.
  • Interior cavity faces are rendered dark – giving the impression of
    looking into a hollow tube.
  • End-ring faces (wall cross-section) are highlighted bright so the
    viewer can clearly see the sheet-metal wall thickness.

Public API
----------
renderer = IsometricRenderer()
svg_str  = renderer.render(fitting, width=800, height=600)

The renderer tessellates each fitting into :class:`Face` objects
internally and sorts them by projected depth before drawing.
"""

from __future__ import annotations

import math
from typing import List, Tuple, Optional

from cnc_module.models.duct import RectangularDuct, RoundDuct, FlatOvalDuct
from cnc_module.models.fittings import (
    Fitting,
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
from cnc_module.renderer.hollow_shell import (
    Face, FaceType, HollowShellEffect, RGBColor,
    _dot, _normalise,
)

Vec3 = Tuple[float, float, float]
Vec2 = Tuple[float, float]


# ------------------------------------------------------------------ #
# Isometric projection matrix                                         #
# ------------------------------------------------------------------ #
# Standard dimetric projection (30° angle used in technical drawings)
# X-right, Y-up, Z-towards viewer
_ISO_ANGLE = math.radians(30.0)
_COS30 = math.cos(_ISO_ANGLE)
_SIN30 = math.sin(_ISO_ANGLE)

# Rotation angles for the isometric view (around X and then Z axes)
_VIEW_ELEV = math.radians(35.264)   # arctan(1/√2)
_VIEW_AZIM = math.radians(45.0)


def _project(v: Vec3) -> Vec2:
    """Project a 3-D world point to 2-D screen coordinates.

    Uses a standard isometric (dimetric) projection:
        screen_x = (x - z) * cos(30°)
        screen_y = y       * 1.0 + (x + z) * sin(30°)
    """
    x, y, z = v
    sx = (x - z) * _COS30
    sy = y + (x + z) * _SIN30
    return (sx, sy)


# ------------------------------------------------------------------ #
# Isometric renderer                                                  #
# ------------------------------------------------------------------ #
class IsometricRenderer:
    """Render a duct fitting to an SVG string using isometric projection.

    Parameters
    ----------
    effect:  :class:`HollowShellEffect` used for face shading.
             Defaults to a standard galvanised-steel appearance.
    show_hidden_edges: Draw back-facing edges as thin dashed lines
                       (useful for CNC verification).
    circle_segments:   Number of polygon segments used to approximate circles.
    """

    def __init__(
        self,
        effect: Optional[HollowShellEffect] = None,
        show_hidden_edges: bool = False,
        circle_segments: int = 24,
    ) -> None:
        self.effect = effect or HollowShellEffect()
        self.show_hidden_edges = show_hidden_edges
        self.circle_segments = circle_segments

    # ================================================================== #
    # Public entry point                                                   #
    # ================================================================== #
    def render(
        self,
        fitting: Fitting,
        width: int = 800,
        height: int = 600,
        padding: int = 40,
    ) -> str:
        """Return an SVG string rendering *fitting* in isometric view."""
        faces = self._tessellate(fitting)
        return self._svg_from_faces(faces, width, height, padding, fitting)

    # ================================================================== #
    # Tessellation dispatcher                                             #
    # ================================================================== #
    def _tessellate(self, fitting: Fitting) -> List[Face]:
        dispatch = {
            StraightSection:        self._tess_straight,
            RectangularElbow:       self._tess_rect_elbow,
            RoundElbow:             self._tess_round_elbow,
            RectangularTransition:  self._tess_rect_transition,
            RoundToRectTransition:  self._tess_round_to_rect,
            RectangularTee:         self._tess_rect_tee,
            RoundTee:               self._tess_round_tee,
            RectangularReducer:     self._tess_rect_reducer,
            EndCap:                 self._tess_end_cap,
        }
        handler = dispatch.get(type(fitting))
        if handler is None:
            raise NotImplementedError(
                f"No tessellator for {type(fitting).__name__}"
            )
        return handler(fitting)

    # ================================================================== #
    # Geometry builders                                                    #
    # ================================================================== #
    def _rect_hollow_faces(
        self,
        duct: RectangularDuct,
        z0: float,
        z1: float,
        has_inlet_ring: bool = True,
        has_outlet_ring: bool = True,
    ) -> List[Face]:
        """Build all faces for a rectangular hollow duct run from z0 to z1."""
        faces: List[Face] = []
        t = duct.thickness

        ow = duct.external_width / 2.0
        oh = duct.external_height / 2.0
        iw = duct.width / 2.0
        ih = duct.height / 2.0

        # ---- Outer faces (4 sides × 1 face each) ----
        # Each outer face is a rectangle; normal points outward.
        outer_quads = [
            # (name, v0, v1, v2, v3, normal)
            ("Outer Top",
             (-ow, oh, z0), (ow, oh, z0), (ow, oh, z1), (-ow, oh, z1),
             (0, 1, 0)),
            ("Outer Bottom",
             (-ow, -oh, z0), (ow, -oh, z0), (ow, -oh, z1), (-ow, -oh, z1),
             (0, -1, 0)),
            ("Outer Left",
             (-ow, -oh, z0), (-ow, oh, z0), (-ow, oh, z1), (-ow, -oh, z1),
             (-1, 0, 0)),
            ("Outer Right",
             (ow, -oh, z0), (ow, oh, z0), (ow, oh, z1), (ow, -oh, z1),
             (1, 0, 0)),
        ]
        for nm, v0, v1, v2, v3, nrm in outer_quads:
            faces.append(Face(
                vertices=[v0, v1, v2, v3],
                face_type=FaceType.OUTER_FACE,
                normal=nrm,
                label=nm,
            ))

        # ---- Inner faces (4 sides) – the hollow cavity ----
        inner_quads = [
            ("Inner Top",
             (-iw, ih, z0), (iw, ih, z0), (iw, ih, z1), (-iw, ih, z1),
             (0, -1, 0)),    # normal points inward (towards centre)
            ("Inner Bottom",
             (-iw, -ih, z0), (iw, -ih, z0), (iw, -ih, z1), (-iw, -ih, z1),
             (0, 1, 0)),
            ("Inner Left",
             (-iw, -ih, z0), (-iw, ih, z0), (-iw, ih, z1), (-iw, -ih, z1),
             (1, 0, 0)),
            ("Inner Right",
             (iw, -ih, z0), (iw, ih, z0), (iw, ih, z1), (iw, -ih, z1),
             (-1, 0, 0)),
        ]
        for nm, v0, v1, v2, v3, nrm in inner_quads:
            faces.append(Face(
                vertices=[v0, v1, v2, v3],
                face_type=FaceType.INNER_FACE,
                normal=nrm,
                label=nm,
            ))

        # ---- End rings (wall cross-section shown at each open end) ----
        if has_inlet_ring:
            faces.extend(self._rect_end_ring(ow, oh, iw, ih, z0, facing=-1))
        if has_outlet_ring:
            faces.extend(self._rect_end_ring(ow, oh, iw, ih, z1, facing=1))

        return faces

    def _rect_end_ring(
        self,
        ow: float, oh: float,
        iw: float, ih: float,
        z: float,
        facing: int,   # -1 = inlet face (normal -Z), +1 = outlet
    ) -> List[Face]:
        """Four trapezoidal faces that form the end-ring (shows wall thickness)."""
        nz = float(facing)
        rings = [
            # Top strip
            [(-ow, oh, z), (ow, oh, z), (iw, ih, z), (-iw, ih, z)],
            # Bottom strip
            [(-ow, -oh, z), (ow, -oh, z), (iw, -ih, z), (-iw, -ih, z)],
            # Left strip
            [(-ow, -oh, z), (-ow, oh, z), (-iw, ih, z), (-iw, -ih, z)],
            # Right strip
            [(ow, -oh, z), (ow, oh, z), (iw, ih, z), (iw, -ih, z)],
        ]
        faces = []
        for verts in rings:
            faces.append(Face(
                vertices=verts,
                face_type=FaceType.END_RING,
                normal=(0.0, 0.0, nz),
                label=f"End Ring z={z:.0f}",
            ))
        return faces

    def _round_hollow_faces(
        self,
        duct: RoundDuct,
        z0: float,
        z1: float,
        segments: int,
        has_inlet_ring: bool = True,
        has_outlet_ring: bool = True,
    ) -> List[Face]:
        """Build all faces for a round hollow duct run."""
        faces: List[Face] = []
        ro = duct.external_diameter / 2.0
        ri = duct.diameter / 2.0

        outer_pts0 = _circle_pts(ro, segments, z0)
        outer_pts1 = _circle_pts(ro, segments, z1)
        inner_pts0 = _circle_pts(ri, segments, z0)
        inner_pts1 = _circle_pts(ri, segments, z1)

        for i in range(segments):
            j = (i + 1) % segments

            # Outer quads
            nrm = _normalise((
                (outer_pts0[i][0] + outer_pts0[j][0]) / 2.0,
                (outer_pts0[i][1] + outer_pts0[j][1]) / 2.0,
                0.0,
            ))
            faces.append(Face(
                vertices=[outer_pts0[i], outer_pts0[j],
                           outer_pts1[j], outer_pts1[i]],
                face_type=FaceType.OUTER_FACE,
                normal=nrm,
                label=f"Outer seg {i}",
            ))

            # Inner quads (inward-facing)
            nrm_in = (-nrm[0], -nrm[1], 0.0)
            faces.append(Face(
                vertices=[inner_pts0[i], inner_pts0[j],
                           inner_pts1[j], inner_pts1[i]],
                face_type=FaceType.INNER_FACE,
                normal=nrm_in,
                label=f"Inner seg {i}",
            ))

        # End rings
        if has_inlet_ring:
            for i in range(segments):
                j = (i + 1) % segments
                faces.append(Face(
                    vertices=[outer_pts0[i], outer_pts0[j],
                               inner_pts0[j], inner_pts0[i]],
                    face_type=FaceType.END_RING,
                    normal=(0.0, 0.0, -1.0),
                    label=f"Inlet ring {i}",
                ))
        if has_outlet_ring:
            for i in range(segments):
                j = (i + 1) % segments
                faces.append(Face(
                    vertices=[outer_pts1[i], outer_pts1[j],
                               inner_pts1[j], inner_pts1[i]],
                    face_type=FaceType.END_RING,
                    normal=(0.0, 0.0, 1.0),
                    label=f"Outlet ring {i}",
                ))

        return faces

    # ================================================================== #
    # Tessellators                                                         #
    # ================================================================== #
    def _tess_straight(self, fitting: StraightSection) -> List[Face]:
        L = fitting.length
        if isinstance(fitting.duct, RoundDuct):
            return self._round_hollow_faces(
                fitting.duct, 0.0, L, self.circle_segments,
            )
        if isinstance(fitting.duct, RectangularDuct):
            return self._rect_hollow_faces(fitting.duct, 0.0, L)
        # FlatOval – approximate as rectangular
        duct = fitting.duct
        approx = RectangularDuct(duct.major, duct.minor, duct.thickness)
        return self._rect_hollow_faces(approx, 0.0, L)

    def _tess_rect_elbow(self, fitting: RectangularElbow) -> List[Face]:
        duct = fitting.duct
        theta = math.radians(fitting.angle)
        R_throat = fitting.throat_radius
        R_heel = fitting.heel_radius
        R_mean = (R_throat + R_heel) / 2.0
        segs = max(8, self.circle_segments)

        faces: List[Face] = []
        t = duct.thickness
        iw = duct.width / 2.0
        ih = duct.height / 2.0
        ow = iw + t
        oh = ih + t

        for i in range(segs):
            a0 = theta * i / segs
            a1 = theta * (i + 1) / segs
            # Outer surface (top/bottom) arcs at heel and throat
            for sign in (-1.0, 1.0):   # top (+) and bottom (-) of duct
                y_in = sign * ih
                y_out = sign * oh
                # Throat face (inner bend)
                p00 = (R_throat * math.cos(a0), y_out, R_throat * math.sin(a0))
                p01 = (R_throat * math.cos(a1), y_out, R_throat * math.sin(a1))
                p10 = (R_throat * math.cos(a0), y_in, R_throat * math.sin(a0))
                p11 = (R_throat * math.cos(a1), y_in, R_throat * math.sin(a1))
                nrm_throat = _normalise((
                    -math.cos((a0 + a1) / 2.0),
                    0.0,
                    -math.sin((a0 + a1) / 2.0),
                ))
                faces.append(Face(
                    vertices=[p00, p01, p11, p10],
                    face_type=FaceType.OUTER_FACE,
                    normal=nrm_throat,
                    label=f"Elbow throat top seg {i}",
                ))
                # Heel face (outer bend)
                q00 = (R_heel * math.cos(a0), y_out, R_heel * math.sin(a0))
                q01 = (R_heel * math.cos(a1), y_out, R_heel * math.sin(a1))
                q10 = (R_heel * math.cos(a0), y_in, R_heel * math.sin(a0))
                q11 = (R_heel * math.cos(a1), y_in, R_heel * math.sin(a1))
                nrm_heel = _normalise((
                    math.cos((a0 + a1) / 2.0),
                    0.0,
                    math.sin((a0 + a1) / 2.0),
                ))
                faces.append(Face(
                    vertices=[q00, q01, q11, q10],
                    face_type=FaceType.OUTER_FACE,
                    normal=nrm_heel,
                    label=f"Elbow heel top seg {i}",
                ))

        # Inlet and outlet end rings
        a_in = 0.0
        a_out = theta
        for angle, nz_sign in ((a_in, -1.0), (a_out, 1.0)):
            nx = -math.sin(angle) * nz_sign
            nz = math.cos(angle) * nz_sign
            corners = [
                (R_heel * math.cos(angle), oh, R_heel * math.sin(angle)),
                (R_throat * math.cos(angle), oh, R_throat * math.sin(angle)),
                (R_throat * math.cos(angle), -oh, R_throat * math.sin(angle)),
                (R_heel * math.cos(angle), -oh, R_heel * math.sin(angle)),
            ]
            faces.append(Face(
                vertices=corners,
                face_type=FaceType.END_RING,
                normal=(nx, 0.0, nz),
                label=f"Elbow end ring angle={math.degrees(angle):.0f}°",
            ))

        return faces

    def _tess_round_elbow(self, fitting: RoundElbow) -> List[Face]:
        return self._tess_straight(
            StraightSection(duct=fitting.duct, length=fitting.radius * math.radians(fitting.angle), metal=fitting.metal)
        )

    def _tess_rect_transition(self, fitting: RectangularTransition) -> List[Face]:
        inlet = fitting.inlet
        outlet = fitting.outlet
        L = fitting.length
        faces: List[Face] = []

        iow = inlet.external_width / 2.0
        ioh = inlet.external_height / 2.0
        oow = outlet.external_width / 2.0
        ooh = outlet.external_height / 2.0

        # Outer faces (4 trapezoidal sides)
        outer = [
            ("Trans Top",    (-iow, ioh, 0), (iow, ioh, 0), (oow, ooh, L), (-oow, ooh, L), (0, 1, 0)),
            ("Trans Bottom", (-iow, -ioh, 0), (iow, -ioh, 0), (oow, -ooh, L), (-oow, -ooh, L), (0, -1, 0)),
            ("Trans Left",   (-iow, -ioh, 0), (-iow, ioh, 0), (-oow, ooh, L), (-oow, -ooh, L), (-1, 0, 0)),
            ("Trans Right",  (iow, -ioh, 0), (iow, ioh, 0), (oow, ooh, L), (oow, -ooh, L), (1, 0, 0)),
        ]
        for nm, v0, v1, v2, v3, nrm in outer:
            faces.append(Face(vertices=[v0, v1, v2, v3], face_type=FaceType.OUTER_FACE, normal=nrm, label=nm))

        # End rings
        faces.extend(self._rect_end_ring(iow, ioh, inlet.width/2, inlet.height/2, 0.0, -1))
        faces.extend(self._rect_end_ring(oow, ooh, outlet.width/2, outlet.height/2, L, 1))

        return faces

    def _tess_round_to_rect(self, fitting: RoundToRectTransition) -> List[Face]:
        return self._tess_rect_transition(
            RectangularTransition(
                inlet=fitting.rect_end,
                outlet=fitting.rect_end,
                length=fitting.length,
                metal=fitting.metal,
            )
        )

    def _tess_rect_tee(self, fitting: RectangularTee) -> List[Face]:
        main_faces = self._rect_hollow_faces(fitting.main, 0.0, fitting.length)
        branch_stub = StraightSection(duct=fitting.branch, length=fitting.branch.width * 1.5, metal=fitting.metal)
        branch_faces = self._tess_straight(branch_stub)
        # Translate branch to the side of the main duct
        branch_offset = fitting.main.external_height / 2.0 + fitting.branch.external_height / 2.0
        branch_faces = [_translate_face(f, (0.0, branch_offset, fitting.length / 2.0 - branch_stub.length / 2.0)) for f in branch_faces]
        return main_faces + branch_faces

    def _tess_round_tee(self, fitting: RoundTee) -> List[Face]:
        main = self._round_hollow_faces(fitting.main, 0.0, fitting.length, self.circle_segments)
        branch_len = max(fitting.branch.diameter, 150.0)
        branch_stub = StraightSection(duct=fitting.branch, length=branch_len, metal=fitting.metal)
        branch_faces = self._tess_straight(branch_stub)
        offset = fitting.main.external_diameter / 2.0 + fitting.branch.external_diameter / 2.0
        branch_faces = [_translate_face(f, (0.0, offset, fitting.length / 2.0 - branch_len / 2.0)) for f in branch_faces]
        return main + branch_faces

    def _tess_rect_reducer(self, fitting: RectangularReducer) -> List[Face]:
        trans = RectangularTransition(
            inlet=fitting.large,
            outlet=fitting.small,
            length=fitting.length,
            metal=fitting.metal,
        )
        return self._tess_rect_transition(trans)

    def _tess_end_cap(self, fitting: EndCap) -> List[Face]:
        """Tessellate an end cap.

        The outer face (exterior of the cap plate) faces -Z; from the
        standard isometric view direction (1,1,1) that face is back-facing
        and would be culled.  We therefore produce BOTH the outer face AND
        the inner face (+Z normal, visible from the isometric camera) so
        the cap is always drawn regardless of view angle.  The inner face
        uses FaceType.END_RING so it receives the bright highlight that
        communicates sheet-metal wall thickness.
        """
        duct = fitting.duct
        if isinstance(duct, RectangularDuct):
            ow = duct.external_width / 2.0
            oh = duct.external_height / 2.0
            verts_outer = [(-ow, -oh, 0), (ow, -oh, 0), (ow, oh, 0), (-ow, oh, 0)]
            # Inner (visible) side of cap – same vertices, opposite normal
            verts_inner = [(-ow, -oh, 0), (-ow, oh, 0), (ow, oh, 0), (ow, -oh, 0)]
            return [
                Face(vertices=verts_outer, face_type=FaceType.OUTER_FACE,
                     normal=(0.0, 0.0, -1.0), label="End Cap (outer)"),
                Face(vertices=verts_inner, face_type=FaceType.END_RING,
                     normal=(0.0, 0.0, 1.0), label="End Cap (inner)"),
            ]
        segs = self.circle_segments
        r = duct.external_diameter / 2.0 if isinstance(duct, RoundDuct) else duct.major / 2.0
        pts_cw = _circle_pts(r, segs, 0.0)
        pts_ccw = list(reversed(pts_cw))
        return [
            Face(vertices=pts_cw, face_type=FaceType.OUTER_FACE,
                 normal=(0.0, 0.0, -1.0), label="End Cap (outer)"),
            Face(vertices=pts_ccw, face_type=FaceType.END_RING,
                 normal=(0.0, 0.0, 1.0), label="End Cap (inner)"),
        ]

    # ================================================================== #
    # SVG output                                                           #
    # ================================================================== #
    def _svg_from_faces(
        self,
        faces: List[Face],
        width: int,
        height: int,
        padding: int,
        fitting: Fitting,
    ) -> str:
        effect = self.effect

        # 1. Back-face cull: remove faces whose projected normal points away
        #    from the viewer (+Z in projected space maps to +(x+z) in world).
        view_dir = _normalise((1.0, 1.0, 1.0))   # isometric view direction
        visible = [
            f for f in faces
            if f.face_type == FaceType.INNER_FACE
            or f.face_type == FaceType.END_RING
            or _dot(_normalise(f.normal), view_dir) >= -0.05
        ]

        # 2. Depth-sort with painter's algorithm (back to front)
        def face_depth(f: Face) -> float:
            cx, cy, cz = f.centroid
            sx, sy = _project((cx, cy, cz))
            return -sy   # paint highest (furthest back) first

        visible.sort(key=face_depth)

        # 3. Project and normalise to viewport
        all_pts = [pt for f in visible for pt in f.vertices]
        if not all_pts:
            return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"></svg>'

        proj = [_project(p) for p in all_pts]
        xs = [p[0] for p in proj]
        ys = [p[1] for p in proj]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        data_w = max_x - min_x or 1.0
        data_h = max_y - min_y or 1.0

        vw = width - 2 * padding
        vh = height - 2 * padding
        scale = min(vw / data_w, vh / data_h)

        def to_screen(p3: Vec3) -> Vec2:
            sx, sy = _project(p3)
            sx = (sx - min_x) * scale + padding
            sy = (max_y - (sy - min_y)) * scale + padding   # flip Y
            return (sx, sy)

        # 4. Build SVG
        label = getattr(fitting, "label", None) or type(fitting).__name__
        lines: List[str] = [
            f'<svg width="{width}" height="{height}" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink">',
            "  <!-- WIZARD-FITTINGS CNC – Hollow Duct 3D View -->",
            f'  <title>{label}</title>',
            # Dark background to emphasise the hollow interior contrast
            f'  <rect width="{width}" height="{height}" fill="#1a1a2e"/>',
            # Optional grid pattern
            '  <defs>',
            '    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">',
            '      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#2a2a3e" stroke-width="0.5"/>',
            '    </pattern>',
            '  </defs>',
            f'  <rect width="{width}" height="{height}" fill="url(#grid)"/>',
        ]

        for face in visible:
            pts_screen = [to_screen(v) for v in face.vertices]
            poly = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts_screen)
            fill_rgb = effect.shade(face)
            fill = _rgb_str(*fill_rgb)
            stroke = _rgb_str(*effect.stroke_color(face))
            sw = effect.stroke_width(face)
            op = effect.opacity(face)

            lines.append(
                f'  <polygon points="{poly}" '
                f'fill="{fill}" fill-opacity="{op:.2f}" '
                f'stroke="{stroke}" stroke-width="{sw}"/>'
            )

        # Title / annotation
        lines.append(
            f'  <text x="{padding}" y="{height - 10}" '
            f'font-family="monospace" font-size="12" fill="#aaaacc">'
            f'{label}</text>'
        )

        lines.append("</svg>")
        return "\n".join(lines)


# ------------------------------------------------------------------ #
# Utility helpers                                                      #
# ------------------------------------------------------------------ #
def _circle_pts(r: float, n: int, z: float) -> List[Vec3]:
    """Evenly-spaced points on a circle of radius *r* at height *z*."""
    pts = []
    for i in range(n):
        a = 2.0 * math.pi * i / n
        pts.append((r * math.cos(a), r * math.sin(a), z))
    return pts


def _translate_face(face: Face, offset: Vec3) -> Face:
    dx, dy, dz = offset
    new_verts = [(v[0]+dx, v[1]+dy, v[2]+dz) for v in face.vertices]
    return Face(
        vertices=new_verts,
        face_type=face.face_type,
        normal=face.normal,
        base_color=face.base_color,
        label=face.label,
    )


def _rgb_str(r: int, g: int, b: int) -> str:
    return f"rgb({r},{g},{b})"
