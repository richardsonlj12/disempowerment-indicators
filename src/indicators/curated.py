"""Curated (hand-entered, cited) items: counter-evidence panel and the oversight citation."""
from __future__ import annotations

from pathlib import Path

import yaml

REQUIRED = ("id", "label", "domain", "metric", "value", "unit", "date",
            "source_name", "source_url", "verified", "verified_on", "note")
KINDS = ("policy", "welfare", "data_signal")


def _validate(item: dict, index: int, require_kind: bool) -> None:
    where = f"item {index} ({item.get('id', '?')})"
    for key in REQUIRED:
        if key not in item:
            raise ValueError(f"{where}: missing field {key}")
    for key in ("id", "source_name", "source_url"):
        if not isinstance(item[key], str) or not item[key].strip():
            raise ValueError(f"{where}: {key} must be a non-empty string")
    if not item["source_url"].startswith("https://"):
        raise ValueError(f"{where}: source_url must be an https URL")
    if not isinstance(item["verified"], bool):
        raise ValueError(f"{where}: verified must be true or false")
    if item["verified"] and not item["verified_on"]:
        raise ValueError(f"{where}: verified items need verified_on")
    if require_kind and item.get("kind") not in KINDS:
        raise ValueError(f"{where}: kind must be one of {KINDS}")


def load_curated(path: Path | str) -> tuple[dict, list[dict]]:
    """Return (header, items); header is every top-level key except `items`."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    items = raw.get("items") or []
    header = {k: v for k, v in raw.items() if k != "items"}
    is_counter = "inclusion_criteria" in header or any("kind" in i for i in items)
    if is_counter and not str(header.get("inclusion_criteria", "")).strip():
        raise ValueError("counter-evidence file needs inclusion_criteria")
    ids = [i.get("id") for i in items]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate item ids")
    for n, item in enumerate(items):
        _validate(item, n, require_kind=is_counter)
    return header, items


def published(items: list[dict]) -> list[dict]:
    """Only verified items may appear on the site."""
    return [i for i in items if i["verified"] is True]
