"""
Sketch generator – produces a full isometric sketch for a SMACNA fitting.

A *sketch* is a dict with the following structure::

    {
        "fitting_id":  "RE-4",
        "geometry":    "rectElbow_radius",
        "theme":       "light_technical",
        "viewport":    {"width": 800, "height": 600},
        "draw_cmds":   [ ... ],        # list of draw-command dicts
        "metadata":    { ... },        # title block fields
        "annotations": { ... },        # annotation block fields
    }

The ``draw_cmds`` list can be passed directly to a front-end Canvas2D
renderer.

Usage::

    from geometric_engine.renderer.sketch import SketchGenerator
    from geometric_engine.registry.fitting_registry import get_fitting

    gen = SketchGenerator(theme="light_technical")
    sketch = gen.generate(
        fitting_id="RE-4",
        params={"W": 0.4, "H": 0.3, "R": 0.6},
        metadata={"project": "Site A", "prepared_by": "J. Smith"},
    )
"""

from __future__ import annotations

import math
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .isometric import (
    IsometricProjection,
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
from .theme import ThemeManager
from ..registry.fitting_registry import get_fitting, FittingEntry


# ---------------------------------------------------------------------------
# Geometry render categories
# ---------------------------------------------------------------------------

class _RenderCategory(Enum):
    """Internal category used to route geometry-key → render function."""
    RECT_BOX   = "rect_box"    # rectangular duct / cap / offset / special / supports
    CYLINDER   = "cylinder"    # circular duct
    OVAL_DUCT  = "oval_duct"   # flat-oval duct
    CONE       = "cone"        # reducer / expander (concentric cone frustum)
    ELBOW_ARC  = "elbow_arc"   # elbow (swept arc)
    FALLBACK   = "fallback"    # unknown – render as generic box


# Geometry key → render category mapping
# The keys are exact geometry strings from fitting_registry.py.
# Any key not listed falls back to FALLBACK (which renders as a box).
_GEOMETRY_CATEGORY: Dict[str, _RenderCategory] = {}

# Rectangular box group
for _g in [
    "rectBox_miter_90", "rectElbow_radius", "rectElbow_radius_45",
    "rectElbow_adjustable", "rectElbow_long_radius", "rectElbow_angle",
    "rectOffset_single", "rectOffset_double", "rectOffset_symmetric",
    "rectOffset_vertical", "rectOffset_lateral",
    "rectTee_equal", "rectTee_conical", "rectTee_splitter", "rectLateral_45",
    "rectWye_equal", "rectTee_vaned", "rectBoot", "rectTee_unequal",
    "rectTap_straight", "rectWye_conical",
    "rectReducer_symmetric", "rectReducer_eccentric", "rectExpander",
    "rectReducer_offset", "rectToRound", "rectToOval",
    "rectReducer_sharp", "rectTransition_multi",
    "rectCap_flat", "rectCap_angled", "rectDamperFrame", "rectTestPort",
    "rectDamperVCD", "rectFireDamper", "rectFSD", "rectAccessDoor",
    "rectFlexConnector", "rectLinerThroat", "rectPlenumTakeoff",
    "rectRegisterBoot", "rectDoubleWall",
    "hanger_strap", "hanger_trapeze", "hanger_beamClamp", "hanger_tieRod",
    "seismic_longitudinal", "seismic_transverse",
]:
    _GEOMETRY_CATEGORY[_g] = _RenderCategory.RECT_BOX

# Circular cylinder group
for _g in [
    "circElbow_5gore_90", "circElbow_3gore_45", "circElbow_30",
    "circElbow_4gore_60", "circElbow_adjustable", "circElbow_longR",
    "circElbow_mitered",
    "circTee_90", "circWye_45_equal", "circTee_equal", "circLateral_45",
    "circSaddleTap", "circWye_unequal", "circSpinIn", "circTee_reducing",
    "circManifold", "circWye_30",
    "hanger_clevis", "hanger_band", "circBellMouth",
]:
    _GEOMETRY_CATEGORY[_g] = _RenderCategory.CYLINDER

# Oval group
for _g in [
    "ovalElbow_90", "ovalElbow_45", "ovalTee_90", "ovalWye_45",
    "ovalReducer", "ovalToRound", "ovalToRect", "ovalOffset",
]:
    _GEOMETRY_CATEGORY[_g] = _RenderCategory.OVAL_DUCT

# Cone / reducer group
for _g in [
    "circReducer_concentric", "circReducer_eccentric", "circToRect",
    "circToOval", "circExpander", "circReducer_abrupt", "circReducer_gored",
]:
    _GEOMETRY_CATEGORY[_g] = _RenderCategory.CONE

# Elbow arc group (circular elbows that look better as arcs than cylinders)
# (re-assigned; the circ-elbow entries above already use CYLINDER –
#  leave them; this group is for any additional arc-specific keys)


class SketchGenerator:
    """
    Generates isometric sketches for SMACNA fittings.

    Parameters
    ----------
    theme:
        Theme name (``"light_technical"``, ``"dark_professional"``,
        ``"blueprint"``).
    scale:
        Pixels per metre.
    viewport_width, viewport_height:
        Sketch canvas dimensions in pixels.
    """

    def __init__(
        self,
        theme: str = "light_technical",
        scale: float = 200.0,
        viewport_width: float = 800.0,
        viewport_height: float = 600.0,
    ) -> None:
        self._tm = ThemeManager(theme)
        self._scale = scale
        self._vw = viewport_width
        self._vh = viewport_height
        self._proj = IsometricProjection(
            scale=scale,
            offset_cx=viewport_width / 2,
            offset_cy=viewport_height / 2,
        )

    @property
    def theme_manager(self) -> ThemeManager:
        return self._tm

    def generate(
        self,
        fitting_id: str,
        params: Dict[str, float],
        metadata: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a sketch dict for *fitting_id* with *params*.

        Parameters
        ----------
        fitting_id:
            SMACNA fitting ID (e.g. ``"RE-4"``).
        params:
            Dict mapping parameter names to values (metres).
        metadata:
            Fields for the title block (e.g. ``project``, ``prepared_by``).
        annotations:
            Fields for the annotation block.
        """
        entry = get_fitting(fitting_id)
        draw_cmds: List[Dict[str, Any]] = []

        # Background
        draw_cmds.append({
            "type": "background",
            "fill": self._tm.theme.background,
        })

        # Fitting geometry
        geom_cmds = self._generate_geometry(entry, params)
        draw_cmds.extend(geom_cmds)

        # Dimension lines
        dim_cmds = self._generate_dimensions(entry, params)
        draw_cmds.extend(dim_cmds)

        # Coordinate cube
        draw_cmds.extend(iso_coord_cube(
            position="top_right",
            size_px=80,
            viewport_w=self._vw,
            viewport_h=self._vh,
        ))

        # Title block
        tb_fields = {
            "fitting_id": fitting_id,
            "geometry":   entry.geometry,
            "category":   entry.label,
        }
        if metadata:
            tb_fields.update(metadata)
        draw_cmds.extend(iso_title_block(
            fields=tb_fields,
            position="bottom_right",
            viewport_w=self._vw,
            viewport_h=self._vh,
        ))

        # Annotation block
        ann_fields = {
            "description": entry.description,
            "params":      ", ".join(f"{k}={v}" for k, v in params.items()),
        }
        if annotations:
            ann_fields.update(annotations)
        draw_cmds.extend(iso_annotation_block(
            fields=ann_fields,
            position="bottom_left",
            viewport_w=self._vw,
            viewport_h=self._vh,
        ))

        return {
            "fitting_id":  fitting_id,
            "geometry":    entry.geometry,
            "theme":       self._tm.theme.name,
            "viewport":    {"width": self._vw, "height": self._vh},
            "draw_cmds":   draw_cmds,
            "metadata":    tb_fields,
            "annotations": ann_fields,
        }

    # ------------------------------------------------------------------
    # Geometry generators – dispatch via _GEOMETRY_CATEGORY registry
    # ------------------------------------------------------------------

    def _generate_geometry(
        self,
        entry: FittingEntry,
        params: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """Dispatch to the correct geometry builder via the category registry."""
        category = _GEOMETRY_CATEGORY.get(entry.geometry, _RenderCategory.FALLBACK)
        fc = self._tm.face_colors()

        if category == _RenderCategory.RECT_BOX:
            return self._render_rect_box(params, fc)
        if category == _RenderCategory.CYLINDER:
            return self._render_cylinder(params, fc)
        if category == _RenderCategory.OVAL_DUCT:
            return self._render_oval(params, fc)
        if category == _RenderCategory.CONE:
            return self._render_cone(params, fc)
        if category == _RenderCategory.ELBOW_ARC:
            return self._render_elbow_arc(params, fc)
        # FALLBACK
        return self._render_rect_box(params, fc)

    def _render_rect_box(
        self,
        params: Dict[str, float],
        fc: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        W = params.get("W", params.get("W1", params.get("W_main", 0.4)))
        H = params.get("H", params.get("H1", params.get("H_main", 0.3)))
        L = params.get("L", params.get("length", W))
        return iso_box(self._proj, -L / 2, 0, -W / 2, W, H, L, fc)

    def _render_cylinder(
        self,
        params: Dict[str, float],
        fc: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        D = params.get("D", params.get("D1", params.get("D_main", 0.4)))
        L = params.get("L", D)
        return iso_cylinder(
            self._proj, -L / 2, -D / 4, 0, D / 2, L, axis="X", theme_colors=fc
        )

    def _render_oval(
        self,
        params: Dict[str, float],
        fc: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        Wo = params.get("Wo", params.get("Wo1", 0.5))
        Ho = params.get("Ho", params.get("Ho1", 0.25))
        L = params.get("L", Wo)
        return iso_flat_oval(
            self._proj, -L / 2, 0, -Wo / 2, Wo, Ho, L, axis="X", theme_colors=fc
        )

    def _render_cone(
        self,
        params: Dict[str, float],
        fc: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        D1 = params.get("D1", params.get("D", 0.5))
        D2 = params.get("D2", D1 * 0.7)
        L = params.get("L", D1 * 1.5)
        return iso_cone(
            self._proj, -L / 2, 0, 0, D1 / 2, D2 / 2, L, axis="X", theme_colors=fc
        )

    def _render_elbow_arc(
        self,
        params: Dict[str, float],
        fc: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        D = params.get("D", params.get("W", 0.4))
        R = params.get("R", D * 1.5)
        end_angle = params.get("angle", 90.0)
        return iso_elbow_arc(
            self._proj, 0, 0, 0, R, D, 0, end_angle, axis="Y", theme_colors=fc
        )

    def _generate_dimensions(
        self,
        entry: FittingEntry,
        params: Dict[str, float],
    ) -> List[Dict[str, Any]]:
        """Add dimension lines for the primary parameters."""
        cmds: List[Dict[str, Any]] = []
        dim_color = self._tm.dim_color()

        W = params.get("W", params.get("W1", params.get("D", 0.4)))
        H = params.get("H", params.get("H1", params.get("D", W)))
        L = params.get("L", W)

        # Width dimension (along Z)
        cmds.extend(iso_dim_line(
            self._proj,
            p1=(0, 0, -W / 2),
            p2=(0, 0,  W / 2),
            label=f"W={W * 1000:.0f}mm",
            offset=0.06,
            color=dim_color,
        ))

        # Height dimension (along Y)
        cmds.extend(iso_dim_line(
            self._proj,
            p1=(0, 0,     W / 2),
            p2=(0, H,     W / 2),
            label=f"H={H * 1000:.0f}mm",
            offset=0.06,
            color=dim_color,
        ))

        # Length/depth dimension (along X)
        cmds.extend(iso_dim_line(
            self._proj,
            p1=(-L / 2, H / 2, W / 2),
            p2=( L / 2, H / 2, W / 2),
            label=f"L={L * 1000:.0f}mm",
            offset=0.06,
            color=dim_color,
        ))

        return cmds

