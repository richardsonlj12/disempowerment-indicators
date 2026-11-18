"""E3: automation and augmentation share of Claude.ai conversations (Anthropic Economic Index).

Keyless: public files of the Hugging Face dataset `Anthropic/EconomicIndex`.

Each release publishes the human-AI collaboration pattern shares in a different layout, so
`RELEASE_SCHEMAS` records, per release, the file, the exact layout expected, and which patterns
count as automation and augmentation. Anything unexpected (a renamed column, a new pattern
label, a release directory with no entry here) raises `SourceError`; nothing is guessed.

Definition used for every release (Anthropic's own, from the 2025-09-15 and 2026-06-26 data
documentation): shares are percent of *classifiable* conversations, so patterns `none` and
`not_classified` are excluded from the denominator and automation + augmentation = 100.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
import requests

from indicators import http
from indicators.http import SourceError
from indicators.sources import utc_now_iso
from indicators.store import SeriesMeta, assign_segments

DATASET_URL = "https://huggingface.co/datasets/Anthropic/EconomicIndex"
RESOLVE = DATASET_URL + "/resolve/main/"
TREE_URL = "https://huggingface.co/api/datasets/Anthropic/EconomicIndex/tree/main"

LICENSE = (
    "Data released under CC-BY, code released under MIT License (dataset README, License section; "
    "the dataset card front matter says license: mit)"
)

AUTOMATION = ("directive", "feedback loop")
AUGMENTATION = ("validation", "task iteration", "learning")
EXCLUDED = ("none", "not_classified")

RAW_HEADER = [
    "geo_id", "geography", "date_start", "date_end", "platform_and_product",
    "facet", "level", "variable", "cluster_name", "value",
]  # fmt: skip
MONTHLY_HEADER = [
    "date_start", "date_end", "geo_id", "geo_level", "category_name",
    "hierarchy_level", "metric_id", "value", "node_name", "node_external_id",
]  # fmt: skip

_RAW_BASE = {
    "kind": "raw_long",
    "header": RAW_HEADER,
    "automation": AUTOMATION,
    "augmentation": AUGMENTATION,
    "excluded": EXCLUDED,
}

RELEASE_SCHEMAS: dict[str, dict] = {
    "release_2025_02_10": {
        "kind": "interaction_csv",
        "path": "release_2025_02_10/automation_vs_augmentation.csv",
        "header": ["interaction_type", "pct"],
        "dates": ["2025-02-10"],
        "automation": AUTOMATION,
        "augmentation": AUGMENTATION,
        "excluded": ("none",),
        "window": "first report sample, Claude.ai Free and Pro, 2024-12-16 to 2024-12-23 (Handa et al., "
        "arXiv 2503.04761, Appendix E, automation vs. augmentation sample)",
    },
    "release_2025_03_27": {
        "kind": "interaction_csv",
        "path": "release_2025_03_27/automation_vs_augmentation_v2.csv",
        "header": ["interaction_type", "pct"],
        "dates": ["2025-03-27"],
        "automation": AUTOMATION,
        "augmentation": AUGMENTATION,
        "excluded": ("none",),
        "window": "second report sample (Claude 3.7 Sonnet), Claude.ai Free and Pro, Feb-Mar 2025",
    },
    "release_2025_09_15": {
        **_RAW_BASE,
        "path": "release_2025_09_15/data/intermediate/aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv",
        "dates": ["2025-09-15"],
        "window": ("2025-08-04", "2025-08-11"),
    },
    "release_2026_01_15": {
        **_RAW_BASE,
        "path": "release_2026_01_15/data/intermediate/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv",
        "dates": ["2026-01-15"],
        "window": ("2025-11-13", "2025-11-20"),
    },
    "release_2026_03_24": {
        **_RAW_BASE,
        "path": "release_2026_03_24/data/aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv",
        "dates": ["2026-03-24"],
        "window": ("2026-02-05", "2026-02-12"),
    },
    "release_2026_06_26": {
        "kind": "monthly_buckets",
        "path": "release_2026_06_26/data/aei_claude_ai_2026-06-26.csv",
        "header": MONTHLY_HEADER,
        "dates": ["2026-04-01", "2026-05-01"],
        "automation_metric": "collaboration_bucket_automation_pct",
        "augmentation_metric": "collaboration_bucket_augmentation_pct",
    },
}

BREAKS = [
    {
        "date": "2025-09-15",
        "note": "Release layout changed from a six-row interaction-type summary to the raw long-format "
        "file (patterns read from the collaboration facet, global rows); shares now recomputed "
        "from patterns.",
    },
    {
        "date": "2026-03-24",
        "note": "Claude.ai population widened from 'Free and Pro' to 'Free, Pro, and Max' plans.",
    },
    {
        "date": "2026-04-01",
        "note": "Release layout changed to calendar-month aggregates with published automation and "
        "augmentation buckets; Claude.ai source now includes Cowork (per the release data "
        "documentation).",
    },
]

NOTES = (
    "Percent of categorized Claude.ai conversations, those that fit one of the five patterns (Anthropic's labels \"none\" and \"not classified\" excluded, so the two "
    "shares sum to 100), global, one row per release date; the April and May 2026 monthly aggregates of the "
    "2026-06-26 release are dated by month start. Mapping (Anthropic's categorisation in the 2025-09-15 "
    "enrichment code and the 2026-06-26 data documentation): automation = directive + feedback loop; "
    "augmentation = validation + task iteration + learning. "
    "Release mappings: "
    "release_2025_02_10 and release_2025_03_27 read automation_vs_augmentation.csv and "
    "automation_vs_augmentation_v2.csv (columns interaction_type, pct); "
    "release_2025_09_15, release_2026_01_15 and release_2026_03_24 read the raw claude_ai file, rows "
    "geo_id=GLOBAL, facet=collaboration, level=0, variable=collaboration_pct, cluster_name = the pattern; "
    "release_2026_06_26 reads the claude_ai file, rows geo_id=GLOBAL, category_name=overall, "
    "hierarchy_level=0, metric_id collaboration_bucket_automation_pct and collaboration_bucket_augmentation_pct. "
    "Only the Claude.ai source is used; the first-party API files are a different population and are "
    "excluded. Shares including none and not_classified in the denominator are lower (for example 49.10 "
    "percent automation for the 2025-08 sample, against 51.07 here). Releases without a conversation-level "
    "automation and augmentation split (labor_market_impacts, robot_exposure) are excluded. "
    "Data windows: " + "; ".join(
        f"{name} {s['window'] if isinstance(s['window'], str) else ' to '.join(s['window'])}"
        for name, s in RELEASE_SCHEMAS.items()
        if "window" in s
    )
    + "; release_2026_06_26 April and May 2026."
)  # fmt: skip


def _shares(auto: float, aug: float, release: str) -> tuple[float, float]:
    total = auto + aug
    if total <= 0:
        raise SourceError(f"{release}: no classifiable conversations")
    return auto / total * 100, aug / total * 100


def _check_labels(labels, schema: dict, release: str) -> None:
    known = set(schema["automation"]) | set(schema["augmentation"]) | set(schema["excluded"])
    unknown = set(labels) - known
    if unknown:
        raise SourceError(f"{release}: unknown collaboration pattern(s) {sorted(unknown)}; add a mapping")
    missing = (set(schema["automation"]) | set(schema["augmentation"])) - set(labels)
    if missing:
        raise SourceError(f"{release}: collaboration pattern(s) {sorted(missing)} absent")


def _patterns_to_shares(values: dict[str, float], schema: dict, release: str) -> tuple[float, float]:
    _check_labels(values, schema, release)
    return _shares(
        sum(values[k] for k in schema["automation"]),
        sum(values[k] for k in schema["augmentation"]),
        release,
    )


def _from_interaction_csv(release: str, schema: dict) -> dict[str, tuple[float, float]]:
    url = RESOLVE + schema["path"]
    rows = list(csv.reader(http.get(url, expect="csv").text.splitlines()))
    if not rows or rows[0] != schema["header"]:
        raise SourceError(f"{release}: unexpected header {rows[0] if rows else None}; expected {schema['header']}")
    values = {r[0]: float(r[1]) for r in rows[1:] if r}
    return {schema["dates"][0]: _patterns_to_shares(values, schema, release)}


def _stream_lines(url: str, keep) -> tuple[str, list[str]]:
    """Return (header line, kept data lines) without holding a 100+ MB file in memory."""
    for attempt in range(http.RETRIES + 1):
        response = requests.get(url, headers={"User-Agent": http.USER_AGENT}, stream=True, timeout=120)
        if (response.status_code == 429 or response.status_code >= 500) and attempt < http.RETRIES:
            response.close()
            http._sleep(http.BACKOFF_SECONDS * (2**attempt))
            continue
        break
    with response:
        response.raise_for_status()
        response.encoding = "utf-8"
        lines = response.iter_lines(decode_unicode=True)
        header = next(lines, "")
        if "<html" in header.lower() or "<!doctype" in header.lower():
            raise SourceError(f"{url} returned HTML where csv was expected")
        return header, [line for line in lines if keep(line)]


def _from_raw_long(release: str, schema: dict) -> dict[str, tuple[float, float]]:
    url = RESOLVE + schema["path"]
    header, lines = _stream_lines(
        url,
        lambda l: l.startswith("GLOBAL,global,") and ",collaboration,0,collaboration_pct," in l,
    )
    if next(csv.reader([header]), None) != schema["header"]:
        raise SourceError(f"{release}: unexpected header {header!r}; expected {schema['header']}")
    values: dict[str, float] = {}
    for row in csv.DictReader(lines, fieldnames=schema["header"]):
        if (row["date_start"], row["date_end"]) != schema["window"]:
            raise SourceError(f"{release}: unexpected data window {row['date_start']} to {row['date_end']}")
        values[row["cluster_name"]] = float(row["value"])
    if not values:
        raise SourceError(f"{release}: no global collaboration rows found")
    return {schema["dates"][0]: _patterns_to_shares(values, schema, release)}


def _from_monthly_buckets(release: str, schema: dict) -> dict[str, tuple[float, float]]:
    url = RESOLVE + schema["path"]
    metrics = (schema["automation_metric"], schema["augmentation_metric"])
    header, lines = _stream_lines(
        url, lambda l: ",GLOBAL,global,overall,0," in l and "collaboration_bucket_" in l
    )
    if next(csv.reader([header]), None) != schema["header"]:
        raise SourceError(f"{release}: unexpected header {header!r}; expected {schema['header']}")
    months: dict[str, dict[str, float]] = {}
    for row in csv.DictReader(lines, fieldnames=schema["header"]):
        if row["metric_id"] not in metrics:
            raise SourceError(f"{release}: unknown bucket metric {row['metric_id']!r}; add a mapping")
        months.setdefault(row["date_start"], {})[row["metric_id"]] = float(row["value"])
    out = {}
    for month, got in sorted(months.items()):
        if set(got) != set(metrics):
            raise SourceError(f"{release}: {month} lacks one of {metrics}")
        auto, aug = got[metrics[0]], got[metrics[1]]
        if abs(auto + aug - 100) > 0.05:
            raise SourceError(f"{release}: {month} buckets sum to {auto + aug}, expected 100")
        out[month] = (auto, aug)
    if sorted(out) != schema["dates"]:
        raise SourceError(f"{release}: months {sorted(out)} differ from expected {schema['dates']}")
    return out


_READERS = {
    "interaction_csv": _from_interaction_csv,
    "raw_long": _from_raw_long,
    "monthly_buckets": _from_monthly_buckets,
}


def _check_listing() -> None:
    entries = http.get(TREE_URL, expect="json").json()
    releases = {e["path"] for e in entries if e.get("type") == "directory" and e["path"].startswith("release_")}
    unmapped = sorted(releases - set(RELEASE_SCHEMAS))
    if unmapped:
        raise SourceError(
            f"Economic Index release(s) {unmapped} have no entry in RELEASE_SCHEMAS; read the release "
            "documentation and add a verified mapping (or record why it is excluded)"
        )


def _committed(data_dir: Path) -> dict[str, dict[str, float]] | None:
    """Previously fetched shares by series, or None if either file is missing."""
    out = {}
    for sid in ("aei_automation_share", "aei_augmentation_share"):
        path = Path(data_dir) / f"{sid}.csv"
        if not path.exists():
            return None
        old = pd.read_csv(path, parse_dates=["date"])
        out[sid] = {d.strftime("%Y-%m-%d"): float(v) for d, v in zip(old["date"], old["value"])}
    return out


def fetch(data_dir: Path | str = "data", full: bool = False) -> list[tuple[pd.DataFrame, SeriesMeta]]:
    """Releases are immutable, so committed ones are reused unless `full` is set.

    The raw files are 19 to 219 MB each; this keeps a routine refresh to the listing request
    plus any new release.
    """
    fetched_at = utc_now_iso()
    _check_listing()
    committed = None if full else _committed(Path(data_dir))

    auto_rows: dict[str, float] = {}
    aug_rows: dict[str, float] = {}
    for release, schema in RELEASE_SCHEMAS.items():
        if committed and all(d in committed["aei_automation_share"] and d in committed["aei_augmentation_share"] for d in schema["dates"]):
            for d in schema["dates"]:
                auto_rows[d] = committed["aei_automation_share"][d]
                aug_rows[d] = committed["aei_augmentation_share"][d]
            continue
        for d, (auto, aug) in _READERS[schema["kind"]](release, schema).items():
            auto_rows[d], aug_rows[d] = auto, aug

    def frame(rows: dict[str, float]) -> pd.DataFrame:
        df = pd.DataFrame({"date": pd.to_datetime(list(rows)), "value": list(rows.values())})
        df = df.sort_values("date").reset_index(drop=True)
        df["value"] = df["value"].astype(float)
        return assign_segments(df, BREAKS)

    def meta(series_id: str, title: str, role: str, df: pd.DataFrame) -> SeriesMeta:
        return SeriesMeta(
            series_id=series_id,
            indicator_id="E3",
            title=title,
            units="percent",
            frequency="irregular",
            source_name="Anthropic Economic Index (Hugging Face)",
            source_url=DATASET_URL,
            license=LICENSE,
            fetched_at=fetched_at,
            data_through=df["date"].max().strftime("%Y-%m-%d"),
            max_lag_days=270,  # irregular releases; generous
            breaks=[dict(b) for b in BREAKS],
            notes=NOTES,
            role=role,
        )

    auto_df, aug_df = frame(auto_rows), frame(aug_rows)
    return [
        (auto_df, meta("aei_automation_share", "Automation share of categorized Claude.ai conversations", "primary", auto_df)),
        (aug_df, meta("aei_augmentation_share", "Augmentation share of categorized Claude.ai conversations", "context", aug_df)),
    ]
