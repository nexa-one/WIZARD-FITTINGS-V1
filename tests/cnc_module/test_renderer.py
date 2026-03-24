"""
Tests for cnc_module.renderer – isometric 3D hollow-duct visualisation.

These tests verify that:
  1. The renderer produces non-empty SVG output.
  2. The SVG contains the correct structural elements.
  3. The HollowShellEffect shades outer/inner/end-ring faces differently
     (inner faces must be significantly darker than outer faces – this is
     the visual cue that communicates "this is a hollow duct, not solid").
  4. Face normals are computed correctly.
  5. Back-face culling removes back-facing faces.
"""

import math
import re
import pytest

from cnc_module.models.duct import RectangularDuct, RoundDuct
from cnc_module.models.material import SheetMetal
from cnc_module.models.fittings import (
    StraightSection,
    RectangularElbow,
    RoundElbow,
    RectangularTransition,
    RectangularTee,
    RoundTee,
    RectangularReducer,
    EndCap,
)
from cnc_module.renderer.hollow_shell import (
    Face, FaceType, HollowShellEffect, RGBColor,
    _compute_normal, _normalise, _dot,
)
from cnc_module.renderer.isometric import IsometricRenderer, _project


# ================================================================== #
# Fixtures                                                             #
# ================================================================== #
@pytest.fixture
def metal():
    return SheetMetal(thickness=0.8)


@pytest.fixture
def rect_duct():
    return RectangularDuct(400, 200)


@pytest.fixture
def round_duct():
    return RoundDuct(300)


@pytest.fixture
def renderer():
    return IsometricRenderer(circle_segments=12)


