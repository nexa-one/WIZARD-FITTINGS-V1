"""
DXF exporter – AutoCAD R12 / LT2 format.

Layers
------
CUT_OUTLINE   – closed outer cut boundary (colour 7 = white)
BEND_LINES    – bend / fold lines         (colour 3 = green)
MARKING_TEXT  – part ID / dimension text  (colour 2 = yellow)
NOTCHES       – corner and seam notches   (colour 1 = red)

Entities
--------
POLYLINE / VERTEX / SEQEND  – for closed polygons (R12 compatible)
LINE                        – for individual line segments
TEXT                        – for marking labels

All coordinates are written in mm, rounded to 4 decimal places.
DXF group-code pairs are separated by CRLF for maximum compatibility.
"""

from __future__ import annotations

import io
import math
from typing import List, Optional, Sequence, Tuple

from .models import FittingParameters, FlatPattern, Vector2D

__all__ = [
    "LAYER_CUT_OUTLINE",
    "LAYER_BEND_LINES",
    "LAYER_MARKING_TEXT",
    "LAYER_NOTCHES",
    "DXFWriter",
    "export_flat_pattern",
]

# Layer names (match the DXF export specification)
LAYER_CUT_OUTLINE = "CUT_OUTLINE"
LAYER_BEND_LINES = "BEND_LINES"
LAYER_MARKING_TEXT = "MARKING_TEXT"
LAYER_NOTCHES = "NOTCHES"

# Layer colours (AutoCAD ACI colour index)
_LAYER_COLOUR = {
    LAYER_CUT_OUTLINE:  7,   # white
    LAYER_BEND_LINES:   3,   # green
    LAYER_MARKING_TEXT: 2,   # yellow
    LAYER_NOTCHES:      1,   # red
}

_DXF_HEADER = "AC1009"   # AutoCAD R12


# ---------------------------------------------------------------------------
# DXF writer
# ---------------------------------------------------------------------------


