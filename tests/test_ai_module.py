"""Tests for VisionAIModelGenerator (AI module)."""
import pytest

from geometric_engine.ai_module import (
    ACCEPTED_FORMATS,
    DETECTION_TARGETS,
    VisionAIModelGenerator,
    _extract_dimension,
    _extract_fitting_type,
)
from geometric_engine.models import FittingType


class TestAcceptedFormats:
    def test_formats_defined(self):
        assert "natural_language" in ACCEPTED_FORMATS
        assert "image_upload" in ACCEPTED_FORMATS


class TestDetectionTargets:
    def test_all_targets_present(self):
        required = {
            "fitting_type", "angle", "width", "height", "length",
            "neck_in", "neck_out", "pressure_class", "connection_type",
            "insulation_type",
        }
        assert required.issubset(set(DETECTION_TARGETS))


class TestExtractFittingType:
    def test_detects_straight(self):
        ft, conf = _extract_fitting_type("24x12 straight duct")
        assert ft is FittingType.STRAIGHT
        assert conf > 0

    def test_detects_elbow_90(self):
        ft, _ = _extract_fitting_type("90 degree elbow 24x12")
        assert ft is FittingType.ELBOW_90

    def test_detects_tee(self):
        ft, _ = _extract_fitting_type("tee fitting 24 wide")
        assert ft is FittingType.TEE

    def test_unrecognized_returns_none(self):
        ft, conf = _extract_fitting_type("unknown widget")
        assert ft is None
        assert conf == 0.0


class TestExtractDimension:
    def test_width_colon_format(self):
        assert _extract_dimension("width: 24", "width") == 24.0

    def test_wxh_format_width(self):
        assert _extract_dimension("24x12", "width") == 24.0

    def test_wxh_format_height(self):
        assert _extract_dimension("24x12", "height") == 12.0

    def test_dimension_after_label(self):
        assert _extract_dimension("24\" wide duct", "wide") == 24.0


class TestProcessNaturalLanguage:
    def setup_method(self):
        self.ai = VisionAIModelGenerator()

    def test_basic_straight(self):
        result = self.ai.process_natural_language("24x12 straight duct")
        assert result["fitting_type"] == "straight"
        assert result["dimensions"]["width"] == 24
        assert result["dimensions"]["height"] == 12
        assert "confidence_score" in result
        assert result["geometry_core_compatible"] is True

    def test_result_has_validation_report(self):
        result = self.ai.process_natural_language("24x12 straight duct")
        assert "validation_report" in result
        assert isinstance(result["validation_report"]["is_valid"], bool)

    def test_result_has_gauge(self):
        result = self.ai.process_natural_language("24x12 straight duct")
        assert "gauge" in result
        assert isinstance(result["gauge"], int)

    def test_tdc_connection_detected(self):
        result = self.ai.process_natural_language("24x12 straight duct, TDC connection")
        assert result["connection_type"] == "tdc"

    def test_elbow_90_detected(self):
        result = self.ai.process_natural_language("90 elbow 18x12")
        assert result["fitting_type"] == "elbow_90"

    def test_empty_description_raises(self):
        with pytest.raises(ValueError):
            self.ai.process_natural_language("")

    def test_missing_dimensions_raises(self):
        with pytest.raises(ValueError, match="width and height"):
            self.ai.process_natural_language("a straight duct, no dimensions here")

    def test_confidence_score_in_range(self):
        result = self.ai.process_natural_language("24x12 straight TDC 2 WG")
        score = result["confidence_score"]
        assert 0.0 <= score <= 1.0


class TestProcessImage:
    def setup_method(self):
        self.ai = VisionAIModelGenerator()

    def test_basic_image_metadata(self):
        result = self.ai.process_image({
            "fitting_type": "elbow_90",
            "width": 18,
            "height": 12,
            "confidence_score": 0.9,
        })
        assert result["fitting_type"] == "elbow_90"
        assert result["confidence_score"] == pytest.approx(0.9, abs=0.1)

    def test_geometry_core_compatible(self):
        result = self.ai.process_image({
            "fitting_type": "straight",
            "width": 24,
            "height": 12,
        })
        assert result["geometry_core_compatible"] is True

    def test_empty_metadata_raises(self):
        with pytest.raises(ValueError):
            self.ai.process_image({})

    def test_missing_dimensions_raises(self):
        with pytest.raises(ValueError):
            self.ai.process_image({"fitting_type": "straight"})

    def test_unknown_fitting_type_defaults_to_straight(self):
        result = self.ai.process_image({
            "fitting_type": "unknown_fitting",
            "width": 12,
            "height": 8,
        })
        assert result["fitting_type"] == "straight"

    def test_all_fitting_types_accepted(self):
        for ft in ("straight", "elbow_90", "elbow_45", "transition",
                   "reducer", "square_to_round", "offset_z", "tee"):
            result = self.ai.process_image({"fitting_type": ft, "width": 24, "height": 12})
            assert result["fitting_type"] == ft
