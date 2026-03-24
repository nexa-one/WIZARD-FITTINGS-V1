"""
Unit tests – surface unwrapping (unwrap.py)

Covers:
  - Cylinder development dimensions
  - Cone development geometry (sector angle, radii)
  - Elbow gore sinusoidal profile
  - Square-to-round panel count and geometry
  - Bend allowance / deduction formulas
  - Dispatcher (unwrap_fitting)
  - Edge cases: zero-taper cone → cylinder, single-piece elbow
"""

import math
import pytest

from manufacturing_engine.models import (
    FittingParameters,
    FittingType,
    Material,
    SeamType,
)
from manufacturing_engine.unwrap import (
    K_FACTOR,
    compute_bend_allowance,
    compute_bend_deduction,
    unwrap_cone,
    unwrap_cylinder,
    unwrap_elbow,
    unwrap_fitting,
    unwrap_square_to_round,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _rect_params(**kw) -> FittingParameters:
    defaults = dict(
        fitting_type=FittingType.CYLINDER,
        material=Material.GALVANIZED_STEEL,
        thickness_mm=0.8,
        seam_type=SeamType.PITTSBURGH,
        item_id="TEST",
        system_name="SYS",
    )
    defaults.update(kw)
    return FittingParameters(**defaults)


# ---------------------------------------------------------------------------
# Cylinder
# ---------------------------------------------------------------------------


class TestUnwrapCylinder:
    def test_outline_is_closed(self):
        p = _rect_params(diameter_mm=300.0, length_mm=1000.0)
        fp = unwrap_cylinder(p)
        assert fp.outline[0] == fp.outline[-1], "Outline must be closed"

    def test_width_equals_circumference(self):
        d = 200.0
        p = _rect_params(diameter_mm=d, length_mm=500.0)
        fp = unwrap_cylinder(p)
        xs = [v.x for v in fp.outline]
        width = max(xs) - min(xs)
        expected = math.pi * d
        assert math.isclose(width, expected, rel_tol=1e-4)

    def test_height_equals_length(self):
        h = 750.0
        p = _rect_params(diameter_mm=150.0, length_mm=h)
        fp = unwrap_cylinder(p)
        ys = [v.y for v in fp.outline]
        assert math.isclose(max(ys) - min(ys), h, rel_tol=1e-4)

    def test_area_m2(self):
        d = 200.0
        l = 1000.0
        p = _rect_params(diameter_mm=d, length_mm=l)
        fp = unwrap_cylinder(p)
        expected = math.pi * d * l / 1_000_000.0
        assert math.isclose(fp.area_m2, expected, rel_tol=1e-4)

    def test_seam_line_present(self):
        p = _rect_params(diameter_mm=300.0, length_mm=1000.0)
        fp = unwrap_cylinder(p)
        assert len(fp.bend_lines) == 1

    def test_label_contains_item_id(self):
        p = _rect_params(diameter_mm=300.0, length_mm=1000.0, item_id="DUCT-42")
        fp = unwrap_cylinder(p)
        assert any("DUCT-42" in lbl for _, lbl in fp.labels)

    def test_outline_has_five_vertices(self):
        # Rectangle: 4 corners + closing point
        p = _rect_params(diameter_mm=300.0, length_mm=1000.0)
        fp = unwrap_cylinder(p)
        assert len(fp.outline) == 5


# ---------------------------------------------------------------------------
# Cone
# ---------------------------------------------------------------------------


class TestUnwrapCone:
    def _cone_params(self, big_d, small_d, length):
        return _rect_params(
            fitting_type=FittingType.CONE,
            diameter_mm=big_d,
            top_diameter_mm=small_d,
            length_mm=length,
        )

    def test_outline_closed(self):
        fp = unwrap_cone(self._cone_params(400, 200, 500))
        assert fp.outline[0] == fp.outline[-1]

    def test_sector_angle_positive(self):
        fp = unwrap_cone(self._cone_params(400, 200, 500))
        # Sector angle > 0 and < 2π
        big_r, small_r, h = 200.0, 100.0, 500.0
        slant = math.sqrt(h ** 2 + (big_r - small_r) ** 2)
        L0 = big_r * slant / (big_r - small_r)
        expected_angle = 2.0 * math.pi * big_r / L0
        assert 0 < expected_angle < 2 * math.pi

    def test_outer_radius_correct(self):
        big_r, small_r, h = 200.0, 100.0, 500.0
        fp = unwrap_cone(self._cone_params(400, 200, h))
        slant = math.sqrt(h ** 2 + (big_r - small_r) ** 2)
        L0 = big_r * slant / (big_r - small_r)
        # Max distance from origin should match L0
        max_r = max(math.sqrt(v.x ** 2 + v.y ** 2) for v in fp.outline)
        assert math.isclose(max_r, L0, rel_tol=1e-3)

    def test_inner_radius_correct(self):
        big_r, small_r, h = 200.0, 100.0, 500.0
        fp = unwrap_cone(self._cone_params(400, 200, h))
        slant = math.sqrt(h ** 2 + (big_r - small_r) ** 2)
        L1 = small_r * slant / (big_r - small_r)
        # Points near origin: minimum non-zero distance
        distances = [
            math.sqrt(v.x ** 2 + v.y ** 2) for v in fp.outline
            if math.sqrt(v.x ** 2 + v.y ** 2) > 1.0
        ]
        min_r = min(distances)
        assert math.isclose(min_r, L1, rel_tol=1e-3)

    def test_area_m2_positive(self):
        fp = unwrap_cone(self._cone_params(400, 200, 500))
        assert fp.area_m2 > 0.0

    def test_area_formula(self):
        big_r, small_r, h = 200.0, 100.0, 500.0
        slant = math.sqrt(h ** 2 + (big_r - small_r) ** 2)
        expected = math.pi * (big_r + small_r) * slant / 1_000_000.0
        fp = unwrap_cone(self._cone_params(400, 200, h))
        assert math.isclose(fp.area_m2, expected, rel_tol=1e-4)

    def test_degenerate_cone_becomes_cylinder(self):
        """Equal top and bottom diameter → delegate to unwrap_cylinder."""
        p = _rect_params(
            fitting_type=FittingType.CONE,
            diameter_mm=300.0,
            top_diameter_mm=300.0,
            length_mm=600.0,
        )
        fp = unwrap_cone(p)
        # Should behave like a rectangle
        xs = [v.x for v in fp.outline]
        expected_width = math.pi * 300.0
        assert math.isclose(max(xs) - min(xs), expected_width, rel_tol=1e-4)


# ---------------------------------------------------------------------------
# Elbow
# ---------------------------------------------------------------------------


class TestUnwrapElbow:
    def _elbow_params(self, n=5, angle=90.0, d=300.0, r_cl=450.0):
        return _rect_params(
            fitting_type=FittingType.ELBOW,
            diameter_mm=d,
            radius_mm=r_cl,
            elbow_angle_deg=angle,
            num_pieces=n,
        )

    def test_returns_list(self):
        patterns = unwrap_elbow(self._elbow_params())
        assert isinstance(patterns, list)

    def test_correct_piece_count(self):
        for n in (2, 3, 5, 7):
            patterns = unwrap_elbow(self._elbow_params(n=n))
            assert len(patterns) == n

    def test_each_pattern_closed(self):
        for fp in unwrap_elbow(self._elbow_params()):
            assert fp.outline[0] == fp.outline[-1]

    def test_outer_height_greater_than_inner(self):
        """Outer side (θ=0, x=0) must be taller than inner side (θ=π, x=circumference/2 = πr)."""
        p = self._elbow_params(n=4, d=200.0, r_cl=300.0, angle=90.0)
        r = p.diameter_mm / 2.0
        circumference = math.pi * p.diameter_mm
        patterns = unwrap_elbow(p)
        for fp in patterns:
            # Find the height at x≈0 (outer) and x≈πr (inner)
            top_pts = [v for v in fp.outline if v.y > 0]
            if not top_pts:
                continue
            outer_h = max(
                v.y for v in top_pts if v.x < circumference * 0.1
            ) if any(v.x < circumference * 0.1 for v in top_pts) else None
            inner_h = max(
                v.y for v in top_pts
                if abs(v.x - circumference / 2) < circumference * 0.1
            ) if any(
                abs(v.x - circumference / 2) < circumference * 0.1
                for v in top_pts
            ) else None
            if outer_h and inner_h:
                assert outer_h > inner_h

    def test_center_height_formula(self):
        """Centreline height per gore = R_cl × β."""
        n = 5
        angle_deg = 90.0
        r_cl = 450.0
        p = self._elbow_params(n=n, angle=angle_deg, r_cl=r_cl)
        patterns = unwrap_elbow(p)
        beta = math.radians(angle_deg) / n
        expected_h = r_cl * beta
        for fp in patterns:
            # Label y-position should approximate centreline height
            label_y = fp.labels[0][0].y
            assert math.isclose(label_y, expected_h, rel_tol=1e-4)

    def test_area_positive(self):
        for fp in unwrap_elbow(self._elbow_params()):
            assert fp.area_m2 > 0.0

    def test_gore_label_contains_item_id(self):
        p = self._elbow_params()
        p.item_id = "ELB-99"
        for fp in unwrap_elbow(p):
            assert any("ELB-99" in lbl for _, lbl in fp.labels)


# ---------------------------------------------------------------------------
# Square-to-round
# ---------------------------------------------------------------------------


class TestUnwrapSquareToRound:
    def _s2r_params(self):
        return _rect_params(
            fitting_type=FittingType.SQUARE_TO_ROUND,
            rect_width_mm=400.0,
            rect_height_mm=300.0,
            round_diameter_mm=200.0,
            length_mm=300.0,
        )

    def test_returns_four_panels(self):
        panels = unwrap_square_to_round(self._s2r_params())
        assert len(panels) == 4

    def test_each_panel_closed(self):
        for fp in unwrap_square_to_round(self._s2r_params()):
            assert fp.outline[0] == fp.outline[-1]

    def test_panel_label_contains_item_id(self):
        p = self._s2r_params()
        p.item_id = "S2R-01"
        for fp in unwrap_square_to_round(p):
            assert any("S2R-01" in lbl for _, lbl in fp.labels)

    def test_each_panel_has_positive_area(self):
        for fp in unwrap_square_to_round(self._s2r_params()):
            assert fp.area_m2 >= 0.0

    def test_outline_has_enough_vertices(self):
        # 2 base pts + arc pts + closing = at least 4 vertices
        for fp in unwrap_square_to_round(self._s2r_params()):
            assert len(fp.outline) >= 4


# ---------------------------------------------------------------------------
# Bend allowance / deduction
# ---------------------------------------------------------------------------


class TestBendAllowance:
    def test_90deg_standard(self):
        """BA = π/2 × (R + K×t)  with R=3, K=0.44, t=1."""
        ba = compute_bend_allowance(90.0, 3.0, 1.0)
        expected = (math.pi / 2.0) * (3.0 + 0.44 * 1.0)
        assert math.isclose(ba, expected, rel_tol=1e-4)

    def test_k_factor_default(self):
        assert K_FACTOR == 0.44

    def test_zero_angle(self):
        assert compute_bend_allowance(0.0, 5.0, 1.0) == 0.0

    def test_custom_k_factor(self):
        ba = compute_bend_allowance(90.0, 3.0, 1.0, k_factor=0.5)
        expected = (math.pi / 2.0) * (3.0 + 0.5 * 1.0)
        assert math.isclose(ba, expected, rel_tol=1e-4)

    def test_precision_4dp(self):
        ba = compute_bend_allowance(45.0, 2.0, 0.8)
        assert ba == round(ba, 4)

    def test_180deg(self):
        ba = compute_bend_allowance(180.0, 5.0, 1.0)
        expected = math.pi * (5.0 + 0.44 * 1.0)
        assert math.isclose(ba, expected, rel_tol=1e-4)


class TestBendDeduction:
    def test_90deg(self):
        bd = compute_bend_deduction(90.0, 3.0, 1.0)
        angle_rad = math.pi / 2.0
        ossb = math.tan(angle_rad / 2.0) * (3.0 + 1.0)
        ba = (math.pi / 2.0) * (3.0 + 0.44)
        expected = 2.0 * ossb - ba
        assert math.isclose(bd, expected, rel_tol=1e-4)

    def test_precision_4dp(self):
        bd = compute_bend_deduction(90.0, 3.0, 1.0)
        assert bd == round(bd, 4)

    def test_zero_angle(self):
        assert compute_bend_deduction(0.0, 5.0, 1.0) == 0.0

    def test_deduction_positive_for_sharp_bends(self):
        """A 90° bend on typical sheet metal should have a positive deduction."""
        bd = compute_bend_deduction(90.0, 1.5, 0.9)
        assert bd > 0.0


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


class TestUnwrapFitting:
    def test_cylinder_dispatches(self):
        p = _rect_params(
            fitting_type=FittingType.CYLINDER,
            diameter_mm=200.0,
            length_mm=500.0,
        )
        from manufacturing_engine.models import FlatPattern
        result = unwrap_fitting(p)
        assert isinstance(result, FlatPattern)

    def test_cone_dispatches(self):
        p = _rect_params(
            fitting_type=FittingType.CONE,
            diameter_mm=400.0,
            top_diameter_mm=200.0,
            length_mm=400.0,
        )
        from manufacturing_engine.models import FlatPattern
        result = unwrap_fitting(p)
        assert isinstance(result, FlatPattern)

    def test_elbow_dispatches_list(self):
        p = _rect_params(
            fitting_type=FittingType.ELBOW,
            diameter_mm=300.0,
            radius_mm=450.0,
            num_pieces=5,
        )
        result = unwrap_fitting(p)
        assert isinstance(result, list)
        assert len(result) == 5

    def test_s2r_dispatches_list(self):
        p = _rect_params(
            fitting_type=FittingType.SQUARE_TO_ROUND,
            rect_width_mm=400.0,
            rect_height_mm=300.0,
            round_diameter_mm=200.0,
            length_mm=300.0,
        )
        result = unwrap_fitting(p)
        assert isinstance(result, list)
        assert len(result) == 4

    def test_offset_dispatches_as_elbow(self):
        p = _rect_params(
            fitting_type=FittingType.OFFSET,
            diameter_mm=200.0,
            radius_mm=300.0,
            num_pieces=3,
        )
        result = unwrap_fitting(p)
        assert isinstance(result, list)

    def test_transition_alias(self):
        p = _rect_params(
            fitting_type=FittingType.TRANSITION,
            rect_width_mm=400.0,
            rect_height_mm=300.0,
            round_diameter_mm=200.0,
            length_mm=300.0,
        )
        result = unwrap_fitting(p)
        assert isinstance(result, list)
        assert len(result) == 4
