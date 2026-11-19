from datetime import date
from pathlib import Path

import pytest
import yaml

from indicators.curated import load_curated, published

ROOT = Path(__file__).resolve().parents[1]
COUNTER = ROOT / "config" / "curated" / "counter_evidence.yaml"
OVERSIGHT = ROOT / "config" / "curated" / "oversight.yaml"

ITEM = {
    "id": "x",
    "label": "A label",
    "domain": "government",
    "metric": "a metric",
    "value": 1.5,
    "unit": "percent",
    "date": date(2026, 1, 1),
    "source_name": "Somebody",
    "source_url": "https://example.org/x",
    "verified": True,
    "verified_on": date(2026, 11, 17),
    "note": "n",
}


def _write(tmp_path, items, header=None):
    path = tmp_path / "c.yaml"
    path.write_text(yaml.safe_dump({**(header or {}), "items": items}, sort_keys=False))
    return path


def test_curated_requires_source_url(tmp_path):
    bad = {k: v for k, v in ITEM.items() if k != "source_url"}
    with pytest.raises(ValueError, match="source_url"):
        load_curated(_write(tmp_path, [bad]))
    blank = {**ITEM, "source_url": ""}
    with pytest.raises(ValueError, match="source_url"):
        load_curated(_write(tmp_path, [blank]))


def test_verified_item_needs_verified_on(tmp_path):
    bad = {**ITEM, "verified_on": None}
    with pytest.raises(ValueError, match="verified_on"):
        load_curated(_write(tmp_path, [bad]))


def test_unverified_items_not_published(tmp_path):
    unverified = {**ITEM, "id": "y", "verified": False, "verified_on": None}
    _, items = load_curated(_write(tmp_path, [ITEM, unverified]))
    assert [i["id"] for i in published(items)] == ["x"]


def test_counter_evidence_has_inclusion_criteria():
    header, items = load_curated(COUNTER)
    assert header["inclusion_criteria"].strip()
    assert items
    assert all(i["kind"] in {"policy", "data_signal"} for i in items)


def test_counter_evidence_has_no_welfare_kind():
    header, items = load_curated(COUNTER)
    assert not any(i["kind"] == "welfare" for i in items)
    assert "welfare-improving" not in header["inclusion_criteria"]
    assert "us_real_median_household_income" not in {i["id"] for i in items}


def test_ai_legislation_counts_verified_from_chapter_pdf():
    _, items = load_curated(COUNTER)
    item = next(i for i in items if i["id"] == "ai_legislation_counts")
    assert item["verified"] is True and item["verified_on"]
    assert item["value"] == {"us_federal_bills_2016_2025": 25, "us_state_bills_enacted_2025": 150}
    assert item["source_url"].endswith("ai_index_report_2026_chapter_8_policy_and_governance.pdf")


def test_oversight_note_gives_the_registered_policy_shift():
    _, items = load_curated(OVERSIGHT)
    note = " ".join(items[0]["note"].split())
    assert "17-percentage-point" not in note
    assert "0.17 policy shift" in note and "95% CI −6% to 40%" in note and "one-sided p = 0.069" in note
    assert "not statistically significant" in note
    assert items[0]["value"] == 86 and "50 analysts" in items[0]["metric"]
    assert items[0]["caveat"].startswith("The researchers deliberately strengthened the agent's lean")


def test_oversight_cites_herdagdelen():
    _, items = load_curated(OVERSIGHT)
    assert any(i["source_key"] == "herdagdelen2026a" for i in items)  # cited through the Sources page
    assert all(i["source_url"].startswith("https://") for i in items)
