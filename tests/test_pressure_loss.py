"""Tests for pressure-loss calculation utilities."""

import math
import pytest

from geometric_engine.calculations.pressure_loss import (
    AIR_DENSITY_STD,
    dynamic_pressure,
    fitting_pressure_drop,
    reynolds_number,
    friction_factor,
    duct_pressure_drop,
    velocity_from_flow,
)


class TestDynamicPressure:
    def test_standard_air_5ms(self):
        # 0.5 * 1.2 * 5^2 = 15
        assert math.isclose(dynamic_pressure(5.0), 15.0)

    def test_zero_velocity(self):
        assert dynamic_pressure(0.0) == 0.0


class TestFittingPressureDrop:
    def test_elbow(self):
        # C=0.3, v=4 m/s -> ΔP = 0.3 * 0.5 * 1.2 * 16 = 2.88 Pa
        dp = fitting_pressure_drop(0.3, 4.0)
        assert math.isclose(dp, 2.88)


class TestReynoldsNumber:
    def test_typical_value(self):
        # v=5 m/s, D=0.5 m, rho=1.2, mu=1.81e-5
        re = reynolds_number(5.0, 0.5)
        expected = 1.2 * 5.0 * 0.5 / 1.81e-5
        assert math.isclose(re, expected)


class TestFrictionFactor:
    def test_laminar(self):
        f = friction_factor(1000)
        assert math.isclose(f, 64 / 1000)

    def test_turbulent_positive(self):
        f = friction_factor(100_000, relative_roughness=0.0001)
        assert 0.01 < f < 0.05

    def test_negative_roughness_raises(self):
        with pytest.raises(ValueError):
            friction_factor(10_000, relative_roughness=-0.001)

    def test_nonpositive_re_raises(self):
        with pytest.raises(ValueError):
            friction_factor(0)


class TestDuctPressureDrop:
    def test_positive_drop(self):
        dp = duct_pressure_drop(
            velocity=5.0,
            length=10.0,
            hydraulic_diameter=0.4,
        )
        assert dp > 0

    def test_proportional_to_length(self):
        dp1 = duct_pressure_drop(5.0, length=5.0, hydraulic_diameter=0.4)
        dp2 = duct_pressure_drop(5.0, length=10.0, hydraulic_diameter=0.4)
        assert math.isclose(dp2, dp1 * 2, rel_tol=0.01)


class TestVelocityFromFlow:
    def test_basic(self):
        v = velocity_from_flow(flow_rate=1.0, area=0.5)
        assert math.isclose(v, 2.0)

    def test_zero_area_raises(self):
        with pytest.raises(ValueError):
            velocity_from_flow(1.0, area=0.0)

    def test_negative_area_raises(self):
        with pytest.raises(ValueError):
            velocity_from_flow(1.0, area=-0.1)

    def test_negative_flow_rate_raises(self):
        with pytest.raises(ValueError):
            velocity_from_flow(-0.5, area=0.5)

    def test_zero_flow_rate(self):
        assert velocity_from_flow(0.0, area=0.5) == 0.0
