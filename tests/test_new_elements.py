"""Tests for new fitting elements added in v2.0.0 (offsets, oval, special, supports)."""

import math
import pytest

from geometric_engine.core.dimensions import Dimensions
from geometric_engine.elements.offsets import (
    RectangularSingleOffset,
    RectangularDoubleOffset,
    RectangularSymmetricOffset,
    RectangularVerticalOffset,
    RectangularLateralOffset,
)
from geometric_engine.elements.oval import (
    OvalElbow90,
    OvalElbow45,
    OvalTee90,
    OvalWye45,
    OvalReducer,
    OvalToRound,
    OvalToRect,
    OvalOffset,
)
from geometric_engine.elements.special import (
    VolumeControlDamper,
    FireDamper,
    FireSmokeDamper,
    AccessDoor,
    FlexConnector,
    LinerThroat,
    CircularBellMouth,
    PlenumTakeoff,
    RegisterBoot,
    DoubleWallSection,
)
from geometric_engine.elements.supports import (
    StrapHanger,
    TrapezeBracket,
    ClevisHanger,
    BandHanger,
    BeamClamp,
    TieRod,
    SeismicLongitudinal,
    SeismicTransverse,
)
from geometric_engine.elements.base import FittingType


# ---------------------------------------------------------------------------
# Rectangular Offsets
# ---------------------------------------------------------------------------

class TestRectangularOffsets:
    def setup_method(self):
        self.dims = Dimensions(width=0.4, height=0.3)

    def test_single_offset_loss(self):
        o = RectangularSingleOffset(self.dims, length=1.0, offset=0.2)
        assert o.loss_coefficient() > 0
        assert o.volume() > 0

    def test_single_offset_bigger_offset_bigger_loss(self):
        c1 = RectangularSingleOffset(self.dims, length=1.0, offset=0.1).loss_coefficient()
        c2 = RectangularSingleOffset(self.dims, length=1.0, offset=0.3).loss_coefficient()
        assert c2 > c1

    def test_double_offset(self):
        o = RectangularDoubleOffset(self.dims, length_x=0.5, length_y=0.5)
        assert o.loss_coefficient() > 0

    def test_symmetric_offset(self):
        o = RectangularSymmetricOffset(self.dims, length=1.0)
        assert math.isclose(o.loss_coefficient(), 0.4)

    def test_vertical_offset(self):
        o = RectangularVerticalOffset(self.dims, rise=0.3)
        assert o.surface_area() > 0

    def test_lateral_offset(self):
        o = RectangularLateralOffset(self.dims, lateral=0.2)
        assert o.volume() > 0

    def test_requires_rect_dims(self):
        with pytest.raises(ValueError):
            RectangularSingleOffset(Dimensions(diameter=0.5), length=1.0, offset=0.1)

    def test_offset_type(self):
        assert RectangularSingleOffset(self.dims, 1.0, 0.2).fitting_type == FittingType.OFFSET


# ---------------------------------------------------------------------------
# Flat-Oval Elements
# ---------------------------------------------------------------------------

class TestOvalFittings:
    def setup_method(self):
        self.oval = Dimensions(major_axis=0.6, minor_axis=0.3)
        self.round_out = Dimensions(diameter=0.4)
        self.rect_out = Dimensions(width=0.5, height=0.3)

    def test_oval_elbow_90_positive(self):
        e = OvalElbow90(self.oval, radius_ratio=1.5)
        assert e.surface_area() > 0
        assert e.volume() > 0
        assert e.loss_coefficient() > 0

    def test_oval_elbow_45_less_loss_than_90(self):
        c90 = OvalElbow90(self.oval).loss_coefficient()
        c45 = OvalElbow45(self.oval).loss_coefficient()
        assert c45 < c90

    def test_oval_tee(self):
        t = OvalTee90(self.oval, self.round_out)
        assert t.loss_coefficient() > 0

    def test_oval_wye(self):
        w = OvalWye45(self.oval, self.oval, self.oval)
        assert w.loss_coefficient() > 0

    def test_oval_reducer(self):
        outlet = Dimensions(major_axis=0.4, minor_axis=0.2)
        r = OvalReducer(self.oval, outlet, length=0.4)
        assert r.volume() > 0

    def test_oval_to_round(self):
        t = OvalToRound(self.oval, self.round_out, length=0.5)
        assert t.surface_area() > 0

    def test_oval_to_rect(self):
        t = OvalToRect(self.oval, self.rect_out, length=0.5)
        assert t.volume() > 0

    def test_oval_offset(self):
        o = OvalOffset(self.oval, offset=0.2)
        assert o.volume() > 0

    def test_oval_elbow_requires_oval_dims(self):
        with pytest.raises(ValueError):
            OvalElbow90(Dimensions(width=0.4, height=0.3))


