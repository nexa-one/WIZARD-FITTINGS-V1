"""Tests for SMACNAGuidedWizard (wizard module)."""
import pytest

from geometric_engine.wizard_module import (
    AUTOMATIC_BEHAVIORS,
    STEP_1_OPTIONS,
    STEP_2_FIELDS,
    STEP_3_OPTIONS,
    STEP_4_FIELDS,
    SMACNAGuidedWizard,
)


class TestSpecConstants:
    def test_step_1_options(self):
        expected = {
            "straight", "elbow_90", "elbow_45", "transition",
            "reducer", "square_to_round", "offset_z", "tee",
        }
        assert set(STEP_1_OPTIONS) == expected

    def test_step_2_fields(self):
        assert set(STEP_2_FIELDS) == {"width", "height", "neck_in", "neck_out", "angle"}

    def test_step_3_options(self):
        assert set(STEP_3_OPTIONS) == {"raw", "tdc", "ductmate_frame", "slip_and_drive"}

    def test_step_4_fields(self):
        required = {"turning_vanes", "gauge", "pressure_class",
                    "water_gauge", "insulation_type", "flange_out", "corner_fill"}
        assert required.issubset(set(STEP_4_FIELDS))

    def test_automatic_behaviors_all_enabled(self):
        for key, val in AUTOMATIC_BEHAVIORS.items():
            assert val is True, f"Behavior {key!r} should be True"


class TestStepByStep:
    def setup_method(self):
        self.wizard = SMACNAGuidedWizard()

    def test_step_1_sets_type(self):
        state = self.wizard.step_1(fitting_type="straight")
        assert state["fitting_type"] == "straight"
        assert state["step"] == 1

    def test_step_1_invalid_type_raises(self):
        with pytest.raises(ValueError):
            self.wizard.step_1(fitting_type="banana_fitting")

    def test_step_2_sets_dimensions(self):
        self.wizard.step_1(fitting_type="straight")
        state = self.wizard.step_2(width=24, height=12)
        assert state["width"] == 24
        assert state["height"] == 12
        assert state["step"] == 2

    def test_step_2_applies_default_necks(self):
        self.wizard.step_1(fitting_type="straight")
        state = self.wizard.step_2(width=24, height=12)
        assert state["neck_in"] == 6.0
        assert state["neck_out"] == 6.0

    def test_step_2_explicit_necks_preserved(self):
        self.wizard.step_1(fitting_type="straight")
        state = self.wizard.step_2(width=24, height=12, neck_in=4.0, neck_out=8.0)
        assert state["neck_in"] == 4.0
        assert state["neck_out"] == 8.0

    def test_step_2_without_step_1_raises(self):
        with pytest.raises(RuntimeError):
            self.wizard.step_2(width=24, height=12)

    def test_step_2_zero_width_raises(self):
        self.wizard.step_1(fitting_type="straight")
        with pytest.raises(ValueError):
            self.wizard.step_2(width=0, height=12)

    def test_step_3_sets_connection(self):
        self.wizard.step_1(fitting_type="straight")
        self.wizard.step_2(width=24, height=12)
        state = self.wizard.step_3(connection_type="tdc")
        assert state["connection_type"] == "tdc"

    def test_step_3_without_step_2_raises(self):
        self.wizard.step_1(fitting_type="straight")
        with pytest.raises(RuntimeError):
            self.wizard.step_3(connection_type="raw")

    def test_step_3_invalid_connection_raises(self):
        self.wizard.step_1(fitting_type="straight")
        self.wizard.step_2(width=24, height=12)
        with pytest.raises(ValueError):
            self.wizard.step_3(connection_type="bolted_flange")

    def test_step_4_returns_result(self):
        self.wizard.step_1(fitting_type="elbow_90")
        self.wizard.step_2(width=24, height=12)
        self.wizard.step_3(connection_type="tdc")
        result = self.wizard.step_4(pressure_class="2")
        assert result["fitting_type"] == "elbow_90"
        assert result["geometry_core_compatible"] is True
        assert "bom_data" in result
        assert "manufacturing_data" in result

    def test_step_4_without_step_3_raises(self):
        self.wizard.step_1(fitting_type="straight")
        self.wizard.step_2(width=24, height=12)
        with pytest.raises(RuntimeError):
            self.wizard.step_4()


class TestBuildSingleCall:
    def setup_method(self):
        self.wizard = SMACNAGuidedWizard()

    @pytest.mark.parametrize("ft", [
        "straight", "elbow_90", "elbow_45", "transition",
        "reducer", "square_to_round", "offset_z", "tee",
    ])
    def test_all_fitting_types(self, ft):
        result = self.wizard.build(
            fitting_type=ft, width=24, height=12
        )
        assert result["fitting_type"] == ft

    def test_bom_has_items(self):
        result = self.wizard.build(
            fitting_type="straight", width=24, height=12
        )
        assert "bom_data" in result
        assert len(result["bom_data"]["items"]) >= 1

    def test_bom_includes_turning_vanes(self):
        result = self.wizard.build(
            fitting_type="elbow_90", width=24, height=12,
            connection_type="tdc", turning_vanes=True,
        )
        parts = [item["part"] for item in result["bom_data"]["items"]]
        assert "turning_vanes" in parts

    def test_bom_includes_flange_system(self):
        result = self.wizard.build(
            fitting_type="straight", width=24, height=12,
            connection_type="tdc",
        )
        parts = [item["part"] for item in result["bom_data"]["items"]]
        assert "flange_system" in parts

    def test_manufacturing_ready_flag_valid(self):
        result = self.wizard.build(
            fitting_type="straight", width=24, height=12
        )
        assert result["manufacturing_ready"] is True

    def test_wizard_steps_completed(self):
        result = self.wizard.build(
            fitting_type="straight", width=24, height=12
        )
        assert result["wizard_steps_completed"] == 4

    def test_gauge_auto_selected(self):
        result = self.wizard.build(
            fitting_type="straight", width=24, height=12, pressure_class="2"
        )
        assert result["gauge"] == 24  # SMACNA minimum for 24" at 2 WG

    def test_reinforcement_large_duct(self):
        result = self.wizard.build(
            fitting_type="straight", width=30, height=24, pressure_class="2"
        )
        assert result["reinforcement_required"] is True

    def test_reset_clears_state(self):
        self.wizard.step_1(fitting_type="straight")
        self.wizard.reset()
        with pytest.raises(RuntimeError):
            self.wizard.step_2(width=24, height=12)
