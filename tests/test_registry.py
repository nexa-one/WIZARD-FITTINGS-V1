"""Tests for the v2.0.0 fitting registry."""

import pytest
from geometric_engine.registry.fitting_registry import (
    FITTING_REGISTRY,
    FittingEntry,
    get_fitting,
    list_category,
    list_all_categories,
    registry_summary,
)


class TestRegistryCompleteness:
    def test_total_count_is_87(self):
        assert len(FITTING_REGISTRY) == 87

    def test_all_categories_present(self):
        cats = set(list_all_categories())
        expected = {"RE", "RO", "RT", "RR", "RC", "CE", "CT", "CR", "FO", "SP", "SU"}
        assert cats == expected

    def test_category_counts(self):
        summary = registry_summary()
        assert summary["RE"] == 10
        assert summary["RO"] == 5
        assert summary["RT"] == 10
        assert summary["RR"] == 8
        assert summary["RC"] == 4
        assert summary["CE"] == 7
        assert summary["CT"] == 10
        assert summary["CR"] == 7
        assert summary["FO"] == 8
        assert summary["SP"] == 10
        assert summary["SU"] == 8


class TestGetFitting:
    def test_get_existing(self):
        entry = get_fitting("RE-4")
        assert isinstance(entry, FittingEntry)
        assert entry.id == "RE-4"
        assert "rectElbow_radius" in entry.geometry
        assert "W" in entry.params
        assert "H" in entry.params
        assert "R" in entry.params

    def test_get_unknown_raises(self):
        with pytest.raises(KeyError):
            get_fitting("XX-99")

    def test_entry_frozen(self):
        entry = get_fitting("CE-1")
        with pytest.raises(Exception):
            entry.id = "XX"  # type: ignore[misc]


class TestListCategory:
    def test_list_RE(self):
        entries = list_category("RE")
        assert len(entries) == 10
        ids = [e.id for e in entries]
        assert "RE-1" in ids
        assert "RE-10" in ids

    def test_list_FO(self):
        entries = list_category("FO")
        assert len(entries) == 8

    def test_list_unknown_raises(self):
        with pytest.raises(ValueError):
            list_category("ZZ")

    def test_sorted_by_id(self):
        entries = list_category("CT")
        ids = [e.id for e in entries]
        assert ids == sorted(ids)


class TestFittingEntryFields:
    def test_vanes_field(self):
        assert get_fitting("RE-2").vanes == "single"
        assert get_fitting("RE-3").vanes == "double"
        assert get_fitting("RE-4").vanes is False

    def test_all_entries_have_params(self):
        for entry in FITTING_REGISTRY.values():
            assert isinstance(entry.params, list)
            assert len(entry.params) >= 1

    def test_all_entries_have_geometry(self):
        for entry in FITTING_REGISTRY.values():
            assert isinstance(entry.geometry, str)
            assert len(entry.geometry) > 0

    def test_all_entries_have_description(self):
        for entry in FITTING_REGISTRY.values():
            assert isinstance(entry.description, str)