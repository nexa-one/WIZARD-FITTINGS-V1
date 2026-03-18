"""
Tests for cnc_module.export – DXF and SVG exporters.
"""

import os
import re
import tempfile
import pytest

from cnc_module.models.duct import RectangularDuct, RoundDuct
from cnc_module.models.material import SheetMetal
from cnc_module.models.fittings import StraightSection, RectangularElbow, EndCap
from cnc_module.flat_pattern.generator import FlatPatternGenerator
from cnc_module.flat_pattern.seam import SeamType
from cnc_module.renderer.isometric import IsometricRenderer
from cnc_module.export.dxf_writer import DXFExporter
from cnc_module.export.svg_writer import SVGExporter


@pytest.fixture
def metal():
    return SheetMetal(thickness=0.8)


@pytest.fixture
def rect_duct():
    return RectangularDuct(400, 200)


@pytest.fixture
def gen():
    return FlatPatternGenerator(seam_type=SeamType.PITTSBURGH)


@pytest.fixture
def renderer():
    return IsometricRenderer(circle_segments=12)


# ================================================================== #
# DXF Exporter                                                         #
# ================================================================== #
class TestDXFExporter:
    def test_to_string_not_empty(self, gen, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        dxf = DXFExporter()
        content = dxf.to_string(fp)
        assert len(content) > 100

    def test_dxf_starts_with_section(self, gen, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        dxf = DXFExporter()
        content = dxf.to_string(fp)
        assert "SECTION" in content

    def test_dxf_contains_eof(self, gen, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        dxf = DXFExporter()
        content = dxf.to_string(fp)
        assert "EOF" in content

    def test_dxf_contains_layers(self, gen, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        dxf = DXFExporter()
        content = dxf.to_string(fp)
        assert "CUT" in content
        assert "BEND" in content

    def test_dxf_contains_lwpolyline(self, gen, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        dxf = DXFExporter()
        content = dxf.to_string(fp)
        assert "LWPOLYLINE" in content

    def test_dxf_export_to_file(self, gen, metal, rect_duct, tmp_path):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        dxf = DXFExporter()
        out = str(tmp_path / "test_duct.dxf")
        dxf.export(fp, out)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_dxf_version_r2010(self, gen, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        dxf = DXFExporter()
        content = dxf.to_string(fp)
        assert "AC1024" in content   # DXF R2010 version code

    def test_dxf_elbow(self, gen, metal, rect_duct):
        fitting = RectangularElbow(duct=rect_duct, angle=90, throat_radius=100, metal=metal)
        fp = gen.generate(fitting)
        dxf = DXFExporter()
        content = dxf.to_string(fp)
        assert "LWPOLYLINE" in content

    def test_dxf_round_duct(self, gen, metal):
        fitting = StraightSection(duct=RoundDuct(300), length=1000, metal=metal)
        fp = gen.generate(fitting)
        dxf = DXFExporter()
        content = dxf.to_string(fp)
        assert "LWPOLYLINE" in content


# ================================================================== #
# SVG Exporter – Flat Pattern                                          #
# ================================================================== #
class TestSVGFlatPattern:
    def test_to_string_not_empty(self, gen, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        svg_exp = SVGExporter()
        svg = svg_exp.flat_pattern_to_string(fp)
        assert len(svg) > 100

    def test_svg_starts_with_svg_tag(self, gen, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        svg_exp = SVGExporter()
        svg = svg_exp.flat_pattern_to_string(fp)
        assert svg.startswith("<svg")

    def test_svg_ends_with_svg_close(self, gen, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        svg_exp = SVGExporter()
        svg = svg_exp.flat_pattern_to_string(fp)
        assert "</svg>" in svg

    def test_svg_contains_panels(self, gen, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        svg_exp = SVGExporter()
        svg = svg_exp.flat_pattern_to_string(fp)
        # Each panel boundary is a <polygon>
        assert svg.count("<polygon") == fp.panel_count

    def test_svg_cut_lines_red(self, gen, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        svg_exp = SVGExporter()
        svg = svg_exp.flat_pattern_to_string(fp)
        # Cut boundary polygons have red stroke
        assert "#e63946" in svg

    def test_svg_bend_lines_blue(self, gen, metal, rect_duct):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        svg_exp = SVGExporter()
        svg = svg_exp.flat_pattern_to_string(fp)
        assert "#4361ee" in svg   # blue bend lines

    def test_svg_export_to_file(self, gen, metal, rect_duct, tmp_path):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        svg_exp = SVGExporter()
        out = str(tmp_path / "flat_pattern.svg")
        svg_exp.export_flat_pattern(fp, out)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_svg_empty_pattern(self):
        from cnc_module.flat_pattern.pattern import FlatPattern
        fp = FlatPattern("Empty")
        svg_exp = SVGExporter()
        svg = svg_exp.flat_pattern_to_string(fp)
        assert "<svg" in svg


# ================================================================== #
# SVG Exporter – 3D view                                               #
# ================================================================== #
class TestSVG3DView:
    def test_export_3d_view_to_file(self, renderer, metal, rect_duct, tmp_path):
        fitting = StraightSection(duct=rect_duct, length=1000, metal=metal)
        svg_content = renderer.render(fitting)
        out = str(tmp_path / "3d_view.svg")
        svg_exp = SVGExporter()
        svg_exp.export_3d_view(svg_content, out)
        assert os.path.exists(out)
        with open(out) as f:
            content = f.read()
        assert "<svg" in content
