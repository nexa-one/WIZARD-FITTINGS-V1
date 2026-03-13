"""
cnc_module.models
=================
Core data-model classes for HVAC duct cross-sections, sheet-metal
properties, and SMACNA-style fittings.
"""

from cnc_module.models.duct import (
    DuctShape,
    RectangularDuct,
    RoundDuct,
    FlatOvalDuct,
)
from cnc_module.models.material import SheetMetal, GaugeTable
from cnc_module.models.fittings import (
    Fitting,
    StraightSection,
    RectangularElbow,
    RoundElbow,
    RectangularTransition,
    RoundToRectTransition,
    RectangularTee,
    RoundTee,
    RectangularReducer,
    EndCap,
)

__all__ = [
    "DuctShape",
    "RectangularDuct",
    "RoundDuct",
    "FlatOvalDuct",
    "SheetMetal",
    "GaugeTable",
    "Fitting",
    "StraightSection",
    "RectangularElbow",
    "RoundElbow",
    "RectangularTransition",
    "RoundToRectTransition",
    "RectangularTee",
    "RoundTee",
    "RectangularReducer",
    "EndCap",
]
