"""Tests for core data models."""
import pytest

from geometric_engine.models import (
    STRAIGHT_DEFAULT_LENGTH,
    DEFAULT_NECK_LENGTH,
    ConnectionType,
    FittingParameters,
    FittingResult,
    FittingType,
    InsulationType,
    PressureClass,
    ValidationReport,
)


class TestFittingType:
    def test_all_values_defined(self):
        expected = {
            "straight", "elbow_90", "elbow_45", "transition",
            "reducer", "square_to_round", "offset_z", "tee",
        }
        assert {ft.value for ft in FittingType} == expected

    def test_string_construction(self):
        assert FittingType("elbow_90") is FittingType.ELBOW_90


class TestConnectionType:
    def test_all_values_defined(self):
        expected = {"raw", "tdc", "ductmate_frame", "slip_and_drive"}
        assert {ct.value for ct in ConnectionType} == expected


class TestInsulationType:
    def test_all_values_defined(self):
        expected = {"single_wall", "double_wall", "internal_liner"}
        assert {it.value for it in InsulationType} == expected


class TestPressureClass:
    def test_all_values_defined(self):
        expected = {"0.5", "1", "2", "3", "4", "6", "10"}
        assert {pc.value for pc in PressureClass} == expected


class TestFittingParameters:
    def test_required_fields(self):
        p = FittingParameters(
            fitting_type=FittingType.STRAIGHT, width=24, height=12
        )
        assert p.fitting_type is FittingType.STRAIGHT
        assert p.width == 24
        assert p.height == 12

    def test_string_coercion(self):
        p = FittingParameters(
            fitting_type="elbow_90",
            width=24,
            height=12,
            connection_type="tdc",
            pressure_class="2",
            insulation_type="double_wall",
        )
        assert p.fitting_type is FittingType.ELBOW_90
        assert p.connection_type is ConnectionType.TDC
        assert p.pressure_class is PressureClass.WG_2
        assert p.insulation_type is InsulationType.DOUBLE_WALL

    def test_optional_fields_default_to_none(self):
        p = FittingParameters(fitting_type=FittingType.STRAIGHT, width=12, height=8)
        assert p.length is None
        assert p.neck_in is None
        assert p.neck_out is None
        assert p.angle is None
        assert p.gauge_override is None


class TestValidationReport:
    def test_initial_state_is_valid(self):
        r = ValidationReport()
        assert r.is_valid is True
        assert r.errors == []
        assert r.warnings == []

    def test_add_error_invalidates(self):
        r = ValidationReport()
        r.add_error("something wrong")
        assert r.is_valid is False
        assert "something wrong" in r.errors

    def test_add_warning_does_not_invalidate(self):
        r = ValidationReport()
        r.add_warning("minor issue")
        assert r.is_valid is True
        assert "minor issue" in r.warnings

    def test_to_dict_keys(self):
        r = ValidationReport()
        d = r.to_dict()
        assert set(d.keys()) >= {
            "is_valid", "errors", "warnings",
            "smacna_compliant", "geometry_valid", "fabrication_feasible",
        }


class TestSystemConfig:
    def test_defaults(self):
        assert STRAIGHT_DEFAULT_LENGTH == 56
        assert DEFAULT_NECK_LENGTH == 6