class DXFWriter:
    """Minimal AutoCAD R12 DXF file builder.

    Usage::

        w = DXFWriter()
        w.add_polyline(pts, layer=LAYER_CUT_OUTLINE, closed=True)
        w.add_line(start, end, layer=LAYER_BEND_LINES)
        w.add_text("DUCT-01", position, height=5.0, layer=LAYER_MARKING_TEXT)
        dxf_str = w.to_string()
    """

    def __init__(self) -> None:
        self._entities: List[str] = []

    # ------------------------------------------------------------------
    # Entity builders
    # ------------------------------------------------------------------

    def add_polyline(
        self,
        points: Sequence[Vector2D],
        layer: str = LAYER_CUT_OUTLINE,
        closed: bool = True,
    ) -> None:
        """Append a 2-D polyline (POLYLINE / VERTEX / SEQEND) to the drawing.

        Args:
            points:  Sequence of 2-D vertices.
            layer:   DXF layer name.
            closed:  Whether to set the closed-polyline flag (bit 1 of flag
                     group code 70).
        """
        flag = 1 if closed else 0
        buf = io.StringIO()

        # POLYLINE header
        buf.write("0\nPOLYLINE\n")
        buf.write(f"8\n{layer}\n")
        buf.write("66\n1\n")       # vertices-follow flag
        buf.write("10\n0.0\n")
        buf.write("20\n0.0\n")
        buf.write("30\n0.0\n")
        buf.write(f"70\n{flag}\n")

        # VERTEX entities
        for pt in points:
            buf.write("0\nVERTEX\n")
            buf.write(f"8\n{layer}\n")
            buf.write(f"10\n{pt.x:.4f}\n")
            buf.write(f"20\n{pt.y:.4f}\n")
            buf.write("30\n0.0\n")

        buf.write("0\nSEQEND\n")
        self._entities.append(buf.getvalue())

    def add_line(
        self,
        start: Vector2D,
        end: Vector2D,
        layer: str = LAYER_BEND_LINES,
    ) -> None:
        """Append a LINE entity.

        Args:
            start: Start point.
            end:   End point.
            layer: DXF layer name.
        """
        self._entities.append(
            "0\nLINE\n"
            f"8\n{layer}\n"
            f"10\n{start.x:.4f}\n"
            f"20\n{start.y:.4f}\n"
            "30\n0.0\n"
            f"11\n{end.x:.4f}\n"
            f"21\n{end.y:.4f}\n"
            "31\n0.0\n"
        )

    def add_text(
        self,
        text: str,
        position: Vector2D,
        height: float = 5.0,
        layer: str = LAYER_MARKING_TEXT,
        rotation_deg: float = 0.0,
    ) -> None:
        """Append a TEXT entity.

        Args:
            text:         Text string to draw.
            position:     Insertion point.
            height:       Character height in mm.
            layer:        DXF layer name.
            rotation_deg: Text rotation in degrees (default 0).
        """
        self._entities.append(
            "0\nTEXT\n"
            f"8\n{layer}\n"
            f"10\n{position.x:.4f}\n"
            f"20\n{position.y:.4f}\n"
            "30\n0.0\n"
            f"40\n{height:.4f}\n"
            f"1\n{text}\n"
            f"50\n{rotation_deg:.4f}\n"
        )

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_string(self) -> str:
        """Serialise the drawing to an AutoCAD R12 DXF string.

        Returns:
            Complete DXF file content as a UTF-8 string.
        """
        buf = io.StringIO()

        # HEADER section
        buf.write(
            "0\nSECTION\n"
            "2\nHEADER\n"
            f"9\n$ACADVER\n1\n{_DXF_HEADER}\n"
            "9\n$INSUNITS\n70\n4\n"  # 4 = mm
            "0\nENDSEC\n"
        )

        # TABLES section – LAYER table
        buf.write(
            "0\nSECTION\n"
            "2\nTABLES\n"
            "0\nTABLE\n"
            "2\nLAYER\n"
            f"70\n{len(_LAYER_COLOUR)}\n"
        )
        for lname, colour in _LAYER_COLOUR.items():
            buf.write(
                "0\nLAYER\n"
                f"2\n{lname}\n"
                "70\n0\n"
                f"62\n{colour}\n"
                "6\nCONTINUOUS\n"
            )
        buf.write("0\nENDTAB\n0\nENDSEC\n")

        # BLOCKS section (required even if empty)
        buf.write(
            "0\nSECTION\n"
            "2\nBLOCKS\n"
            "0\nBLOCK\n"
            "2\n*MODEL_SPACE\n"
            "70\n0\n"
            "10\n0.0\n20\n0.0\n30\n0.0\n"
            "3\n*MODEL_SPACE\n"
            "0\nENDBLK\n"
            "0\nENDSEC\n"
        )

        # ENTITIES section
        buf.write("0\nSECTION\n2\nENTITIES\n")
        for ent in self._entities:
            buf.write(ent)
        buf.write("0\nENDSEC\n")

        buf.write("0\nEOF\n")
        return buf.getvalue()


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------


def export_flat_pattern(
    pattern: FlatPattern,
    params: Optional[FittingParameters] = None,
    text_height_mm: float = 5.0,
) -> str:
    """Convert a FlatPattern into a complete AutoCAD R12 DXF string.

    The pattern is written using four layers:
    * ``CUT_OUTLINE``   – outer cut boundary (closed polyline)
    * ``BEND_LINES``    – fold/bend line segments
    * ``MARKING_TEXT``  – part labels
    * ``NOTCHES``       – corner notch polygons

    Args:
        pattern:        FlatPattern to export.
        params:         Optional FittingParameters (unused internally, kept
                        for API symmetry with future enrichment).
        text_height_mm: Character height for MARKING_TEXT entities (mm).

    Returns:
        DXF file content as a string.
    """
    writer = DXFWriter()

    # Cut outline
    if pattern.outline:
        writer.add_polyline(
            pattern.outline, layer=LAYER_CUT_OUTLINE, closed=True
        )

    # Bend lines
    for start, end in pattern.bend_lines:
        writer.add_line(start, end, layer=LAYER_BEND_LINES)

    # Notches
    for notch_poly in pattern.notches:
        if notch_poly:
            writer.add_polyline(
                notch_poly, layer=LAYER_NOTCHES, closed=True
            )

    # Marking text
    for pos, text in pattern.labels:
        writer.add_text(
            text, pos, height=text_height_mm, layer=LAYER_MARKING_TEXT
        )

    return writer.to_string()
