"""
cnc_module.flat_pattern.pattern
================================
Core data classes for 2-D flat-pattern panels.

A :class:`FlatPattern` is a collection of :class:`Panel` objects.
Each panel holds a closed polygon (cut boundary) plus annotated lines
(bend lines, seam allowances, hole/slot cut-outs).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple, Optional

Point2D = Tuple[float, float]


class LineType(Enum):
    """Classification of lines inside a flat panel."""
    CUT = auto()        # outer or inner cut boundary (CNC tool path)
    BEND = auto()       # fold / press-brake line
    SEAM = auto()       # seam allowance boundary
    ETCH = auto()       # reference / annotation engraving
    HOLE = auto()       # punched hole or slot
    SCRIBE = auto()     # scribe / score mark


@dataclass
class AnnotatedLine:
    """A line segment with a semantic type and optional label."""
    start: Point2D
    end: Point2D
    line_type: LineType
    label: str = ""
    layer: str = ""    # DXF layer name


@dataclass
class Panel:
    """A single 2-D sheet-metal panel ready for CNC cutting.

    Attributes
    ----------
    name:         Human-readable panel identifier (e.g. "Top face", "Gore 1").
    boundary:     Closed polygon – list of (x, y) points in mm.  The last
                  point is automatically connected back to the first.
    lines:        Internal lines (bend, seam, etch, holes).
    holes:        List of hole centre points + diameter for punch operations.
    material_id:  Reference to :class:`SheetMetal` key (for multi-gauge jobs).
    grain_dir:    Preferred rolling/grain direction angle (degrees from +X).
    """

    name: str
    boundary: List[Point2D]
    lines: List[AnnotatedLine] = field(default_factory=list)
    holes: List[Tuple[Point2D, float]] = field(default_factory=list)
    material_id: str = "default"
    grain_dir: float = 0.0

    # ------------------------------------------------------------------ #
    # Geometry helpers                                                     #
    # ------------------------------------------------------------------ #
    @property
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """Return (min_x, min_y, max_x, max_y) of the boundary polygon."""
        xs = [p[0] for p in self.boundary]
        ys = [p[1] for p in self.boundary]
        return min(xs), min(ys), max(xs), max(ys)

    @property
    def width(self) -> float:
        mn, _, mx, _ = self.bounding_box
        return mx - mn

    @property
    def height(self) -> float:
        _, mn, _, mx = self.bounding_box
        return mx - mn

    @property
    def area(self) -> float:
        """Shoelace formula for polygon area (mm²)."""
        pts = self.boundary
        n = len(pts)
        a = 0.0
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            a += x0 * y1 - x1 * y0
        return abs(a) / 2.0

    def translate(self, dx: float, dy: float) -> "Panel":
        """Return a copy of this panel shifted by (dx, dy)."""
        new_boundary = [(x + dx, y + dy) for x, y in self.boundary]
        new_lines = [
            AnnotatedLine(
                (l.start[0] + dx, l.start[1] + dy),
                (l.end[0] + dx, l.end[1] + dy),
                l.line_type, l.label, l.layer,
            )
            for l in self.lines
        ]
        new_holes = [((cx + dx, cy + dy), d) for (cx, cy), d in self.holes]
        return Panel(
            name=self.name,
            boundary=new_boundary,
            lines=new_lines,
            holes=new_holes,
            material_id=self.material_id,
            grain_dir=self.grain_dir,
        )


@dataclass
class FlatPattern:
    """Collection of panels that together form a complete duct fitting.

    Attributes
    ----------
    fitting_label: Human-readable fitting description.
    panels:        Ordered list of :class:`Panel` objects.
    sheet_width:   Width of the raw sheet stock (mm).
    sheet_height:  Height of the raw sheet stock (mm).
    nesting_gap:   Minimum gap between panels during nesting (mm).
    """

    fitting_label: str
    panels: List[Panel] = field(default_factory=list)
    sheet_width: float = 2440.0   # 4 ft × 8 ft sheet = 1220 × 2440 mm
    sheet_height: float = 1220.0
    nesting_gap: float = 5.0

    def add_panel(self, panel: Panel) -> None:
        self.panels.append(panel)

    # ------------------------------------------------------------------ #
    # Nesting – trivial linear strip nesting (left-to-right, row wrap)   #
    # ------------------------------------------------------------------ #
    def nest(self) -> List[Panel]:
        """Return panels translated into a simple strip-nested arrangement.

        Panels are placed left-to-right; a new row is started when the
        cumulative width exceeds ``sheet_width``.  This is a best-effort
        nesting for estimation purposes; production systems should use a
        dedicated 2-D nesting algorithm.
        """
        placed: List[Panel] = []
        cursor_x = self.nesting_gap
        cursor_y = self.nesting_gap
        row_height = 0.0

        for panel in self.panels:
            pw = panel.width + self.nesting_gap
            ph = panel.height + self.nesting_gap

            if cursor_x + pw > self.sheet_width:
                # Start a new row
                cursor_x = self.nesting_gap
                cursor_y += row_height
                row_height = 0.0

            mn_x, mn_y, _, _ = panel.bounding_box
            dx = cursor_x - mn_x
            dy = cursor_y - mn_y
            placed.append(panel.translate(dx, dy))

            cursor_x += pw
            row_height = max(row_height, ph)

        return placed

    @property
    def total_area(self) -> float:
        """Total flat-pattern area of all panels (mm²)."""
        return sum(p.area for p in self.panels)

    @property
    def panel_count(self) -> int:
        return len(self.panels)

    def __repr__(self) -> str:
        return (
            f"FlatPattern('{self.fitting_label}', "
            f"{self.panel_count} panels, area={self.total_area:.1f} mm²)"
        )
