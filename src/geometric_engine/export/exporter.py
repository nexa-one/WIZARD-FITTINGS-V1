"""
Export interface for WIZARD-FITTINGS v2.0.0.

Provides a unified ``FittingExporter`` that can export sketch data to
multiple formats:

* **PNG**  – Raster image export (via stdlib ``json`` dump as a placeholder
             that a front-end can render; full raster export requires a
             canvas backend such as Pillow or a headless browser).
* **PDF**  – Portable document export (placeholder; integrate with ReportLab
             or a front-end PDF library for production use).
* **STL**  – ASCII STL export of the fitting's solid geometry primitives.
* **STEP** – STEP AP214 stub (geometry kernels such as FreeCAD/OCC required
             for full STEP output; a manifest JSON is emitted instead).

In all cases the method returns a string (file content) or raises an
``ExportError`` with a clear message.

Usage::

    from geometric_engine.export.exporter import FittingExporter

    exp = FittingExporter()
    content = exp.export(sketch, fmt="png")   # or "pdf", "stl", "step"
    with open("fitting.json", "w") as f:
        f.write(content)
"""

from __future__ import annotations

import json
import math
from typing import Any, Dict, List, Optional


class ExportError(Exception):
    """Raised when an export operation cannot be completed."""


SUPPORTED_FORMATS = ("pdf", "stl", "step", "png")


