import math
from typing import Any, Dict


def _rectangular_to_vertices(w: float, h: float, z: float = 0.0):
    hw, hh = w / 2, h / 2
    return [
        [-hw, -hh, z], [hw, -hh, z],
        [hw, hh, z], [-hw, hh, z],
    ]


def _elbow_geometry(dims: Dict) -> Dict:
    w = dims.get("width_inlet", 12.0)
    h = dims.get("height_inlet", 12.0)
    angle = dims.get("angle", 90.0)
    radius = dims.get("radius", max(w, h) * 1.5)
    return {
        "type": "elbow",
        "inlet": {"width": w, "height": h, "vertices": _rectangular_to_vertices(w, h, 0)},
        "outlet": {"width": w, "height": h, "vertices": _rectangular_to_vertices(w, h, radius)},
        "angle_deg": angle,
        "centerline_radius": radius,
        "segments": 16,
    }


def _tee_geometry(dims: Dict) -> Dict:
    wi = dims.get("width_inlet", 12.0)
    hi = dims.get("height_inlet", 12.0)
    wn = dims.get("neck_width", wi * 0.6)
    hn = dims.get("neck_height", hi * 0.6)
    length = dims.get("length", 24.0)
    return {
        "type": "tee",
        "main_inlet": {"width": wi, "height": hi},
        "main_outlet": {"width": wi, "height": hi},
        "branch": {"width": wn, "height": hn},
        "main_length": length,
        "branch_offset": length / 2,
    }


def _reducer_geometry(dims: Dict) -> Dict:
    wi = dims.get("width_inlet", 16.0)
    hi = dims.get("height_inlet", 12.0)
    wo = dims.get("width_outlet", 12.0)
    ho = dims.get("height_outlet", 10.0)
    length = dims.get("length", 12.0)
    return {
        "type": "reducer",
        "inlet": {"width": wi, "height": hi, "vertices": _rectangular_to_vertices(wi, hi, 0)},
        "outlet": {"width": wo, "height": ho, "vertices": _rectangular_to_vertices(wo, ho, length)},
        "length": length,
    }


def _offset_geometry(dims: Dict) -> Dict:
    w = dims.get("width_inlet", 12.0)
    h = dims.get("height_inlet", 12.0)
    ox = dims.get("offset_x", 6.0)
    oy = dims.get("offset_y", 0.0)
    length = dims.get("length", 18.0)
    return {
        "type": "offset",
        "inlet": {"width": w, "height": h},
        "outlet": {"width": w, "height": h, "shift_x": ox, "shift_y": oy},
        "length": length,
    }


def _duct_geometry(dims: Dict) -> Dict:
    w = dims.get("width_inlet", 12.0)
    h = dims.get("height_inlet", 12.0)
    length = dims.get("length", 48.0)
    return {
        "type": "duct",
        "cross_section": {"width": w, "height": h},
        "length": length,
        "vertices_start": _rectangular_to_vertices(w, h, 0),
        "vertices_end": _rectangular_to_vertices(w, h, length),
    }


def _cap_geometry(dims: Dict) -> Dict:
    w = dims.get("width_inlet", 12.0)
    h = dims.get("height_inlet", 12.0)
    return {
        "type": "cap",
        "face": {"width": w, "height": h, "vertices": _rectangular_to_vertices(w, h, 0)},
    }


_GEOMETRY_BUILDERS = {
    "elbow": _elbow_geometry,
    "tee": _tee_geometry,
    "reducer": _reducer_geometry,
    "transition": _reducer_geometry,
    "offset": _offset_geometry,
    "duct": _duct_geometry,
    "cap": _cap_geometry,
}


def compute_fitting_geometry(fitting_type: str, dims: Dict[str, Any]) -> Dict[str, Any]:
    builder = _GEOMETRY_BUILDERS.get(fitting_type, _duct_geometry)
    return builder(dims)
