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
    assert all(i["kind"] in {"policy", "welfare", "data_signal"} for i in items)


def test_counter_evidence_includes_welfare_kind():
    _, items = load_curated(COUNTER)
    assert any(i["kind"] == "welfare" for i in items)


def test_oversight_cites_herdagdelen():
    _, items = load_curated(OVERSIGHT)
    assert any("Tamkin" in i["source_name"] for i in items)
    assert all(i["source_url"].startswith("https://") for i in items)
