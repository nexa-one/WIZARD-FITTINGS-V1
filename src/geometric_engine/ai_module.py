"""
AI Module – Vision AI Model Generator
======================================
Spec: ``modules.ai_module`` (Vision_AI_Model_Generator)

Accepts natural-language descriptions or image-upload metadata and returns a
``FittingResult`` with a confidence score and a full validation report.

Because no real ML/CV runtime is bundled (the system has *no runtime
dependencies*), the NL parser is a deterministic rule-based extractor and the
image handler works from structured metadata dicts.  In production, these
stubs would be replaced by calls to a real vision / LLM service while keeping
the same public interface.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

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
from geometric_engine.smacna import apply_defaults, minimum_gauge, reinforcement_required
from geometric_engine.validation import validate

# ---------------------------------------------------------------------------
# Supported I/O definitions (spec)
# ---------------------------------------------------------------------------

ACCEPTED_FORMATS: List[str] = ["natural_language", "image_upload"]

DETECTION_TARGETS: List[str] = [
    "fitting_type",
    "angle",
    "width",
    "height",
    "length",
    "neck_in",
    "neck_out",
    "pressure_class",
    "connection_type",
    "insulation_type",
]

# ---------------------------------------------------------------------------
# Natural-language keyword maps
# ---------------------------------------------------------------------------

_FITTING_TYPE_KEYWORDS: Dict[str, FittingType] = {
    "straight": FittingType.STRAIGHT,
    "90": FittingType.ELBOW_90,
    "elbow 90": FittingType.ELBOW_90,
    "elbow90": FittingType.ELBOW_90,
    "45": FittingType.ELBOW_45,
    "elbow 45": FittingType.ELBOW_45,
    "elbow45": FittingType.ELBOW_45,
    "transition": FittingType.TRANSITION,
    "reducer": FittingType.REDUCER,
    "square to round": FittingType.SQUARE_TO_ROUND,
    "square_to_round": FittingType.SQUARE_TO_ROUND,
    "offset": FittingType.OFFSET_Z,
    "offset_z": FittingType.OFFSET_Z,
    "z offset": FittingType.OFFSET_Z,
    "tee": FittingType.TEE,
}

_CONNECTION_KEYWORDS: Dict[str, ConnectionType] = {
    "tdc": ConnectionType.TDC,
    "ductmate": ConnectionType.DUCTMATE_FRAME,
    "slip": ConnectionType.SLIP_AND_DRIVE,
    "slip and drive": ConnectionType.SLIP_AND_DRIVE,
    "raw": ConnectionType.RAW,
}

_INSULATION_KEYWORDS: Dict[str, InsulationType] = {
    "single wall": InsulationType.SINGLE_WALL,
    "single_wall": InsulationType.SINGLE_WALL,
    "double wall": InsulationType.DOUBLE_WALL,
    "double_wall": InsulationType.DOUBLE_WALL,
    "liner": InsulationType.INTERNAL_LINER,
    "internal liner": InsulationType.INTERNAL_LINER,
    "internal_liner": InsulationType.INTERNAL_LINER,
}

_PRESSURE_KEYWORDS: Dict[str, PressureClass] = {
    "0.5": PressureClass.WG_0_5,
    "1 wg": PressureClass.WG_1,
    "1wg": PressureClass.WG_1,
    "2 wg": PressureClass.WG_2,
    "2wg": PressureClass.WG_2,
    "3 wg": PressureClass.WG_3,
    "3wg": PressureClass.WG_3,
    "4 wg": PressureClass.WG_4,
    "4wg": PressureClass.WG_4,
    "6 wg": PressureClass.WG_6,
    "6wg": PressureClass.WG_6,
    "10 wg": PressureClass.WG_10,
    "10wg": PressureClass.WG_10,
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _extract_fitting_type(text: str) -> Tuple[Optional[FittingType], float]:
    """Return (fitting_type, confidence) from NL text."""
    lower = text.lower()
    for keyword, ft in _FITTING_TYPE_KEYWORDS.items():
        if keyword in lower:
            return ft, 0.85
    return None, 0.0


def _extract_dimension(text: str, label: str) -> Optional[float]:
    """
    Extract a numeric dimension (inches) associated with *label* from text.
    Supports patterns like "24 wide", "width: 24", "24x12", "24\" wide".
    """
    patterns = [
        rf"{label}\s*[:\s=]\s*([0-9]+(?:\.[0-9]+)?)",
        rf"([0-9]+(?:\.[0-9]+)?)\s*[\"']?\s*{label}",
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

    # WxH shorthand (e.g. "24x12")
    if label in ("width", "w"):
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*[xX×]\s*[0-9]", text)
        if m:
            return float(m.group(1))
    if label in ("height", "h"):
        m = re.search(r"[0-9]+(?:\.[0-9]+)?\s*[xX×]\s*([0-9]+(?:\.[0-9]+)?)", text)
        if m:
            return float(m.group(1))
    return None


def _extract_connection(text: str) -> Optional[ConnectionType]:
    lower = text.lower()
    for kw, ct in _CONNECTION_KEYWORDS.items():
        if kw in lower:
            return ct
    return None


def _extract_insulation(text: str) -> Optional[InsulationType]:
    lower = text.lower()
    for kw, it in _INSULATION_KEYWORDS.items():
        if kw in lower:
            return it
    return None


def _extract_pressure(text: str) -> Optional[PressureClass]:
    lower = text.lower()
    for kw, pc in _PRESSURE_KEYWORDS.items():
        if kw in lower:
            return pc
    return None


def _confidence_from_fields(params: FittingParameters, base: float) -> float:
    """Boost confidence when more fields were detected."""
    filled = sum(
        1
        for v in (
            params.length,
            params.neck_in,
            params.neck_out,
            params.angle,
        )
        if v is not None
    )
    return min(0.99, base + filled * 0.03)


# ---------------------------------------------------------------------------
# Public class
# ---------------------------------------------------------------------------


class VisionAIModelGenerator:
    """
    AI-powered fitting detection and parametric model generator.

    Spec: ``modules.ai_module`` (Vision_AI_Model_Generator)

    Inputs accepted:
    - Natural-language text description  → :meth:`process_natural_language`
    - Structured image-metadata dict     → :meth:`process_image`

    Both methods return a ``FittingResult`` with:
    - Full dimensional parameters (with SMACNA defaults applied)
    - SMACNA-compliant gauge selection
    - Validation report
    - Confidence score (0–1)
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

    def process_natural_language(self, description: str) -> Dict[str, Any]:
        """
        Parse *description* (free-form text) and return a structured JSON
        result compatible with the geometry core.

        Parameters
        ----------
        description:
            Natural-language fitting description, e.g.
            "24x12 straight duct, TDC, 2 WG".

        Returns
        -------
        dict
            Structured JSON with keys ``fitting``, ``validation_report``,
            ``confidence_score``, and ``geometry_core_compatible``.
        """
        if not description or not description.strip():
            raise ValueError("description must not be empty")

        fitting_type, base_confidence = _extract_fitting_type(description)
        if fitting_type is None:
            fitting_type = FittingType.STRAIGHT
            base_confidence = 0.4

        width = _extract_dimension(description, "width") or _extract_dimension(
            description, "w"
        )
        height = _extract_dimension(description, "height") or _extract_dimension(
            description, "h"
        )

        if width is None or height is None:
            raise ValueError(
                "Could not extract width and height from description. "
                "Please specify dimensions, e.g. '24x12' or 'width 24 height 12'."
            )

        params = FittingParameters(
            fitting_type=fitting_type,
            width=width,
            height=height,
            length=_extract_dimension(description, "length"),
            connection_type=_extract_connection(description) or ConnectionType.RAW,
            pressure_class=_extract_pressure(description) or PressureClass.WG_2,
            insulation_type=_extract_insulation(description) or InsulationType.SINGLE_WALL,
        )

        return self._build_result(params, base_confidence)

    def process_image(self, image_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a fitting result from structured image-analysis metadata.

        In a production system the metadata would be produced by a CV model.
        The expected keys match :attr:`DETECTION_TARGETS`.

        Parameters
        ----------
        image_metadata:
            Dict with detected fields, e.g.::

                {
                    "fitting_type": "elbow_90",
                    "width": 18,
                    "height": 12,
                    "connection_type": "tdc",
                    "confidence_score": 0.91
                }

        Returns
        -------
        dict
            Structured JSON result (same format as
            :meth:`process_natural_language`).
        """
        if not image_metadata:
            raise ValueError("image_metadata must not be empty")

        base_confidence = float(image_metadata.get("confidence_score", 0.75))

        raw_type = image_metadata.get("fitting_type", "straight")
        try:
            fitting_type = FittingType(raw_type)
        except ValueError:
            fitting_type = FittingType.STRAIGHT
            base_confidence = max(0.0, base_confidence - 0.2)

        width = float(image_metadata.get("width", 0))
        height = float(image_metadata.get("height", 0))
        if width <= 0 or height <= 0:
            raise ValueError("image_metadata must include positive 'width' and 'height'.")

        params = FittingParameters(
            fitting_type=fitting_type,
            width=width,
            height=height,
            length=image_metadata.get("length"),
            neck_in=image_metadata.get("neck_in"),
            neck_out=image_metadata.get("neck_out"),
            angle=image_metadata.get("angle"),
            connection_type=ConnectionType(
                image_metadata.get("connection_type", ConnectionType.RAW.value)
            ),
            pressure_class=PressureClass(
                image_metadata.get("pressure_class", PressureClass.WG_2.value)
            ),
            insulation_type=InsulationType(
                image_metadata.get("insulation_type", InsulationType.SINGLE_WALL.value)
            ),
        )

        return self._build_result(params, base_confidence)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_result(
        self, params: FittingParameters, base_confidence: float
    ) -> Dict[str, Any]:
        """Apply defaults, validate, compute geometry, and return JSON output."""
        apply_defaults(params)

        validation_report = validate(params, smacna_enforcement=self.smacna_enforcement)

        if self.auto_gauge_selection and params.gauge_override is None:
            gauge = minimum_gauge(params.width, params.height, params.pressure_class)
        else:
            gauge = params.gauge_override or minimum_gauge(
                params.width, params.height, params.pressure_class
            )

        geometry = compute_geometry(params)
        surface_area = compute_surface_area(geometry)

        from geometric_engine.geometry import compute_weight

        weight = compute_weight(surface_area, gauge)
        reinf = reinforcement_required(params.width, params.height, params.pressure_class)

        result = FittingResult(
            parameters=params,
            gauge=gauge,
            reinforcement_required=reinf,
            surface_area=surface_area,
            material_weight=weight,
            geometry=geometry,
            validation_report=validation_report,
        )

        confidence = _confidence_from_fields(params, base_confidence)
        if not validation_report.is_valid:
            confidence = max(0.0, confidence - 0.3)

        output = result.to_dict()
        output["confidence_score"] = round(confidence, 4)
        output["geometry_core_compatible"] = True
        return output
