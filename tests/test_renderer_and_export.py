"""Tests for the isometric renderer, themes, sketch generator, and exporter."""

import json
import math
import pytest

from geometric_engine.renderer.isometric import (
    IsometricProjection,
    ScreenPoint,
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
from geometric_engine.renderer.theme import ThemeManager, THEMES
from geometric_engine.renderer.sketch import SketchGenerator
from geometric_engine.export.exporter import FittingExporter, ExportError


# ---------------------------------------------------------------------------
# Isometric Projection
# ---------------------------------------------------------------------------

class TestIsometricProjection:
    def setup_method(self):
        self.proj = IsometricProjection(scale=100.0, offset_cx=400.0, offset_cy=300.0)

    def test_project_origin(self):
        sp = self.proj.project(0, 0, 0)
        assert math.isclose(sp.sx, 400.0)
        assert math.isclose(sp.sy, 300.0)

    def test_project_y_shifts_up(self):
        sp = self.proj.project(0, 1, 0)
        assert sp.sy < 300.0  # y up → screen_y decreases

    def test_project_z_right(self):
        # When x=0, z=1: screen_x = (0-1)*cos30*100 + 400 < 400 (moves left on screen)
        sp = self.proj.project(0, 0, 1)
        assert sp.sx < 400.0  # (x-z)*cos30 is negative → sx shifts left

    def test_project_all(self):
        pts = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        sps = self.proj.project_all(pts)
        assert len(sps) == 3
        assert all(isinstance(sp, ScreenPoint) for sp in sps)

    def test_formula_explicit(self):
        x, y, z = 1.0, 0.5, 0.5
        cos30 = math.cos(math.radians(30))
        sin30 = math.sin(math.radians(30))
        expected_sx = (x - z) * cos30 * 100 + 400
        expected_sy = (x + z) * sin30 * 100 - y * 100 + 300
        sp = self.proj.project(x, y, z)
        assert math.isclose(sp.sx, expected_sx, rel_tol=1e-9)
        assert math.isclose(sp.sy, expected_sy, rel_tol=1e-9)


# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------

class TestIsoBox:
    def setup_method(self):
        self.proj = IsometricProjection(scale=200.0)

    def test_returns_3_polygon_commands(self):
        cmds = iso_box(self.proj, 0, 0, 0, 0.4, 0.3, 0.4)
        polys = [c for c in cmds if c["type"] == "polygon"]
        assert len(polys) == 3

    def test_polygon_has_4_points(self):
        cmds = iso_box(self.proj, 0, 0, 0, 0.4, 0.3, 0.4)
        for c in cmds:
            if c["type"] == "polygon":
                assert len(c["points"]) == 4

    def test_custom_colors(self):
        cmds = iso_box(self.proj, 0, 0, 0, 0.4, 0.3, 0.4,
                       theme_colors={"top": "#FF0000"})
        top_poly = cmds[0]
        assert top_poly["fill"] == "#FF0000"


class TestIsoCylinder:
    def setup_method(self):
        self.proj = IsometricProjection(scale=200.0)

    def test_returns_cmds(self):
        cmds = iso_cylinder(self.proj, 0, 0, 0, 0.25, 1.0)
        assert len(cmds) > 0
        types = {c["type"] for c in cmds}
        assert "polygon" in types

    def test_has_two_caps(self):
        cmds = iso_cylinder(self.proj, 0, 0, 0, 0.25, 1.0, n_segments=8)
        polys = [c for c in cmds if c["type"] == "polygon"]
        # 8 side quads + 2 caps = 10
        assert len(polys) == 10


class TestIsoCone:
    def test_returns_cmds(self):
        proj = IsometricProjection(scale=200.0)
        cmds = iso_cone(proj, 0, 0, 0, 0.3, 0.1, 0.6, n_segments=8)
        assert any(c["type"] == "polygon" for c in cmds)


class TestIsoElbowArc:
    def test_returns_line_cmds(self):
        proj = IsometricProjection(scale=200.0)
        cmds = iso_elbow_arc(proj, 0, 0, 0, 0.6, 0.4, 0, 90, n_segments=8)
        assert all(c["type"] == "line" for c in cmds)
        assert len(cmds) == 8


class TestIsoFlatOval:
    def test_returns_cmds(self):
        proj = IsometricProjection(scale=200.0)
        cmds = iso_flat_oval(proj, 0, 0, 0, 0.6, 0.3, 1.0, n_cap_segments=4)
        assert len(cmds) > 0


class TestIsoDimLine:
    def test_returns_4_cmds(self):
        proj = IsometricProjection(scale=200.0)
        cmds = iso_dim_line(proj, (0, 0, 0), (0, 0, 0.4), label="W=400mm")
        assert len(cmds) == 4
        types = [c["type"] for c in cmds]
        assert "line" in types
        assert "text" in types

    def test_label_in_text_cmd(self):
        proj = IsometricProjection(scale=200.0)
        cmds = iso_dim_line(proj, (0, 0, 0), (0, 0, 0.4), label="W=400mm")
        text_cmds = [c for c in cmds if c["type"] == "text"]
        assert any("W=400mm" in c["text"] for c in text_cmds)


class TestIsoCoordCube:
    def test_returns_cmds(self):
        cmds = iso_coord_cube("top_right", size_px=80)
        assert len(cmds) > 0
        has_text = any(c["type"] == "text" for c in cmds)
        assert has_text

    def test_axes_labels(self):
        cmds = iso_coord_cube()
        labels = {c["text"] for c in cmds if c["type"] == "text"}
        assert "X" in labels
        assert "Y" in labels
        assert "Z" in labels


class TestIsoTitleBlock:
    def test_returns_cmds(self):
        cmds = iso_title_block({"project": "Site A", "by": "John"})
        assert len(cmds) > 0

    def test_contains_field_values(self):
        cmds = iso_title_block({"project": "ACME"})
        texts = [c["text"] for c in cmds if c["type"] == "text"]
        assert any("ACME" in t for t in texts)


# ---------------------------------------------------------------------------
# Theme Manager
# ---------------------------------------------------------------------------

class TestThemeManager:
    def test_default_theme(self):
        tm = ThemeManager()
        assert tm.theme.name == "light_technical"

    def test_set_dark(self):
        tm = ThemeManager("dark_professional")
        assert tm.theme.background == "#12161C"

    def test_blueprint(self):
        tm = ThemeManager("blueprint")
        assert tm.theme.background == "#003366"

    def test_unknown_theme_raises(self):
        with pytest.raises(ValueError):
            ThemeManager("neon_rainbow")

    def test_available_themes(self):
        themes = ThemeManager.available_themes()
        assert "light_technical" in themes
        assert "dark_professional" in themes
        assert "blueprint" in themes

    def test_face_colors_keys(self):
        tm = ThemeManager()
        fc = tm.face_colors()
        assert "top" in fc
        assert "left" in fc
        assert "right" in fc
        assert "outline" in fc

    def test_switch_theme(self):
        tm = ThemeManager("light_technical")
        tm.set_theme("blueprint")
        assert tm.theme.name == "blueprint"


# ---------------------------------------------------------------------------
# Sketch Generator
# ---------------------------------------------------------------------------

class TestSketchGenerator:
    def setup_method(self):
        self.gen = SketchGenerator(theme="light_technical")

    def _gen_sketch(self, fid: str, params: dict) -> dict:
        return self.gen.generate(fitting_id=fid, params=params)

    def test_sketch_structure(self):
        s = self._gen_sketch("RE-4", {"W": 0.4, "H": 0.3, "R": 0.6})
        assert s["fitting_id"] == "RE-4"
        assert s["geometry"] == "rectElbow_radius"
        assert s["theme"] == "light_technical"
        assert "viewport" in s
        assert "draw_cmds" in s
        assert "metadata" in s
        assert "annotations" in s

    def test_draw_cmds_not_empty(self):
        s = self._gen_sketch("RE-4", {"W": 0.4, "H": 0.3, "R": 0.6})
        assert len(s["draw_cmds"]) > 0

    def test_has_background_cmd(self):
        s = self._gen_sketch("CE-1", {"D": 0.5, "R": 0.75})
        bgs = [c for c in s["draw_cmds"] if c["type"] == "background"]
        assert len(bgs) == 1

    def test_metadata_contains_fitting_id(self):
        s = self._gen_sketch("FO-1", {"Wo": 0.6, "Ho": 0.3, "R": 0.9})
        assert s["metadata"]["fitting_id"] == "FO-1"

    def test_custom_metadata(self):
        s = self.gen.generate(
            "RE-4", {"W": 0.4, "H": 0.3, "R": 0.6},
            metadata={"project": "ACME Plant"},
        )
        assert s["metadata"]["project"] == "ACME Plant"

    def test_dark_theme(self):
        gen = SketchGenerator(theme="dark_professional")
        s = gen.generate("RC-1", {"W": 0.4, "H": 0.3})
        bg_cmd = next(c for c in s["draw_cmds"] if c["type"] == "background")
        assert bg_cmd["fill"] == "#12161C"

    def test_blueprint_theme(self):
        gen = SketchGenerator(theme="blueprint")
        s = gen.generate("SP-7", {"D": 0.4, "R": 0.08})
        assert s["theme"] == "blueprint"

    def test_unknown_fitting_raises(self):
        with pytest.raises(KeyError):
            self.gen.generate("XX-1", {})


# ---------------------------------------------------------------------------
# Exporter
# ---------------------------------------------------------------------------

class TestFittingExporter:
    def setup_method(self):
        gen = SketchGenerator()
        self.sketch = gen.generate("RE-4", {"W": 0.4, "H": 0.3, "R": 0.6})
        self.exp = FittingExporter()

    def test_default_format_pdf(self):
        content = self.exp.export(self.sketch)
        data = json.loads(content)
        assert data["format"] == "pdf"

    def test_export_png(self):
        content = self.exp.export(self.sketch, fmt="png")
        data = json.loads(content)
        assert data["format"] == "png"
        assert "draw_cmds" in data

    def test_export_stl(self):
        content = self.exp.export(self.sketch, fmt="stl")
        assert "solid RE-4" in content
        assert "endsolid RE-4" in content

    def test_export_step(self):
        content = self.exp.export(self.sketch, fmt="step")
        data = json.loads(content)
        assert data["format"] == "step"
        assert data["standard"] == "AP214"

    def test_unsupported_format_raises(self):
        with pytest.raises(ExportError):
            self.exp.export(self.sketch, fmt="dxf")

    def test_bad_default_format_raises(self):
        with pytest.raises(ValueError):
            FittingExporter(default_format="doc")

    def test_supported_formats(self):
        assert set(self.exp.supported_formats) == {"pdf", "stl", "step", "png"}

    def test_stl_has_facets(self):
        content = self.exp.export(self.sketch, fmt="stl")
        assert "facet normal" in content

    def test_pdf_has_page_dimensions(self):
        content = self.exp.export(self.sketch, fmt="pdf")
        data = json.loads(content)
        assert "page" in data
        assert data["page"]["width_mm"] > 0
