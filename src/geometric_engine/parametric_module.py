"""
Parametric Module – Manual Parametric Input System
====================================================
Spec: ``modules.parametric_module`` (Manual_Parametric_Input_System)

Industrial-grade manual fitting builder.  Accepts required inputs
(fitting_type, width, height) plus any subset of optional inputs and returns
a ``FittingResult`` with all automatic calculations applied.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from geometric_engine.geometry import compute_geometry, compute_surface_area, compute_weight
from geometric_engine.models import (
    AUTO_GAUGE_SELECTION,
    SMACNA_ENFORCEMENT,
    ConnectionType,
    FittingParameters,
    FittingResult,
    FittingType,
    InsulationType,
    PressureClass,
    ValidationReport,
)
from geometric_engine.smacna import (
    apply_defaults,
    minimum_gauge,
    reinforcement_required,
    transition_minimum_length,
)
from geometric_engine.validation import validate

# ---------------------------------------------------------------------------
# Spec-defined input/output lists (informational constants)
# ---------------------------------------------------------------------------

REQUIRED_INPUTS: List[str] = ["fitting_type", "width", "height"]

OPTIONAL_INPUTS: List[str] = [
    "length",
    "neck_in",
    "neck_out",
    "angle",
    "connection_type",
    "pressure_class",
    "gauge_override",
    "turning_vanes",
    "insulation_type",
    "water_gauge",
]

AUTOMATIC_CALCULATIONS: List[str] = [
    "minimum_gauge",
    "reinforcement_required",
    "transition_minimum_length",
    "material_weight",
    "surface_area",
]


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------


class ManualParametricInputSystem:
    """
    Manual industrial-grade parametric fitting builder.

    Spec: ``modules.parametric_module`` (Manual_Parametric_Input_System)

    Required inputs: *fitting_type*, *width*, *height*.
    All other fields are optional.  Default values and SMACNA calculations are
    applied automatically.

    Example
    -------
    >>> system = ManualParametricInputSystem()
    >>> result = system.build_fitting(
    ...     fitting_type="elbow_90",
    ...     width=24,
    ...     height=12,
    ...     connection_type="tdc",
    ...     pressure_class="2",
    ... )
    >>> result["gauge"]
    24
    """

    def __init__(
        self,
        *,
        auto_gauge_selection: bool = AUTO_GAUGE_SELECTION,
        smacna_enforcement: bool = SMACNA_ENFORCEMENT,
    ) -> None:
        self.auto_gauge_selection = auto_gauge_selection
        self.smacna_enforcement = smacna_enforcement

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_fitting(
        self,
        *,
        fitting_type: str,
        width: float,
        height: float,
        length: Optional[float] = None,
        neck_in: Optional[float] = None,
        neck_out: Optional[float] = None,
        angle: Optional[float] = None,
        connection_type: str = ConnectionType.RAW.value,
        pressure_class: str = PressureClass.WG_2.value,
        gauge_override: Optional[int] = None,
        turning_vanes: bool = False,
        insulation_type: str = InsulationType.SINGLE_WALL.value,
        water_gauge: Optional[float] = None,
        flange_out: bool = False,
        corner_fill: bool = False,
    ) -> Dict[str, Any]:
        """
        Build and validate a fitting from parametric inputs.

        Parameters
        ----------
        fitting_type:
            One of the supported fitting type strings (e.g. ``"straight"``,
            ``"elbow_90"``).
        width, height:
            Duct cross-section in inches.  Both must be > 0.
        length, neck_in, neck_out, angle:
            Optional dimensional overrides; SMACNA defaults applied when None.
        connection_type:
            Flange/connection style (default ``"raw"``).
        pressure_class:
            Static-pressure class in WG (default ``"2"``).
        gauge_override:
            Force a specific gauge; validated against SMACNA minimum.
        turning_vanes:
            Include turning vanes (elbows).
        insulation_type:
            Wall construction type.
        water_gauge:
            Actual operating pressure in WG when it differs from the class.
        flange_out, corner_fill:
            Advanced fabrication options.

        Returns
        -------
        dict
            ``geometry_core_compatible`` structured JSON with manufacturing data.

        Raises
        ------
        ValueError
            When required inputs are missing or dimensions are invalid.
        """
        if not fitting_type:
            raise ValueError("fitting_type is required")
        if width is None or height is None:
            raise ValueError("width and height are required")

        params = FittingParameters(
            fitting_type=FittingType(fitting_type),
            width=float(width),
            height=float(height),
            length=float(length) if length is not None else None,
            neck_in=float(neck_in) if neck_in is not None else None,
            neck_out=float(neck_out) if neck_out is not None else None,
            angle=float(angle) if angle is not None else None,
            connection_type=ConnectionType(connection_type),
            pressure_class=PressureClass(pressure_class),
            gauge_override=int(gauge_override) if gauge_override is not None else None,
            turning_vanes=bool(turning_vanes),
            insulation_type=InsulationType(insulation_type),
            water_gauge=float(water_gauge) if water_gauge is not None else None,
            flange_out=bool(flange_out),
            corner_fill=bool(corner_fill),
        )

        # Apply SMACNA defaults for any unspecified fields
        apply_defaults(params)

        # Validate
        validation_report = validate(params, smacna_enforcement=self.smacna_enforcement)

        # Gauge selection
        if self.auto_gauge_selection and params.gauge_override is None:
            gauge = minimum_gauge(params.width, params.height, params.pressure_class)
        else:
            gauge = params.gauge_override or minimum_gauge(
                params.width, params.height, params.pressure_class
            )

        # Geometry
        geometry = compute_geometry(params)
        surface_area = compute_surface_area(geometry)
        weight = compute_weight(surface_area, gauge)
        reinf = reinforcement_required(params.width, params.height, params.pressure_class)

        # Automatic calculations
        auto_calcs = self._compute_automatic_calculations(params, gauge, surface_area, weight)

        result = FittingResult(
            parameters=params,
            gauge=gauge,
            reinforcement_required=reinf,
            surface_area=surface_area,
            material_weight=weight,
            geometry=geometry,
            validation_report=validation_report,
            manufacturing_data=self._manufacturing_summary(params, gauge, reinf, weight),
        )

        output = result.to_dict()
        output["automatic_calculations"] = auto_calcs
        output["geometry_core_compatible"] = True
        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_automatic_calculations(
        self,
        params: FittingParameters,
        gauge: int,
        surface_area: float,
        weight: float,
    ) -> Dict[str, Any]:
        calcs: Dict[str, Any] = {
            "minimum_gauge": gauge,
            "reinforcement_required": reinforcement_required(
                params.width, params.height, params.pressure_class
            ),
            "surface_area_sq_in": round(surface_area, 4),
            "material_weight_lb": weight,
        }

        # Transition minimum length
        if params.fitting_type in (FittingType.TRANSITION, FittingType.REDUCER):
            w_out = params.neck_out if params.neck_out is not None else params.width * 0.5
            h_out = params.height
            calcs["transition_minimum_length"] = round(
                transition_minimum_length(params.width, params.height, w_out, h_out),
                4,
            )

        return calcs

    def _manufacturing_summary(
        self,
        params: FittingParameters,
        gauge: int,
        reinf: bool,
        weight: float,
    ) -> Dict[str, Any]:
        return {
            "gauge": gauge,
            "reinforcement_required": reinf,
            "connection_type": params.connection_type.value,
            "insulation_type": params.insulation_type.value,
            "turning_vanes": params.turning_vanes,
            "material_weight_lb": weight,
            "pressure_class_wg": params.pressure_class.value,
            "flange_out": params.flange_out,
            "corner_fill": params.corner_fill,
        }
