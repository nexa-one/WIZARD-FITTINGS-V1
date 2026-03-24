"""
Unit tests – DXF export (dxf_export.py)

Covers:
  - DXF string contains mandatory sections (HEADER, TABLES, ENTITIES, EOF)
  - Correct ACADVER marker (AC1009 = R12)
  - All four required layers present in TABLES section
  - Entities section contains expected keywords per entity type
  - export_flat_pattern produces a valid DXF for various patterns
  - DXFWriter API: add_polyline, add_line, add_text
  - Layer name constants
"""

import pytest

from manufacturing_engine.dxf_export import (
    LAYER_BEND_LINES,
    LAYER_CUT_OUTLINE,
    LAYER_MARKING_TEXT,
    LAYER_NOTCHES,
    DXFWriter,
    export_flat_pattern,
)
from manufacturing_engine.models import (
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


def _simple_pattern() -> FlatPattern:
    params = FittingParameters(
        fitting_type=FittingType.CYLINDER,
        material=Material.GALVANIZED_STEEL,
        thickness_mm=0.8,
        seam_type=SeamType.PITTSBURGH,
        item_id="DXF-TEST",
        system_name="SYS",
        diameter_mm=200.0,
        length_mm=600.0,
    )
    return unwrap_cylinder(params)


def _rect_pts():
    return [
        Vector2D(0, 0), Vector2D(100, 0),
        Vector2D(100, 200), Vector2D(0, 200), Vector2D(0, 0),
    ]


# ---------------------------------------------------------------------------
# Layer name constants
# ---------------------------------------------------------------------------


class TestLayerConstants:
    def test_cut_outline_name(self):
        assert LAYER_CUT_OUTLINE == "CUT_OUTLINE"

    def test_bend_lines_name(self):
        assert LAYER_BEND_LINES == "BEND_LINES"

    def test_marking_text_name(self):
        assert LAYER_MARKING_TEXT == "MARKING_TEXT"

    def test_notches_name(self):
        assert LAYER_NOTCHES == "NOTCHES"


# ---------------------------------------------------------------------------
# DXFWriter.to_string structure
# ---------------------------------------------------------------------------


class TestDXFWriterStructure:
    def _base_dxf(self) -> str:
        w = DXFWriter()
        w.add_polyline(_rect_pts(), layer=LAYER_CUT_OUTLINE)
        return w.to_string()

    def test_contains_section_header(self):
        assert "SECTION" in self._base_dxf()

    def test_contains_header_section(self):
        dxf = self._base_dxf()
        assert "HEADER" in dxf

    def test_acadver_r12(self):
        assert "AC1009" in self._base_dxf()

    def test_contains_tables_section(self):
        assert "TABLES" in self._base_dxf()

    def test_contains_entities_section(self):
        assert "ENTITIES" in self._base_dxf()

    def test_ends_with_eof(self):
        dxf = self._base_dxf()
        assert dxf.strip().endswith("EOF")

    def test_endsec_present(self):
        dxf = self._base_dxf()
        assert dxf.count("ENDSEC") >= 3  # HEADER, TABLES, ENTITIES


# ---------------------------------------------------------------------------
# Layer definitions in TABLES section
# ---------------------------------------------------------------------------


class TestLayerTable:
    def _dxf(self) -> str:
        w = DXFWriter()
        w.add_polyline(_rect_pts())
        return w.to_string()

    def test_cut_outline_layer_defined(self):
        assert LAYER_CUT_OUTLINE in self._dxf()

    def test_bend_lines_layer_defined(self):
        assert LAYER_BEND_LINES in self._dxf()

    def test_marking_text_layer_defined(self):
        assert LAYER_MARKING_TEXT in self._dxf()

    def test_notches_layer_defined(self):
        assert LAYER_NOTCHES in self._dxf()


# ---------------------------------------------------------------------------
# Entity output
# ---------------------------------------------------------------------------


class TestDXFEntities:
    def test_polyline_entity_written(self):
        w = DXFWriter()
        w.add_polyline(_rect_pts(), layer=LAYER_CUT_OUTLINE)
        dxf = w.to_string()
        assert "POLYLINE" in dxf
        assert "VERTEX" in dxf
        assert "SEQEND" in dxf

    def test_polyline_uses_correct_layer(self):
        w = DXFWriter()
        w.add_polyline(_rect_pts(), layer=LAYER_CUT_OUTLINE)
        dxf = w.to_string()
        assert LAYER_CUT_OUTLINE in dxf

    def test_line_entity_written(self):
        w = DXFWriter()
        w.add_line(Vector2D(0, 0), Vector2D(100, 100), layer=LAYER_BEND_LINES)
        dxf = w.to_string()
        assert "LINE" in dxf

    def test_line_contains_coordinates(self):
        w = DXFWriter()
        w.add_line(Vector2D(10.5, 20.3), Vector2D(50.0, 80.0))
        dxf = w.to_string()
        assert "10.5000" in dxf
        assert "20.3000" in dxf

    def test_text_entity_written(self):
        w = DXFWriter()
        w.add_text("HELLO", Vector2D(0, 0), height=5.0)
        dxf = w.to_string()
        assert "TEXT" in dxf
        assert "HELLO" in dxf

    def test_text_height_written(self):
        w = DXFWriter()
        w.add_text("X", Vector2D(0, 0), height=7.5)
        dxf = w.to_string()
        assert "7.5000" in dxf

    def test_multiple_entities(self):
        w = DXFWriter()
        w.add_polyline(_rect_pts())
        w.add_line(Vector2D(0, 0), Vector2D(100, 0))
        w.add_text("LBL", Vector2D(50, 100))
        dxf = w.to_string()
        assert "POLYLINE" in dxf
        assert "LINE" in dxf
        assert "TEXT" in dxf


# ---------------------------------------------------------------------------
# export_flat_pattern convenience function
# ---------------------------------------------------------------------------


class TestExportFlatPattern:
    def test_returns_string(self):
        fp = _simple_pattern()
        result = export_flat_pattern(fp)
        assert isinstance(result, str)

    def test_dxf_is_non_empty(self):
        fp = _simple_pattern()
        assert len(export_flat_pattern(fp)) > 0

    def test_contains_cut_outline_layer(self):
        fp = _simple_pattern()
        assert LAYER_CUT_OUTLINE in export_flat_pattern(fp)

    def test_contains_bend_lines_layer(self):
        fp = _simple_pattern()
        dxf = export_flat_pattern(fp)
        assert LAYER_BEND_LINES in dxf

    def test_contains_marking_text_layer(self):
        fp = _simple_pattern()
        dxf = export_flat_pattern(fp)
        assert LAYER_MARKING_TEXT in dxf

    def test_contains_item_id_label(self):
        fp = _simple_pattern()
        dxf = export_flat_pattern(fp)
        assert "DXF-TEST" in dxf

    def test_with_notches(self):
        from manufacturing_engine.seam_engine import apply_seam
        fp = _simple_pattern()
        fp_seamed = apply_seam(fp, SeamType.PITTSBURGH)
        dxf = export_flat_pattern(fp_seamed)
        assert LAYER_NOTCHES in dxf

    def test_empty_pattern_still_valid(self):
        fp = FlatPattern(outline=[], bend_lines=[], notches=[], labels=[])
        dxf = export_flat_pattern(fp)
        assert "ENDSEC" in dxf
        assert dxf.strip().endswith("EOF")
