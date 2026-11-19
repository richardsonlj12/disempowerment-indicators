"""EA2: automation and augmentation share of Claude.ai conversations (Anthropic Economic Index).

Keyless: public files of the Hugging Face dataset `Anthropic/EconomicIndex`.

Each release publishes the human-AI collaboration pattern shares in a different layout, so
`RELEASE_SCHEMAS` records, per release, the file, the exact layout expected, and which patterns
count as automation and augmentation. Anything unexpected (a renamed column, a new pattern
label, a release directory with no entry here) raises `SourceError`; nothing is guessed.

Definition used for every release (Anthropic's own, from the 2025-09-15 and 2026-06-26 data
documentation): shares are percent of *classifiable* conversations, so patterns `none` and
`not_classified` are excluded from the denominator and automation + augmentation = 100.

Each point is dated by the first day of the window its conversations were sampled in, not by the
release date, and carries a `period` label for that window, its `sample_end` and its `release`
date (owner review, 2026-11-19). Besides the two totals, the five pattern shares are kept
(`aei_patterns`, long format, one group per pattern) for the stacked-bar chart.
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
AUGMENTATION = ("task iteration", "learning", "validation")
EXCLUDED = ("none", "not_classified")
PATTERNS = AUTOMATION + AUGMENTATION  # stacking order, bottom to top
PATTERN_KEYS = {p: p.replace(" ", "_") for p in PATTERNS}  # group labels in aei_patterns

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

# samples: (first day, last day, label) of each sample window the release reports.
RELEASE_SCHEMAS: dict[str, dict] = {
    "release_2025_02_10": {
        "kind": "interaction_csv",
        "path": "release_2025_02_10/automation_vs_augmentation.csv",
        "header": ["interaction_type", "pct"],
        "samples": [("2024-12-16", "2024-12-23", "16–23 Dec 2024")],
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
        # Anthropic gives only "the 11 days following the launch" of Claude 3.7 Sonnet, labelled
        # "Feb '25 - March '25" in its figure, so the point is dated by that span, not guessed days.
        "samples": [("2025-02-01", "2025-03-31", "Feb–Mar 2025")],
        "automation": AUTOMATION,
        "augmentation": AUGMENTATION,
        "excluded": ("none",),
        "window": "second report sample, the 11 days after the Claude 3.7 Sonnet launch (Anthropic's figure: "
        "Feb '25 - March '25), Claude.ai Free and Pro",
    },
    "release_2025_09_15": {
        **_RAW_BASE,
        "path": "release_2025_09_15/data/intermediate/aei_raw_claude_ai_2025-08-04_to_2025-08-11.csv",
        "samples": [("2025-08-04", "2025-08-11", "4–11 Aug 2025")],
        "window": ("2025-08-04", "2025-08-11"),
    },
    "release_2026_01_15": {
        **_RAW_BASE,
        "path": "release_2026_01_15/data/intermediate/aei_raw_claude_ai_2025-11-13_to_2025-11-20.csv",
        "samples": [("2025-11-13", "2025-11-20", "13–20 Nov 2025")],
        "window": ("2025-11-13", "2025-11-20"),
    },
    "release_2026_03_24": {
        **_RAW_BASE,
        "path": "release_2026_03_24/data/aei_raw_claude_ai_2026-02-05_to_2026-02-12.csv",
        "samples": [("2026-02-05", "2026-02-12", "5–12 Feb 2026")],
        "window": ("2026-02-05", "2026-02-12"),
    },
    "release_2026_06_26": {
        "kind": "monthly_buckets",
        "path": "release_2026_06_26/data/aei_claude_ai_2026-06-26.csv",
        "header": MONTHLY_HEADER,
        "samples": [("2026-04-01", "2026-04-30", "April 2026"), ("2026-05-01", "2026-05-31", "May 2026")],
        "automation": AUTOMATION,
        "augmentation": AUGMENTATION,
        "excluded": ("none", "not_classified"),
        "automation_metric": "collaboration_bucket_automation_pct",
        "augmentation_metric": "collaboration_bucket_augmentation_pct",
    },
}

# Dated at the first sample of each new method group, because points are dated by sample window.
BREAKS = [
    {
        "date": "2025-08-04",
        "note": "Release layout changed from a six-row interaction-type summary to the raw long-format "
        "file (patterns read from the collaboration facet, global rows); shares now recomputed "
        "from patterns.",
    },
    {
        "date": "2026-02-05",
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
    "shares sum to 100), global, one row per sample, dated by the first day of the sample window (column period "
    "names the window, sample_end its last day, release the release date). The series aei_patterns gives the five "
    "pattern shares on the same denominator. Mapping (Anthropic's categorisation in the 2025-09-15 "
    "enrichment code and the 2026-06-26 data documentation): automation = directive + feedback loop; "
    "augmentation = validation + task iteration + learning. "
    "Release mappings: "
    "release_2025_02_10 and release_2025_03_27 read automation_vs_augmentation.csv and "
    "automation_vs_augmentation_v2.csv (columns interaction_type, pct); "
    "release_2025_09_15, release_2026_01_15 and release_2026_03_24 read the raw claude_ai file, rows "
    "geo_id=GLOBAL, facet=collaboration, level=0, variable=collaboration_pct, cluster_name = the pattern; "
    "release_2026_06_26 reads the claude_ai file, rows geo_id=GLOBAL, category_name=overall, "
    "hierarchy_level=0, metric_ids collaboration_<pattern>_pct, checked against Anthropic's published "
    "collaboration_bucket_automation_pct and collaboration_bucket_augmentation_pct (within 0.05 points). "
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


def _check_labels(labels, schema: dict, release: str) -> None:
    known = set(schema["automation"]) | set(schema["augmentation"]) | set(schema["excluded"])
    unknown = set(labels) - known
    if unknown:
        raise SourceError(f"{release}: unknown collaboration pattern(s) {sorted(unknown)}; add a mapping")
    missing = (set(schema["automation"]) | set(schema["augmentation"])) - set(labels)
    if missing:
        raise SourceError(f"{release}: collaboration pattern(s) {sorted(missing)} absent")


def _normalize(values: dict[str, float], schema: dict, release: str) -> dict[str, float]:
    """The five pattern shares as percent of classifiable conversations (they add to 100)."""
    _check_labels(values, schema, release)
    total = sum(values[k] for k in PATTERNS)
    if total <= 0:
        raise SourceError(f"{release}: no classifiable conversations")
    return {k: values[k] / total * 100 for k in PATTERNS}


def _from_interaction_csv(release: str, schema: dict) -> dict[str, dict[str, float]]:
    url = RESOLVE + schema["path"]
    rows = list(csv.reader(http.get(url, expect="csv").text.splitlines()))
    if not rows or rows[0] != schema["header"]:
        raise SourceError(f"{release}: unexpected header {rows[0] if rows else None}; expected {schema['header']}")
    values = {r[0]: float(r[1]) for r in rows[1:] if r}
    return {schema["samples"][0][0]: _normalize(values, schema, release)}


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


def _from_raw_long(release: str, schema: dict) -> dict[str, dict[str, float]]:
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
    return {schema["samples"][0][0]: _normalize(values, schema, release)}


def _from_monthly_buckets(release: str, schema: dict) -> dict[str, dict[str, float]]:
    url = RESOLVE + schema["path"]
    buckets = (schema["automation_metric"], schema["augmentation_metric"])
    header, lines = _stream_lines(url, lambda l: ",GLOBAL,global,overall,0,collaboration_" in l)
    if next(csv.reader([header]), None) != schema["header"]:
        raise SourceError(f"{release}: unexpected header {header!r}; expected {schema['header']}")
    months: dict[str, dict[str, float]] = {}
    totals: dict[str, dict[str, float]] = {}
    for row in csv.DictReader(lines, fieldnames=schema["header"]):
        metric = row["metric_id"]
        if metric in buckets:
            totals.setdefault(row["date_start"], {})[metric] = float(row["value"])
        elif metric.startswith("collaboration_") and metric.endswith("_pct") and "bucket" not in metric:
            label = metric[len("collaboration_"):-len("_pct")]
            label = label if label == "not_classified" else label.replace("_", " ")
            months.setdefault(row["date_start"], {})[label] = float(row["value"])
        else:
            raise SourceError(f"{release}: unknown collaboration metric {metric!r}; add a mapping")
    expected = [start for start, _, _ in schema["samples"]]
    if sorted(months) != expected or sorted(totals) != expected:
        raise SourceError(f"{release}: months {sorted(months)} differ from expected {expected}")
    out = {}
    for month in expected:
        shares = _normalize(months[month], schema, release)
        got = totals[month]
        if set(got) != set(buckets):
            raise SourceError(f"{release}: {month} lacks one of {buckets}")
        auto = sum(shares[k] for k in AUTOMATION)
        if abs(auto - got[buckets[0]]) > 0.05 or abs(100 - auto - got[buckets[1]]) > 0.05:
            raise SourceError(
                f"{release}: {month} patterns give {auto:.2f} percent automation, but Anthropic's totals are "
                f"{got[buckets[0]]} and {got[buckets[1]]}"
            )
        out[month] = shares
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
    """Previously fetched pattern shares by sample start date, or None if the file is missing."""
    path = Path(data_dir) / "aei_patterns.csv"
    if not path.exists():
        return None
    old = pd.read_csv(path, parse_dates=["date"], dtype={"group": str})
    by_key = {v: k for k, v in PATTERN_KEYS.items()}
    out: dict[str, dict[str, float]] = {}
    for d, g, v in zip(old["date"], old["group"], old["value"]):
        out.setdefault(d.strftime("%Y-%m-%d"), {})[by_key.get(g, g)] = float(v)
    return out


def fetch(data_dir: Path | str = "data", full: bool = False) -> list[tuple[pd.DataFrame, SeriesMeta]]:
    """Releases are immutable, so committed ones are reused unless `full` is set.

    The raw files are 19 to 219 MB each; this keeps a routine refresh to the listing request
    plus any new release.
    """
    fetched_at = utc_now_iso()
    _check_listing()
    committed = None if full else _committed(Path(data_dir))

    shares: dict[str, dict[str, float]] = {}  # sample start -> pattern -> percent
    info: dict[str, tuple[str, str, str]] = {}  # sample start -> (last day, period label, release date)
    for release, schema in RELEASE_SCHEMAS.items():
        release_date = release.removeprefix("release_").replace("_", "-")
        starts = []
        for start, end, period in schema["samples"]:
            info[start] = (end, period, release_date)
            starts.append(start)
        if committed and all(set(committed.get(d, {})) == set(PATTERNS) for d in starts):
            for d in starts:
                shares[d] = committed[d]
            continue
        shares.update(_READERS[schema["kind"]](release, schema))

    dates = sorted(shares)

    def describe(df: pd.DataFrame) -> pd.DataFrame:
        keys = df["date"].dt.strftime("%Y-%m-%d")
        df["period"] = [info[k][1] for k in keys]
        df["sample_end"] = [info[k][0] for k in keys]
        df["release"] = [info[k][2] for k in keys]
        return df

    def total(patterns: tuple[str, ...]) -> pd.DataFrame:
        df = pd.DataFrame({
            "date": pd.to_datetime(dates),
            "value": [float(sum(shares[d][p] for p in patterns)) for d in dates],
        })
        return describe(assign_segments(df, BREAKS))

    long = pd.DataFrame(
        [{"date": d, "group": PATTERN_KEYS[p], "value": float(shares[d][p])} for p in PATTERNS for d in dates]
    )
    long["date"] = pd.to_datetime(long["date"])
    long = describe(assign_segments(long, BREAKS))
    data_through = max(info[d][0] for d in dates)

    def meta(series_id: str, title: str, role: str) -> SeriesMeta:
        return SeriesMeta(
            series_id=series_id,
            indicator_id="EA2",
            title=title,
            units="percent",
            frequency="irregular",
            source_name="Anthropic Economic Index (Hugging Face)",
            source_url=DATASET_URL,
            license=LICENSE,
            fetched_at=fetched_at,
            data_through=data_through,  # last day of the latest sample window
            max_lag_days=270,  # irregular releases; generous
            breaks=[dict(b) for b in BREAKS],
            notes=NOTES,
            role=role,
        )

    return [
        (total(AUTOMATION), meta("aei_automation_share", "Automation share of categorized Claude.ai conversations", "primary")),
        (total(AUGMENTATION), meta("aei_augmentation_share", "Augmentation share of categorized Claude.ai conversations", "context")),
        (long, meta("aei_patterns", "Share of each collaboration pattern in categorized Claude.ai conversations", "context")),
    ]
