"""
Unit tests – BOM generator and weight calculator (bom.py)

Covers:
  - MATERIAL_DENSITY constant values
  - calculate_weight formula correctness for both materials
  - calculate_weight precision (4 d.p.)
  - generate_bom: field mapping, quantity, weight auto-calculation
  - bom_to_csv: header row, column names, data rows
  - bom_to_json: valid JSON, correct structure
  - Edge cases: zero area, multiple items, large area
"""

import csv
import io
import json
import math

import pytest

from manufacturing_engine.bom import (
    MATERIAL_DENSITY,
    bom_to_csv,
    bom_to_json,
    calculate_weight,
    generate_bom,
)
from manufacturing_engine.models import (
    BOMItem,
    FittingParameters,
    FittingType,
    FlatPattern,
    Material,
    SeamType,
    Vector2D,
)
from manufacturing_engine.unwrap import unwrap_cylinder


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _params(
    item_id="ITEM-01",
    system="SYS-A",
    material=Material.GALVANIZED_STEEL,
    thickness=0.8,
    d=300.0,
    l=1000.0,
    qty=1,
):
    return FittingParameters(
        fitting_type=FittingType.CYLINDER,
        material=material,
        thickness_mm=thickness,
        seam_type=SeamType.PITTSBURGH,
        item_id=item_id,
        system_name=system,
        diameter_mm=d,
        length_mm=l,
        quantity=qty,
    )


def _pattern(d=300.0, l=1000.0):
    return unwrap_cylinder(_params(d=d, l=l))


# ---------------------------------------------------------------------------
# MATERIAL_DENSITY constant
# ---------------------------------------------------------------------------


class TestMaterialDensity:
    def test_galvanized_steel_density(self):
        assert MATERIAL_DENSITY[Material.GALVANIZED_STEEL] == 7850.0

    def test_stainless_steel_density(self):
        assert MATERIAL_DENSITY[Material.STAINLESS_STEEL] == 7930.0

    def test_both_materials_present(self):
        assert Material.GALVANIZED_STEEL in MATERIAL_DENSITY
        assert Material.STAINLESS_STEEL in MATERIAL_DENSITY


# ---------------------------------------------------------------------------
# calculate_weight
# ---------------------------------------------------------------------------


class TestCalculateWeight:
    def test_galvanized_formula(self):
        """Weight = Area × (t/1000) × ρ"""
        area = 1.0  # m²
        t = 1.0     # mm
        expected = 1.0 * (1.0 / 1000.0) * 7850.0
        assert math.isclose(calculate_weight(area, t, Material.GALVANIZED_STEEL),
                             expected, rel_tol=1e-6)

    def test_stainless_formula(self):
        area = 2.0
        t = 1.5
        expected = 2.0 * (1.5 / 1000.0) * 7930.0
        assert math.isclose(calculate_weight(area, t, Material.STAINLESS_STEEL),
                             expected, rel_tol=1e-6)

    def test_zero_area_gives_zero_weight(self):
        assert calculate_weight(0.0, 1.0, Material.GALVANIZED_STEEL) == 0.0

    def test_precision_4dp(self):
        w = calculate_weight(0.5, 0.8, Material.GALVANIZED_STEEL)
        assert w == round(w, 4)

    def test_weight_positive_for_positive_inputs(self):
        assert calculate_weight(0.5, 0.9, Material.GALVANIZED_STEEL) > 0.0

    def test_stainless_heavier_than_galvanized_same_dimensions(self):
        """Stainless steel is denser than galvanized steel."""
        w_gal = calculate_weight(1.0, 1.0, Material.GALVANIZED_STEEL)
        w_ss = calculate_weight(1.0, 1.0, Material.STAINLESS_STEEL)
        assert w_ss > w_gal

    def test_thickness_linearity(self):
        """Doubling thickness doubles weight."""
        w1 = calculate_weight(1.0, 1.0, Material.GALVANIZED_STEEL)
        w2 = calculate_weight(1.0, 2.0, Material.GALVANIZED_STEEL)
        assert math.isclose(w2, 2.0 * w1, rel_tol=1e-6)

    def test_area_linearity(self):
        """Doubling area doubles weight."""
        w1 = calculate_weight(1.0, 1.0, Material.GALVANIZED_STEEL)
        w2 = calculate_weight(2.0, 1.0, Material.GALVANIZED_STEEL)
        assert math.isclose(w2, 2.0 * w1, rel_tol=1e-6)


# ---------------------------------------------------------------------------
# generate_bom
# ---------------------------------------------------------------------------