# ---------------------------------------------------------------------------
# Special fittings
# ---------------------------------------------------------------------------

class TestSpecialFittings:
    def setup_method(self):
        self.rect = Dimensions(width=0.5, height=0.4)
        self.round = Dimensions(diameter=0.4)

    def test_vcd_loss(self):
        v = VolumeControlDamper(self.rect, length=0.15)
        assert math.isclose(v.loss_coefficient(), 0.52)

    def test_fire_damper_loss(self):
        f = FireDamper(self.rect, length=0.15)
        assert math.isclose(f.loss_coefficient(), 1.0)

    def test_fsd_loss(self):
        fsd = FireSmokeDamper(self.rect)
        assert fsd.loss_coefficient() == 1.5

    def test_access_door(self):
        a = AccessDoor(self.rect, panel_width=0.3, panel_height=0.3)
        assert math.isclose(a.panel_area_m2, 0.09)
        assert a.loss_coefficient() == 0.0

    def test_flex_connector(self):
        fc = FlexConnector(self.rect, length=0.15)
        assert fc.loss_coefficient() == 0.05

    def test_liner_throat(self):
        lt = LinerThroat(self.rect, liner_thickness=0.025)
        assert lt.net_area_m2 > 0
        assert lt.loss_coefficient() > 0

    def test_liner_throat_loss_increases_with_thickness(self):
        c1 = LinerThroat(self.rect, liner_thickness=0.01).loss_coefficient()
        c2 = LinerThroat(self.rect, liner_thickness=0.05).loss_coefficient()
        assert c2 > c1

    def test_bell_mouth_good_r(self):
        bm = CircularBellMouth(self.round, bell_radius=0.1)
        assert math.isclose(bm.loss_coefficient(), 0.04)

    def test_bell_mouth_small_r(self):
        bm = CircularBellMouth(self.round, bell_radius=0.04)
        assert bm.loss_coefficient() > 0.04

    def test_plenum_takeoff(self):
        pt = PlenumTakeoff(self.rect, outlet_width=0.3, outlet_height=0.25)
        assert pt.loss_coefficient() >= 0.5

    def test_register_boot(self):
        rb = RegisterBoot(self.rect, neck_diameter=0.25)
        assert rb.loss_coefficient() == 1.0

    def test_double_wall(self):
        dw = DoubleWallSection(self.rect, liner_thickness=0.025)
        assert dw.inner_area_m2 < self.rect.cross_section_area()
        assert dw.loss_coefficient() == 0.0

    def test_fitting_type_special(self):
        assert VolumeControlDamper(self.rect, length=0.1).fitting_type == FittingType.SPECIAL


# ---------------------------------------------------------------------------
# Supports & Hangers
# ---------------------------------------------------------------------------

class TestSupports:
    def setup_method(self):
        self.rect = Dimensions(width=0.6, height=0.4)
        self.round = Dimensions(diameter=0.5)

    def test_strap_hanger(self):
        s = StrapHanger(self.rect, strap_width=0.05)
        assert s.surface_area() > 0
        assert s.loss_coefficient() == 0.0

    def test_trapeze(self):
        t = TrapezeBracket(self.rect, span=1.0, rod_dia=0.012)
        assert t.surface_area() > 0
        assert t.loss_coefficient() == 0.0

    def test_clevis(self):
        c = ClevisHanger(self.round)
        assert c.surface_area() > 0
        assert c.volume() == 0.0

    def test_band_hanger(self):
        b = BandHanger(self.round, band_width=0.05)
        assert b.surface_area() > 0

    def test_beam_clamp(self):
        bc = BeamClamp(self.rect, flange_size=0.1)
        assert bc.surface_area() > 0

    def test_tie_rod(self):
        tr = TieRod(self.rect, rod_dia=0.012)
        assert tr.surface_area() > 0

    def test_seismic_longitudinal(self):
        sl = SeismicLongitudinal(self.rect, duct_size=0.6, splay_angle=45.0)
        assert sl.brace_type == "longitudinal"
        assert sl.surface_area() > 0

    def test_seismic_transverse(self):
        st = SeismicTransverse(self.round, duct_size=0.5, splay_angle=30.0)
        assert st.brace_type == "transverse"

    def test_seismic_bad_angle(self):
        with pytest.raises(ValueError):
            SeismicLongitudinal(self.rect, duct_size=0.6, splay_angle=0.0)

    def test_support_fitting_type(self):
        assert StrapHanger(self.rect, 0.05).fitting_type == FittingType.SUPPORT
