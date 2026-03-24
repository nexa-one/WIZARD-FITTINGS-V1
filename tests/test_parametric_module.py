"""Tests for ManualParametricInputSystem (parametric module)."""
import pytest

from geometric_engine.parametric_module import (
    AUTOMATIC_CALCULATIONS,
    OPTIONAL_INPUTS,
    REQUIRED_INPUTS,
    ManualParametricInputSystem,
)


class TestSpecLists:
    def test_required_inputs_defined(self):
        assert set(REQUIRED_INPUTS) == {"fitting_type", "width", "height"}

    def test_all_optional_inputs_defined(self):
        required_optionals = {
            "length", "neck_in", "neck_out", "angle",
            "connection_type", "pressure_class", "gauge_override",
            "turning_vanes", "insulation_type", "water_gauge",
        }
        assert required_optionals.issubset(set(OPTIONAL_INPUTS))

    def test_automatic_calculations_defined(self):
        required = {
            "minimum_gauge", "reinforcement_required",
            "transition_minimum_length", "material_weight", "surface_area",
        }
        assert required.issubset(set(AUTOMATIC_CALCULATIONS))


class TestBuildFitting:
    def setup_method(self):
        self.system = ManualParametricInputSystem()

    # --- Required inputs ---

    def test_straight_basic(self):
        result = self.system.build_fitting(
            fitting_type="straight", width=24, height=12
        )
        assert result["fitting_type"] == "straight"
        assert result["dimensions"]["width"] == 24
        assert result["dimensions"]["height"] == 12

    def test_missing_fitting_type_raises(self):
        with pytest.raises(ValueError):
            self.system.build_fitting(fitting_type="", width=24, height=12)

    def test_zero_width_fails_validation(self):
        result = self.system.build_fitting(
            fitting_type="straight", width=0, height=12
        )
        assert not result["validation_report"]["is_valid"]

    # --- Automatic calculations ---

    def test_gauge_computed(self):
        result = self.system.build_fitting(
            fitting_type="straight", width=24, height=12
        )
        assert "gauge" in result
        assert isinstance(result["gauge"], int)

    def test_surface_area_in_calcs(self):
        result = self.system.build_fitting(
            fitting_type="straight", width=24, height=12
        )
        calcs = result["automatic_calculations"]
        assert calcs["surface_area_sq_in"] > 0

    def test_transition_min_length_computed(self):
        result = self.system.build_fitting(
            fitting_type="transition", width=24, height=12, neck_out=12.0
        )
        calcs = result["automatic_calculations"]
        assert "transition_minimum_length" in calcs
        assert calcs["transition_minimum_length"] > 0

    def test_reinf_flag_present(self):
        result = self.system.build_fitting(
            fitting_type="straight", width=30, height=12, pressure_class="2"
        )
        calcs = result["automatic_calculations"]
        assert isinstance(calcs["reinforcement_required"], bool)

    # --- Optional inputs ---

    def test_connection_type_accepted(self):
        result = self.system.build_fitting(
            fitting_type="straight", width=24, height=12,
            connection_type="tdc",
        )
        assert result["connection_type"] == "tdc"

    def test_gauge_override_accepted(self):
        result = self.system.build_fitting(
            fitting_type="straight", width=24, height=12,
            gauge_override=22,
        )
        assert result["gauge"] == 22

    def test_turning_vanes_accepted(self):
        result = self.system.build_fitting(
            fitting_type="elbow_90", width=24, height=12,
            turning_vanes=True,
        )
        assert result["dimensions"] is not None

    def test_insulation_type_accepted(self):
        result = self.system.build_fitting(
            fitting_type="straight", width=24, height=12,
            insulation_type="double_wall",
        )
        assert result["manufacturing_data"]["insulation_type"] == "double_wall"

    # --- All fitting types ---

    @pytest.mark.parametrize("ft", [
        "straight", "elbow_90", "elbow_45", "transition",
        "reducer", "square_to_round", "offset_z", "tee",
    ])
    def test_all_fitting_types_build(self, ft):
        result = self.system.build_fitting(
            fitting_type=ft, width=24, height=12
        )
        assert result["fitting_type"] == ft

    # --- Output structure ---

    def test_geometry_core_compatible_flag(self):
        result = self.system.build_fitting(
            fitting_type="straight", width=24, height=12
        )
        assert result["geometry_core_compatible"] is True

    def test_manufacturing_data_present(self):
        result = self.system.build_fitting(
            fitting_type="straight", width=24, height=12
        )
        assert "manufacturing_data" in result
        mfg = result["manufacturing_data"]
        assert "gauge" in mfg
        assert "connection_type" in mfg
