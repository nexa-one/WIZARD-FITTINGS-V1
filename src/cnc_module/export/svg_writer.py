"""
cnc_module.export.svg_writer
============================
SVG exporter for flat-pattern panels (2-D cutting templates) and
3-D hollow-duct isometric views.

SVG output is compatible with Inkscape, web browsers, and most
pre-press workflows.  Flat-pattern panels are colour-coded:

  • Red solid lines   = CUT boundary
  • Blue dashed lines = BEND / fold lines
  • Green dashed      = SEAM allowances
  • Magenta dash-dot  = ETCH / reference marks
"""

from __future__ import annotations

import os
from typing import List, Tuple

from cnc_module.flat_pattern.pattern import (
    FlatPattern, Panel, AnnotatedLine, LineType,
)

# Pixel scale: 1 mm → _SCALE px
_SCALE = 1.0   # 1:1 (SVG user units = mm)

_LAYER_STYLE = {
    LineType.CUT:    'stroke="#e63946" stroke-width="1.5" fill="none"',
    LineType.BEND:   'stroke="#4361ee" stroke-width="1" stroke-dasharray="6,3" fill="none"',
    LineType.SEAM:   'stroke="#2d6a4f" stroke-width="1" stroke-dasharray="4,4" fill="none"',
    LineType.ETCH:   'stroke="#9b2226" stroke-width="0.7" stroke-dasharray="3,2,1,2" fill="none"',
    LineType.HOLE:   'stroke="#e63946" stroke-width="1" fill="none"',
    LineType.SCRIBE: 'stroke="#6d6875" stroke-width="0.5" fill="none"',
}

_PANEL_FILL = "#f1f5f9"    # light blue-grey panel fill
_PANEL_STROKE = "#e63946"  # red boundary


class SVGExporter:
    """Export flat-pattern panels or 3-D renders to SVG.

    Parameters
    ----------
    margin:  Border margin around the content (mm → SVG user units).
    """

    def __init__(self, margin: float = 20.0) -> None:
        self.margin = margin

    # ================================================================== #
    # Flat-pattern 2-D export                                             #
    # ================================================================== #
    def export_flat_pattern(
        self,
        pattern: FlatPattern,
        filepath: str,
        nest: bool = True,
    ) -> None:
        """Write the flat pattern to *filepath* as an SVG file."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        svg = self.flat_pattern_to_string(pattern, nest=nest)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg)

    def flat_pattern_to_string(
        self,
        pattern: FlatPattern,
        nest: bool = True,
    ) -> str:
        """Return the flat-pattern SVG as a string."""
        panels = pattern.nest() if nest else pattern.panels
        return self._build_flat_svg(panels, pattern.fitting_label)

    def _build_flat_svg(self, panels: List[Panel], title: str) -> str:
        m = self.margin
        if not panels:
            return f'<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg"><text x="10" y="50">No panels</text></svg>'

        # Determine canvas size from nested panel extents
        max_x = max_y = 0.0
        for p in panels:
            _, _, px, py = p.bounding_box
            max_x = max(max_x, px)
            max_y = max(max_y, py)

        vw = max_x + 2 * m
        vh = max_y + 2 * m

        lines: List[str] = [
            f'<svg width="{vw:.1f}mm" height="{vh:.1f}mm" '
            f'viewBox="0 0 {vw:.2f} {vh:.2f}" '
            f'xmlns="http://www.w3.org/2000/svg">',
            f'  <title>{title} – Flat Pattern</title>',
            "  <!-- WIZARD-FITTINGS CNC Flat Metal Template -->",
            # Light background
            f'  <rect width="{vw:.2f}" height="{vh:.2f}" fill="#f8f9fa"/>',
            # Sheet outline
            f'  <rect x="{m:.2f}" y="{m:.2f}" '
            f'width="{max_x:.2f}" height="{max_y:.2f}" '
            f'fill="none" stroke="#cccccc" stroke-width="0.5" stroke-dasharray="10,5"/>',
        ]

        for panel in panels:
            lines.extend(self._panel_svg(panel, m, m))

        # Title
        lines.append(
            f'  <text x="{m}" y="{vh - 5}" '
            f'font-family="sans-serif" font-size="4" fill="#555555">'
            f'{title}</text>'
        )
        lines.append("</svg>")
        return "\n".join(lines)

    def _panel_svg(self, panel: Panel, ox: float, oy: float) -> List[str]:
        """Generate SVG elements for a single panel."""
        lines: List[str] = []
        # Boundary polygon
        pts = " ".join(
            f"{x:.3f},{y:.3f}" for x, y in panel.boundary
        )
        lines.append(
            f'  <polygon points="{pts}" '
            f'fill="{_PANEL_FILL}" fill-opacity="0.9" '
            f'stroke="{_PANEL_STROKE}" stroke-width="1.5"/>'
        )

        # Annotated internal lines
        for al in panel.lines:
            style = _LAYER_STYLE.get(al.line_type, _LAYER_STYLE[LineType.ETCH])
            x1, y1 = al.start
            x2, y2 = al.end
            lines.append(
                f'  <line x1="{x1:.3f}" y1="{y1:.3f}" '
                f'x2="{x2:.3f}" y2="{y2:.3f}" {style}/>'
            )

        # Holes
        for (cx, cy), dia in panel.holes:
            lines.append(
                f'  <circle cx="{cx:.3f}" cy="{cy:.3f}" '
                f'r="{dia/2:.3f}" {_LAYER_STYLE[LineType.HOLE]}/>'
            )

        # Label
        mn_x, mn_y, _, _ = panel.bounding_box
        lines.append(
            f'  <text x="{mn_x + 3:.2f}" y="{mn_y + 8:.2f}" '
            f'font-family="sans-serif" font-size="4" fill="#1a1a2e">'
            f'{panel.name}</text>'
        )
        # Dimension label
        lines.append(
            f'  <text x="{mn_x + 3:.2f}" y="{mn_y + 14:.2f}" '
            f'font-family="monospace" font-size="3" fill="#555555">'
            f'{panel.width:.0f} × {panel.height:.0f} mm</text>'
        )
        return lines

    # ================================================================== #
    # 3-D render export                                                    #
    # ================================================================== #
    def export_3d_view(
        self,
        svg_content: str,
        filepath: str,
    ) -> None:
        """Write an already-rendered SVG string to *filepath*."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg_content)
