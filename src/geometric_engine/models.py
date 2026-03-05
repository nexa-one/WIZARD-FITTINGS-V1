"""
Core data models for the enterprise HVAC AI system.

All dimensions are in **inches**.  The system targets SMACNA rectangular
duct standards; default rules (from the system specification) are encoded
as module-level constants so every module can import them without circular
dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# System-wide default rules (spec: default_rules)
# ---------------------------------------------------------------------------

UNITS: str = "inches"
STRAIGHT_DEFAULT_LENGTH: float = 56.0
DEFAULT_NECK_LENGTH: float = 6.0
TRANSITIONS_DEFAULT_ALIGNMENT: str = "centered"
ELBOW_DEFAULT_RADIUS_MULTIPLIER: float = 1.5  # radius = width * 1.5
AUTO_GAUGE_SELECTION: bool = True
SMACNA_ENFORCEMENT: bool = True

SYSTEM_CONFIG: Dict[str, Any] = {
    "version": "1.0.0",
    "units": UNITS,
    "default_rules": {
        "straight_default_length": STRAIGHT_DEFAULT_LENGTH,
        "default_neck_length": DEFAULT_NECK_LENGTH,
        "transitions_default_alignment": TRANSITIONS_DEFAULT_ALIGNMENT,
        "elbow_default_radius_formula": "width * 1.5",
        "auto_gauge_selection": AUTO_GAUGE_SELECTION,
        "smacna_enforcement": SMACNA_ENFORCEMENT,
    },
}


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class FittingType(str, Enum):
    """Supported HVAC fitting types."""

    STRAIGHT = "straight"
    ELBOW_90 = "elbow_90"
    ELBOW_45 = "elbow_45"
    TRANSITION = "transition"
    REDUCER = "reducer"
    SQUARE_TO_ROUND = "square_to_round"
    OFFSET_Z = "offset_z"
    TEE = "tee"


class ConnectionType(str, Enum):
    """Duct connection / flange types."""

    RAW = "raw"
    TDC = "tdc"
    DUCTMATE_FRAME = "ductmate_frame"
    SLIP_AND_DRIVE = "slip_and_drive"


class InsulationType(str, Enum):
    """Duct insulation / wall construction types."""

    SINGLE_WALL = "single_wall"
    DOUBLE_WALL = "double_wall"
    INTERNAL_LINER = "internal_liner"


class PressureClass(str, Enum):
    """SMACNA static-pressure classes (water gauge)."""

    WG_0_5 = "0.5"
    WG_1 = "1"
    WG_2 = "2"
    WG_3 = "3"
    WG_4 = "4"
    WG_6 = "6"
    WG_10 = "10"


# ---------------------------------------------------------------------------
# Parameter containers
# ---------------------------------------------------------------------------


@dataclass
class FittingParameters:
    """
    Complete set of parameters describing one HVAC fitting.

    Required fields are *fitting_type*, *width*, and *height*.
    All other fields are optional and will be filled in with SMACNA defaults
    when not supplied.
    """

    fitting_type: FittingType
    width: float
    height: float

    # Optional dimensions
    length: Optional[float] = None
    neck_in: Optional[float] = None
    neck_out: Optional[float] = None
    angle: Optional[float] = None  # degrees

    # Connection / construction
    connection_type: ConnectionType = ConnectionType.RAW
    pressure_class: PressureClass = PressureClass.WG_2
    gauge_override: Optional[int] = None
    turning_vanes: bool = False
    insulation_type: InsulationType = InsulationType.SINGLE_WALL
    water_gauge: Optional[float] = None
    flange_out: bool = False
    corner_fill: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.fitting_type, str):
            self.fitting_type = FittingType(self.fitting_type)
        if isinstance(self.connection_type, str):
            self.connection_type = ConnectionType(self.connection_type)
        if isinstance(self.pressure_class, str):
            self.pressure_class = PressureClass(self.pressure_class)
        if isinstance(self.insulation_type, str):
            self.insulation_type = InsulationType(self.insulation_type)


# ---------------------------------------------------------------------------
# Validation report
# ---------------------------------------------------------------------------


@dataclass
class ValidationReport:
    """Structured record of all validation checks run against a fitting."""

    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    smacna_compliant: bool = True
    geometry_valid: bool = True
    fabrication_feasible: bool = True

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "smacna_compliant": self.smacna_compliant,
            "geometry_valid": self.geometry_valid,
            "fabrication_feasible": self.fabrication_feasible,
        }


# ---------------------------------------------------------------------------
# Fitting result (output)
# ---------------------------------------------------------------------------


@dataclass
class FittingResult:
    """
    Complete output for a resolved fitting, ready for downstream geometry
    processing or BOM generation.
    """

    parameters: FittingParameters
    gauge: int
    reinforcement_required: bool
    surface_area: float  # sq-in
    material_weight: float  # lb (galvanized steel ≈ 2.156 lb/sq-ft at 24 ga)
    geometry: Dict[str, Any]
    validation_report: ValidationReport
    bom_data: Dict[str, Any] = field(default_factory=dict)
    manufacturing_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        p = self.parameters
        return {
            "fitting_type": p.fitting_type.value,
            "dimensions": {
                "width": p.width,
                "height": p.height,
                "length": p.length,
                "neck_in": p.neck_in,
                "neck_out": p.neck_out,
                "angle": p.angle,
            },
            "connection_type": p.connection_type.value,
            "pressure_class": p.pressure_class.value,
            "gauge": self.gauge,
            "turning_vanes": p.turning_vanes,
            "insulation_type": p.insulation_type.value,
            "reinforcement_required": self.reinforcement_required,
            "surface_area_sq_in": self.surface_area,
            "material_weight_lb": self.material_weight,
            "geometry": self.geometry,
            "validation_report": self.validation_report.to_dict(),
            "bom_data": self.bom_data,
            "manufacturing_data": self.manufacturing_data,
        }
