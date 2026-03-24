"""
WIZARD-FITTINGS-V1 – Phase 2: Manufacturing Engine
====================================================

Public API for the HVAC sheet-metal manufacturing engine.

Modules
-------
models       – data classes and enumerations
unwrap       – surface development (cylinder / cone / elbow / S2R)
flat_pattern – K-factor bend allowance & flat blank length
seam_engine  – seam allowance injection and corner notching
dxf_export   – AutoCAD R12 DXF serialisation
bom          – Bill of Materials generation and weight calculation

Quick-start example::

    from manufacturing_engine import (
        FittingParameters, FittingType, Material, SeamType,
        unwrap_fitting, apply_seam, export_flat_pattern,
        generate_bom, bom_to_csv,
    )

    params = FittingParameters(
        fitting_type=FittingType.CYLINDER,
        material=Material.GALVANIZED_STEEL,
        thickness_mm=0.8,
        seam_type=SeamType.PITTSBURGH,
        item_id="DUCT-001",
        system_name="SUPPLY-01",
        diameter_mm=300.0,
        length_mm=1000.0,
    )

    pattern = unwrap_fitting(params)
    pattern = apply_seam(pattern, params.seam_type)
    dxf = export_flat_pattern(pattern, params)
    bom = generate_bom([(pattern, params)])
    print(bom_to_csv(bom))
"""

from .models import (
    BOMItem,
    FittingParameters,
    FittingType,
    FlatPattern,
    Material,
    SeamType,
    Vector2D,
    Vector3D,
)
from .unwrap import (
    K_FACTOR,
    compute_bend_allowance,
    compute_bend_deduction,
    unwrap_cone,
    unwrap_cylinder,
    unwrap_elbow,
    unwrap_fitting,
    unwrap_square_to_round,
)
from .flat_pattern import (
    compute_flat_blank_length,
    neutral_bend_radius,
)
from .seam_engine import (
    SEAM_ALLOWANCES,
    apply_seam,
    generate_corner_notches,
)
from .dxf_export import (
    LAYER_BEND_LINES,
    LAYER_CUT_OUTLINE,
    LAYER_MARKING_TEXT,
    LAYER_NOTCHES,
    DXFWriter,
    export_flat_pattern,
)
from .bom import (
    MATERIAL_DENSITY,
    bom_to_csv,
    bom_to_json,
    calculate_weight,
    generate_bom,
)

__all__ = [
    # models
    "BOMItem",
    "FittingParameters",
    "FittingType",
    "FlatPattern",
    "Material",
    "SeamType",
    "Vector2D",
    "Vector3D",
    # unwrap
    "K_FACTOR",
    "compute_bend_allowance",
    "compute_bend_deduction",
    "unwrap_cone",
    "unwrap_cylinder",
    "unwrap_elbow",
    "unwrap_fitting",
    "unwrap_square_to_round",
    # flat_pattern
    "compute_flat_blank_length",
    "neutral_bend_radius",
    # seam_engine
    "SEAM_ALLOWANCES",
    "apply_seam",
    "generate_corner_notches",
    # dxf_export
    "LAYER_BEND_LINES",
    "LAYER_CUT_OUTLINE",
    "LAYER_MARKING_TEXT",
    "LAYER_NOTCHES",
    "DXFWriter",
    "export_flat_pattern",
    # bom
    "MATERIAL_DENSITY",
    "bom_to_csv",
    "bom_to_json",
    "calculate_weight",
    "generate_bom",
]

__version__ = "2.0.0"
