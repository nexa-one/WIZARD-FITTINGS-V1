"""
Unit tests – seam allowance & notch engine (seam_engine.py)

Covers:
  - SEAM_ALLOWANCES constant values
  - apply_seam: Pittsburgh and Snaplock expand the correct dimension
  - apply_seam: custom allowance for S_CLEAT / DRIVE
  - apply_seam: ValueError when custom type used without allowance
  - generate_corner_notches: correct count, polygon count, side size
  - Notch side property (right / left / top / bottom)
  - Idempotency: seam does not modify the original FlatPattern
"""

import math
import pytest

from manufacturing_engine.models import (
    FittingParameters,
    FittingType,
    FlatPattern,
    Material,
    SeamType,
    Vector2D,
)
from manufacturing_engine.seam_engine import (
    SEAM_ALLOWANCES,
    apply_seam,
    generate_corner_notches,
)
from manufacturing_engine.unwrap import unwrap_cylinder


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_cylinder_pattern(d=300.0, l=1000.0) -> FlatPattern:
    params = FittingParameters(
        fitting_type=FittingType.CYLINDER,
        material=Material.GALVANIZED_STEEL,
        thickness_mm=0.8,
        seam_type=SeamType.PITTSBURGH,
        item_id="TEST",
        system_name="SYS",
        diameter_mm=d,
        length_mm=l,
    )
    return unwrap_cylinder(params)


def _bbox(pts):
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------------------
# SEAM_ALLOWANCES constant
# ---------------------------------------------------------------------------


class TestSeamAllowancesConstant:
    def test_pittsburgh_value(self):
        assert SEAM_ALLOWANCES[SeamType.PITTSBURGH] == 12.7

    def test_snaplock_value(self):
        assert SEAM_ALLOWANCES[SeamType.SNAPLOCK] == 9.5

    def test_s_cleat_is_none(self):
        assert SEAM_ALLOWANCES[SeamType.S_CLEAT] is None

    def test_drive_is_none(self):
        assert SEAM_ALLOWANCES[SeamType.DRIVE] is None


# ---------------------------------------------------------------------------
# apply_seam – Pittsburgh
# ---------------------------------------------------------------------------


class TestApplySeamPittsburgh:
    def test_right_edge_expanded(self):
        fp = _make_cylinder_pattern()
        orig_xmax = _bbox(fp.outline)[2]
        seamed = apply_seam(fp, SeamType.PITTSBURGH, seam_side="right")
        new_xmax = _bbox(seamed.outline)[2]
        assert math.isclose(new_xmax - orig_xmax, 12.7, abs_tol=0.001)

    def test_height_unchanged(self):
        fp = _make_cylinder_pattern(d=200.0, l=500.0)
        orig_h = _bbox(fp.outline)[3] - _bbox(fp.outline)[1]
        seamed = apply_seam(fp, SeamType.PITTSBURGH, seam_side="right")
        new_h = _bbox(seamed.outline)[3] - _bbox(seamed.outline)[1]
        assert math.isclose(orig_h, new_h, abs_tol=0.001)

    def test_notches_added(self):
        fp = _make_cylinder_pattern()
        seamed = apply_seam(fp, SeamType.PITTSBURGH, seam_side="right")
        assert len(seamed.notches) == 2

    def test_outline_is_closed(self):
        fp = _make_cylinder_pattern()
        seamed = apply_seam(fp, SeamType.PITTSBURGH, seam_side="right")
        assert seamed.outline[0] == seamed.outline[-1]

    def test_original_unmodified(self):
        fp = _make_cylinder_pattern()
        orig_pts = list(fp.outline)
        _ = apply_seam(fp, SeamType.PITTSBURGH, seam_side="right")
        assert fp.outline == orig_pts


# ---------------------------------------------------------------------------
# apply_seam – Snaplock
# ---------------------------------------------------------------------------


class TestApplySeamSnaplock:
    def test_right_edge_expanded_by_9_5(self):
        fp = _make_cylinder_pattern()
        orig_xmax = _bbox(fp.outline)[2]
        seamed = apply_seam(fp, SeamType.SNAPLOCK, seam_side="right")
        new_xmax = _bbox(seamed.outline)[2]
        assert math.isclose(new_xmax - orig_xmax, 9.5, abs_tol=0.001)

    def test_smaller_than_pittsburgh(self):
        fp = _make_cylinder_pattern()
        snap = apply_seam(fp, SeamType.SNAPLOCK)
        pitt = apply_seam(fp, SeamType.PITTSBURGH)
        snap_xmax = _bbox(snap.outline)[2]
        pitt_xmax = _bbox(pitt.outline)[2]
        assert snap_xmax < pitt_xmax


