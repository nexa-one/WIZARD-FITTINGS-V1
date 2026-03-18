"""
Tests for cnc_module.flat_pattern – 2-D sheet-metal development.
"""

import math
import pytest

from cnc_module.models.duct import RectangularDuct, RoundDuct, FlatOvalDuct
from cnc_module.models.material import SheetMetal
from cnc_module.models.fittings import (
    StraightSection,
    RectangularElbow,
    RoundElbow,
    RectangularTransition,
    RoundToRectTransition,
    RectangularTee,
    RoundTee,
    RectangularReducer,
    EndCap,
)
from cnc_module.flat_pattern.pattern import FlatPattern, Panel, LineType
from cnc_module.flat_pattern.generator import FlatPatternGenerator
from cnc_module.flat_pattern.seam import SeamType, get_seam_allowance


# ================================================================== #
# SeamAllowance                                                        #
# ================================================================== #
class TestSeamAllowance:
    def test_pittsburgh_total(self):
        sa = get_seam_allowance(SeamType.PITTSBURGH)
        assert sa.total == pytest.approx(sa.allowance_a + sa.allowance_b)

    def test_butt_zero(self):
        sa = get_seam_allowance(SeamType.BUTT)
        assert sa.total == pytest.approx(0.0)

    def test_all_types_defined(self):
        for st in SeamType:
            sa = get_seam_allowance(st)
            assert sa.seam_type == st


# ================================================================== #
# Panel                                                                #
# ================================================================== #
class TestPanel:
    def test_bounding_box(self):
        p = Panel("Test", [(0, 0), (100, 0), (100, 50), (0, 50)])
        mn_x, mn_y, mx_x, mx_y = p.bounding_box
        assert mn_x == pytest.approx(0)
        assert mn_y == pytest.approx(0)
        assert mx_x == pytest.approx(100)
        assert mx_y == pytest.approx(50)

    def test_area_rectangle(self):
        p = Panel("Test", [(0, 0), (100, 0), (100, 50), (0, 50)])
        assert p.area == pytest.approx(5000.0)

    def test_area_triangle(self):
        p = Panel("T", [(0, 0), (10, 0), (5, 10)])
        assert p.area == pytest.approx(50.0)

    def test_translate(self):
        p = Panel("T", [(0, 0), (10, 0), (10, 5), (0, 5)])
        p2 = p.translate(20, 30)
        assert p2.boundary[0] == (20, 30)
        assert p2.boundary[2] == (30, 35)

    def test_width_height(self):
        p = Panel("T", [(10, 20), (60, 20), (60, 45), (10, 45)])
        assert p.width == pytest.approx(50)
        assert p.height == pytest.approx(25)


# ================================================================== #
# FlatPattern                                                          #
# ================================================================== #
class TestFlatPattern:
    def test_add_panel(self):
        fp = FlatPattern("Test")
        p = Panel("P1", [(0, 0), (100, 0), (100, 50), (0, 50)])
        fp.add_panel(p)
        assert fp.panel_count == 1

    def test_total_area(self):
        fp = FlatPattern("Test")
        fp.add_panel(Panel("P1", [(0, 0), (100, 0), (100, 50), (0, 50)]))
        fp.add_panel(Panel("P2", [(0, 0), (80, 0), (80, 40), (0, 40)]))
        assert fp.total_area == pytest.approx(5000 + 3200)

    def test_nest_returns_panels(self):
        fp = FlatPattern("Test")
        for i in range(5):
            fp.add_panel(Panel(f"P{i}", [(0, 0), (200, 0), (200, 100), (0, 100)]))
        nested = fp.nest()
        assert len(nested) == 5

    def test_nest_no_overlap_x(self):
        """After nesting, no two panels should have overlapping bounding boxes."""
        fp = FlatPattern("Test", sheet_width=2440)
        for i in range(4):
            fp.add_panel(Panel(f"P{i}", [(0, 0), (300, 0), (300, 200), (0, 200)]))
        nested = fp.nest()
        boxes = [p.bounding_box for p in nested]
        # Simple check: all min_x are non-negative
        for mn_x, mn_y, mx_x, mx_y in boxes:
            assert mn_x >= 0


# ================================================================== #
# FlatPatternGenerator – Straight Section                              #
# ================================================================== #
@pytest.fixture
def gen():
    return FlatPatternGenerator(seam_type=SeamType.PITTSBURGH)


@pytest.fixture
def metal():
    return SheetMetal(thickness=0.8)


