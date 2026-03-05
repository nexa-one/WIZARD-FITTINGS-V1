"""
Flat-pattern bend compensation using the K-factor method.

K-factor (0.44) represents the position of the neutral axis relative to
the inside bend radius.  All calculations follow SMACNA sheet-metal
fabrication standards.

All measurements in mm.  Precision: 4 decimal places.
"""

from __future__ import annotations

import math
from typing import List, Sequence

from .unwrap import K_FACTOR, compute_bend_allowance, compute_bend_deduction

__all__ = [
    "K_FACTOR",
    "compute_bend_allowance",
    "compute_bend_deduction",
    "compute_flat_blank_length",
    "neutral_bend_radius",
]


def neutral_bend_radius(inside_radius_mm: float, thickness_mm: float,
                        k_factor: float = K_FACTOR) -> float:
    """Return the neutral-axis radius for a sheet-metal bend.

    Formula:
        R_neutral = R_inside + K × t

    Args:
        inside_radius_mm: Inside bend radius in mm.
        thickness_mm:     Sheet thickness in mm.
        k_factor:         K-factor (default 0.44).

    Returns:
        Neutral-axis bend radius in mm, rounded to 4 d.p.
    """
    return round(inside_radius_mm + k_factor * thickness_mm, 4)


def compute_flat_blank_length(
    flange_lengths_mm: Sequence[float],
    bend_angles_deg: Sequence[float],
    bend_radii_mm: Sequence[float],
    thickness_mm: float,
    k_factor: float = K_FACTOR,
) -> float:
    """Compute the total flat blank length for a part with multiple bends.

    The flat blank length equals the sum of all flat (unbent) flange
    lengths plus the bend allowances for each bend.

    Formula:
        L_blank = Σ flange_lengths + Σ BA_i

    where BA_i = angle_i_rad × (R_i + K × t)

    Args:
        flange_lengths_mm: List of straight-flange lengths (N+1 values for
                           N bends, or N values—both interpretations give the
                           same total when used consistently).
        bend_angles_deg:   List of bend angles in degrees (N values).
        bend_radii_mm:     List of inside bend radii in mm (N values).
        thickness_mm:      Sheet thickness in mm.
        k_factor:          K-factor (default 0.44).

    Returns:
        Total flat blank length in mm, rounded to 4 d.p.

    Raises:
        ValueError: If bend_angles_deg and bend_radii_mm have different lengths.
    """
    if len(bend_angles_deg) != len(bend_radii_mm):
        raise ValueError(
            "bend_angles_deg and bend_radii_mm must have the same length; "
            f"got {len(bend_angles_deg)} and {len(bend_radii_mm)}."
        )

    total_flanges = sum(flange_lengths_mm)
    total_ba = sum(
        compute_bend_allowance(a, r, thickness_mm, k_factor)
        for a, r in zip(bend_angles_deg, bend_radii_mm)
    )
    return round(total_flanges + total_ba, 4)
