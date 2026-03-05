"""Tests for the Dimensions class and unit conversion helpers."""

import math
import pytest
from geometric_engine.core.dimensions import (
    Dimensions,
    UnitSystem,
    inches_to_metres,
    metres_to_inches,
    feet_to_metres,
    metres_to_feet,
)


class TestConversions:
    def test_inch_metre_roundtrip(self):
        assert math.isclose(metres_to_inches(inches_to_metres(12.0)), 12.0)

    def test_feet_metre_roundtrip(self):
        assert math.isclose(metres_to_feet(feet_to_metres(5.0)), 5.0)

    def test_one_inch_in_metres(self):
        assert math.isclose(inches_to_metres(1.0), 0.0254)

    def test_one_foot_in_metres(self):
        assert math.isclose(feet_to_metres(1.0), 0.3048)


class TestDimensionsRectangular:
    def setup_method(self):
        self.dims = Dimensions(width=0.4, height=0.3)  # metric, m

    def test_area(self):
        assert math.isclose(self.dims.cross_section_area(), 0.12)

    def test_perimeter(self):
        assert math.isclose(self.dims.perimeter(), 1.4)

    def test_hydraulic_diameter(self):
        # D_h = 4A/P = 4*0.12 / 1.4
        expected = 4 * 0.12 / 1.4
        assert math.isclose(self.dims.hydraulic_diameter(), expected)

    def test_aspect_ratio(self):
        assert math.isclose(self.dims.aspect_ratio(), 0.4 / 0.3)


class TestDimensionsRound:
    def setup_method(self):
        self.dims = Dimensions(diameter=0.5)

    def test_area(self):
        assert math.isclose(self.dims.cross_section_area(), math.pi * 0.25**2)

    def test_perimeter(self):
        assert math.isclose(self.dims.perimeter(), math.pi * 0.5)

    def test_hydraulic_diameter_equals_diameter(self):
        assert math.isclose(self.dims.hydraulic_diameter(), 0.5)

    def test_aspect_ratio_raises(self):
        with pytest.raises(ValueError):
            self.dims.aspect_ratio()


class TestDimensionsOval:
    def setup_method(self):
        self.dims = Dimensions(major_axis=0.6, minor_axis=0.3)

    def test_area(self):
        expected = math.pi * 0.3 * 0.15
        assert math.isclose(self.dims.cross_section_area(), expected)

    def test_perimeter_positive(self):
        assert self.dims.perimeter() > 0


class TestDimensionsImperial:
    def setup_method(self):
        # 16 in × 12 in duct
        self.dims = Dimensions(width=16.0, height=12.0, unit_system=UnitSystem.IMPERIAL)

    def test_width_m(self):
        assert math.isclose(self.dims.width_m, 16 * 0.0254)

    def test_area_in_m2(self):
        expected = 16 * 0.0254 * 12 * 0.0254
        assert math.isclose(self.dims.cross_section_area(), expected)


class TestDimensionsErrors:
    def test_area_raises_if_no_dims(self):
        with pytest.raises(ValueError):
            Dimensions().cross_section_area()

    def test_perimeter_raises_if_no_dims(self):
        with pytest.raises(ValueError):
            Dimensions().perimeter()