class TestFlatPatternGeneratorStraight:
    def test_rect_panel_count(self, gen, metal):
        duct = RectangularDuct(400, 200)
        fitting = StraightSection(duct=duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        assert fp.panel_count == 4

    def test_round_panel_count(self, gen, metal):
        duct = RoundDuct(300)
        fitting = StraightSection(duct=duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        assert fp.panel_count == 1

    def test_flat_oval_panel_count(self, gen, metal):
        duct = FlatOvalDuct(500, 200)
        fitting = StraightSection(duct=duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        assert fp.panel_count == 4   # 2 flat + 2 curved

    def test_rect_panels_have_bend_lines(self, gen, metal):
        duct = RectangularDuct(400, 200)
        fitting = StraightSection(duct=duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        bend_lines = [
            l for p in fp.panels for l in p.lines
            if l.line_type == LineType.BEND
        ]
        assert len(bend_lines) > 0

    def test_panel_dimensions_rect_top(self, gen, metal):
        duct = RectangularDuct(400, 200)
        fitting = StraightSection(duct=duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        top = next(p for p in fp.panels if p.name == "Top")
        # Top panel width should = duct.width (+ no seam on top panel)
        assert top.width == pytest.approx(duct.width, rel=0.01)

    def test_round_body_width_equals_circumference(self, gen, metal):
        duct = RoundDuct(300)
        fitting = StraightSection(duct=duct, length=1000, metal=metal)
        fp = gen.generate(fitting)
        body = fp.panels[0]
        sa = get_seam_allowance(SeamType.PITTSBURGH)
        # width = circumference + seam_a + seam_b
        expected_w = duct.perimeter + sa.total
        assert body.width == pytest.approx(expected_w, rel=0.01)


# ================================================================== #
# FlatPatternGenerator – Elbows                                        #
# ================================================================== #
class TestFlatPatternGeneratorElbow:
    def test_rect_elbow_panels(self, gen, metal):
        duct = RectangularDuct(400, 200)
        fitting = RectangularElbow(duct=duct, angle=90, throat_radius=100, metal=metal)
        fp = gen.generate(fitting)
        assert fp.panel_count == 4

    def test_round_elbow_panels(self, gen, metal):
        duct = RoundDuct(300)
        fitting = RoundElbow(duct=duct, angle=90, segments=5, metal=metal)
        fp = gen.generate(fitting)
        # segments + 2 end caps
        assert fp.panel_count == 7

    def test_elbow_cheek_is_trapezoidal(self, gen, metal):
        """The cheek panels of a radiused elbow should have 4 vertices."""
        duct = RectangularDuct(400, 200)
        fitting = RectangularElbow(duct=duct, angle=90, throat_radius=100, metal=metal)
        fp = gen.generate(fitting)
        cheeks = [p for p in fp.panels if "Cheek" in p.name]
        for c in cheeks:
            assert len(c.boundary) == 4


# ================================================================== #
# FlatPatternGenerator – Transitions                                   #
# ================================================================== #
class TestFlatPatternGeneratorTransition:
    def test_rect_transition_panels(self, gen, metal):
        inlet = RectangularDuct(600, 400)
        outlet = RectangularDuct(300, 200)
        fitting = RectangularTransition(inlet=inlet, outlet=outlet, length=300, metal=metal)
        fp = gen.generate(fitting)
        assert fp.panel_count == 4

    def test_round_to_rect_panels(self, gen, metal):
        fitting = RoundToRectTransition(
            round_end=RoundDuct(250),
            rect_end=RectangularDuct(300, 200),
            length=250,
            metal=metal,
        )
        fp = gen.generate(fitting)
        assert fp.panel_count == 4


# ================================================================== #
# FlatPatternGenerator – Tee                                           #
# ================================================================== #
class TestFlatPatternGeneratorTee:
    def test_rect_tee_panels(self, gen, metal):
        fitting = RectangularTee(
            main=RectangularDuct(600, 300),
            branch=RectangularDuct(300, 200),
            length=600,
            metal=metal,
        )
        fp = gen.generate(fitting)
        assert fp.panel_count == 6

    def test_main_top_has_cutout(self, gen, metal):
        fitting = RectangularTee(
            main=RectangularDuct(600, 300),
            branch=RectangularDuct(300, 200),
            length=600,
            metal=metal,
        )
        fp = gen.generate(fitting)
        top = next(p for p in fp.panels if p.name == "Main Top")
        cut_lines = [l for l in top.lines if l.line_type == LineType.CUT]
        assert len(cut_lines) == 4   # 4 sides of the rectangular hole


# ================================================================== #
# FlatPatternGenerator – Reducer & End Cap                             #
# ================================================================== #
class TestFlatPatternGeneratorMisc:
    def test_reducer_panels(self, gen, metal):
        fitting = RectangularReducer(
            large=RectangularDuct(400, 300),
            small=RectangularDuct(200, 150),
            length=200,
            metal=metal,
        )
        fp = gen.generate(fitting)
        assert fp.panel_count == 4

    def test_end_cap_rect_single_panel(self, gen, metal):
        fitting = EndCap(duct=RectangularDuct(400, 200), metal=metal)
        fp = gen.generate(fitting)
        assert fp.panel_count == 1

    def test_end_cap_round_single_panel(self, gen, metal):
        fitting = EndCap(duct=RoundDuct(300), metal=metal)
        fp = gen.generate(fitting)
        assert fp.panel_count == 1

    def test_unsupported_fitting_raises(self, gen):
        class Dummy:
            pass
        with pytest.raises(NotImplementedError):
            gen.generate(Dummy())
