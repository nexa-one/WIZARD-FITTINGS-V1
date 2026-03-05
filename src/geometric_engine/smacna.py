"""
SMACNA (Sheet Metal and Air Conditioning Contractors' National Association)
standards implementation.

References
----------
* SMACNA HVAC Duct Construction Standards – Metal and Flexible, 3rd edition.
* Table 1-13  : Minimum gauges for rectangular galvanized steel ducts.
* Table 1-14  : Reinforcement requirements.
* Section 4.6 : Transition/reducer slope limits (max 30° included angle).

All dimensions are in **inches**; pressure in **inches water gauge (WG)**.
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

from geometric_engine.models import (
    FittingParameters,
    FittingType,
    PressureClass,
    ValidationReport,
)

# ---------------------------------------------------------------------------
# Gauge tables
# ---------------------------------------------------------------------------
# Structured as a list of (max_longest_side, gauge) tuples per pressure tier.
# Pressure tiers (WG):
#   LOW    : ≤ 2" WG
#   MEDIUM : > 2" and ≤ 4" WG
#   HIGH   : > 4" WG

_GAUGE_TABLE_LOW = [
    (12, 26),
    (30, 24),
    (54, 22),
    (84, 20),
    (96, 18),
    (float("inf"), 16),
]

_GAUGE_TABLE_MEDIUM = [
    (12, 24),
    (30, 22),
    (54, 20),
    (84, 18),
    (float("inf"), 16),
]

_GAUGE_TABLE_HIGH = [
    (12, 24),
    (30, 22),
    (54, 18),
    (float("inf"), 16),
]

# Reinforcement required when longest side exceeds this threshold (in.)
# for a given pressure tier.
_REINF_THRESHOLD_LOW: float = 24.0
_REINF_THRESHOLD_MEDIUM: float = 19.0
_REINF_THRESHOLD_HIGH: float = 12.0

# ---------------------------------------------------------------------------
# Helpers – pressure tier
# ---------------------------------------------------------------------------


def _pressure_value(pressure_class: PressureClass) -> float:
    """Return numeric water-gauge value for a PressureClass."""
    return float(pressure_class.value)


def _pressure_tier(pressure_class: PressureClass) -> str:
    wg = _pressure_value(pressure_class)
    if wg <= 2.0:
        return "low"
    if wg <= 4.0:
        return "medium"
    return "high"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def minimum_gauge(width: float, height: float, pressure_class: PressureClass) -> int:
    """
    Return the minimum SMACNA gauge (higher number = thinner sheet).

    Parameters
    ----------
    width, height:
        Duct cross-section dimensions in inches.
    pressure_class:
        Operating static-pressure class.
    """
    longest_side = max(width, height)
    tier = _pressure_tier(pressure_class)

    table = {
        "low": _GAUGE_TABLE_LOW,
        "medium": _GAUGE_TABLE_MEDIUM,
        "high": _GAUGE_TABLE_HIGH,
    }[tier]

    for max_side, gauge in table:
        if longest_side <= max_side:
            return gauge
    return 16  # fallback (should not reach here due to inf sentinel)


def reinforcement_required(
    width: float, height: float, pressure_class: PressureClass
) -> bool:
    """Return True when SMACNA requires transverse reinforcement."""
    longest_side = max(width, height)
    tier = _pressure_tier(pressure_class)
    thresholds = {
        "low": _REINF_THRESHOLD_LOW,
        "medium": _REINF_THRESHOLD_MEDIUM,
        "high": _REINF_THRESHOLD_HIGH,
    }
    return longest_side > thresholds[tier]


def transition_minimum_length(
    width_in: float,
    height_in: float,
    width_out: float,
    height_out: float,
    max_half_angle_deg: float = 15.0,
) -> float:
    """
    Return the minimum transition length (in.) to keep the included angle
    ≤ 30° (i.e. each side ≤ 15°) per SMACNA Section 4.6.

    The critical plane is whichever produces the greater required length.
    """
    if max_half_angle_deg <= 0:
        raise ValueError("max_half_angle_deg must be positive")
    tan_angle = math.tan(math.radians(max_half_angle_deg))
    # Half-change in each direction
    delta_w = abs(width_out - width_in) / 2.0
    delta_h = abs(height_out - height_in) / 2.0
    # Required length for each plane
    length_w = delta_w / tan_angle if delta_w > 0 else 0.0
    length_h = delta_h / tan_angle if delta_h > 0 else 0.0
    return max(length_w, length_h)


def elbow_radius(width: float) -> float:
    """Return the SMACNA default centerline radius for a rectangular elbow."""
    return width * 1.5


def apply_defaults(params: FittingParameters) -> FittingParameters:
    """
    Fill in default lengths / radii / necks according to system defaults and
    SMACNA rules for any unspecified optional fields.  Returns the *same*
    object (mutated in place) for convenience.
    """
    from geometric_engine.models import (
        STRAIGHT_DEFAULT_LENGTH,
        DEFAULT_NECK_LENGTH,
    )

    ft = params.fitting_type

    # Length defaults
    if params.length is None:
        if ft == FittingType.STRAIGHT:
            params.length = STRAIGHT_DEFAULT_LENGTH
        elif ft in (FittingType.ELBOW_90, FittingType.ELBOW_45):
            # elbow length ≈ arc length at centreline radius
            radius = elbow_radius(params.width)
            angle = 90.0 if ft == FittingType.ELBOW_90 else 45.0
            params.length = round(math.pi * radius * angle / 180.0, 4)
        elif ft in (FittingType.TRANSITION, FittingType.REDUCER):
            # Use minimum transition length as default
            w_out = params.neck_out if params.neck_out is not None else params.width * 0.5
            h_out = params.height * 0.5
            params.length = round(
                transition_minimum_length(params.width, params.height, w_out, h_out),
                4,
            )

    # Neck defaults
    if params.neck_in is None:
        params.neck_in = DEFAULT_NECK_LENGTH
    if params.neck_out is None:
        params.neck_out = DEFAULT_NECK_LENGTH

    # Angle defaults for elbows
    if params.angle is None:
        if ft == FittingType.ELBOW_90:
            params.angle = 90.0
        elif ft == FittingType.ELBOW_45:
            params.angle = 45.0

    return params


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def check_smacna_compliance(
    params: FittingParameters, report: ValidationReport
) -> None:
    """Add SMACNA-specific errors / warnings to *report*."""
    # Minimum gauge check (only when gauge_override supplied)
    if params.gauge_override is not None:
        required = minimum_gauge(params.width, params.height, params.pressure_class)
        if params.gauge_override > required:  # higher number = thinner
            report.add_error(
                f"Gauge override {params.gauge_override} is thinner than SMACNA "
                f"minimum {required} for {params.width}\"×{params.height}\" at "
                f"{params.pressure_class.value}\" WG."
            )
            report.smacna_compliant = False

    # Transition slope check
    if params.fitting_type in (FittingType.TRANSITION, FittingType.REDUCER):
        if params.length is not None and params.neck_out is not None:
            min_len = transition_minimum_length(
                params.width, params.height, params.neck_out, params.height
            )
            if params.length < min_len:
                report.add_warning(
                    f"Transition length {params.length}\" is shorter than SMACNA "
                    f"recommended minimum {min_len:.2f}\" (30° included angle rule)."
                )
