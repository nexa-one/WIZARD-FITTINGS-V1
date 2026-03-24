"""
BOM (Bill of Materials) generator and weight calculator.

Weight formula:
    Weight_kg = Area_m2 × (Thickness_mm / 1000) × Density_kg_m3

Default densities (kg/m³):
    Galvanized steel : 7850
    Stainless steel  : 7930

All measurements in mm / m².  Precision: 4 decimal places.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Dict, List, Sequence, Tuple

from .models import BOMItem, FittingParameters, FlatPattern, Material

__all__ = [
    "MATERIAL_DENSITY",
    "calculate_weight",
    "generate_bom",
    "bom_to_csv",
    "bom_to_json",
]

# Densities in kg/m³
MATERIAL_DENSITY: Dict[Material, float] = {
    Material.GALVANIZED_STEEL: 7850.0,
    Material.STAINLESS_STEEL:  7930.0,
}


# ---------------------------------------------------------------------------
# Weight calculation
# ---------------------------------------------------------------------------


def calculate_weight(
    area_m2: float,
    thickness_mm: float,
    material: Material,
) -> float:
    """Calculate the mass of a flat-pattern piece.

    Formula:
        Weight_kg = Area_m2 × (Thickness_mm / 1000) × Density_kg_m3

    Args:
        area_m2:      Developed surface area in square metres.
        thickness_mm: Sheet thickness in mm.
        material:     Material enum value.

    Returns:
        Mass in kilograms, rounded to 4 decimal places.

    Raises:
        KeyError: If the material is not in :data:`MATERIAL_DENSITY`.
    """
    density = MATERIAL_DENSITY[material]
    thickness_m = thickness_mm / 1000.0
    return round(area_m2 * thickness_m * density, 4)


# ---------------------------------------------------------------------------
# BOM generation
# ---------------------------------------------------------------------------


def generate_bom(
    items: Sequence[Tuple[FlatPattern, FittingParameters]],
) -> List[BOMItem]:
    """Build a Bill of Materials from a list of (FlatPattern, FittingParameters) pairs.

    For multi-panel fittings (elbows, S2R) call this function once per panel
    or pre-aggregate the total area before passing it in.

    Args:
        items: Sequence of (pattern, params) tuples.  Each tuple corresponds
               to one manufactured piece.

    Returns:
        List of :class:`~manufacturing_engine.models.BOMItem` objects.
    """
    bom: List[BOMItem] = []
    for pattern, params in items:
        weight = calculate_weight(
            pattern.area_m2, params.thickness_mm, params.material
        )
        bom.append(
            BOMItem(
                item_id=params.item_id,
                system=params.system_name,
                material=params.material.value,
                thickness_mm=params.thickness_mm,
                area_m2=round(pattern.area_m2, 4),
                weight_kg=weight,
                quantity=params.quantity,
            )
        )
    return bom


# ---------------------------------------------------------------------------
# Export formats
# ---------------------------------------------------------------------------


def bom_to_csv(bom_items: Sequence[BOMItem]) -> str:
    """Serialise a BOM to a CSV string.

    Column order matches the export specification:
    ID, System, Material, Thickness, Area_m2, Weight_kg, Quantity.

    Args:
        bom_items: Sequence of BOMItem objects.

    Returns:
        CSV-formatted string (with header row).
    """
    buf = io.StringIO()
    fieldnames = ["ID", "System", "Material", "Thickness",
                  "Area_m2", "Weight_kg", "Quantity"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for item in bom_items:
        writer.writerow(item.to_dict())
    return buf.getvalue()


def bom_to_json(bom_items: Sequence[BOMItem], indent: int = 2) -> str:
    """Serialise a BOM to a JSON string.

    Args:
        bom_items: Sequence of BOMItem objects.
        indent:    JSON indentation level (default 2).

    Returns:
        Pretty-printed JSON string.
    """
    return json.dumps([item.to_dict() for item in bom_items], indent=indent)
