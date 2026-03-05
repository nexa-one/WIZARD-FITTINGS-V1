"""
Wizard Module – SMACNA Guided Wizard
======================================
Spec: ``modules.wizard_fittings_module`` (SMACNA_Guided_Wizard)

Graphical step-by-step industrial fitting builder.  The wizard walks through
four sequential steps collecting inputs, applies automatic SMACNA behaviors,
and produces a manufacturing-ready validated-geometry JSON.

Steps
-----
1. Visual template selection (fitting type)
2. Dimension input (width, height, neck_in, neck_out, angle)
3. Connection selection (connection type)
4. Advanced parameters (turning vanes, gauge, pressure class, insulation …)
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from geometric_engine.geometry import compute_geometry, compute_surface_area, compute_weight
from geometric_engine.models import (
    AUTO_GAUGE_SELECTION,
    DEFAULT_NECK_LENGTH,
    SMACNA_ENFORCEMENT,
    STRAIGHT_DEFAULT_LENGTH,
    ConnectionType,
    FittingParameters,
    FittingResult,
    FittingType,
    InsulationType,
    PressureClass,
)
from geometric_engine.smacna import (
    apply_defaults,
    minimum_gauge,
    reinforcement_required,
)
from geometric_engine.validation import validate

# ---------------------------------------------------------------------------
# Spec-defined step schemas (informational)
# ---------------------------------------------------------------------------

STEP_1_OPTIONS: List[str] = [ft.value for ft in FittingType]
STEP_2_FIELDS: List[str] = ["width", "height", "neck_in", "neck_out", "angle"]
STEP_3_OPTIONS: List[str] = [ct.value for ct in ConnectionType]
STEP_4_FIELDS: List[str] = [
    "turning_vanes",
    "gauge",
    "pressure_class",
    "water_gauge",
    "insulation_type",
    "flange_out",
    "corner_fill",
]

# ---------------------------------------------------------------------------
# Automatic behaviors (spec: automatic_behaviors)
# ---------------------------------------------------------------------------

AUTOMATIC_BEHAVIORS: Dict[str, bool] = {
    "apply_default_neck_length": True,
    "apply_default_straight_length": True,
    "apply_centered_transitions": True,
    "apply_elbow_radius_formula": True,
    "auto_apply_smacna_gauge": True,
    "auto_insert_reinforcement": True,
}


class WizardState:
    """Holds intermediate state between wizard steps."""

    def __init__(self) -> None:
        self.step: int = 0
        self.fitting_type: Optional[FittingType] = None
        self.width: Optional[float] = None
        self.height: Optional[float] = None
        self.neck_in: Optional[float] = None
        self.neck_out: Optional[float] = None
        self.angle: Optional[float] = None
        self.connection_type: ConnectionType = ConnectionType.RAW
        self.pressure_class: PressureClass = PressureClass.WG_2
        self.gauge_override: Optional[int] = None
        self.turning_vanes: bool = False
        self.insulation_type: InsulationType = InsulationType.SINGLE_WALL
        self.water_gauge: Optional[float] = None
        self.flange_out: bool = False
        self.corner_fill: bool = False

    def is_complete(self) -> bool:
        return self.step >= 4 and self.fitting_type is not None \
            and self.width is not None and self.height is not None

    def to_summary(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "fitting_type": self.fitting_type.value if self.fitting_type else None,
            "width": self.width,
            "height": self.height,
            "neck_in": self.neck_in,
            "neck_out": self.neck_out,
            "angle": self.angle,
            "connection_type": self.connection_type.value,
            "pressure_class": self.pressure_class.value,
            "gauge_override": self.gauge_override,
            "turning_vanes": self.turning_vanes,
            "insulation_type": self.insulation_type.value,
            "water_gauge": self.water_gauge,
            "flange_out": self.flange_out,
            "corner_fill": self.corner_fill,
        }


class SMACNAGuidedWizard:
    """
    Graphical step-by-step SMACNA-compliant fitting builder.

    Spec: ``modules.wizard_fittings_module`` (SMACNA_Guided_Wizard)

    Usage
    -----
    The wizard can be used in two ways:

    **Step-by-step (interactive)**::

        wizard = SMACNAGuidedWizard()
        wizard.step_1(fitting_type="elbow_90")
        wizard.step_2(width=24, height=12)
        wizard.step_3(connection_type="tdc")
        result = wizard.step_4(pressure_class="2")

    **Single-call (programmatic)**::

        wizard = SMACNAGuidedWizard()
        result = wizard.build(
            fitting_type="elbow_90",
            width=24,
            height=12,
            connection_type="tdc",
            pressure_class="2",
        )
    """

    def __init__(
        self,
        *,
        auto_gauge_selection: bool = AUTO_GAUGE_SELECTION,
        smacna_enforcement: bool = SMACNA_ENFORCEMENT,
    ) -> None:
        self.auto_gauge_selection = auto_gauge_selection
        self.smacna_enforcement = smacna_enforcement
        self._state = WizardState()

    # ------------------------------------------------------------------
    # Step methods
    # ------------------------------------------------------------------

    def step_1(self, *, fitting_type: str) -> Dict[str, Any]:
        """
        Step 1 – Visual template selection.

        Parameters
        ----------
        fitting_type:
            One of the supported fitting type strings.

        Returns
        -------
        dict
            Current wizard state summary.
        """
        if fitting_type not in STEP_1_OPTIONS:
            raise ValueError(
                f"fitting_type must be one of {STEP_1_OPTIONS}, got '{fitting_type}'"
            )
        self._state.fitting_type = FittingType(fitting_type)
        self._state.step = 1
        return self._state.to_summary()

    def step_2(
        self,
        *,
        width: float,
        height: float,
        neck_in: Optional[float] = None,
        neck_out: Optional[float] = None,
        angle: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Step 2 – Dimension input.

        Parameters
        ----------
        width, height:
            Cross-section in inches; both must be > 0.
        neck_in, neck_out:
            Inlet/outlet neck lengths; SMACNA default (6") applied when None.
        angle:
            For elbows; auto-set from fitting type when None.

        Returns
        -------
        dict
            Current wizard state summary.
        """
        if self._state.step < 1:
            raise RuntimeError("Step 1 (fitting type selection) must be completed first.")
        if width <= 0 or height <= 0:
            raise ValueError("width and height must be > 0")

        self._state.width = float(width)
        self._state.height = float(height)
        # Apply default neck lengths if not provided
        self._state.neck_in = float(neck_in) if neck_in is not None else DEFAULT_NECK_LENGTH
        self._state.neck_out = float(neck_out) if neck_out is not None else DEFAULT_NECK_LENGTH
        self._state.angle = float(angle) if angle is not None else None
        self._state.step = 2
        return self._state.to_summary()

    def step_3(self, *, connection_type: str) -> Dict[str, Any]:
        """
        Step 3 – Connection type selection.

        Parameters
        ----------
        connection_type:
            One of ``"raw"``, ``"tdc"``, ``"ductmate_frame"``,
            ``"slip_and_drive"``.

        Returns
        -------
        dict
            Current wizard state summary.
        """
        if self._state.step < 2:
            raise RuntimeError("Step 2 (dimension input) must be completed first.")
        if connection_type not in STEP_3_OPTIONS:
            raise ValueError(
                f"connection_type must be one of {STEP_3_OPTIONS}, "
                f"got '{connection_type}'"
            )
        self._state.connection_type = ConnectionType(connection_type)
        self._state.step = 3
        return self._state.to_summary()

    def step_4(
        self,
        *,
        turning_vanes: bool = False,
        gauge: Optional[int] = None,
        pressure_class: str = PressureClass.WG_2.value,
        water_gauge: Optional[float] = None,
        insulation_type: str = InsulationType.SINGLE_WALL.value,
        flange_out: bool = False,
        corner_fill: bool = False,
    ) -> Dict[str, Any]:
        """
        Step 4 – Advanced parameters; returns the completed fitting result.

        Returns
        -------
        dict
            ``validated_geometry_json`` with BOM and manufacturing data.
        """
        if self._state.step < 3:
            raise RuntimeError("Step 3 (connection selection) must be completed first.")

        self._state.turning_vanes = bool(turning_vanes)
        self._state.gauge_override = int(gauge) if gauge is not None else None
        self._state.pressure_class = PressureClass(pressure_class)
        self._state.water_gauge = float(water_gauge) if water_gauge is not None else None
        self._state.insulation_type = InsulationType(insulation_type)
        self._state.flange_out = bool(flange_out)
        self._state.corner_fill = bool(corner_fill)
        self._state.step = 4

        return self._finalise()

    # ------------------------------------------------------------------
    # Single-call convenience
    # ------------------------------------------------------------------

    def build(
        self,
        *,
        fitting_type: str,
        width: float,
        height: float,
        neck_in: Optional[float] = None,
        neck_out: Optional[float] = None,
        angle: Optional[float] = None,
        connection_type: str = ConnectionType.RAW.value,
        turning_vanes: bool = False,
        gauge: Optional[int] = None,
        pressure_class: str = PressureClass.WG_2.value,
        water_gauge: Optional[float] = None,
        insulation_type: str = InsulationType.SINGLE_WALL.value,
        flange_out: bool = False,
        corner_fill: bool = False,
    ) -> Dict[str, Any]:
        """
        Build a fitting in a single call (all four wizard steps at once).

        Returns
        -------
        dict
            ``validated_geometry_json`` with BOM and manufacturing data.
        """
        self._state = WizardState()  # reset
        self.step_1(fitting_type=fitting_type)
        self.step_2(width=width, height=height, neck_in=neck_in, neck_out=neck_out, angle=angle)
        self.step_3(connection_type=connection_type)
        return self.step_4(
            turning_vanes=turning_vanes,
            gauge=gauge,
            pressure_class=pressure_class,
            water_gauge=water_gauge,
            insulation_type=insulation_type,
            flange_out=flange_out,
            corner_fill=corner_fill,
        )

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Reset the wizard to its initial state."""
        self._state = WizardState()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _finalise(self) -> Dict[str, Any]:
        """Assemble FittingParameters from state, apply defaults, build output."""
        s = self._state
        assert s.fitting_type is not None
        assert s.width is not None and s.height is not None

        params = FittingParameters(
            fitting_type=s.fitting_type,
            width=s.width,
            height=s.height,
            neck_in=s.neck_in,
            neck_out=s.neck_out,
            angle=s.angle,
            connection_type=s.connection_type,
            pressure_class=s.pressure_class,
            gauge_override=s.gauge_override,
            turning_vanes=s.turning_vanes,
            insulation_type=s.insulation_type,
            water_gauge=s.water_gauge,
            flange_out=s.flange_out,
            corner_fill=s.corner_fill,
        )

        # Automatic behaviors (spec: automatic_behaviors)
        apply_defaults(params)  # neck lengths, straight/elbow lengths, angle

        # Validate
        validation_report = validate(
            params, smacna_enforcement=self.smacna_enforcement
        )

        # Auto gauge
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

        bom = self._build_bom(params, gauge, surface_area, weight, reinf)
        mfg = self._manufacturing_summary(params, gauge, reinf, weight)

        result = FittingResult(
            parameters=params,
            gauge=gauge,
            reinforcement_required=reinf,
            surface_area=surface_area,
            material_weight=weight,
            geometry=geometry,
            validation_report=validation_report,
            bom_data=bom,
            manufacturing_data=mfg,
        )

        output = result.to_dict()
        output["geometry_core_compatible"] = True
        output["manufacturing_ready"] = validation_report.is_valid
        output["wizard_steps_completed"] = self._state.step
        return output

    def _build_bom(
        self,
        params: FittingParameters,
        gauge: int,
        surface_area: float,
        weight: float,
        reinf: bool,
    ) -> Dict[str, Any]:
        bom: Dict[str, Any] = {
            "items": [
                {
                    "part": "galvanized_steel_sheet",
                    "gauge": gauge,
                    "surface_area_sq_in": round(surface_area, 4),
                    "weight_lb": weight,
                    "quantity": 1,
                }
            ]
        }
        if reinf:
            bom["items"].append(
                {
                    "part": "transverse_reinforcement",
                    "type": "hat_channel" if params.pressure_class in (
                        PressureClass.WG_0_5, PressureClass.WG_1, PressureClass.WG_2
                    ) else "angle_iron",
                    "quantity": "as_required",
                }
            )
        if params.turning_vanes:
            bom["items"].append(
                {"part": "turning_vanes", "material": "galvanized_steel", "quantity": 1}
            )
        if params.connection_type != ConnectionType.RAW:
            bom["items"].append(
                {
                    "part": "flange_system",
                    "type": params.connection_type.value,
                    "quantity": 2,
                }
            )
        return bom

    def _manufacturing_summary(
        self,
        params: FittingParameters,
        gauge: int,
        reinf: bool,
        weight: float,
    ) -> Dict[str, Any]:
        return {
            "fitting_type": params.fitting_type.value,
            "gauge": gauge,
            "reinforcement_required": reinf,
            "connection_type": params.connection_type.value,
            "insulation_type": params.insulation_type.value,
            "turning_vanes": params.turning_vanes,
            "material_weight_lb": weight,
            "pressure_class_wg": params.pressure_class.value,
            "flange_out": params.flange_out,
            "corner_fill": params.corner_fill,
            "smacna_compliant": True,
        }