class TestGenerateBom:
    def test_single_item(self):
        fp = _pattern()
        p = _params()
        bom = generate_bom([(fp, p)])
        assert len(bom) == 1

    def test_item_id_mapped(self):
        fp = _pattern()
        p = _params(item_id="DUCT-007")
        bom = generate_bom([(fp, p)])
        assert bom[0].item_id == "DUCT-007"

    def test_system_mapped(self):
        fp = _pattern()
        p = _params(system="SUPPLY-MAIN")
        bom = generate_bom([(fp, p)])
        assert bom[0].system == "SUPPLY-MAIN"

    def test_material_value_string(self):
        fp = _pattern()
        p = _params(material=Material.GALVANIZED_STEEL)
        bom = generate_bom([(fp, p)])
        assert bom[0].material == "galvanized_steel"

    def test_thickness_mapped(self):
        fp = _pattern()
        p = _params(thickness=1.2)
        bom = generate_bom([(fp, p)])
        assert bom[0].thickness_mm == 1.2

    def test_area_positive(self):
        fp = _pattern()
        p = _params()
        bom = generate_bom([(fp, p)])
        assert bom[0].area_m2 > 0.0

    def test_weight_matches_calculate_weight(self):
        fp = _pattern(d=300.0, l=1000.0)
        p = _params(thickness=0.8)
        bom = generate_bom([(fp, p)])
        expected = calculate_weight(
            fp.area_m2, 0.8, Material.GALVANIZED_STEEL
        )
        assert bom[0].weight_kg == expected

    def test_quantity_mapped(self):
        fp = _pattern()
        p = _params(qty=3)
        bom = generate_bom([(fp, p)])
        assert bom[0].quantity == 3

    def test_multiple_items(self):
        items = [((_pattern(d=d, l=l)), _params(item_id=f"I{i}", d=d, l=l))
                 for i, (d, l) in enumerate([(200, 500), (300, 800), (400, 1200)])]
        bom = generate_bom(items)
        assert len(bom) == 3
        ids = {item.item_id for item in bom}
        assert ids == {"I0", "I1", "I2"}

    def test_empty_input(self):
        bom = generate_bom([])
        assert bom == []


# ---------------------------------------------------------------------------
# bom_to_csv
# ---------------------------------------------------------------------------


class TestBomToCsv:
    def _bom(self):
        fp = _pattern()
        p = _params(item_id="CSV-01", system="SYS-X", qty=2)
        return generate_bom([(fp, p)])

    def test_returns_string(self):
        assert isinstance(bom_to_csv(self._bom()), str)

    def test_header_row_present(self):
        csv_str = bom_to_csv(self._bom())
        reader = csv.DictReader(io.StringIO(csv_str))
        fieldnames = reader.fieldnames
        assert "ID" in fieldnames
        assert "System" in fieldnames
        assert "Material" in fieldnames
        assert "Thickness" in fieldnames
        assert "Area_m2" in fieldnames
        assert "Weight_kg" in fieldnames
        assert "Quantity" in fieldnames

    def test_data_row_count(self):
        bom = self._bom() + self._bom()
        csv_str = bom_to_csv(bom)
        rows = list(csv.DictReader(io.StringIO(csv_str)))
        assert len(rows) == 2

    def test_item_id_in_csv(self):
        assert "CSV-01" in bom_to_csv(self._bom())

    def test_quantity_in_csv(self):
        csv_str = bom_to_csv(self._bom())
        rows = list(csv.DictReader(io.StringIO(csv_str)))
        assert rows[0]["Quantity"] == "2"

    def test_empty_bom_has_only_header(self):
        csv_str = bom_to_csv([])
        lines = [l for l in csv_str.splitlines() if l.strip()]
        assert len(lines) == 1  # header only


# ---------------------------------------------------------------------------
# bom_to_json
# ---------------------------------------------------------------------------


class TestBomToJson:
    def _bom(self):
        fp = _pattern()
        p = _params(item_id="JSON-01")
        return generate_bom([(fp, p)])

    def test_returns_valid_json(self):
        json_str = bom_to_json(self._bom())
        parsed = json.loads(json_str)
        assert isinstance(parsed, list)

    def test_item_count(self):
        bom = self._bom() + self._bom()
        parsed = json.loads(bom_to_json(bom))
        assert len(parsed) == 2

    def test_fields_present(self):
        parsed = json.loads(bom_to_json(self._bom()))
        row = parsed[0]
        for field in ("ID", "System", "Material", "Thickness",
                      "Area_m2", "Weight_kg", "Quantity"):
            assert field in row

    def test_item_id_value(self):
        parsed = json.loads(bom_to_json(self._bom()))
        assert parsed[0]["ID"] == "JSON-01"

    def test_weight_is_float(self):
        parsed = json.loads(bom_to_json(self._bom()))
        assert isinstance(parsed[0]["Weight_kg"], float)

    def test_empty_bom_is_empty_json_array(self):
        parsed = json.loads(bom_to_json([]))
        assert parsed == []


# ---------------------------------------------------------------------------
# BOMItem.to_dict
# ---------------------------------------------------------------------------


class TestBOMItemToDict:
    def test_all_fields_present(self):
        item = BOMItem(
            item_id="X1", system="S", material="galvanized_steel",
            thickness_mm=0.8, area_m2=1.2, weight_kg=7.524, quantity=1,
        )
        d = item.to_dict()
        assert d == {
            "ID": "X1",
            "System": "S",
            "Material": "galvanized_steel",
            "Thickness": 0.8,
            "Area_m2": 1.2,
            "Weight_kg": 7.524,
            "Quantity": 1,
        }