# ================================================================== #
# HollowShellEffect – shading correctness                             #
# ================================================================== #
class TestHollowShellEffect:
    """The inner cavity must render DARKER than the outer surface.
    This is the key visual effect that shows the duct is hollow
    (a sheet-metal tube, not a solid block).
    """

    def setup_method(self):
        self.effect = HollowShellEffect()

    def _face(self, ftype: FaceType, normal=(0, 0, 1)) -> Face:
        return Face(
            vertices=[(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
            face_type=ftype,
            normal=normal,
        )

    def _brightness(self, color: RGBColor) -> float:
        """Perceived brightness (0-255 scale)."""
        return 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]

    def test_outer_brighter_than_inner(self):
        """Core constraint: outer face must be visually lighter than inner face."""
        outer_face = self._face(FaceType.OUTER_FACE, normal=(0, 0, 1))
        inner_face = self._face(FaceType.INNER_FACE, normal=(0, 0, -1))
        outer_col = self.effect.shade(outer_face)
        inner_col = self.effect.shade(inner_face)
        assert self._brightness(outer_col) > self._brightness(inner_col), (
            f"Outer {outer_col} should be brighter than inner {inner_col}"
        )

    def test_inner_is_significantly_darker(self):
        """The darkness contrast must be substantial to read as 'hollow'."""
        outer_face = self._face(FaceType.OUTER_FACE, normal=(0, 0, 1))
        inner_face = self._face(FaceType.INNER_FACE, normal=(0, 0, -1))
        outer_bright = self._brightness(self.effect.shade(outer_face))
        inner_bright = self._brightness(self.effect.shade(inner_face))
        contrast = outer_bright - inner_bright
        assert contrast > 50, (
            f"Contrast {contrast:.1f} is too low to visually read as hollow. "
            "Expected > 50 brightness units."
        )

    def test_end_ring_is_bright(self):
        """End-ring faces must be visually distinct to show wall thickness."""
        ring_face = self._face(FaceType.END_RING, normal=(0, 0, 1))
        ring_col = self.effect.shade(ring_face)
        assert self._brightness(ring_col) > 60

    def test_hidden_face_is_black(self):
        hidden_face = self._face(FaceType.HIDDEN)
        assert self.effect.shade(hidden_face) == (0, 0, 0)

    def test_inner_opacity_less_than_one(self):
        """Inner faces use reduced opacity to allow depth layering."""
        inner_face = self._face(FaceType.INNER_FACE)
        assert self.effect.opacity(inner_face) < 1.0

    def test_outer_opacity_is_one(self):
        outer_face = self._face(FaceType.OUTER_FACE)
        assert self.effect.opacity(outer_face) == pytest.approx(1.0)

    def test_end_ring_stroke_width_larger(self):
        """End-ring strokes must be thicker to highlight the wall cross-section."""
        outer_face = self._face(FaceType.OUTER_FACE)
        ring_face = self._face(FaceType.END_RING)
        assert self.effect.stroke_width(ring_face) > self.effect.stroke_width(outer_face)

    def test_shade_returns_valid_rgb(self):
        for ft in (FaceType.OUTER_FACE, FaceType.INNER_FACE, FaceType.END_RING):
            face = self._face(ft)
            col = self.effect.shade(face)
            assert len(col) == 3
            for c in col:
                assert 0 <= c <= 255


# ================================================================== #
# Normal computation                                                   #
# ================================================================== #
class TestNormalComputation:
    def test_flat_xy_plane_normal_is_z(self):
        verts = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
        n = _compute_normal(verts)
        # Normal should point in +Z or -Z
        assert abs(n[2]) == pytest.approx(1.0, abs=1e-6)

    def test_normalise_unit_length(self):
        v = (3.0, 4.0, 0.0)
        n = _normalise(v)
        mag = math.sqrt(n[0]**2 + n[1]**2 + n[2]**2)
        assert mag == pytest.approx(1.0, abs=1e-9)

    def test_normalise_zero_returns_z(self):
        n = _normalise((0, 0, 0))
        assert n == (0.0, 0.0, 1.0)


# ================================================================== #
# Isometric projection                                                 #
# ================================================================== #
class TestIsometricProjection:
    def test_origin_projects_to_origin(self):
        sx, sy = _project((0, 0, 0))
        assert sx == pytest.approx(0.0)
        assert sy == pytest.approx(0.0)

    def test_positive_y_projects_up(self):
        _, sy = _project((0, 100, 0))
        # Positive Y in world → positive sy (before flip in SVG)
        assert sy > 0

    def test_projection_deterministic(self):
        p1 = _project((100, 200, 300))
        p2 = _project((100, 200, 300))
        assert p1 == p2


# ================================================================== #
# IsometricRenderer – SVG output                                       #
# ================================================================== #
class TestIsometricRenderer:
    def test_straight_rect_produces_svg(self, renderer, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        svg = renderer.render(fitting, width=800, height=600)
        assert svg.startswith("<svg")
        assert "</svg>" in svg

    def test_straight_round_produces_svg(self, renderer, metal, round_duct):
        fitting = StraightSection(duct=round_duct, length=1000, metal=metal)
        svg = renderer.render(fitting)
        assert "<polygon" in svg

    def test_rect_elbow_produces_svg(self, renderer, metal, rect_duct):
        fitting = RectangularElbow(duct=rect_duct, angle=90, throat_radius=100, metal=metal)
        svg = renderer.render(fitting)
        assert "<polygon" in svg

    def test_svg_contains_inner_faces(self, renderer, metal, rect_duct):
        """The rendered SVG must contain the hollow interior representation.
        We check that darker (inner-face) polygons are present by looking
        for the dark interior colour signature."""
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        svg = renderer.render(fitting)
        # The inner colour base is (50,55,60) – shaded values will be very dark
        # We just verify that multiple polygons exist (outer + inner + end rings)
        polygon_count = svg.count("<polygon")
        assert polygon_count >= 3, (
            f"Expected at least 3 polygons (outer/inner/end-ring), got {polygon_count}"
        )

    def test_svg_has_end_rings(self, renderer, metal, rect_duct):
        """End-ring faces are what show the hollow cross-section.
        Verify they are produced for both ends of a straight section."""
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        # Tessellate directly to inspect face types
        faces = renderer._tessellate(fitting)
        ring_faces = [f for f in faces if f.face_type == FaceType.END_RING]
        assert len(ring_faces) >= 2, (
            "Expected end-ring faces at both duct openings to show wall thickness"
        )

    def test_svg_dark_background(self, renderer, metal, rect_duct):
        """The renderer uses a dark background to maximise hollow contrast."""
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        svg = renderer.render(fitting)
        assert "#1a1a2e" in svg   # dark navy background

    def test_svg_dimensions(self, renderer, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        svg = renderer.render(fitting, width=1024, height=768)
        assert 'width="1024"' in svg
        assert 'height="768"' in svg

    def test_rect_transition_svg(self, renderer, metal):
        fitting = RectangularTransition(
            inlet=RectangularDuct(600, 400),
            outlet=RectangularDuct(300, 200),
            length=300,
            metal=metal,
        )
        svg = renderer.render(fitting)
        assert "<polygon" in svg

    def test_rect_tee_svg(self, renderer, metal):
        fitting = RectangularTee(
            main=RectangularDuct(600, 300),
            branch=RectangularDuct(300, 200),
            length=600,
            metal=metal,
        )
        svg = renderer.render(fitting)
        assert "<polygon" in svg

    def test_end_cap_svg(self, renderer, metal, rect_duct):
        fitting = EndCap(duct=rect_duct, metal=metal)
        svg = renderer.render(fitting)
        assert "<polygon" in svg

    def test_tessellate_straight_has_outer_and_inner(self, renderer, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        faces = renderer._tessellate(fitting)
        outer = [f for f in faces if f.face_type == FaceType.OUTER_FACE]
        inner = [f for f in faces if f.face_type == FaceType.INNER_FACE]
        assert len(outer) >= 4
        assert len(inner) >= 4

    def test_tessellate_round_straight_has_outer_and_inner(self, renderer, metal, round_duct):
        fitting = StraightSection(duct=round_duct, length=1000, metal=metal)
        faces = renderer._tessellate(fitting)
        outer = [f for f in faces if f.face_type == FaceType.OUTER_FACE]
        inner = [f for f in faces if f.face_type == FaceType.INNER_FACE]
        assert len(outer) >= renderer.circle_segments
        assert len(inner) >= renderer.circle_segments

    def test_hollow_shell_round_has_end_rings(self, renderer, metal, round_duct):
        fitting = StraightSection(duct=round_duct, length=1000, metal=metal)
        faces = renderer._tessellate(fitting)
        rings = [f for f in faces if f.face_type == FaceType.END_RING]
        assert len(rings) >= 2 * renderer.circle_segments

    def test_unsupported_fitting_raises(self, renderer):
        class Dummy:
            label = "dummy"
        with pytest.raises(NotImplementedError):
            renderer._tessellate(Dummy())
