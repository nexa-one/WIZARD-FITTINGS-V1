"""Tests for SMACNA standards module."""
import math
import pytest

from geometric_engine.models import FittingParameters, FittingType, PressureClass
from geometric_engine.smacna import (
    apply_defaults,
    check_smacna_compliance,
    elbow_radius,
    minimum_gauge,
    reinforcement_required,
    transition_minimum_length,
)


class TestMinimumGauge:
    """Gauge increases (lower number) as duct size / pressure grows."""

    def test_small_duct_low_pressure(self):
        assert minimum_gauge(10, 8, PressureClass.WG_2) == 26

    def test_medium_duct_low_pressure(self):
        assert minimum_gauge(24, 12, PressureClass.WG_2) == 24

    def test_large_duct_low_pressure(self):
        # longest side 60" falls in the 55-84" band → gauge 20
        assert minimum_gauge(60, 24, PressureClass.WG_2) == 20

    def test_very_large_duct_low_pressure(self):
        # longest side 90" falls in the 85-96" band → gauge 18
        assert minimum_gauge(90, 30, PressureClass.WG_2) == 18

    def test_small_duct_high_pressure(self):
        # High pressure (> 4 WG) – small duct → 24 gauge
        assert minimum_gauge(10, 8, PressureClass.WG_6) == 24

    def test_medium_duct_high_pressure(self):
        assert minimum_gauge(24, 12, PressureClass.WG_6) == 22

    def test_highest_pressure_large_duct(self):
        # longest side 60" at >4 WG → exceeds 54" threshold → gauge 16
        assert minimum_gauge(60, 40, PressureClass.WG_10) == 16

    def test_width_vs_height_uses_longest(self):
        # 12" wide × 30" tall: longest side = 30 → gauge same as 30" side
        assert minimum_gauge(12, 30, PressureClass.WG_2) == 24
        assert minimum_gauge(30, 12, PressureClass.WG_2) == 24


class TestReinforcementRequired:
    def test_small_duct_no_reinf(self):
        assert reinforcement_required(12, 8, PressureClass.WG_2) is False

    def test_large_duct_low_requires_reinf(self):
        assert reinforcement_required(30, 24, PressureClass.WG_2) is True

    def test_medium_pressure_lower_threshold(self):
        # threshold is 19" for medium pressure
        assert reinforcement_required(20, 8, PressureClass.WG_3) is True
        assert reinforcement_required(18, 8, PressureClass.WG_3) is False

    def test_high_pressure_lowest_threshold(self):
        assert reinforcement_required(13, 8, PressureClass.WG_6) is True
        assert reinforcement_required(10, 8, PressureClass.WG_6) is False


class TestTransitionMinimumLength:
    def test_symmetric_reduction(self):
        # 24→12 width, centered → each side reduces 6" → min len = 6/tan(15°)
        length = transition_minimum_length(24, 12, 12, 12)
        assert length == pytest.approx(6 / math.tan(math.radians(15)), rel=1e-4)

    def test_no_change_zero_length(self):
        length = transition_minimum_length(24, 12, 24, 12)
        assert length == 0.0

    def test_invalid_angle(self):
        with pytest.raises(ValueError):
            transition_minimum_length(24, 12, 12, 12, max_half_angle_deg=0)

    def test_height_change_dominates(self):
        length_h = transition_minimum_length(24, 24, 24, 12)  # only height changes
        length_w = transition_minimum_length(24, 12, 12, 12)  # only width changes
        # Both change by the same amount; lengths should be equal
        assert length_h == pytest.approx(length_w, rel=1e-4)


class TestElbowRadius:
    def test_formula(self):
        assert elbow_radius(24) == pytest.approx(36.0)

    def test_small_duct(self):
        assert elbow_radius(6) == pytest.approx(9.0)


class TestApplyDefaults:
    def test_straight_gets_default_length(self):
        p = FittingParameters(FittingType.STRAIGHT, 24, 12)
        apply_defaults(p)
        assert p.length == 56.0

    def test_straight_respects_explicit_length(self):
        p = FittingParameters(FittingType.STRAIGHT, 24, 12, length=48.0)
        apply_defaults(p)
        assert p.length == 48.0

    def test_elbow_90_gets_arc_length(self):
        p = FittingParameters(FittingType.ELBOW_90, 24, 12)
        apply_defaults(p)
        r = elbow_radius(24)
        expected = math.pi * r * 90 / 180
        assert p.length == pytest.approx(expected, rel=1e-4)

    def test_elbow_90_gets_angle(self):
        p = FittingParameters(FittingType.ELBOW_90, 24, 12)
        apply_defaults(p)
        assert p.angle == 90.0

    def test_elbow_45_gets_angle(self):
        p = FittingParameters(FittingType.ELBOW_45, 12, 8)
        apply_defaults(p)
        assert p.angle == 45.0

    def test_neck_defaults_applied(self):
        p = FittingParameters(FittingType.STRAIGHT, 24, 12)
        apply_defaults(p)
        assert p.neck_in == 6.0
        assert p.neck_out == 6.0

    def test_neck_explicit_preserved(self):
        p = FittingParameters(FittingType.STRAIGHT, 24, 12, neck_in=4.0)
        apply_defaults(p)
        assert p.neck_in == 4.0


class TestCheckSMACNACompliance:
    def test_gauge_too_thin_raises_error(self):
        from geometric_engine.models import ValidationReport

        p = FittingParameters(
            FittingType.STRAIGHT, 24, 12,
            pressure_class=PressureClass.WG_2,
            gauge_override=28,  # thinner than allowed
        )
        report = ValidationReport()
        check_smacna_compliance(p, report)
        assert not report.is_valid
        assert not report.smacna_compliant

    def test_acceptable_gauge_override_is_fine(self):
        from geometric_engine.models import ValidationReport

        p = FittingParameters(
            FittingType.STRAIGHT, 24, 12,
            pressure_class=PressureClass.WG_2,
            gauge_override=22,  # thicker than minimum 24 → OK
        )
        report = ValidationReport()
        check_smacna_compliance(p, report)
        assert report.is_valid
