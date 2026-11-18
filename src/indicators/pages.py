"""Site generator: writes the Quarto sources that depend on config, data and content.

`build(repo_root)` copies data/ and the public config files into site/, writes one page per
Release 1 indicator from site/_indicator_template.qmd, writes trend CSVs for the long-running
series, and writes the generated parts of the summary and methodology pages (site/_generated/,
included by index.qmd and methodology.qmd). CLI: `python -m indicators.pages [repo_root]`.

Public text uses display labels only; internal keys (layer, comparison, tier) never reach a page.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import yaml

from indicators import registry as reg
from indicators.curated import load_curated, published
from indicators.store import SeriesMeta, assign_segments, read_series, stale_since, staleness
from indicators.trend import pre_ai_trend

RELEASE = 1
SITE_NAME = "KEEL"
DOMAINS = ("economic", "government", "cultural")
LAYERS = ("exposure", "erosion", "lockin")

TIMING = {
    "leading": "Leading: likely to move early, before any effect is entrenched",
    "lagging": "Lagging: likely to move only after a change is well under way",
}
COMPARISON = {
    "structural": "A long-running series, compared with {baseline}.",
    "ai_native": "A series that measures AI use directly and has no period before AI, compared with {baseline}.",
}
# What each indicator is read against. CD1's index starts in June 2012 (2019 = 100), so it has no
# 2010 to 2019 baseline.
BASELINE_TEXT = {"ED1": "its 2010 to 2019 trend", "GD1": "its 2010 to 2019 trend", "CD1": "its 2012 to 2019 history"}
DEFAULT_BASELINE = {"structural": "its 2010 to 2019 trend", "ai_native": "its own recent path"}
AI_LINK_QUESTIONS = (
    ("directness", "Does it measure AI itself?"),
    ("comparison_group", "Is there a comparison group?"),
    ("timing", "Does the timing fit?"),
    ("confounders", "Are other possible causes addressed?"),
)
SECTIONS = (
    "Why this matters for gradual disempowerment",
    "What it shows",
    "What it doesn't show",
    "What would change our reading",
    "Data and calculation",
    "Caveats",
)
KIND_LABELS = {"policy": "Policy pushback", "data_signal": "Data signal"}
PUBLIC_CONFIG = ("indicators.yaml", "readings.yaml", "chart_markers.yaml", "cd1_comparison_sites.yaml",
                 "curated/counter_evidence.yaml", "curated/oversight.yaml")

# Chart views per indicator. kind: level (one series at a time, selector when several; standard
# errors as a band; optional dashed 2010-19 trend), deviation (from the 2010-19 trend), band (line
# plus a shaded range from two other series), multi (all series together, groups expanded).
CHART_VIEWS: dict[str, list[dict]] = {
    "ED1": [
        {"label": "Level", "kind": "level", "series": ["labor_share_nfb", "profit_share"], "trend": True},
        {"label": "Deviation from 2010–19 trend", "kind": "deviation", "series": ["labor_share_nfb", "profit_share"]},
    ],
    "EA1": [
        {"label": "All firms", "kind": "level", "series": ["btos_ai_use"]},
        {"label": "By firm size", "kind": "multi", "series": ["btos_ai_use_by_size"]},
    ],
    "EA2": [
        {"label": "Automation and augmentation shares", "kind": "multi",
         "series": ["aei_automation_share", "aei_augmentation_share"]},
    ],
    "GD1": [
        {"label": "Level", "kind": "level",
         "series": ["us_labor_tax_share", "oecd_labor_tax_share_usa", "oecd_labor_tax_share_avg"], "trend": True},
        {"label": "Deviation from 2010–19 trend", "kind": "deviation",
         "series": ["us_labor_tax_share", "oecd_labor_tax_share_usa", "oecd_labor_tax_share_avg"]},
    ],
    "CD1": [
        {"label": "Relative activity index (2019 = 100)", "kind": "band", "series": ["so_relative_index"],
         "band": ["so_relative_index_loo_min", "so_relative_index_loo_max"], "rule": 100,
         "note": "Shaded band: the lowest and highest index when each comparison site is left out in turn."},
        {"label": "Change since November 2022", "kind": "level", "series": ["so_change_since_chatgpt"], "rule": 0},
        {"label": "Year-over-year gap (alternative view)", "kind": "level", "series": ["so_vs_comparison_yoy"], "rule": 0},
        {"label": "Monthly questions", "kind": "multi",
         "series": ["so_questions_monthly", "se_comparison_questions_monthly"], "log_option": True},
        {"label": "Wikipedia", "kind": "level", "series": ["wiki_user_pageviews_en", "wiki_active_editors_en"]},
    ],
}
# Legend labels for multi-series views (grouped series are labelled by group).
SERIES_LABELS = {
    "aei_automation_share": "Automation",
    "aei_augmentation_share": "Augmentation",
    "so_questions_monthly": "Stack Overflow",
}
SE_NOTE = "Shaded band: plus or minus 1.96 standard errors (about a 95 percent interval), as published by the source."


# ------------------------------------------------------------------ formatting

def fmt_date(d: date | str) -> str:
    d = date.fromisoformat(str(d)[:10])
    return f"{d.day} {d:%B %Y}"


def fmt_period(d: date | str, frequency: str) -> str:
    d = date.fromisoformat(str(d)[:10])
    if frequency == "quarterly":
        return f"{d.year} Q{(d.month - 1) // 3 + 1}"
    if frequency == "monthly":
        return f"{d:%B %Y}"
    if frequency == "annual":
        return str(d.year)
    return fmt_date(d)


def fmt_value(value: float, units: str) -> str:
    number = f"{value:,.0f}" if abs(value) >= 1000 else f"{value:.1f}"
    if units == "percent":
        return f"{number} percent"
    index = re.fullmatch(r"index \((.*)\)", units)
    if index:
        return f"{number} (index, {index.group(1)})"
    return f"{number} {units}"


def _cell(text: str) -> str:
    """Make text safe inside a pipe-table cell."""
    return " ".join(str(text).split()).replace("|", "\\|")


def _url(url: str) -> str:
    """Encode square brackets so a URL is safe inside a Markdown link."""
    return url.replace("[", "%5B").replace("]", "%5D")


# ------------------------------------------------------------------ inputs

def baseline_text(ind: reg.Indicator) -> str:
    return BASELINE_TEXT.get(ind.id, DEFAULT_BASELINE[ind.comparison])


def split_content(text: str) -> tuple[dict, dict[str, str]]:
    """Front matter and the level-2 sections of a content page, by heading. The sections must be
    exactly SECTIONS, with no text before the first one."""
    if not text.startswith("---\n"):
        raise ValueError("content page has no front matter")
    _, fm_text, body = text.split("---\n", 2)
    front = yaml.safe_load(fm_text) or {}
    sections: dict[str, str] = {}
    parts = re.split(r"^## (.+)$", body, flags=re.M)
    if parts[0].strip():
        raise ValueError("content page has text before its first level-2 heading")
    for heading, content in zip(parts[1::2], parts[2::2]):
        sections[heading.strip()] = content.strip()
    missing = [s for s in SECTIONS if s not in sections]
    if missing:
        raise ValueError(f"content page is missing sections: {missing}")
    unknown = [s for s in sections if s not in SECTIONS]
    if unknown:
        raise ValueError(f"content page has unknown sections: {unknown}")
    return front, sections


def _load_series(data_dir: Path, series_ids: list[str]) -> dict[str, tuple]:
    """(frame, meta) for each series whose files exist; absent series are left out."""
    out = {}
    for sid in series_ids:
        if (data_dir / f"{sid}.csv").exists() and (data_dir / f"{sid}.meta.json").exists():
            out[sid] = read_series(sid, data_dir)
    return out


def _latest(frame) -> tuple[float, str] | None:
    if frame is None or frame.empty or "group" in frame.columns:
        return None
    row = frame.sort_values("date").iloc[-1]
    return float(row["value"]), row["date"].date().isoformat()


# ------------------------------------------------------------------ pieces

NO_VALUE = "Latest value not yet available (data still being collected)"


def latest_value_text(ind: reg.Indicator, series: dict) -> str:
    """'[series title], latest value: X (period)', naming the series so multi-series pages are clear."""
    primary = series.get(ind.primary_series)
    latest = _latest(primary[0]) if primary else None
    if latest is None:
        return NO_VALUE
    meta = primary[1]
    return f"{meta.title}, latest value: {fmt_value(latest[0], meta.units)} ({fmt_period(latest[1], meta.frequency)})"


def latest_value_parts(ind: reg.Indicator, series: dict) -> list[str]:
    """[series title, value, period] for the summary grid (one per line), or [NO_VALUE]."""
    primary = series.get(ind.primary_series)
    latest = _latest(primary[0]) if primary else None
    if latest is None:
        return [NO_VALUE]
    meta = primary[1]
    return [meta.title, fmt_value(latest[0], meta.units), fmt_period(latest[1], meta.frequency)]


def reading_lines(ind: reg.Indicator, reading: reg.Reading, series: dict) -> list[str]:
    """The three-line reading: state label; magnitude naming the baseline (no baseline clause while
    there is no value); interpretation with the AI link."""
    label = reg.STATE_LABELS[reading.state]
    value = latest_value_text(ind, series)
    magnitude = reading.magnitude or (value if value == NO_VALUE else f"{value}, against {baseline_text(ind)}")
    interpretive = f"AI link: {ind.ai_link.capitalize()}"
    if reading.interpretation:
        interpretive += f". {reading.interpretation}"
    return [f"**{label}**", magnitude, interpretive]


def summary_table(ind, front, reading, series) -> str:
    primary = series.get(ind.primary_series)
    through = (f"data through {fmt_period(primary[1].data_through, primary[1].frequency)}"
               if primary else "data through: not yet available (data still being collected)")
    sources = "<br>".join(f"[{_cell(s['name'])}]({_url(s['url'])})" for s in front["data_sources"])
    rows = [
        ("Summary", reg.content_summary(front)),
        ("Current reading", "<br>".join(_cell(x) for x in reading_lines(ind, reading, series))),
        ("Grid position", f"{reg.layer_label(ind.layer)} · {ind.domain.capitalize()}"),
        ("AI link", f"{ind.ai_link.capitalize()}. A draft rating, to be reviewed in Stage 2; the four criteria are under "
                    "[Method](#method)."),
        ("Leading or lagging", TIMING[ind.timing]),
        ("Warning sign", front["warning_sign"]),
        ("Data source(s)", sources),
        ("Calculation", front["calculation"]),
        ("Coverage", f"{front['coverage']} · {through}"),
    ]
    lines = ["::: {.keel-summary}", "", "|   |   |", "|:----------|:--------------------------------------------|"]
    lines += [f"| {label} | {value if label in ('Current reading', 'Data source(s)') else _cell(value)} |"
              for label, value in rows]
    lines += ["", ":::"]
    return "\n".join(lines)


def _stale_item(meta: SeriesMeta) -> str:
    due = fmt_date(stale_since(meta))
    latest = fmt_period(meta.data_through, meta.frequency)
    if meta.frequency == "irregular":
        return (f"- **Stale since {due}.** {meta.title}: the latest data are for {latest}. The source "
                f"publishes irregular releases, and a new release was expected by {due}.")
    return f"- **Stale since {due}.** {meta.title}: the latest data are for {latest}, and newer data were expected by {due}."


def notices(ind, views, series, today: date) -> str:
    out = []
    primary = series.get(ind.primary_series)
    if primary:
        meta = primary[1]
        out.append(f"*Data last fetched {fmt_date(meta.fetched_at)}; "
                   f"data through {fmt_period(meta.data_through, meta.frequency)}.*")
    stale = [meta for _, meta in series.values() if staleness(meta, today)]
    if stale:
        items = "\n".join(_stale_item(meta) for meta in stale)
        out.append('::: {.callout-warning title="Stale data"}\n'
                   f"{items}\n\nThe chart shows the last data received.\n:::")
    if ind.headline_caveat:
        caveat = ind.headline_caveat.rstrip()
        caveat = caveat if caveat[-1:] in ".!?" else caveat + "."
        out.append(f'::: {{.callout-important title="Caveat"}}\n**{caveat}**\n:::')
    if ind.disclosure:
        out.append(f'::: {{.callout-note title="Disclosure"}}\n{ind.disclosure}\n:::')
    waiting = [v["label"] for v in views if not v["available"]]
    if waiting:
        out.append('::: {.callout-note title="Data still being collected"}\n'
                   "**Data still being collected.** Some series for this indicator are still "
                   "being downloaded from their source and will appear when the download is complete. Chart views "
                   f"waiting for data: {', '.join(waiting)}.\n:::")
    return "\n\n".join(out)


def chart_spec(ind, views, series, markers, group_labels) -> dict:
    spec_series = {}
    for v in views:
        for sid in v["series"] + v.get("band", []):
            if sid in spec_series:
                continue
            entry = {"available": sid in series, "file": f"{sid}.csv", "label": SERIES_LABELS.get(sid)}
            if sid in series:
                meta = series[sid][1]
                entry.update(title=meta.title, units=meta.units, frequency=meta.frequency, breaks=meta.breaks)
            spec_series[sid] = entry
    return {
        "id": ind.id,
        "chartTitle": ind.chart_title or ind.name,
        "dataBase": "../data/",
        "views": views,
        "series": spec_series,
        "markers": markers,
        "groupLabels": group_labels,
        "seNote": SE_NOTE,
    }


def chart_block(spec: dict, trend_files: set[str]) -> str:
    for sid, entry in spec["series"].items():
        entry["trendFile"] = f"{sid}_trend.csv" if sid in trend_files else None
    payload = json.dumps(spec, ensure_ascii=False, indent=1)
    return "\n".join([
        "```{ojs}",
        "//| echo: false",
        'import { TIMEFRAMES, loadData, themeChanges, viewInput, seriesInput, logInput, renderChart } from "../js/charts.js"',
        f"keelSpec = ({payload})",
        "keelData = loadData(d3, keelSpec)",
        "keelTheme = themeChanges()",
        "viewof keelView = viewInput(Inputs, keelSpec)",
        'viewof keelTimeframe = Inputs.radio(TIMEFRAMES.map(t => t.label), {label: "Timeframe", value: "All"})',
        "viewof keelSeries = seriesInput(Inputs, keelSpec, keelView)",
        "viewof keelLog = logInput(Inputs, keelSpec, keelView)",
        "renderChart(Plot, d3, keelSpec, keelData, {view: keelView, timeframe: keelTimeframe, "
        "series: keelSeries, log: keelLog, theme: keelTheme, width})",
        "```",
    ])


def reading_history(readings: list[reg.Reading]) -> str:
    reviewed = sorted((r for r in readings if r.state != "not_yet_reviewed"), key=lambda r: r.date, reverse=True)
    if not reviewed:
        return ("No reviewed readings yet. Readings begin in Stage 3, once the threshold rule is reviewed and "
                "frozen. Every reading will be listed here with its date and rationale "
                "([readings file](../config/readings.yaml)).")
    lines = []
    for r in reviewed:
        line = f"- **{fmt_date(r.date)}: {reg.STATE_LABELS[r.state]}**"
        if r.kind != "current":
            line += " (retrospective)"
        if r.rationale:
            line += f". {r.rationale}"
        lines.append(line)
    return "\n".join(lines)


def method_section(ind, series, markers) -> str:
    lines = [f"- **Comparison and baseline.** {COMPARISON[ind.comparison].format(baseline=baseline_text(ind))}",
             "- **Threshold rule and sensitivity table.** Stage 2.",
             f"- **AI link: {ind.ai_link.capitalize()}** (draft, to be reviewed in Stage 2), judged on four criteria:"]
    for key, question in AI_LINK_QUESTIONS:
        lines.append(f"    - *{question}* {ind.ai_link_criteria.get(key, 'Not yet assessed.')}")
    lines.append("- **Sources.**")
    for s in ind.sources:
        lines.append(f"    - [{s['name']}]({_url(s['url'])}). License: {s['license']}.")
    breaks = [(b["date"], meta.title, b["note"]) for _, meta in series.values() for b in meta.breaks]
    if breaks:
        lines.append("- **Series breaks.** The chart does not join the line across a break.")
        for d, title, note in sorted(breaks):
            lines.append(f"    - {fmt_date(d)} ({title}): {note}")
    else:
        lines.append("- **Series breaks.** None recorded.")
    if markers:
        lines.append("- **Chart markers.** Dated events marked on the chart without splitting the line.")
        for m in markers:
            lines.append(f"    - {fmt_date(m['date'])}: {m['label']}")
    if series:
        lines.append("- **Last fetched.**")
        for _, meta in series.values():
            lines.append(f"    - {meta.title}: fetched {fmt_date(meta.fetched_at)}, data through "
                         f"{fmt_period(meta.data_through, meta.frequency)}.")
    lines.append("- **Registry entry.** [indicators.yaml](../config/indicators.yaml) (YAML).")
    return "\n".join(lines)


def downloads(views, series, trend_files) -> str:
    wanted = []
    for v in views:
        for sid in v["series"] + v.get("band", []):
            if sid not in wanted:
                wanted.append(sid)
    lines = []
    for sid in wanted:
        if sid not in series:
            continue
        title = series[sid][1].title
        lines.append(f"- [{title}](../data/{sid}.csv) (CSV) · [metadata](../data/{sid}.meta.json) (JSON)")
        if sid in trend_files:
            lines.append(f"- [{title}, with the 2010–19 trend and the deviation from it](../data/{sid}_trend.csv) (CSV)")
    if any(sid not in series for sid in wanted):
        lines.append("- Some series are still being collected and will be listed here when available.")
    return "\n".join(lines)


# ------------------------------------------------------------------ pages

def write_trend_csv(frame, meta: SeriesMeta, out_dir: Path) -> None:
    if "segment" not in frame.columns:
        frame = assign_segments(frame, meta.breaks)
    trend = pre_ai_trend(frame)[["date", "value", "trend", "deviation", "segment"]]
    trend.to_csv(out_dir / f"{meta.series_id}_trend.csv", index=False, date_format="%Y-%m-%d", lineterminator="\n")


def indicator_page(template: str, ind, front, sections, reading, history, views, series, markers,
                   group_labels, trend_files, today) -> str:
    title = f"{ind.name} ({ind.id})"
    fm = yaml.safe_dump({"title": title, "pagetitle": f"{title} · {SITE_NAME}"}, allow_unicode=True,
                        sort_keys=False, width=1000).strip()
    spec = chart_spec(ind, views, series, markers, group_labels)
    chart = f"**{ind.chart_title or ind.name}**\n\n{chart_block(spec, trend_files)}"

    def section(name):
        return f"## {name}\n\n{sections[name]}"

    replacements = {
        "%%FRONT_MATTER%%": fm,
        "%%SUMMARY_TABLE%%": summary_table(ind, front, reading, series),
        "%%NOTICES%%": notices(ind, views, series, today),
        "%%WHY%%": section(SECTIONS[0]),
        "%%CHART%%": chart,
        "%%READING_HISTORY%%": reading_history(history),
        "%%SHOWS%%": section(SECTIONS[1]),
        "%%DOESNT_SHOW%%": section(SECTIONS[2]),
        "%%CHANGE%%": section(SECTIONS[3]),
        "%%DATA_AND_CALCULATION%%": section(SECTIONS[4]),
        "%%METHOD%%": method_section(ind, series, markers),
        "%%CAVEATS%%": section(SECTIONS[5]),
        "%%DOWNLOADS%%": downloads(views, series, trend_files),
    }
    text = template
    for token, value in replacements.items():
        if token not in text:
            raise ValueError(f"template is missing {token}")
        text = text.replace(token, value)
    leftover = re.findall(r"%%[A-Z_]+%%", text)
    if leftover:
        raise ValueError(f"unfilled template tokens: {leftover}")
    return text


def _cell_div(layer, domain, body) -> str:
    row, dom = reg.layer_label(layer), domain.capitalize()
    caption = f"[{row} · {dom}]{{.keel-cell-caption}}"
    return f'::: {{.keel-cell row="{row}" domain="{dom}"}}\n{caption}\n\n{body}\n:::'


def summary_page(indicators, grid, oversight, readings, latest_text, oversight_items, counter_header,
                 counter_items) -> str:
    by_id = {i.id: i for i in indicators}
    cells = {(c.layer, c.domain): c for c in grid}
    out = ["These indicators show whether the conditions for disempowerment are present. "
           "They do not show whether it is happening. [How the indicators work](methodology.qmd).", "",
           "::: {.callout-note title=\"What the data is telling us\"}",
           "Readings begin after the threshold rule is reviewed and frozen (Stages 2 and 3). "
           "Until then every indicator shows Not yet reviewed, with its latest data.",
           ":::", "", "## Indicators", "", ":::: {.keel-grid}", "::: {.keel-corner}", "&nbsp;", ":::"]
    for d in DOMAINS:
        out += [f"::: {{.keel-colhead}}\n**{d.capitalize()}**\n:::"]
    for layer in LAYERS:
        out += [f"::: {{.keel-rowhead}}\n**{reg.layer_label(layer)}**\n:::"]
        for d in DOMAINS:
            cell = cells.get((layer, d))
            ids = [i for i in (cell.indicator_ids if cell else []) if i in by_id]
            if not ids:
                body = cell.empty_label if cell else "No public measure yet"
            else:
                parts = []
                for ind_id in ids:
                    ind = by_id[ind_id]
                    state = reg.STATE_LABELS[reg.current_reading(readings, ind_id).state]
                    lines = [f"[{ind.name}](indicators/{ind.id}.qmd) ({ind.id})", f"**{state}**",
                             *latest_text[ind_id],
                             f"[AI link: {ind.ai_link.capitalize()}]{{.keel-badge .keel-badge-{ind.ai_link}}}"]
                    parts.append("\\\n".join(lines))
                body = "\n\n".join(parts)
            out.append(_cell_div(layer, d, body))
    cite = []
    for item in oversight_items:
        cite.append(f"Nearest evidence: [{item['label']}]({_url(item['source_url'])}), {item['source_name']}, "
                    f"{fmt_date(item['date'])}. {item['metric']}: {item['value']} {item['unit']}. "
                    "One study, not a time series.")
    out += ["::: {.keel-oversight}",
            f"**{oversight['row_label']}** · {oversight['label']}", "", *cite, ":::", "::::", ""]

    exposure = [i.id for i in indicators if i.scale == "exposure"]
    baselines = "; ".join(f"{i.id}: {baseline_text(i)}" for i in indicators if i.scale == "baseline")
    baseline = [i.id for i in indicators if i.scale == "baseline"]
    labels = reg.STATE_LABELS
    out += ["**Two sets of labels.** "
            f"Adoption indicators ({_and(exposure)}) will be read as {labels['low']}, {labels['rising']} or "
            f"{labels['pervasive']}. Indicators read against a baseline ({_and(baseline)}) will be read as "
            f"{labels['within']}, {labels['above']}, {labels['below']}, {labels['far_above']} or "
            f"{labels['far_below']}, each against its own baseline ({baselines}). Either can also read "
            f"{labels['no_signal']}. The AI link badge (Strong, Moderate or Weak) says how clearly a movement in a "
            "series can be connected to AI rather than to other causes. See the [methodology](methodology.qmd).", ""]

    out += ["## Counter-evidence", "",
            "Signals that point away from disempowerment, held to the same standard as the indicators.", ""]
    for item in counter_items:
        value = item["value"]
        measured = "" if isinstance(value, dict) else f" {item['metric']}: {value} {item['unit']}."
        out.append(f"- **{item['label']}** ({item['domain'].capitalize()}; "
                   f"{KIND_LABELS.get(item.get('kind'), 'Item')}; dated {fmt_date(item['date'])}).{measured} "
                   f"Source: [{item['source_name']}]({_url(item['source_url'])}).")
    out += ["", "::: {.callout-note collapse=\"true\" title=\"Inclusion criteria\"}",
            " ".join(str(counter_header["inclusion_criteria"]).split()), ":::", "",
            "Earlier snapshots and superseded rules will be kept in the [Archive](archive.qmd).", ""]
    return "\n".join(out)


def _and(ids: list[str]) -> str:
    return ids[0] if len(ids) == 1 else ", ".join(ids[:-1]) + " and " + ids[-1]


# ------------------------------------------------------------------ build

def _reset(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def build(repo_root: Path, today: date | None = None) -> None:
    root = Path(repo_root)
    today = today or date.today()
    site, data_dir, config = root / "site", root / "data", root / "config"

    all_indicators, grid, oversight = reg.load_registry(config / "indicators.yaml")
    readings = reg.load_readings(config / "readings.yaml", all_indicators)  # validates every row
    indicators = [i for i in all_indicators if i.release == RELEASE]
    chart_markers = reg.load_chart_markers(config / "chart_markers.yaml")
    sites = yaml.safe_load((config / "cd1_comparison_sites.yaml").read_text(encoding="utf-8"))
    group_labels = {s["api_site_name"]: s["name"] for s in sites.get("sites", [])}
    _, oversight_items = load_curated(config / "curated" / "oversight.yaml")
    counter_header, counter_items = load_curated(config / "curated" / "counter_evidence.yaml")

    for sub in ("data", "config", "indicators", "_generated"):
        _reset(site / sub)
    for f in data_dir.iterdir():
        if f.is_file() and f.suffix in (".csv", ".json"):
            shutil.copy2(f, site / "data" / f.name)
    for rel in PUBLIC_CONFIG:
        dest = site / "config" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(config / rel, dest)
    shutil.copy2(root / "content" / "methodology.md", site / "_generated" / "methodology.md")

    template = (site / "_indicator_template.qmd").read_text(encoding="utf-8")
    latest_text = {}
    for ind in indicators:
        views = [dict(v) for v in CHART_VIEWS.get(ind.id, [{"label": "Level", "kind": "level", "series": ind.series}])]
        series = _load_series(data_dir, list(dict.fromkeys(ind.series + [s for v in views for s in v["series"]])))
        for v in views:
            v["available"] = all(s in series for s in v["series"] + v.get("band", []))
        trend_files = set()
        if ind.comparison == "structural":
            wanted = {ind.primary_series} | {s for v in views if v["kind"] == "deviation" for s in v["series"]}
            for sid in wanted:
                if sid in series and "group" not in series[sid][0].columns:
                    write_trend_csv(series[sid][0], series[sid][1], site / "data")
                    trend_files.add(sid)
        front, sections = split_content((root / "content" / "indicators" / f"{ind.id}.md").read_text(encoding="utf-8"))
        markers = reg.markers_for(chart_markers, ind.id)
        page = indicator_page(template, ind, front, sections, reg.current_reading(readings, ind.id),
                              readings.get(ind.id, []), views, series, markers, group_labels, trend_files, today)
        (site / "indicators" / f"{ind.id}.qmd").write_text(page, encoding="utf-8")
        latest_text[ind.id] = latest_value_parts(ind, series)

    summary = summary_page(indicators, grid, oversight, readings, latest_text,
                           [i for i in published(oversight_items) if i["id"] == oversight.get("citation_ref")],
                           counter_header, published(counter_items))
    (site / "_generated" / "summary.md").write_text(summary, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    build(Path(argv[0]) if argv else Path.cwd())
    return 0


if __name__ == "__main__":
    sys.exit(main())
