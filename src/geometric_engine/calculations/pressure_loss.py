"""
Pressure-loss calculation utilities for HVAC ductwork.

Functions in this module compute total pressure drop (Pa) for duct runs and
fittings given airflow conditions.  The calculations follow SMACNA HVAC
Duct Construction Standards and Idelchik's *Handbook of Hydraulic Resistance*.

Constants
---------
``AIR_DENSITY_STD``
    Standard air density at 20 °C, 101.325 kPa: 1.2 kg/m³.
``AIR_VISCOSITY_STD``
    Dynamic viscosity of air at 20 °C: 1.81×10⁻⁵ Pa·s.
"""

from __future__ import annotations

import math
from typing import Optional

AIR_DENSITY_STD: float = 1.2        # kg/m³ at 20 °C, 101.325 kPa
AIR_VISCOSITY_STD: float = 1.81e-5  # Pa·s at 20 °C


def dynamic_pressure(velocity: float, density: float = AIR_DENSITY_STD) -> float:
    """
    Compute the dynamic pressure (Pa).

        P_d = ½ · ρ · v²

    Parameters
    ----------
    velocity:
        Mean air velocity in m/s.
    density:
        Air density in kg/m³.  Defaults to standard air (1.2 kg/m³).
    """
    return 0.5 * density * velocity**2


def fitting_pressure_drop(
    loss_coefficient: float,
    velocity: float,
    density: float = AIR_DENSITY_STD,
) -> float:
    """
    Compute the total pressure drop across a fitting (Pa).

        ΔP = C · P_d = C · ½ · ρ · v²

    Parameters
    ----------
    loss_coefficient:
        Dimensionless loss coefficient *C* from :meth:`FittingElement.loss_coefficient`.
    velocity:
        Mean air velocity at the fitting inlet cross-section (m/s).
    density:
        Air density (kg/m³).
    """
    return loss_coefficient * dynamic_pressure(velocity, density)


def reynolds_number(
    velocity: float,
    hydraulic_diameter: float,
    density: float = AIR_DENSITY_STD,
    viscosity: float = AIR_VISCOSITY_STD,
) -> float:
    """
    Compute the Reynolds number for pipe/duct flow.

        Re = ρ · v · D_h / μ

    Parameters
    ----------
    velocity:
        Mean flow velocity (m/s).
    hydraulic_diameter:
        Hydraulic diameter of the cross-section (m).
    density:
        Fluid density (kg/m³).
    viscosity:
        Dynamic viscosity (Pa·s).
    """
    return density * velocity * hydraulic_diameter / viscosity


def friction_factor(reynolds: float, relative_roughness: float = 0.0001) -> float:
    """
    Compute the Darcy–Weisbach friction factor using the Swamee–Jain
    explicit approximation (valid for Re > 5 000 and ε/D < 0.02).

    For laminar flow (Re < 2 300) the exact value f = 64/Re is used.
    The transitional regime (2 300 ≤ Re < 5 000) is linearly interpolated.

    Parameters
    ----------
    reynolds:
        Reynolds number.
    relative_roughness:
        Pipe/duct roughness ε / D_h.  Typical values:

        * Galvanised steel: 0.00015 m → ε/D ≈ 0.0001 for D = 0.5 m
        * Fibreglass: ε = 0.0003 m
        * Flexible duct: ε = 0.009 m

    Returns
    -------
    float
        Darcy–Weisbach friction factor (dimensionless).
    """
    if reynolds <= 0:
        raise ValueError(f"Reynolds number must be positive; got {reynolds}.")
    if reynolds < 2300:
        return 64.0 / reynolds

    f_lam = 64.0 / 2300.0
    if relative_roughness < 0:
        raise ValueError("relative_roughness must be non-negative.")

    # Swamee–Jain
    f_turb = 0.25 / (
        math.log10(relative_roughness / 3.7 + 5.74 / (reynolds**0.9))
    ) ** 2

    if reynolds < 5000:
        t = (reynolds - 2300) / (5000 - 2300)
        return f_lam + t * (f_turb - f_lam)
    return f_turb


def duct_pressure_drop(
    velocity: float,
    length: float,
    hydraulic_diameter: float,
    relative_roughness: float = 0.0001,
    density: float = AIR_DENSITY_STD,
    viscosity: float = AIR_VISCOSITY_STD,
) -> float:
    """
    Compute the friction pressure drop along a straight duct run (Pa).

        ΔP = f · (L / D_h) · ½ · ρ · v²

    Parameters
    ----------
    velocity:
        Mean air velocity (m/s).
    length:
        Duct length (m).
    hydraulic_diameter:
        Hydraulic diameter of the cross-section (m).
    relative_roughness:
        Surface roughness ratio ε / D_h.
    density:
        Air density (kg/m³).
    viscosity:
        Dynamic viscosity (Pa·s).
    """
    re = reynolds_number(velocity, hydraulic_diameter, density, viscosity)
    f = friction_factor(re, relative_roughness)
    return f * (length / hydraulic_diameter) * dynamic_pressure(velocity, density)


def velocity_from_flow(flow_rate: float, area: float) -> float:
    """
    Compute the mean velocity (m/s) from volumetric flow rate and area.

        v = Q / A

    Parameters
    ----------
    flow_rate:
        Volumetric flow rate (m³/s).
    area:
        Cross-sectional area (m²).
    """
    if area <= 0:
        raise ValueError(f"Cross-sectional area must be positive; got {area}.")
    return flow_rate / area
