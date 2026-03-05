"""
WIZARD-FITTINGS Industrial Geometric Engine
============================================

Provides geometric modeling and calculation capabilities for HVAC ductwork
fittings per SMACNA standards (Sheet Metal and Air Conditioning Contractors'
National Association).

Usage::

    from geometric_engine.elements import RectangularElbow, RoundElbow
    from geometric_engine.core import Dimensions, UnitSystem

    dims = Dimensions(width=0.4, height=0.3, unit_system=UnitSystem.METRIC)
    elbow = RectangularElbow(dims, angle=90)
    print(elbow.surface_area())
    print(elbow.loss_coefficient())
"""

from .core.primitives import Point2D, Point3D, Vector2D, Vector3D
from .core.dimensions import Dimensions, UnitSystem
from .elements.base import FittingElement, FittingType
from .elements.ducts import RectangularDuct, RoundDuct, OvalDuct
from .elements.elbows import RectangularElbow, RoundElbow, MiteredElbow
from .elements.transitions import (
    RectangularTransition,
    RoundTransition,
    RectangularToRoundTransition,
)
from .elements.tees import RectangularTee, RoundTee, RectangularWye, RoundWye
from .elements.caps import RectangularCap, RoundCap

__all__ = [
    # Core primitives
    "Point2D",
    "Point3D",
    "Vector2D",
    "Vector3D",
    "Dimensions",
    "UnitSystem",
    # Base
    "FittingElement",
    "FittingType",
    # Duct sections
    "RectangularDuct",
    "RoundDuct",
    "OvalDuct",
    # Elbows
    "RectangularElbow",
    "RoundElbow",
    "MiteredElbow",
    # Transitions
    "RectangularTransition",
    "RoundTransition",
    "RectangularToRoundTransition",
    # Tees / Wyes
    "RectangularTee",
    "RoundTee",
    "RectangularWye",
    "RoundWye",
    # Caps
    "RectangularCap",
    "RoundCap",
]
