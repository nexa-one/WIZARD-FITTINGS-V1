"""
SMACNA Fitting Registry – WIZARD-FITTINGS v2.0.0
==================================================

Catalogue of all 87 SMACNA fittings.  Each entry stores:

* ``id``           – SMACNA reference code (e.g. ``"RE-1"``).
* ``category``     – Two-letter category code (``"RE"``, ``"RO"``, …).
* ``label``        – Human-readable category label.
* ``geometry``     – Internal geometry-generator key used by the renderer.
* ``vanes``        – Turning-vane spec or ``False`` / ``None``.
* ``params``       – List of required dimension parameter names.
* ``description``  – Short free-text description.

Usage::

    from geometric_engine.registry.fitting_registry import FITTING_REGISTRY, get_fitting

    entry = get_fitting("RE-4")
    print(entry.params)          # ['W', 'H', 'R']
    print(entry.geometry)        # 'rectElbow_radius'

    all_re = list_category("RE")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union


@dataclass(frozen=True)
class FittingEntry:
    """Immutable descriptor for one SMACNA fitting instance."""

    id: str
    category: str
    label: str
    geometry: str
    params: List[str]
    vanes: Union[bool, str, None] = False
    description: str = ""


# ---------------------------------------------------------------------------
# Registry data – 87 fittings
# ---------------------------------------------------------------------------

_RAW: List[dict] = [
    # -----------------------------------------------------------------------
    # RE – Rectangular Elbows (10)
    # -----------------------------------------------------------------------
    {"id": "RE-1",  "cat": "RE", "label": "Rectangular Elbows",
     "geometry": "rectBox_miter_90",      "vanes": False,
     "params": ["W", "H", "angle"],
     "description": "Mitered rectangular elbow, no turning vanes"},
    {"id": "RE-2",  "cat": "RE", "label": "Rectangular Elbows",
     "geometry": "rectBox_miter_90",      "vanes": "single",
     "params": ["W", "H", "vane_spacing"],
     "description": "Mitered rectangular elbow, single-blade turning vanes"},
    {"id": "RE-3",  "cat": "RE", "label": "Rectangular Elbows",
     "geometry": "rectBox_miter_90",      "vanes": "double",
     "params": ["W", "H"],
     "description": "Mitered rectangular elbow, double-blade turning vanes"},
    {"id": "RE-4",  "cat": "RE", "label": "Rectangular Elbows",
     "geometry": "rectElbow_radius",      "vanes": False,
     "params": ["W", "H", "R"],
     "description": "Smooth-radius rectangular 90° elbow"},
    {"id": "RE-5",  "cat": "RE", "label": "Rectangular Elbows",
     "geometry": "rectElbow_radius_45",   "vanes": False,
     "params": ["W", "H", "R"],
     "description": "Smooth-radius rectangular 45° elbow"},
    {"id": "RE-6",  "cat": "RE", "label": "Rectangular Elbows",
     "geometry": "rectBox_miter_90",      "vanes": False,
     "params": ["W", "H"],
     "description": "Square-throat mitered elbow"},
    {"id": "RE-7",  "cat": "RE", "label": "Rectangular Elbows",
     "geometry": "rectElbow_adjustable",  "vanes": False,
     "params": ["W", "H", "angle"],
     "description": "Adjustable-angle rectangular elbow"},
    {"id": "RE-8",  "cat": "RE", "label": "Rectangular Elbows",
     "geometry": "rectElbow_radius",      "vanes": "splitter",
     "params": ["W", "H", "R"],
     "description": "Radius elbow with splitter vanes"},
    {"id": "RE-9",  "cat": "RE", "label": "Rectangular Elbows",
     "geometry": "rectElbow_long_radius", "vanes": False,
     "params": ["W", "H", "R"],
     "description": "Long-radius rectangular elbow (R/W ≥ 2)"},
    {"id": "RE-10", "cat": "RE", "label": "Rectangular Elbows",
     "geometry": "rectElbow_angle",       "vanes": False,
     "params": ["W", "H", "angle"],
     "description": "Variable-angle rectangular elbow"},

    # -----------------------------------------------------------------------
    # RO – Rectangular Offsets (5)
    # -----------------------------------------------------------------------
    {"id": "RO-1", "cat": "RO", "label": "Rectangular Offsets",
     "geometry": "rectOffset_single",    "params": ["W", "H", "L", "offset"],
     "description": "Single-plane S-curve offset"},
    {"id": "RO-2", "cat": "RO", "label": "Rectangular Offsets",
     "geometry": "rectOffset_double",    "params": ["W", "H", "Lx", "Ly"],
     "description": "Double-plane (X and Y) offset"},
    {"id": "RO-3", "cat": "RO", "label": "Rectangular Offsets",
     "geometry": "rectOffset_symmetric", "params": ["W", "H", "L"],
     "description": "Symmetric S-curve offset"},
    {"id": "RO-4", "cat": "RO", "label": "Rectangular Offsets",
     "geometry": "rectOffset_vertical",  "params": ["W", "H", "rise"],
     "description": "Vertical rise offset"},
    {"id": "RO-5", "cat": "RO", "label": "Rectangular Offsets",
     "geometry": "rectOffset_lateral",   "params": ["W", "H", "lateral"],
     "description": "Lateral (horizontal) offset"},

    # -----------------------------------------------------------------------
    # RT – Rectangular Tees & Wyes (10)
    # -----------------------------------------------------------------------
    {"id": "RT-1",  "cat": "RT", "label": "Rectangular Tees & Wyes",
     "geometry": "rectTee_equal",    "params": ["W_main", "H_main", "W_branch", "H_branch"],
     "description": "Equal-area rectangular tee"},
    {"id": "RT-2",  "cat": "RT", "label": "Rectangular Tees & Wyes",
     "geometry": "rectTee_conical",  "params": ["W_main", "H_main", "W_branch", "H_branch"],
     "description": "Conical-entrance rectangular tee"},
    {"id": "RT-3",  "cat": "RT", "label": "Rectangular Tees & Wyes",
     "geometry": "rectTee_splitter", "params": ["W", "H", "W_b"],
     "description": "Splitter-vane rectangular tee"},
    {"id": "RT-4",  "cat": "RT", "label": "Rectangular Tees & Wyes",
     "geometry": "rectLateral_45",   "params": ["W_main", "W_branch", "angle"],
     "description": "45° rectangular lateral"},
    {"id": "RT-5",  "cat": "RT", "label": "Rectangular Tees & Wyes",
     "geometry": "rectWye_equal",    "params": ["W_in", "W_b1", "W_b2"],
     "description": "Equal-branch rectangular wye"},
    {"id": "RT-6",  "cat": "RT", "label": "Rectangular Tees & Wyes",
     "geometry": "rectTee_vaned",    "params": ["W_main", "W_branch"],
     "description": "Vaned rectangular tee"},
    {"id": "RT-7",  "cat": "RT", "label": "Rectangular Tees & Wyes",
     "geometry": "rectBoot",         "params": ["W_in", "W_out", "H"],
     "description": "Rectangular boot fitting"},
    {"id": "RT-8",  "cat": "RT", "label": "Rectangular Tees & Wyes",
     "geometry": "rectTee_unequal",  "params": ["W_main", "W_b1", "W_b2"],
     "description": "Unequal-branch rectangular tee"},
    {"id": "RT-9",  "cat": "RT", "label": "Rectangular Tees & Wyes",
     "geometry": "rectTap_straight", "params": ["W_main", "W_tap", "H_tap"],
     "description": "Straight rectangular tap fitting"},
    {"id": "RT-10", "cat": "RT", "label": "Rectangular Tees & Wyes",
     "geometry": "rectWye_conical",  "params": ["W_in", "W_b", "angle"],
     "description": "Conical rectangular wye"},

    # -----------------------------------------------------------------------
    # RR – Rectangular Reducers (8)
    # -----------------------------------------------------------------------
    {"id": "RR-1", "cat": "RR", "label": "Rectangular Reducers",
     "geometry": "rectReducer_symmetric", "params": ["W1", "H1", "W2", "H2", "L"],
     "description": "Symmetric concentric rectangular reducer"},
    {"id": "RR-2", "cat": "RR", "label": "Rectangular Reducers",
     "geometry": "rectReducer_eccentric", "params": ["W1", "H1", "W2", "H2", "L"],
     "description": "Eccentric rectangular reducer"},
    {"id": "RR-3", "cat": "RR", "label": "Rectangular Reducers",
     "geometry": "rectExpander",          "params": ["W1", "W2", "L"],
     "description": "Rectangular expander (diffuser)"},
    {"id": "RR-4", "cat": "RR", "label": "Rectangular Reducers",
     "geometry": "rectReducer_offset",    "params": ["W1", "W2", "offset"],
     "description": "Offset rectangular reducer"},
    {"id": "RR-5", "cat": "RR", "label": "Rectangular Reducers",
     "geometry": "rectToRound",           "params": ["W", "H", "D", "L"],
     "description": "Rectangular-to-round transition"},
    {"id": "RR-6", "cat": "RR", "label": "Rectangular Reducers",
     "geometry": "rectToOval",            "params": ["W", "H", "Wo", "Ho", "L"],
     "description": "Rectangular-to-oval transition"},
    {"id": "RR-7", "cat": "RR", "label": "Rectangular Reducers",
     "geometry": "rectReducer_sharp",     "params": ["W1", "W2", "L"],
     "description": "Sharp-taper rectangular reducer"},
    {"id": "RR-8", "cat": "RR", "label": "Rectangular Reducers",
     "geometry": "rectTransition_multi",  "params": ["custom"],
     "description": "Multi-section rectangular transition"},

    # -----------------------------------------------------------------------
    # RC – Rectangular Caps (4)
    # -----------------------------------------------------------------------
    {"id": "RC-1", "cat": "RC", "label": "Rectangular Caps",
     "geometry": "rectCap_flat",    "params": ["W", "H"],
     "description": "Flat rectangular end-cap"},
    {"id": "RC-2", "cat": "RC", "label": "Rectangular Caps",
     "geometry": "rectCap_angled",  "params": ["W", "H", "angle"],
     "description": "Angled rectangular end-cap"},
    {"id": "RC-3", "cat": "RC", "label": "Rectangular Caps",
     "geometry": "rectDamperFrame", "params": ["W", "H", "L"],
     "description": "Rectangular damper frame"},
    {"id": "RC-4", "cat": "RC", "label": "Rectangular Caps",
     "geometry": "rectTestPort",    "params": ["W", "H"],
     "description": "Rectangular test port cap"},

    # -----------------------------------------------------------------------
    # CE – Circular Elbows (7)
    # -----------------------------------------------------------------------
    {"id": "CE-1", "cat": "CE", "label": "Circular Elbows",
     "geometry": "circElbow_5gore_90",   "params": ["D", "R"],
     "description": "5-gore 90° circular elbow"},
    {"id": "CE-2", "cat": "CE", "label": "Circular Elbows",
     "geometry": "circElbow_3gore_45",   "params": ["D", "R"],
     "description": "3-gore 45° circular elbow"},
    {"id": "CE-3", "cat": "CE", "label": "Circular Elbows",
     "geometry": "circElbow_30",         "params": ["D", "R"],
     "description": "30° circular elbow"},
    {"id": "CE-4", "cat": "CE", "label": "Circular Elbows",
     "geometry": "circElbow_4gore_60",   "params": ["D", "R"],
     "description": "4-gore 60° circular elbow"},
    {"id": "CE-5", "cat": "CE", "label": "Circular Elbows",
     "geometry": "circElbow_adjustable", "params": ["D", "angle"],
     "description": "Adjustable-angle circular elbow"},
    {"id": "CE-6", "cat": "CE", "label": "Circular Elbows",
     "geometry": "circElbow_longR",      "params": ["D", "R"],
     "description": "Long-radius circular elbow"},
    {"id": "CE-7", "cat": "CE", "label": "Circular Elbows",
     "geometry": "circElbow_mitered",    "params": ["D"],
     "description": "Mitered circular elbow"},

    # -----------------------------------------------------------------------
    # CT – Circular Tees & Wyes (10)
    # -----------------------------------------------------------------------
    {"id": "CT-1",  "cat": "CT", "label": "Circular Tees & Wyes",
     "geometry": "circTee_90",       "params": ["D_main", "D_branch"],
     "description": "90° circular tee"},
    {"id": "CT-2",  "cat": "CT", "label": "Circular Tees & Wyes",
     "geometry": "circWye_45_equal", "params": ["D_in", "D_b"],
     "description": "45° equal circular wye"},
    {"id": "CT-3",  "cat": "CT", "label": "Circular Tees & Wyes",
     "geometry": "circTee_equal",    "params": ["D"],
     "description": "Equal circular tee"},
    {"id": "CT-4",  "cat": "CT", "label": "Circular Tees & Wyes",
     "geometry": "circLateral_45",   "params": ["D_main", "D_branch"],
     "description": "45° circular lateral"},
    {"id": "CT-5",  "cat": "CT", "label": "Circular Tees & Wyes",
     "geometry": "circSaddleTap",    "params": ["D_main", "D_tap"],
     "description": "Saddle tap on circular duct"},
    {"id": "CT-6",  "cat": "CT", "label": "Circular Tees & Wyes",
     "geometry": "circWye_unequal",  "params": ["D_in", "D_b1", "D_b2"],
     "description": "Unequal circular wye"},
    {"id": "CT-7",  "cat": "CT", "label": "Circular Tees & Wyes",
     "geometry": "circSpinIn",       "params": ["D_main", "D_tap"],
     "description": "Spin-in circular tee tap"},
    {"id": "CT-8",  "cat": "CT", "label": "Circular Tees & Wyes",
     "geometry": "circTee_reducing", "params": ["D_main", "D_branch"],
     "description": "Reducing circular tee"},
    {"id": "CT-9",  "cat": "CT", "label": "Circular Tees & Wyes",
     "geometry": "circManifold",     "params": ["D_main", "D_branch", "n_branches"],
     "description": "Multi-outlet circular manifold"},
    {"id": "CT-10", "cat": "CT", "label": "Circular Tees & Wyes",
     "geometry": "circWye_30",       "params": ["D_in", "D_b"],
     "description": "30° circular wye"},

    # -----------------------------------------------------------------------
    # CR – Circular Reducers (7)
    # -----------------------------------------------------------------------
    {"id": "CR-1", "cat": "CR", "label": "Circular Reducers",
     "geometry": "circReducer_concentric", "params": ["D1", "D2", "L"],
     "description": "Concentric circular reducer"},
    {"id": "CR-2", "cat": "CR", "label": "Circular Reducers",
     "geometry": "circReducer_eccentric",  "params": ["D1", "D2", "L"],
     "description": "Eccentric circular reducer"},
    {"id": "CR-3", "cat": "CR", "label": "Circular Reducers",
     "geometry": "circToRect",             "params": ["D", "W", "H", "L"],
     "description": "Circular-to-rectangular transition"},
    {"id": "CR-4", "cat": "CR", "label": "Circular Reducers",
     "geometry": "circToOval",             "params": ["D", "Wo", "Ho", "L"],
     "description": "Circular-to-oval transition"},
    {"id": "CR-5", "cat": "CR", "label": "Circular Reducers",
     "geometry": "circExpander",           "params": ["D1", "D2", "L"],
     "description": "Circular expander (diffuser)"},
    {"id": "CR-6", "cat": "CR", "label": "Circular Reducers",
     "geometry": "circReducer_abrupt",     "params": ["D1", "D2"],
     "description": "Abrupt circular reducer"},
    {"id": "CR-7", "cat": "CR", "label": "Circular Reducers",
     "geometry": "circReducer_gored",      "params": ["D1", "D2", "L", "gores"],
     "description": "Gored circular reducer"},

    # -----------------------------------------------------------------------
    # FO – Flat Oval Fittings (8)
    # -----------------------------------------------------------------------
    {"id": "FO-1", "cat": "FO", "label": "Flat Oval Fittings",
     "geometry": "ovalElbow_90",  "params": ["Wo", "Ho", "R"],
     "description": "90° flat-oval elbow"},
    {"id": "FO-2", "cat": "FO", "label": "Flat Oval Fittings",
     "geometry": "ovalElbow_45",  "params": ["Wo", "Ho", "R"],
     "description": "45° flat-oval elbow"},
    {"id": "FO-3", "cat": "FO", "label": "Flat Oval Fittings",
     "geometry": "ovalTee_90",    "params": ["Wo_main", "Ho_main", "D_branch"],
     "description": "Flat-oval main duct with round branch tee"},
    {"id": "FO-4", "cat": "FO", "label": "Flat Oval Fittings",
     "geometry": "ovalWye_45",    "params": ["Wo", "Ho"],
     "description": "45° flat-oval wye"},
    {"id": "FO-5", "cat": "FO", "label": "Flat Oval Fittings",
     "geometry": "ovalReducer",   "params": ["Wo1", "Ho1", "Wo2", "Ho2", "L"],
     "description": "Flat-oval to flat-oval reducer"},
    {"id": "FO-6", "cat": "FO", "label": "Flat Oval Fittings",
     "geometry": "ovalToRound",   "params": ["Wo", "Ho", "D", "L"],
     "description": "Flat-oval to round transition"},
    {"id": "FO-7", "cat": "FO", "label": "Flat Oval Fittings",
     "geometry": "ovalToRect",    "params": ["Wo", "Ho", "W", "H", "L"],
     "description": "Flat-oval to rectangular transition"},
    {"id": "FO-8", "cat": "FO", "label": "Flat Oval Fittings",
     "geometry": "ovalOffset",    "params": ["Wo", "Ho", "offset"],
     "description": "Flat-oval single-plane offset"},

    # -----------------------------------------------------------------------
    # SP – Special & Accessory (10)
    # -----------------------------------------------------------------------
    {"id": "SP-1",  "cat": "SP", "label": "Special & Accessory",
     "geometry": "rectDamperVCD",     "params": ["W", "H", "L"],
     "description": "Rectangular volume-control damper (VCD)"},
    {"id": "SP-2",  "cat": "SP", "label": "Special & Accessory",
     "geometry": "rectFireDamper",    "params": ["W", "H", "L"],
     "description": "Rectangular fire damper frame"},
    {"id": "SP-3",  "cat": "SP", "label": "Special & Accessory",
     "geometry": "rectFSD",           "params": ["W", "H"],
     "description": "Rectangular fire–smoke damper (FSD)"},
    {"id": "SP-4",  "cat": "SP", "label": "Special & Accessory",
     "geometry": "rectAccessDoor",    "params": ["panel_W", "panel_H"],
     "description": "Rectangular duct access door"},
    {"id": "SP-5",  "cat": "SP", "label": "Special & Accessory",
     "geometry": "rectFlexConnector", "params": ["W", "H", "L"],
     "description": "Rectangular flexible connector"},
    {"id": "SP-6",  "cat": "SP", "label": "Special & Accessory",
     "geometry": "rectLinerThroat",   "params": ["W", "H"],
     "description": "Rectangular duct liner throat section"},
    {"id": "SP-7",  "cat": "SP", "label": "Special & Accessory",
     "geometry": "circBellMouth",     "params": ["D", "R"],
     "description": "Circular bell-mouth inlet"},
    {"id": "SP-8",  "cat": "SP", "label": "Special & Accessory",
     "geometry": "rectPlenumTakeoff", "params": ["W", "H", "W_out", "H_out"],
     "description": "Rectangular plenum with offset takeoff"},
    {"id": "SP-9",  "cat": "SP", "label": "Special & Accessory",
     "geometry": "rectRegisterBoot",  "params": ["W", "H", "D_neck"],
     "description": "Rectangular register boot"},
    {"id": "SP-10", "cat": "SP", "label": "Special & Accessory",
     "geometry": "rectDoubleWall",    "params": ["W", "H", "liner_thickness"],
     "description": "Rectangular double-wall duct section"},

    # -----------------------------------------------------------------------
    # SU – Supports & Hangers (8)
    # -----------------------------------------------------------------------
    {"id": "SU-1", "cat": "SU", "label": "Supports & Hangers",
     "geometry": "hanger_strap",       "params": ["W", "strap_width"],
     "description": "Single strap / clevis hanger"},
    {"id": "SU-2", "cat": "SU", "label": "Supports & Hangers",
     "geometry": "hanger_trapeze",     "params": ["span", "rod_dia"],
     "description": "Trapeze hanger with threaded rods"},
    {"id": "SU-3", "cat": "SU", "label": "Supports & Hangers",
     "geometry": "hanger_clevis",      "params": ["D"],
     "description": "Clevis hanger for round duct"},
    {"id": "SU-4", "cat": "SU", "label": "Supports & Hangers",
     "geometry": "hanger_band",        "params": ["D", "band_width"],
     "description": "Band hanger for round duct"},
    {"id": "SU-5", "cat": "SU", "label": "Supports & Hangers",
     "geometry": "hanger_beamClamp",   "params": ["flange_size"],
     "description": "Beam-clamp attachment"},
    {"id": "SU-6", "cat": "SU", "label": "Supports & Hangers",
     "geometry": "hanger_tieRod",      "params": ["W", "rod_dia"],
     "description": "Tie-rod lateral duct support"},
    {"id": "SU-7", "cat": "SU", "label": "Supports & Hangers",
     "geometry": "seismic_longitudinal","params": ["duct_size", "splay_angle"],
     "description": "Seismic longitudinal brace"},
    {"id": "SU-8", "cat": "SU", "label": "Supports & Hangers",
     "geometry": "seismic_transverse",  "params": ["duct_size", "splay_angle"],
     "description": "Seismic transverse brace"},
]

# ---------------------------------------------------------------------------
# Build the registry dict  {id: FittingEntry}
# ---------------------------------------------------------------------------

FITTING_REGISTRY: Dict[str, FittingEntry] = {}

for _raw in _RAW:
    _entry = FittingEntry(
        id=_raw["id"],
        category=_raw["cat"],
        label=_raw["label"],
        geometry=_raw["geometry"],
        params=_raw["params"],
        vanes=_raw.get("vanes", False),
        description=_raw.get("description", ""),
    )
    FITTING_REGISTRY[_entry.id] = _entry

# Sanity check – remove private helpers from module namespace
del _raw, _entry


def get_fitting(fitting_id: str) -> FittingEntry:
    """
    Return the :class:`FittingEntry` for *fitting_id*.

    Raises ``KeyError`` if the ID is not registered.
    """
    try:
        return FITTING_REGISTRY[fitting_id]
    except KeyError:
        raise KeyError(
            f"Unknown fitting ID {fitting_id!r}.  "
            f"Valid IDs: {sorted(FITTING_REGISTRY)}"
        )


def list_category(category: str) -> List[FittingEntry]:
    """
    Return all :class:`FittingEntry` objects for the given category code.

    Parameters
    ----------
    category:
        Two-letter category code (e.g. ``"RE"``, ``"CE"``).  Case-sensitive.
    """
    results = [e for e in FITTING_REGISTRY.values() if e.category == category]
    if not results:
        valid = sorted({e.category for e in FITTING_REGISTRY.values()})
        raise ValueError(
            f"Unknown category {category!r}.  Valid categories: {valid}"
        )
    return sorted(results, key=lambda e: e.id)


def list_all_categories() -> List[str]:
    """Return a sorted list of all category codes."""
    return sorted({e.category for e in FITTING_REGISTRY.values()})


def registry_summary() -> Dict[str, int]:
    """Return a dict mapping category codes to fitting counts."""
    summary: Dict[str, int] = {}
    for entry in FITTING_REGISTRY.values():
        summary[entry.category] = summary.get(entry.category, 0) + 1
    return dict(sorted(summary.items()))