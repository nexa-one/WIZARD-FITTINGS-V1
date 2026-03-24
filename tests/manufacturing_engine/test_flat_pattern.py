"""
Unit tests – flat-pattern bend compensation (flat_pattern.py)

Covers:
  - neutral_bend_radius formula
  - compute_flat_blank_length (single bend, multiple bends)
  - K-factor consistency with unwrap module
  - Edge cases: zero bends, single bend, mismatched list lengths
"""

import math
import pytest

from manufacturing_engine.flat_pattern import (
    K_FACTOR,
    compute_bend_allowance,
    compute_bend_deduction,
    compute_flat_blank_length,
    neutral_bend_radius,
)


class TestNeutralBendRadius:
    def test_formula(self):
        """R_neutral = R_inside + K × t."""
        r = neutral_bend_radius(3.0, 1.0)
        expected = 3.0 + K_FACTOR * 1.0
        assert math.isclose(r, expected, rel_tol=1e-6)

    def test_custom_k(self):
        r = neutral_bend_radius(5.0, 2.0, k_factor=0.5)
        assert math.isclose(r, 6.0, rel_tol=1e-6)

    def test_precision_4dp(self):
        r = neutral_bend_radius(2.375, 0.9)
        assert r == round(r, 4)

    def test_zero_thickness(self):
        r = neutral_bend_radius(4.0, 0.0)
        assert math.isclose(r, 4.0, rel_tol=1e-6)


class TestComputeFlatBlankLength:
    def test_no_bends(self):
        """With no bends total blank = sum of flanges."""
        length = compute_flat_blank_length([100.0, 200.0], [], [], 1.0)
        assert math.isclose(length, 300.0, rel_tol=1e-6)

    def test_single_bend_90deg(self):
        """Single 90° bend: blank = flanges + BA."""
        flanges = [50.0, 50.0]
        angles = [90.0]
        radii = [3.0]
        t = 1.0
        ba = (math.pi / 2.0) * (3.0 + K_FACTOR * t)
        expected = 100.0 + ba
        result = compute_flat_blank_length(flanges, angles, radii, t)
        assert math.isclose(result, expected, rel_tol=1e-4)

    def test_four_bends_box_duct(self):
        """4-sided rectangular duct: 4 × 90° bends."""
        flanges = [100.0, 200.0, 100.0, 200.0]
        angles = [90.0, 90.0, 90.0, 90.0]
        radii = [2.0, 2.0, 2.0, 2.0]
        t = 0.8
        ba_each = (math.pi / 2.0) * (2.0 + K_FACTOR * t)
        expected = sum(flanges) + 4 * ba_each
        result = compute_flat_blank_length(flanges, angles, radii, t)
        assert math.isclose(result, expected, rel_tol=1e-4)

    def test_mismatched_lists_raises(self):
        with pytest.raises(ValueError, match="same length"):
            compute_flat_blank_length([100.0], [90.0, 45.0], [3.0], 1.0)

    def test_precision_4dp(self):
        result = compute_flat_blank_length([75.5], [90.0], [3.0], 0.9)
        assert result == round(result, 4)

    def test_zero_angle_bend_no_contribution(self):
        """A 0° bend contributes no bend allowance."""
        base = compute_flat_blank_length([100.0], [], [], 1.0)
        with_zero = compute_flat_blank_length([100.0], [0.0], [3.0], 1.0)
        assert math.isclose(base, with_zero, rel_tol=1e-6)


class TestKFactorConsistency:
    def test_k_factor_value(self):
        assert K_FACTOR == 0.44

    def test_imported_from_unwrap(self):
        from manufacturing_engine.unwrap import K_FACTOR as K_UNWRAP
        assert K_FACTOR == K_UNWRAP

    def test_bend_allowance_reexported(self):
        """flat_pattern re-exports compute_bend_allowance from unwrap."""
        ba1 = compute_bend_allowance(90.0, 3.0, 1.0)
        from manufacturing_engine.unwrap import compute_bend_allowance as ba_unwrap
        ba2 = ba_unwrap(90.0, 3.0, 1.0)
        assert ba1 == ba2

    def test_bend_deduction_reexported(self):
        bd1 = compute_bend_deduction(90.0, 3.0, 1.0)
        from manufacturing_engine.unwrap import compute_bend_deduction as bd_unwrap
        bd2 = bd_unwrap(90.0, 3.0, 1.0)
        assert bd1 == bd2