class FittingExporter:
    """
    Exports sketch data to the requested file format.

    Parameters
    ----------
    default_format:
        Default format if none is supplied to :meth:`export`.  One of
        ``"pdf"``, ``"stl"``, ``"step"``, ``"png"``.
    """

    def __init__(self, default_format: str = "pdf") -> None:
        if default_format not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported default format {default_format!r}.  "
                f"Supported: {SUPPORTED_FORMATS}"
            )
        self._default_format = default_format

    @property
    def supported_formats(self) -> tuple:
        """Tuple of supported export format strings."""
        return SUPPORTED_FORMATS

    def export(
        self,
        sketch: Dict[str, Any],
        fmt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Export *sketch* to *fmt*.

        Parameters
        ----------
        sketch:
            Sketch dict produced by :class:`~geometric_engine.renderer.sketch.SketchGenerator`.
        fmt:
            Target format (``"pdf"``, ``"stl"``, ``"step"``, ``"png"``).
            Defaults to :attr:`default_format`.
        **kwargs:
            Format-specific options (passed to the underlying exporter).

        Returns
        -------
        str
            File content as a string (JSON, SVG-flavoured text, or ASCII STL).
        """
        if not isinstance(sketch, dict):
            raise ExportError(
                f"sketch must be a dict produced by SketchGenerator; "
                f"got {type(sketch).__name__!r}."
            )
        target = (fmt or self._default_format).lower()
        if target not in SUPPORTED_FORMATS:
            raise ExportError(
                f"Unsupported format {target!r}.  "
                f"Supported: {SUPPORTED_FORMATS}"
            )
        if target == "png":
            return self._export_png(sketch, **kwargs)
        if target == "pdf":
            return self._export_pdf(sketch, **kwargs)
        if target == "stl":
            return self._export_stl(sketch, **kwargs)
        if target == "step":
            return self._export_step(sketch, **kwargs)
        raise ExportError(f"Unhandled format: {target!r}")  # unreachable

    # ------------------------------------------------------------------
    # PNG export
    # ------------------------------------------------------------------

    def _export_png(self, sketch: Dict[str, Any], **_kwargs: Any) -> str:
        """
        Return a JSON serialisation of the sketch draw commands.

        A front-end renderer (Canvas2D / WebGL) should consume this JSON to
        produce the actual raster PNG.  For headless raster generation,
        integrate Pillow or a browser automation tool.
        """
        return json.dumps({
            "format": "png",
            "fitting_id": sketch.get("fitting_id"),
            "theme": sketch.get("theme"),
            "viewport": sketch.get("viewport"),
            "draw_cmds": sketch.get("draw_cmds", []),
        }, indent=2)

    # ------------------------------------------------------------------
    # PDF export
    # ------------------------------------------------------------------

    def _export_pdf(self, sketch: Dict[str, Any], **_kwargs: Any) -> str:
        """
        Return a JSON manifest describing the PDF page layout.

        For production use, pass this manifest to ReportLab, WeasyPrint, or
        a similar PDF library that can render the draw commands.
        """
        vp = sketch.get("viewport", {"width": 800, "height": 600})
        return json.dumps({
            "format":     "pdf",
            "fitting_id": sketch.get("fitting_id"),
            "theme":      sketch.get("theme"),
            "page": {
                "width_mm":  round(vp["width"] * 0.264583, 2),
                "height_mm": round(vp["height"] * 0.264583, 2),
            },
            "title_block":      sketch.get("metadata", {}),
            "annotation_block": sketch.get("annotations", {}),
            "draw_cmds":        sketch.get("draw_cmds", []),
        }, indent=2)

    # ------------------------------------------------------------------
    # STL export
    # ------------------------------------------------------------------

    def _export_stl(self, sketch: Dict[str, Any], **_kwargs: Any) -> str:
        """
        Generate an ASCII STL representation of the fitting's polygon faces.

        Triangulates every ``polygon`` draw command using a fan from the
        first vertex.  The Z coordinate is inferred as 0 (all draw commands
        are 2-D screen projections; a proper 3-D STL requires the world-space
        geometry from the element classes).
        """
        fitting_id = sketch.get("fitting_id", "fitting")
        lines = [f"solid {fitting_id}"]

        for cmd in sketch.get("draw_cmds", []):
            if cmd.get("type") != "polygon":
                continue
            pts = cmd.get("points", [])
            if len(pts) < 3:
                continue
            # Fan triangulation from pts[0]
            p0 = pts[0]
            for i in range(1, len(pts) - 1):
                p1 = pts[i]
                p2 = pts[i + 1]
                normal = _triangle_normal(p0, p1, p2)
                lines.append(f"  facet normal {normal[0]:.6f} {normal[1]:.6f} {normal[2]:.6f}")
                lines.append("    outer loop")
                lines.append(f"      vertex {p0[0]:.6f} {p0[1]:.6f} 0.000000")
                lines.append(f"      vertex {p1[0]:.6f} {p1[1]:.6f} 0.000000")
                lines.append(f"      vertex {p2[0]:.6f} {p2[1]:.6f} 0.000000")
                lines.append("    endloop")
                lines.append("  endfacet")

        lines.append(f"endsolid {fitting_id}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # STEP export
    # ------------------------------------------------------------------

    def _export_step(self, sketch: Dict[str, Any], **_kwargs: Any) -> str:
        """
        Return a JSON manifest for STEP AP214 export.

        Full STEP output requires a geometry kernel (e.g. FreeCAD/PythonOCC).
        This manifest captures the fitting ID, geometry key, and parameters
        needed to reconstruct the solid model.
        """
        return json.dumps({
            "format":     "step",
            "standard":   "AP214",
            "fitting_id": sketch.get("fitting_id"),
            "geometry":   sketch.get("geometry"),
            "metadata":   sketch.get("metadata", {}),
            "note":       (
                "STEP AP214 solid export requires a geometry kernel. "
                "Pass this manifest to a FreeCAD/OCC pipeline to generate "
                "the .step file."
            ),
        }, indent=2)


# ---------------------------------------------------------------------------
# STL helper
# ---------------------------------------------------------------------------

def _triangle_normal(
    p0: tuple, p1: tuple, p2: tuple
) -> tuple:
    """Return the unit normal of the triangle (p0, p1, p2) in 2-D (z=0)."""
    ax, ay = p1[0] - p0[0], p1[1] - p0[1]
    bx, by = p2[0] - p0[0], p2[1] - p0[1]
    nx, ny, nz = 0.0, 0.0, ax * by - ay * bx
    mag = math.sqrt(nx**2 + ny**2 + nz**2) or 1.0
    return (nx / mag, ny / mag, nz / mag)
