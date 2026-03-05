"""Tests for the validation module."""
import pytest

from geometric_engine.models import (
    FittingParameters,
    FittingType,
    PressureClass,
    ValidationReport,
)
from geometric_engine.smacna import apply_defaults
from geometric_engine.validation import (
    check_fabrication_constraints,
    check_invalid_geometry,
    check_no_negative_dimensions,
    validate,
)


class TestNegativeDimensions:
    def test_negative_width_fails(self):
        p = FittingParameters(FittingType.STRAIGHT, -1, 12)
        r = ValidationReport()
        check_no_negative_dimensions(p, r)
        assert not r.is_valid

    def test_zero_height_fails(self):
        p = FittingParameters(FittingType.STRAIGHT, 12, 0)
        r = ValidationReport()
        check_no_negative_dimensions(p, r)
        assert not r.is_valid

    def test_positive_dimensions_pass(self):
        p = FittingParameters(FittingType.STRAIGHT, 12, 8)
        r = ValidationReport()
        check_no_negative_dimensions(p, r)
        assert r.is_valid


class TestFabricationConstraints:
    def test_below_minimum_width_fails(self):
        p = FittingParameters(FittingType.STRAIGHT, 1.0, 8)
        r = ValidationReport()
        check_fabrication_constraints(p, r)
        assert not r.fabrication_feasible

    def test_extreme_aspect_ratio_warns(self):
        # 100:10 = 10:1 → warning
        p = FittingParameters(FittingType.STRAIGHT, 100, 10)
        r = ValidationReport()
        check_fabrication_constraints(p, r)
        assert len(r.warnings) > 0

    def test_reasonable_dimensions_pass(self):
        p = FittingParameters(FittingType.STRAIGHT, 24, 12)
        r = ValidationReport()
        check_fabrication_constraints(p, r)
        assert r.fabrication_feasible
        assert r.is_valid


class TestInvalidGeometry:
    def test_elbow_90_wrong_angle(self):
        p = FittingParameters(FittingType.ELBOW_90, 24, 12, angle=45.0)
        r = ValidationReport()
        check_invalid_geometry(p, r)
        assert not r.is_valid

    def test_elbow_90_correct_angle(self):
        p = FittingParameters(FittingType.ELBOW_90, 24, 12, angle=90.0)
        r = ValidationReport()
        check_invalid_geometry(p, r)
        assert r.is_valid

    def test_negative_length_fails(self):
        p = FittingParameters(FittingType.STRAIGHT, 24, 12, length=-5)
        r = ValidationReport()
        check_invalid_geometry(p, r)
        assert not r.is_valid


class TestFullValidate:
    def test_valid_fitting_passes(self):
        p = FittingParameters(FittingType.STRAIGHT, 24, 12)
        apply_defaults(p)
        r = validate(p)
        assert r.is_valid

    def test_invalid_gauge_override_fails(self):
        p = FittingParameters(
            FittingType.STRAIGHT, 24, 12,
            pressure_class=PressureClass.WG_2,
            gauge_override=28,
        )
        apply_defaults(p)
        r = validate(p, smacna_enforcement=True)
        assert not r.is_valid

    def test_smacna_off_skips_gauge_check(self):
        p = FittingParameters(
            FittingType.STRAIGHT, 24, 12,
            pressure_class=PressureClass.WG_2,
            gauge_override=28,
        )
        apply_defaults(p)
        r = validate(p, smacna_enforcement=False)
        assert r.is_valid