# ---------------------------------------------------------------------------
# apply_seam – custom (S_CLEAT / DRIVE)
# ---------------------------------------------------------------------------


class TestApplySeamCustom:
    def test_s_cleat_custom_allowance(self):
        fp = _make_cylinder_pattern()
        orig_xmax = _bbox(fp.outline)[2]
        seamed = apply_seam(
            fp, SeamType.S_CLEAT, custom_allowance_mm=15.0
        )
        new_xmax = _bbox(seamed.outline)[2]
        assert math.isclose(new_xmax - orig_xmax, 15.0, abs_tol=0.001)

    def test_drive_custom_allowance(self):
        fp = _make_cylinder_pattern()
        orig_xmax = _bbox(fp.outline)[2]
        seamed = apply_seam(
            fp, SeamType.DRIVE, custom_allowance_mm=20.0
        )
        new_xmax = _bbox(seamed.outline)[2]
        assert math.isclose(new_xmax - orig_xmax, 20.0, abs_tol=0.001)

    def test_s_cleat_without_custom_raises(self):
        fp = _make_cylinder_pattern()
        with pytest.raises(ValueError, match="custom_allowance_mm"):
            apply_seam(fp, SeamType.S_CLEAT)

    def test_drive_without_custom_raises(self):
        fp = _make_cylinder_pattern()
        with pytest.raises(ValueError, match="custom_allowance_mm"):
            apply_seam(fp, SeamType.DRIVE)


# ---------------------------------------------------------------------------
# apply_seam – different sides
# ---------------------------------------------------------------------------


class TestApplySeamSides:
    def test_left_side_expands_left(self):
        fp = _make_cylinder_pattern()
        orig_xmin = _bbox(fp.outline)[0]
        seamed = apply_seam(fp, SeamType.PITTSBURGH, seam_side="left")
        new_xmin = _bbox(seamed.outline)[0]
        assert math.isclose(orig_xmin - new_xmin, 12.7, abs_tol=0.001)

    def test_top_side_expands_top(self):
        fp = _make_cylinder_pattern()
        orig_ymax = _bbox(fp.outline)[3]
        seamed = apply_seam(fp, SeamType.PITTSBURGH, seam_side="top")
        new_ymax = _bbox(seamed.outline)[3]
        assert math.isclose(new_ymax - orig_ymax, 12.7, abs_tol=0.001)

    def test_bottom_side_expands_bottom(self):
        fp = _make_cylinder_pattern()
        orig_ymin = _bbox(fp.outline)[1]
        seamed = apply_seam(fp, SeamType.PITTSBURGH, seam_side="bottom")
        new_ymin = _bbox(seamed.outline)[1]
        assert math.isclose(orig_ymin - new_ymin, 12.7, abs_tol=0.001)


# ---------------------------------------------------------------------------
# generate_corner_notches
# ---------------------------------------------------------------------------


class TestGenerateCornerNotches:
    def test_returns_two_notches(self):
        outline = [
            Vector2D(0, 0), Vector2D(500, 0),
            Vector2D(500, 1000), Vector2D(0, 1000), Vector2D(0, 0),
        ]
        notches = generate_corner_notches(outline, "right", 12.7)
        assert len(notches) == 2

    def test_each_notch_is_closed(self):
        outline = [
            Vector2D(0, 0), Vector2D(500, 0),
            Vector2D(500, 800), Vector2D(0, 800), Vector2D(0, 0),
        ]
        for notch in generate_corner_notches(outline, "right", 12.7):
            assert notch[0] == notch[-1]

    def test_notch_size_matches_allowance(self):
        allow = 9.5
        outline = [
            Vector2D(0, 0), Vector2D(400, 0),
            Vector2D(400, 600), Vector2D(0, 600), Vector2D(0, 0),
        ]
        notches = generate_corner_notches(outline, "right", allow)
        for notch in notches:
            xs = [p.x for p in notch]
            ys = [p.y for p in notch]
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)
            assert math.isclose(width, allow, abs_tol=0.001)
            assert math.isclose(height, allow, abs_tol=0.001)

    def test_each_notch_has_five_vertices(self):
        """Square notch = 4 corners + closing point."""
        outline = [
            Vector2D(0, 0), Vector2D(300, 0),
            Vector2D(300, 500), Vector2D(0, 500), Vector2D(0, 0),
        ]
        for notch in generate_corner_notches(outline, "right", 12.7):
            assert len(notch) == 5
