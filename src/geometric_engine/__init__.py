"""
WIZARD-FITTINGS Industrial Geometric Engine  v2.0.0
====================================================

Parametric geometric engine for all 87 SMACNA duct fittings.  Generates
isometric technical sketches with dimensions, annotations, export (PDF/STL/
STEP/PNG), and a three-theme renderer.

Quick start::

    from geometric_engine.registry.fitting_registry import get_fitting
    from geometric_engine.renderer.sketch import SketchGenerator
    from geometric_engine.export.exporter import FittingExporter

    gen  = SketchGenerator(theme="light_technical")
    sketch = gen.generate(
        fitting_id="RE-4",
        params={"W": 0.4, "H": 0.3, "R": 0.6},
        metadata={"project": "Site A"},
    )

    exp = FittingExporter()
    pdf_manifest = exp.export(sketch, fmt="pdf")
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
from .elements.offsets import (
    RectangularSingleOffset,
    RectangularDoubleOffset,
    RectangularSymmetricOffset,
    RectangularVerticalOffset,
    RectangularLateralOffset,
)
from .elements.oval import (
    OvalElbow90,
    OvalElbow45,
    OvalTee90,
    OvalWye45,
    OvalReducer,
    OvalToRound,
    OvalToRect,
    OvalOffset,
)
from .elements.special import (
    VolumeControlDamper,
    FireDamper,
    FireSmokeDamper,
    AccessDoor,
    FlexConnector,
    LinerThroat,
    CircularBellMouth,
    PlenumTakeoff,
    RegisterBoot,
    DoubleWallSection,
)
from .elements.supports import (
    StrapHanger,
    TrapezeBracket,
    ClevisHanger,
    BandHanger,
    BeamClamp,
    TieRod,
    SeismicLongitudinal,
    SeismicTransverse,
)
from .registry.fitting_registry import (
    FITTING_REGISTRY,
    FittingEntry,
    get_fitting,
    list_category,
    list_all_categories,
    registry_summary,
)
from .renderer.isometric import (
    IsometricProjection,
    iso_box,
    iso_cylinder,
    iso_cone,
    iso_elbow_arc,
    iso_flat_oval,
    iso_dim_line,
    iso_coord_cube,
    iso_title_block,
    iso_annotation_block,
)
from .renderer.theme import ThemeManager, THEMES
from .renderer.sketch import SketchGenerator
from .export.exporter import FittingExporter, ExportError

__version__ = "2.0.0"

__all__ = [
    # Core primitives
    "Point2D", "Point3D", "Vector2D", "Vector3D",
    "Dimensions", "UnitSystem",
    # Base
    "FittingElement", "FittingType",
    # Duct sections
    "RectangularDuct", "RoundDuct", "OvalDuct",
    # Elbows
    "RectangularElbow", "RoundElbow", "MiteredElbow",
    # Transitions
    "RectangularTransition", "RoundTransition", "RectangularToRoundTransition",
    # Tees / Wyes
    "RectangularTee", "RoundTee", "RectangularWye", "RoundWye",
    # Caps
    "RectangularCap", "RoundCap",
    # Offsets (RO)
    "RectangularSingleOffset", "RectangularDoubleOffset",
    "RectangularSymmetricOffset", "RectangularVerticalOffset",
    "RectangularLateralOffset",
    # Flat-oval (FO)
    "OvalElbow90", "OvalElbow45", "OvalTee90", "OvalWye45",
    "OvalReducer", "OvalToRound", "OvalToRect", "OvalOffset",
    # Special (SP)
    "VolumeControlDamper", "FireDamper", "FireSmokeDamper",
    "AccessDoor", "FlexConnector", "LinerThroat",
    "CircularBellMouth", "PlenumTakeoff", "RegisterBoot", "DoubleWallSection",
    # Supports (SU)
    "StrapHanger", "TrapezeBracket", "ClevisHanger", "BandHanger",
    "BeamClamp", "TieRod", "SeismicLongitudinal", "SeismicTransverse",
    # Registry
    "FITTING_REGISTRY", "FittingEntry",
    "get_fitting", "list_category", "list_all_categories", "registry_summary",
    # Renderer
    "IsometricProjection",
    "iso_box", "iso_cylinder", "iso_cone", "iso_elbow_arc", "iso_flat_oval",
    "iso_dim_line", "iso_coord_cube", "iso_title_block", "iso_annotation_block",
    "ThemeManager", "THEMES", "SketchGenerator",
    # Export
    "FittingExporter", "ExportError",
    # Version
    "__version__",
]

