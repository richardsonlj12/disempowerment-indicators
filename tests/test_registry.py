from pathlib import Path

import pytest

from indicators.registry import (
    STATE_LABELS, SCALE_STATES, current_reading, load_chart_markers, load_readings, load_registry,
    markers_for, LAYER_LABELS, layer_label, content_summary,
)

ROOT = Path(__file__).resolve().parent.parent
IND = ROOT / "config" / "indicators.yaml"
READ = ROOT / "config" / "readings.yaml"


@pytest.fixture
def registry():
    return load_registry(IND)


def test_release1_ids(registry):
    indicators, _, _ = registry
    assert {i.id for i in indicators} == {"E1", "E2", "E3", "G1", "C1"}
    assert all(i.release == 1 for i in indicators)


def test_exposure_layer_uses_exposure_scale(registry):
    for i in registry[0]:
        assert (i.layer == "exposure") == (i.scale == "exposure")


@pytest.mark.parametrize("ind,state", [("E2", "below"), ("E1", "rising")])
def test_reading_state_matches_scale(registry, tmp_path, ind, state):
    p = tmp_path / "r.yaml"
    p.write_text(f"readings:\n  - {{indicator_id: {ind}, state: {state}, date: 2026-11-17}}\n")
    with pytest.raises(ValueError):
        load_readings(p, registry[0])


def test_all_readings_not_yet_reviewed(registry):
    readings = load_readings(READ, registry[0])
    assert set(readings) == {i.id for i in registry[0]}
    for ind in readings:
        assert current_reading(readings, ind).state == "not_yet_reviewed"


def test_current_reading_defaults_when_missing():
    assert current_reading({}, "E1").state == "not_yet_reviewed"


def test_every_indicator_has_warning_sign_and_alternative_explanations(registry):
    for i in registry[0]:
        assert i.warning_sign.strip() and i.alternative_explanations.strip()
        assert set(i.ai_link_criteria) == {
            "directness", "comparison_group", "timing", "confounders"}


def test_e3_has_caveat_and_disclosure(registry):
    e3 = next(i for i in registry[0] if i.id == "E3")
    assert e3.headline_caveat == "One vendor, one product: Claude usage only"
    assert "Anthropic" in e3.disclosure and "Claude" in e3.disclosure


def test_lockin_row_empty_in_release1(registry):
    _, grid, oversight = registry
    lockin = [c for c in grid if c.layer == "lockin"]
    assert len(lockin) == 3
    assert all(c.indicator_ids == [] and c.empty_label == "No public measure yet" for c in lockin)
    cultural_exposure = next(c for c in grid if c.layer == "exposure" and c.domain == "cultural")
    assert cultural_exposure.indicator_ids == []
    assert oversight["citation_ref"] == "herdagdelen2026"


def test_grid_places_each_indicator_once_in_its_cell(registry):
    indicators, grid, _ = registry
    placed = [i for c in grid for i in c.indicator_ids]
    assert sorted(placed) == sorted(i.id for i in indicators)
    by_id = {i.id: i for i in indicators}
    for c in grid:
        for i in c.indicator_ids:
            assert (by_id[i].layer, by_id[i].domain) == (c.layer, c.domain)


def test_series_ids_unique(registry):
    ids = [s for i in registry[0] for s in i.series]
    assert len(ids) == len(set(ids))
    for i in registry[0]:
        assert i.primary_series in i.series


def test_state_labels_cover_all_states():
    states = set().union(*SCALE_STATES.values())
    assert set(STATE_LABELS) == states
    assert STATE_LABELS["no_signal"] == "No signal / insufficient data"


MARKERS = ROOT / "config" / "chart_markers.yaml"


def test_chart_markers_are_verified_and_sourced():
    markers = load_chart_markers(MARKERS)
    assert set(markers) <= {"all", "E1", "E2", "E3", "G1", "C1"}
    for rows in markers.values():
        for m in rows:
            assert m["verified"] is True and m["source_url"].startswith("https://") and m["label"]


def test_markers_for_merges_all_and_sorts_by_date():
    out = markers_for(load_chart_markers(MARKERS), "C1")
    assert [m["date"] for m in out] == sorted(m["date"] for m in out)
    assert {"date": "2022-11-30", "label": "ChatGPT released to the public"} in out
    assert any("Copilot" in m["label"] for m in out)
    assert all(set(m) == {"date", "label"} for m in out)
    e2 = markers_for(load_chart_markers(MARKERS), "E2")
    assert any(m["date"] == "2026-10-19" and "Super Intelligence" in m["label"] for m in e2)
    assert [m["date"] for m in markers_for(load_chart_markers(MARKERS), "E1")] == ["2022-11-30"]


def test_unverified_markers_are_dropped(tmp_path):
    p = tmp_path / "m.yaml"
    p.write_text("markers:\n  all:\n    - {date: 2020-01-01, label: x, source_url: https://e.org, verified: false}\n")
    assert markers_for(load_chart_markers(p), "E1") == []


def test_ai_link_values_and_summary_present(registry):
    for i in registry[0]:
        assert i.ai_link in {"strong", "moderate", "weak"} and i.summary.strip()


def test_layer_display_names():
    assert LAYER_LABELS == {"exposure": "Adoption", "erosion": "Displacement", "lockin": "Lock-in"}
    assert layer_label("exposure") == "Adoption"
    assert STATE_LABELS["low"] == "Low"  # the exposure scale's own labels are unchanged


def test_registry_text_uses_replacement_not_displacement_wording():
    text = IND.read_text(encoding="utf-8")
    assert "augmentation versus displacement" not in text and "AI-specificity" not in text


def test_content_summary_prefers_summary_and_accepts_takeaway():
    assert content_summary({"summary": "new", "takeaway": "old"}) == "new"
    assert content_summary({"takeaway": "old"}) == "old"
    with pytest.raises(ValueError):
        content_summary({})
