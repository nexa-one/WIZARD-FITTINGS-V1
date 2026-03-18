"""
cnc_module.flat_pattern.seam
============================
Seam allowance definitions and calculators.

HVAC sheet-metal seams (SMACNA classification)
-----------------------------------------------
PITTSBURGH  – Mechanical lock seam; adds ~15 mm on one edge + 5 mm on the other.
SNAP_LOCK   – Snap-lock seam (Duct-Mate style); adds ~8 mm on each edge.
LAP         – Simple lap / rivet seam; adds equal allowances on both edges.
BUTT        – Butt joint (no allowance needed on either edge; uses a separate
              cover strip instead).
GROOVED     – Grooved seam / double lock; adds ~12 mm on each edge.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class SeamType(Enum):
    PITTSBURGH = auto()
    SNAP_LOCK = auto()
    LAP = auto()
    BUTT = auto()
    GROOVED = auto()


@dataclass
class SeamAllowance:
    """Seam allowance dimensions for one seam type.

    Attributes
    ----------
    seam_type: The type of seam.
    allowance_a: Flat-pattern extension added to the *male* (inserted) edge (mm).
    allowance_b: Flat-pattern extension added to the *female* (receiving) edge (mm).
    description: Human-readable note.
    """

    seam_type: SeamType
    allowance_a: float   # male / cleat edge
    allowance_b: float   # female / channel edge
    description: str = ""

    @property
    def total(self) -> float:
        """Sum of both allowances (mm)."""
        return self.allowance_a + self.allowance_b


# Standard SMACNA seam allowances
SEAM_DEFAULTS: dict[SeamType, SeamAllowance] = {
    SeamType.PITTSBURGH: SeamAllowance(
        SeamType.PITTSBURGH,
        allowance_a=14.3,   # ~9/16 in – folded lip inserted into channel
        allowance_b=7.9,    # ~5/16 in – channel pocket
        description="Pittsburgh mechanical lock; most common for rectangular duct",
    ),
    SeamType.SNAP_LOCK: SeamAllowance(
        SeamType.SNAP_LOCK,
        allowance_a=8.0,
        allowance_b=8.0,
        description="Snap-lock seam – used on spiral / round duct",
    ),
    SeamType.LAP: SeamAllowance(
        SeamType.LAP,
        allowance_a=12.7,   # ½ in
        allowance_b=12.7,
        description="Lap seam with rivets or screws",
    ),
    SeamType.BUTT: SeamAllowance(
        SeamType.BUTT,
        allowance_a=0.0,
        allowance_b=0.0,
        description="Butt joint – cover strip applied externally",
    ),
    SeamType.GROOVED: SeamAllowance(
        SeamType.GROOVED,
        allowance_a=12.0,
        allowance_b=12.0,
        description="Double / grooved lock seam",
    ),
}


def get_seam_allowance(seam_type: SeamType) -> SeamAllowance:
    """Return the default :class:`SeamAllowance` for *seam_type*."""
    return SEAM_DEFAULTS[seam_type]
