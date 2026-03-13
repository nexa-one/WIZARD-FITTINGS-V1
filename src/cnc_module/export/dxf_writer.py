"""
cnc_module.export.dxf_writer
============================
Minimal DXF R2010 exporter for flat-pattern panels.

Produces a valid ASCII DXF file that can be opened in AutoCAD, LibreCAD,
and most CNC controller software.  Each :class:`Panel` is written as:

  • LWPOLYLINE on layer ``CUT``      – outer boundary
  • LINE entities on layer ``BEND``  – fold lines
  • LINE entities on layer ``ETCH``  – annotation lines
  • LINE entities on layer ``HOLE``  – hole cut-outs
  • TEXT on layer ``LABEL``          – panel name and dimensions

No external DXF library is required – the file is assembled using
Python string formatting.
"""

from __future__ import annotations

import os
from typing import List, Tuple, TextIO

from cnc_module.flat_pattern.pattern import FlatPattern, Panel, AnnotatedLine, LineType

Point2D = Tuple[float, float]


class DXFExporter:
    """Export a :class:`FlatPattern` to a DXF file.

    Parameters
    ----------
    units: DXF measurement units code.  4 = millimetres (default).
    """

    # DXF layer definitions: name → (colour_index, linetype)
    _LAYERS = {
        "CUT":   (1, "CONTINUOUS"),    # red – cut boundary
        "BEND":  (5, "DASHED"),        # blue – bend / fold line
        "SEAM":  (3, "DASHED2"),       # green – seam allowance
        "ETCH":  (6, "DASHDOT"),       # magenta – etch / reference
        "HOLE":  (1, "CONTINUOUS"),    # red – hole cut-out
        "LABEL": (7, "CONTINUOUS"),    # white – text labels
    }

    _LINETYPE_MAP = {
        LineType.CUT:    "CUT",
        LineType.BEND:   "BEND",
        LineType.SEAM:   "SEAM",
        LineType.ETCH:   "ETCH",
        LineType.HOLE:   "HOLE",
        LineType.SCRIBE: "ETCH",
    }

    def __init__(self, units: int = 4) -> None:
        self.units = units
        self._handle = 100   # DXF entity handle counter

    def export(self, pattern: FlatPattern, filepath: str) -> None:
        """Write *pattern* to *filepath* as a DXF file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            self._write(pattern, f)

    def to_string(self, pattern: FlatPattern) -> str:
        """Return the DXF content as a string (useful for testing)."""
        import io
        buf = io.StringIO()
        self._write(pattern, buf)
        return buf.getvalue()

    # ================================================================== #
    # Internal writers                                                     #
    # ================================================================== #
    def _write(self, pattern: FlatPattern, f: TextIO) -> None:
        self._handle = 100
        self._write_header(f, pattern)
        self._write_classes(f)
        self._write_tables(f)
        self._write_blocks(f)
        self._write_entities(f, pattern)
        self._write_objects(f)
        self._write_eof(f)

    def _next_handle(self) -> str:
        self._handle += 1
        return format(self._handle, "X")

    def _w(self, f: TextIO, group_code: int, value) -> None:
        f.write(f"{group_code:>3}\n{value}\n")

    def _write_header(self, f: TextIO, pattern: FlatPattern) -> None:
        w = self._w
        w(f, 0, "SECTION")
        w(f, 2, "HEADER")
        w(f, 9, "$ACADVER")
        w(f, 1, "AC1024")   # R2010
        w(f, 9, "$DWGCODEPAGE")
        w(f, 3, "ANSI_1252")
        w(f, 9, "$INSUNITS")
        w(f, 70, self.units)
        w(f, 9, "$EXTMIN")
        w(f, 10, 0.0)
        w(f, 20, 0.0)
        w(f, 30, 0.0)
        w(f, 9, "$EXTMAX")
        w(f, 10, pattern.sheet_width)
        w(f, 20, pattern.sheet_height)
        w(f, 30, 0.0)
        w(f, 0, "ENDSEC")

    def _write_classes(self, f: TextIO) -> None:
        w = self._w
        w(f, 0, "SECTION")
        w(f, 2, "CLASSES")
        w(f, 0, "ENDSEC")

    def _write_tables(self, f: TextIO) -> None:
        w = self._w
        w(f, 0, "SECTION")
        w(f, 2, "TABLES")

        # LTYPE table (required line types)
        w(f, 0, "TABLE")
        w(f, 2, "LTYPE")
        w(f, 5, self._next_handle())
        w(f, 100, "AcDbSymbolTable")
        w(f, 70, 5)
        for lt in ("CONTINUOUS", "DASHED", "DASHED2", "DASHDOT"):
            w(f, 0, "LTYPE")
            w(f, 5, self._next_handle())
            w(f, 100, "AcDbSymbolTableRecord")
            w(f, 100, "AcDbLinetypeTableRecord")
            w(f, 2, lt)
            w(f, 70, 0)
            w(f, 3, lt)
            w(f, 72, 65)
            w(f, 73, 0)
            w(f, 40, 0.0)
        w(f, 0, "ENDTAB")

        # LAYER table
        w(f, 0, "TABLE")
        w(f, 2, "LAYER")
        w(f, 5, self._next_handle())
        w(f, 100, "AcDbSymbolTable")
        w(f, 70, len(self._LAYERS))
        for lname, (color, lt) in self._LAYERS.items():
            w(f, 0, "LAYER")
            w(f, 5, self._next_handle())
            w(f, 100, "AcDbSymbolTableRecord")
            w(f, 100, "AcDbLayerTableRecord")
            w(f, 2, lname)
            w(f, 70, 0)
            w(f, 62, color)
            w(f, 6, lt)
        w(f, 0, "ENDTAB")

        # STYLE table (required for TEXT entities)
        w(f, 0, "TABLE")
        w(f, 2, "STYLE")
        w(f, 5, self._next_handle())
        w(f, 100, "AcDbSymbolTable")
        w(f, 70, 1)
        w(f, 0, "STYLE")
        w(f, 5, self._next_handle())
        w(f, 100, "AcDbSymbolTableRecord")
        w(f, 100, "AcDbTextStyleTableRecord")
        w(f, 2, "STANDARD")
        w(f, 70, 0)
        w(f, 40, 0.0)
        w(f, 41, 1.0)
        w(f, 50, 0.0)
        w(f, 71, 0)
        w(f, 42, 2.5)
        w(f, 3, "txt")
        w(f, 4, "")
        w(f, 0, "ENDTAB")

        w(f, 0, "ENDSEC")

    def _write_blocks(self, f: TextIO) -> None:
        w = self._w
        w(f, 0, "SECTION")
        w(f, 2, "BLOCKS")
        # *MODEL_SPACE block (required)
        w(f, 0, "BLOCK")
        w(f, 5, self._next_handle())
        w(f, 100, "AcDbEntity")
        w(f, 8, "0")
        w(f, 100, "AcDbBlockBegin")
        w(f, 2, "*MODEL_SPACE")
        w(f, 70, 0)
        w(f, 10, 0.0)
        w(f, 20, 0.0)
        w(f, 30, 0.0)
        w(f, 3, "*MODEL_SPACE")
        w(f, 1, "")
        w(f, 0, "ENDBLK")
        w(f, 5, self._next_handle())
        w(f, 100, "AcDbEntity")
        w(f, 8, "0")
        w(f, 100, "AcDbBlockEnd")
        w(f, 0, "ENDSEC")

    def _write_entities(self, f: TextIO, pattern: FlatPattern) -> None:
        w = self._w
        w(f, 0, "SECTION")
        w(f, 2, "ENTITIES")

        # Apply simple linear nesting before writing
        nested = pattern.nest()

        for panel in nested:
            self._write_panel(f, panel)

        w(f, 0, "ENDSEC")

    def _write_panel(self, f: TextIO, panel: Panel) -> None:
        w = self._w

        # Boundary as LWPOLYLINE on CUT layer
        w(f, 0, "LWPOLYLINE")
        w(f, 5, self._next_handle())
        w(f, 100, "AcDbEntity")
        w(f, 8, "CUT")
        w(f, 100, "AcDbPolyline")
        w(f, 90, len(panel.boundary))
        w(f, 70, 1)   # 1 = closed polyline
        w(f, 43, 0.0)  # constant width
        for x, y in panel.boundary:
            w(f, 10, f"{x:.4f}")
            w(f, 20, f"{y:.4f}")

        # Annotated internal lines
        for line in panel.lines:
            layer = line.layer or self._LINETYPE_MAP.get(line.line_type, "ETCH")
            self._write_line(f, line.start, line.end, layer)

        # Holes
        for (cx, cy), diameter in panel.holes:
            self._write_circle(f, (cx, cy), diameter / 2.0, "HOLE")

        # Label text
        mn_x, mn_y, _, _ = panel.bounding_box
        w(f, 0, "TEXT")
        w(f, 5, self._next_handle())
        w(f, 100, "AcDbEntity")
        w(f, 8, "LABEL")
        w(f, 100, "AcDbText")
        w(f, 10, f"{mn_x:.4f}")
        w(f, 20, f"{mn_y - 8:.4f}")
        w(f, 30, 0.0)
        w(f, 40, 5.0)   # text height 5 mm
        w(f, 1, f"{panel.name}  ({panel.width:.0f}×{panel.height:.0f} mm)")
        w(f, 100, "AcDbText")

    def _write_line(
        self, f: TextIO, start: Point2D, end: Point2D, layer: str
    ) -> None:
        w = self._w
        w(f, 0, "LINE")
        w(f, 5, self._next_handle())
        w(f, 100, "AcDbEntity")
        w(f, 8, layer)
        w(f, 100, "AcDbLine")
        w(f, 10, f"{start[0]:.4f}")
        w(f, 20, f"{start[1]:.4f}")
        w(f, 30, 0.0)
        w(f, 11, f"{end[0]:.4f}")
        w(f, 21, f"{end[1]:.4f}")
        w(f, 31, 0.0)

    def _write_circle(
        self, f: TextIO, centre: Point2D, radius: float, layer: str
    ) -> None:
        w = self._w
        w(f, 0, "CIRCLE")
        w(f, 5, self._next_handle())
        w(f, 100, "AcDbEntity")
        w(f, 8, layer)
        w(f, 100, "AcDbCircle")
        w(f, 10, f"{centre[0]:.4f}")
        w(f, 20, f"{centre[1]:.4f}")
        w(f, 30, 0.0)
        w(f, 40, f"{radius:.4f}")

    def _write_objects(self, f: TextIO) -> None:
        w = self._w
        w(f, 0, "SECTION")
        w(f, 2, "OBJECTS")
        w(f, 0, "ENDSEC")

    def _write_eof(self, f: TextIO) -> None:
        self._w(f, 0, "EOF")
