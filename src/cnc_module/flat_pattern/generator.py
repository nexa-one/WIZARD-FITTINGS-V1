"""
cnc_module.flat_pattern.generator
===================================
:class:`FlatPatternGenerator` – converts duct-fitting objects into
2-D flat-metal panels ready for CNC plasma / laser / waterjet cutting.

For each supported fitting type the generator:
  1. Decomposes the 3-D fitting surface into developable panels.
  2. Adds seam allowances and bend-line annotations.
  3. Returns a :class:`FlatPattern` (collection of :class:`Panel` objects).

Coordinate convention
---------------------
All panels use a local coordinate system where:
  • +X  = material grain / roll direction
  • +Y  = perpendicular to grain
  • Origin (0, 0) = lower-left corner of the raw blank
"""

from __future__ import annotations

import math
from typing import List, Optional

from cnc_module.models.duct import RectangularDuct, RoundDuct, FlatOvalDuct
from cnc_module.models.material import SheetMetal
from cnc_module.models.fittings import (
    Fitting,
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
from cnc_module.flat_pattern.pattern import FlatPattern, Panel, AnnotatedLine, LineType
from cnc_module.flat_pattern.seam import SeamType, get_seam_allowance


class FlatPatternGenerator:
    """Generate flat-metal cutting templates for HVAC duct fittings.

    Parameters
    ----------
    seam_type:   Default seam type for longitudinal seams.
    tab_length:  Tab length used for transverse (S&D or flanged) joints (mm).
    """

    def __init__(
        self,
        seam_type: SeamType = SeamType.PITTSBURGH,
        tab_length: float = 25.4,
    ) -> None:
        self.seam_type = seam_type
        self.tab_length = tab_length
        self._seam = get_seam_allowance(seam_type)

    # ================================================================== #
    # Public dispatch                                                      #
    # ================================================================== #
    def generate(self, fitting: Fitting) -> FlatPattern:
        """Dispatch to the correct development method and return a :class:`FlatPattern`."""
        dispatch = {
            StraightSection: self._straight,
            RectangularElbow: self._rect_elbow,
            RoundElbow: self._round_elbow,
            RectangularTransition: self._rect_transition,
            RoundToRectTransition: self._round_to_rect,
            RectangularTee: self._rect_tee,
            RoundTee: self._round_tee,
            RectangularReducer: self._rect_reducer,
            EndCap: self._end_cap,
        }
        handler = dispatch.get(type(fitting))
        if handler is None:
            raise NotImplementedError(
                f"No flat-pattern generator for {type(fitting).__name__}"
            )
        return handler(fitting)

    # ================================================================== #
    # Helpers                                                             #
    # ================================================================== #
    def _rect_panel(
        self,
        name: str,
        width: float,
        height: float,
        seam_a: float = 0.0,
        seam_b: float = 0.0,
        top_tab: float = 0.0,
        bottom_tab: float = 0.0,
    ) -> Panel:
        """Create a simple rectangular panel with optional seam / tab extensions."""
        total_w = width + seam_a + seam_b
        total_h = height + top_tab + bottom_tab

        boundary = [
            (0.0, 0.0),
            (total_w, 0.0),
            (total_w, total_h),
            (0.0, total_h),
        ]
        lines: List[AnnotatedLine] = []

        # Bend lines at seam edges
        if seam_a > 0:
            lines.append(AnnotatedLine(
                (seam_a, 0.0), (seam_a, total_h),
                LineType.BEND, label="Seam fold A", layer="BEND",
            ))
        if seam_b > 0:
            lines.append(AnnotatedLine(
                (seam_a + width, 0.0), (seam_a + width, total_h),
                LineType.BEND, label="Seam fold B", layer="BEND",
            ))
        # Tab lines
        if bottom_tab > 0:
            lines.append(AnnotatedLine(
                (0.0, bottom_tab), (total_w, bottom_tab),
                LineType.BEND, label="Bottom tab fold", layer="BEND",
            ))
        if top_tab > 0:
            lines.append(AnnotatedLine(
                (0.0, height + bottom_tab), (total_w, height + bottom_tab),
                LineType.BEND, label="Top tab fold", layer="BEND",
            ))

        return Panel(name=name, boundary=boundary, lines=lines)

    # ================================================================== #
    # Straight section                                                     #
    # ================================================================== #
    def _straight(self, fitting: StraightSection) -> FlatPattern:
        fp = FlatPattern(fitting_label=fitting.label or "Straight Section")
        metal = fitting.metal
        duct = fitting.duct
        L = fitting.length
        sa, sb = self._seam.allowance_a, self._seam.allowance_b
        tab = metal.tab_allowance

        if isinstance(duct, RectangularDuct):
            # 4 panels: top, bottom, left side, right side
            # The seam runs longitudinally along one side panel.
            dims = [
                ("Top",    duct.width,  L),
                ("Bottom", duct.width,  L),
                ("Left",   duct.height, L),
                ("Right",  duct.height, L),
            ]
            for i, (nm, w, h) in enumerate(dims):
                # Only the first "Left" panel gets the full seam allowance
                a = sa if nm == "Left" else 0.0
                b = sb if nm == "Left" else 0.0
                fp.add_panel(self._rect_panel(nm, w, h, a, b, tab, tab))

        elif isinstance(duct, RoundDuct):
            # One rolled panel: width = circumference, height = length
            circumference = duct.perimeter
            fp.add_panel(self._rect_panel(
                "Body (rolled)",
                circumference, L,
                sa, sb, tab, tab,
            ))

        elif isinstance(duct, FlatOvalDuct):
            # Flat oval: two flat sides + two curved-end strips
            flat_w = duct.straight_length
            curved_w = math.pi * duct.radius
            for side in ("Flat Side A", "Flat Side B"):
                fp.add_panel(self._rect_panel(side, flat_w, L, 0, 0, tab, tab))
            for end in ("Curved End A", "Curved End B"):
                fp.add_panel(self._rect_panel(end, curved_w, L, sa, sb, tab, tab))

        return fp

    # ================================================================== #
    # Rectangular elbow                                                    #
    # ================================================================== #
    def _rect_elbow(self, fitting: RectangularElbow) -> FlatPattern:
        fp = FlatPattern(fitting_label=fitting.label or "Rectangular Elbow")
        metal = fitting.metal
        duct = fitting.duct
        theta = math.radians(fitting.angle)
        sa, sb = self._seam.allowance_a, self._seam.allowance_b
        tab = metal.tab_allowance

        r_throat = fitting.throat_radius
        r_heel = fitting.heel_radius

        # Top and Bottom cheeks – trapezoidal development
        #   inner arc   = r_throat × theta
        #   outer arc   = r_heel   × theta
        #   height      = duct.height
        inner_len = r_throat * theta
        outer_len = r_heel * theta

        for nm in ("Top Cheek", "Bottom Cheek"):
            boundary = [
                (0.0, 0.0),
                (inner_len, 0.0),
                (outer_len, duct.height),
                (0.0, duct.height),
            ]
            lines = [
                AnnotatedLine(
                    (0.0, tab), (max(inner_len, outer_len), tab),
                    LineType.BEND, "Bottom tab fold", "BEND",
                ),
                AnnotatedLine(
                    (0.0, duct.height - tab),
                    (max(inner_len, outer_len), duct.height - tab),
                    LineType.BEND, "Top tab fold", "BEND",
                ),
            ]
            fp.add_panel(Panel(name=nm, boundary=boundary, lines=lines))

        # Side panels (straight, one per side of the duct width)
        # Each side is a rectangle of width × arc_length at that side's radius
        for nm, r in (("Inner Throat", r_throat), ("Outer Heel", r_heel)):
            arc = r * theta
            fp.add_panel(self._rect_panel(nm, duct.width, arc, sa if nm == "Inner Throat" else 0, sb if nm == "Inner Throat" else 0, tab, tab))

        return fp

    # ================================================================== #
    # Round elbow (segmented)                                              #
    # ================================================================== #
    def _round_elbow(self, fitting: RoundElbow) -> FlatPattern:
        fp = FlatPattern(fitting_label=fitting.label or "Round Elbow")
        metal = fitting.metal
        duct = fitting.duct
        sa, sb = self._seam.allowance_a, self._seam.allowance_b
        tab = metal.tab_allowance
        n = fitting.segments
        theta_total = math.radians(fitting.angle)
        R = fitting.radius
        D = duct.diameter

        # Each gore is a flat annular sector approximated as a trapezoid.
        theta_gore = theta_total / n
        for i in range(n):
            # Radius at the centreline of each gore
            r_inner = R - D / 2.0
            r_outer = R + D / 2.0
            inner_arc = r_inner * theta_gore
            outer_arc = r_outer * theta_gore

            boundary = [
                (0.0, 0.0),
                (inner_arc, 0.0),
                (outer_arc + sa + sb, duct.perimeter / n),
                (0.0, duct.perimeter / n),
            ]
            lines = []
            if sa > 0:
                lines.append(AnnotatedLine(
                    (sa, 0.0), (sa, duct.perimeter / n),
                    LineType.BEND, "Seam A", "BEND",
                ))
            fp.add_panel(Panel(name=f"Gore {i + 1}", boundary=boundary, lines=lines))

        # Two end caps
        for end in ("End Cap Inlet", "End Cap Outlet"):
            boundary = _circle_polygon(duct.external_diameter / 2.0, segments=36)
            fp.add_panel(Panel(name=end, boundary=boundary))

        return fp

    # ================================================================== #
    # Rectangular transition                                               #
    # ================================================================== #
    def _rect_transition(self, fitting: RectangularTransition) -> FlatPattern:
        fp = FlatPattern(fitting_label=fitting.label or "Rectangular Transition")
        metal = fitting.metal
        inlet = fitting.inlet
        outlet = fitting.outlet
        L = fitting.length
        sa, sb = self._seam.allowance_a, self._seam.allowance_b
        tab = metal.tab_allowance

        panels = [
            ("Top",    inlet.width,  outlet.width,  L),
            ("Bottom", inlet.width,  outlet.width,  L),
            ("Left",   inlet.height, outlet.height, L),
            ("Right",  inlet.height, outlet.height, L),
        ]
        for i, (nm, w1, w2, h) in enumerate(panels):
            # Trapezoidal panel
            seam_a = sa if nm == "Left" else 0.0
            seam_b = sb if nm == "Left" else 0.0
            boundary = [
                (0.0,        0.0),
                (w1 + seam_a + seam_b, 0.0),
                (w2 + seam_a + seam_b, h + tab + tab),
                (0.0,        h + tab + tab),
            ]
            lines = []
            if seam_a > 0:
                lines.append(AnnotatedLine(
                    (seam_a, 0.0), (seam_a, h + tab + tab),
                    LineType.BEND, "Seam fold A", "BEND",
                ))
            lines.append(AnnotatedLine(
                (0.0, tab), (max(w1, w2) + seam_a + seam_b, tab),
                LineType.BEND, "Bottom tab", "BEND",
            ))
            lines.append(AnnotatedLine(
                (0.0, h + tab), (max(w1, w2) + seam_a + seam_b, h + tab),
                LineType.BEND, "Top tab", "BEND",
            ))
            fp.add_panel(Panel(name=nm, boundary=boundary, lines=lines))

        return fp

    # ================================================================== #
    # Round-to-Rect transition                                             #
    # ================================================================== #
    def _round_to_rect(self, fitting: RoundToRectTransition) -> FlatPattern:
        fp = FlatPattern(fitting_label=fitting.label or "Round-to-Rect Transition")
        metal = fitting.metal
        tab = metal.tab_allowance
        L = fitting.length
        rd = fitting.round_end
        rt = fitting.rect_end
        sa, sb = self._seam.allowance_a, self._seam.allowance_b

        # Development: 4 trapezoidal panels (each panel goes from a flat
        # rect side to a chord on the round end).
        rect_sides = [rt.width, rt.height, rt.width, rt.height]
        for i, rs in enumerate(rect_sides):
            # Chord length on round end (perimeter / 4)
            chord = rd.perimeter / 4.0
            boundary = [
                (0.0,  0.0),
                (rs,   0.0),
                (rs,   L + tab + tab),
                (0.0,  L + tab + tab),
            ]
            lines = []
            if i == 0:
                lines.append(AnnotatedLine(
                    (0.0, 0.0), (rs, 0.0),
                    LineType.ETCH, f"Round end chord: {chord:.1f} mm", "ETCH",
                ))
            fp.add_panel(Panel(name=f"Panel {i + 1}", boundary=boundary, lines=lines))

        return fp

    # ================================================================== #
    # Rectangular tee                                                      #
    # ================================================================== #
    def _rect_tee(self, fitting: RectangularTee) -> FlatPattern:
        fp = FlatPattern(fitting_label=fitting.label or "Rectangular Tee")
        metal = fitting.metal
        tab = metal.tab_allowance
        sa, sb = self._seam.allowance_a, self._seam.allowance_b
        main = fitting.main
        branch = fitting.branch
        L = fitting.length

        # Main trunk panels (4 panels with a rectangular hole for branch)
        for nm, w, h in [
            ("Main Top",    main.width,  L),
            ("Main Bottom", main.width,  L),
            ("Main Left",   main.height, L),
            ("Main Right",  main.height, L),
        ]:
            a = sa if nm == "Main Left" else 0.0
            b = sb if nm == "Main Left" else 0.0
            p = self._rect_panel(nm, w, h, a, b, tab, tab)

            # Cut-out for branch on top panel
            if nm == "Main Top":
                bx = (w - branch.width) / 2.0
                by = (h - branch.height) / 2.0 + tab
                p.lines.append(AnnotatedLine(
                    (bx, by), (bx + branch.width, by),
                    LineType.CUT, "Branch opening", "CUT",
                ))
                p.lines.append(AnnotatedLine(
                    (bx + branch.width, by),
                    (bx + branch.width, by + branch.height),
                    LineType.CUT, "Branch opening", "CUT",
                ))
                p.lines.append(AnnotatedLine(
                    (bx + branch.width, by + branch.height),
                    (bx, by + branch.height),
                    LineType.CUT, "Branch opening", "CUT",
                ))
                p.lines.append(AnnotatedLine(
                    (bx, by + branch.height), (bx, by),
                    LineType.CUT, "Branch opening", "CUT",
                ))
            fp.add_panel(p)

        # Branch stub panels (2)
        branch_length = max(branch.width, 150.0)
        for nm, w, h in [
            ("Branch Left",  branch.height, branch_length),
            ("Branch Right", branch.height, branch_length),
        ]:
            fp.add_panel(self._rect_panel(nm, w, h, sa, sb, tab, tab))

        return fp

    # ================================================================== #
    # Round tee                                                            #
    # ================================================================== #
    def _round_tee(self, fitting: RoundTee) -> FlatPattern:
        fp = FlatPattern(fitting_label=fitting.label or "Round Tee")
        metal = fitting.metal
        sa, sb = self._seam.allowance_a, self._seam.allowance_b
        tab = metal.tab_allowance

        # Main body
        main_circ = fitting.main.perimeter
        fp.add_panel(self._rect_panel(
            "Main Body",
            main_circ, fitting.length,
            sa, sb, tab, tab,
        ))

        # Branch stub
        branch_circ = fitting.branch.perimeter
        branch_L = max(fitting.branch.diameter, 150.0)
        fp.add_panel(self._rect_panel(
            "Branch Stub",
            branch_circ, branch_L,
            sa, sb, tab, tab,
        ))

        return fp

    # ================================================================== #
    # Rectangular reducer                                                  #
    # ================================================================== #
    def _rect_reducer(self, fitting: RectangularReducer) -> FlatPattern:
        fp = FlatPattern(fitting_label=fitting.label or "Rectangular Reducer")
        metal = fitting.metal
        sa, sb = self._seam.allowance_a, self._seam.allowance_b
        tab = metal.tab_allowance
        large = fitting.large
        small = fitting.small
        L = fitting.length

        panels = [
            ("Top",    large.width,  small.width,  L),
            ("Bottom", large.width,  small.width,  L),
            ("Left",   large.height, small.height, L),
            ("Right",  large.height, small.height, L),
        ]
        for nm, w_large, w_small, h in panels:
            seam_a = sa if nm == "Left" else 0.0
            seam_b = sb if nm == "Left" else 0.0
            if fitting.eccentric and nm == "Bottom":
                # Bottom face stays flat – rectangular
                boundary = [
                    (0.0, 0.0),
                    (w_large + seam_a + seam_b, 0.0),
                    (w_large + seam_a + seam_b, h + tab + tab),
                    (0.0, h + tab + tab),
                ]
            else:
                boundary = [
                    (0.0, 0.0),
                    (w_large + seam_a + seam_b, 0.0),
                    (w_small + seam_a + seam_b, h + tab + tab),
                    (0.0, h + tab + tab),
                ]
            lines = []
            if seam_a > 0:
                lines.append(AnnotatedLine(
                    (seam_a, 0.0), (seam_a, h + tab + tab),
                    LineType.BEND, "Seam fold", "BEND",
                ))
            fp.add_panel(Panel(name=nm, boundary=boundary, lines=lines))

        return fp

    # ================================================================== #
    # End cap                                                              #
    # ================================================================== #
    def _end_cap(self, fitting: EndCap) -> FlatPattern:
        fp = FlatPattern(fitting_label=fitting.label or "End Cap")
        duct = fitting.duct

        if isinstance(duct, RectangularDuct):
            w = duct.external_width
            h = duct.external_height
            fp.add_panel(self._rect_panel("End Cap", w, h))
        elif isinstance(duct, RoundDuct):
            r = duct.external_diameter / 2.0
            boundary = _circle_polygon(r, segments=64)
            fp.add_panel(Panel(name="End Cap (Round)", boundary=boundary))
        else:
            fp.add_panel(Panel(
                name="End Cap",
                boundary=[(0, 0), (duct.major, 0), (duct.major, duct.minor), (0, duct.minor)],
            ))

        return fp


# ------------------------------------------------------------------ #
# Utility                                                             #
# ------------------------------------------------------------------ #
def _circle_polygon(
    radius: float, segments: int = 64
) -> list[tuple[float, float]]:
    """Return a closed polygon approximating a circle centred at the origin."""
    pts = []
    for i in range(segments):
        angle = 2.0 * math.pi * i / segments
        pts.append((radius * math.cos(angle), radius * math.sin(angle)))
    return pts
