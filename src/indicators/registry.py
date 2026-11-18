"""Indicator registry, scorecard grid and readings, loaded from YAML."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

STATE_LABELS: dict[str, str] = {
    "low": "Low",
    "rising": "Rising",
    "pervasive": "Pervasive",
    "within": "Within baseline",
    "above": "Above baseline",
    "below": "Below baseline",
    "far_above": "Far above baseline",
    "far_below": "Far below baseline",
    "no_signal": "No signal / insufficient data",
    "not_yet_reviewed": "Not yet reviewed",
}

# Display names for the layer keys used internally in the registry and grid.
LAYER_LABELS: dict[str, str] = {
    "exposure": "Adoption",
    "erosion": "Displacement",
    "lockin": "Lock-in",
}

# One-sentence definitions shown as hover/focus tooltips on the summary grid's row headers.
LAYER_DEFINITIONS: dict[str, str] = {
    "exposure": "Is AI entering the system, and how far?",
    "erosion": "Is the system's dependence on human participation falling, and by how much?",
    "lockin": "Is that reduced dependence becoming hard to restore?",
}
CROSS_CUTTING_LABEL = "Cross-cutting"
CROSS_CUTTING_DEFINITION = "Are people handing decisions to AI? This applies across all three domains."

SCALE_STATES: dict[str, set[str]] = {
    "exposure": {"low", "rising", "pervasive", "no_signal", "not_yet_reviewed"},
    "baseline": {"within", "above", "below", "far_above", "far_below",
                 "no_signal", "not_yet_reviewed"},
}


@dataclass(frozen=True)
class Indicator:
    id: str
    release: int
    domain: str
    layer: str
    scale: str
    name: str
    ai_link: str  # strong | moderate | weak: how directly the series ties to AI (the "AI link" badge)
    ai_link_criteria: dict
    timing: str
    comparison: str
    tier: int
    series: list[str]
    primary_series: str | None = None
    chart_title: str | None = None
    headline_caveat: str | None = None
    disclosure: str | None = None
    sources: list[dict] = field(default_factory=list)


@dataclass(frozen=True)
class GridCell:
    layer: str
    domain: str
    indicator_ids: list[str]
    empty_label: str


@dataclass(frozen=True)
class Reading:
    indicator_id: str
    state: str
    date: date
    magnitude: str | None = None
    interpretation: str | None = None
    rationale: str | None = None
    kind: str = "current"


def load_registry(path) -> tuple[list[Indicator], list[GridCell], dict]:
    data = yaml.safe_load(Path(path).read_text())
    indicators = [Indicator(**row) for row in data["indicators"]]
    grid = [GridCell(**row) for row in data["grid"]]
    return indicators, grid, data["oversight"]


def load_readings(path, indicators: list[Indicator] | None = None) -> dict[str, list[Reading]]:
    """Load readings; when indicators are given, each state must fit its indicator's scale."""
    data = yaml.safe_load(Path(path).read_text())
    scales = {i.id: i.scale for i in indicators} if indicators is not None else None
    out: dict[str, list[Reading]] = {}
    for row in data["readings"] or []:
        reading = Reading(**row)
        if reading.state not in STATE_LABELS:
            raise ValueError(f"unknown state {reading.state!r} for {reading.indicator_id}")
        if scales is not None:
            if reading.indicator_id not in scales:
                raise ValueError(f"reading for unknown indicator {reading.indicator_id}")
            if reading.state not in SCALE_STATES[scales[reading.indicator_id]]:
                raise ValueError(
                    f"state {reading.state!r} is not on the "
                    f"{scales[reading.indicator_id]} scale for {reading.indicator_id}")
        out.setdefault(reading.indicator_id, []).append(reading)
    return out


def current_reading(readings: dict[str, list[Reading]], indicator_id: str) -> Reading:
    current = [r for r in readings.get(indicator_id, []) if r.kind == "current"]
    if current:
        return max(current, key=lambda r: r.date)
    return Reading(indicator_id=indicator_id, state="not_yet_reviewed", date=date.today())


def load_chart_markers(path) -> dict[str, list[dict]]:
    """Chart markers by indicator id (key `all` applies to every indicator)."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return data.get("markers") or {}


def markers_for(markers: dict[str, list[dict]], indicator_id: str) -> list[dict]:
    """Verified markers for one indicator, as {"date", "label"} sorted by date (the meta `annotations`)."""
    rows = [m for key in ("all", indicator_id) for m in markers.get(key) or [] if m.get("verified") is True]
    return sorted(({"date": str(m["date"]), "label": m["label"]} for m in rows), key=lambda m: m["date"])


def layer_label(layer: str) -> str:
    """Display name for an internal layer key."""
    return LAYER_LABELS[layer]


def content_summary(front_matter: dict) -> str:
    """Summary text from a content page's front matter. `summary:` is preferred; `takeaway:` (the old
    key, still on the pages until the prose batch renames it) is accepted as a fallback."""
    for key in ("summary", "takeaway"):
        if front_matter.get(key):
            return str(front_matter[key])
    raise ValueError("front matter has no summary")
