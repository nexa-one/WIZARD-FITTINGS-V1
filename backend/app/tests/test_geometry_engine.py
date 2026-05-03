import pytest
from app.engines.geometry_engine import compute_fitting_geometry


def test_elbow_geometry():
    dims = {"width_inlet": 12.0, "height_inlet": 12.0, "angle": 90.0, "radius": 18.0}
    geo = compute_fitting_geometry("elbow", dims)
    assert geo["type"] == "elbow"
    assert geo["angle_deg"] == 90.0
    assert geo["centerline_radius"] == 18.0
    assert len(geo["inlet"]["vertices"]) == 4


def test_tee_geometry():
    dims = {"width_inlet": 12.0, "height_inlet": 12.0, "neck_width": 8.0, "neck_height": 8.0, "length": 24.0}
    geo = compute_fitting_geometry("tee", dims)
    assert geo["type"] == "tee"
    assert geo["branch"]["width"] == 8.0


def test_reducer_geometry():
    dims = {"width_inlet": 16, "height_inlet": 12, "width_outlet": 12, "height_outlet": 10, "length": 12}
    geo = compute_fitting_geometry("reducer", dims)
    assert geo["type"] == "reducer"
    assert geo["inlet"]["width"] == 16
    assert geo["outlet"]["width"] == 12


def test_duct_geometry():
    dims = {"width_inlet": 12, "height_inlet": 8, "length": 48}
    geo = compute_fitting_geometry("duct", dims)
    assert geo["type"] == "duct"
    assert geo["length"] == 48
    assert len(geo["vertices_start"]) == 4
    assert len(geo["vertices_end"]) == 4


def test_cap_geometry():
    dims = {"width_inlet": 12, "height_inlet": 12}
    geo = compute_fitting_geometry("cap", dims)
    assert geo["type"] == "cap"
    assert len(geo["face"]["vertices"]) == 4


def test_unknown_type_falls_back_to_duct():
    geo = compute_fitting_geometry("unknown_type", {"width_inlet": 10, "height_inlet": 10, "length": 24})
    assert geo["type"] == "duct"
