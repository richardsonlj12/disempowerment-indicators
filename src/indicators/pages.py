"""Site generator: writes the Quarto sources that depend on config, data and content.

`build(repo_root)` copies data/ and the public config files into site/, writes one page per
Release 1 indicator from site/_indicator_template.qmd, writes change CSVs for the long-running
series, and writes the generated parts of the summary and methodology pages (site/_generated/,
included by index.qmd and methodology.qmd), including the Sources page rendered from
references/keel.json (indicators.bibliography). CLI: `python -m indicators.pages [repo_root]`.

Public text uses display labels only; internal keys (layer, comparison, tier) never reach a page.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

import pandas as pd
import yaml

from indicators import bibliography
from indicators import registry as reg
from indicators.curated import load_curated, published
from indicators.store import SeriesMeta, assign_segments, read_series, stale_since, staleness
from indicators.trend import change_bands

RELEASE = 1
SITE_NAME = "KEEL"
DOMAINS = ("economic", "government", "cultural")
LAYERS = ("exposure", "erosion", "lockin")

TIMING = {
    "leading": "Leading: likely to move early, before any effect is entrenched",
    "lagging": "Lagging: likely to move only after a change is well under way",
}
COMPARISON = {
    "structural": "A long-running series; its recent changes are compared with {baseline}.",
    "ai_native": "A series that measures AI use directly and has no period before AI, compared with {baseline}.",
}
# What each indicator is read against. CD1's index starts in June 2012 (2019 = 100), so it has no
# 2010 to 2019 baseline.
# Long-running series are read by the distribution-of-changes method (owner decision, 2026-11-19):
# the change over a window against the spread of same-length changes in the baseline period.
BASELINE_TEXT = {"ED1": "same-length changes in 2010 to 2019", "GD1": "same-length changes in 2010 to 2019",
                 "CD1": "same-length changes in June 2012 to December 2019"}
DEFAULT_BASELINE = {"structural": "same-length changes in 2010 to 2019", "ai_native": "its own recent path"}
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
# Optional content sections, placed inside the generated Method section as level-3 headings with
# these anchors (EA2's method groups, owner 2026-11-19; the chart and data table link to them).
OPTIONAL_SECTIONS = ("Method groups",)
OPTIONAL_ANCHORS = {"Method groups": "method-groups"}
KIND_LABELS = {"policy": "Policy pushback", "data_signal": "Data signal"}
PUBLIC_CONFIG = ("indicators.yaml", "readings.yaml", "chart_markers.yaml", "cd1_comparison_sites.yaml",
                 "curated/counter_evidence.yaml", "curated/oversight.yaml")

# Chart views per indicator. kind: level (one series at a time, selector when several; standard
# errors as a band), change (the change over 1, 3 or 5 years; no σ bands until Stage 2 sets the
# baseline, owner decision 2026-11-19), band (line
# plus a shaded range from two other series), multi (all series together, groups expanded), stacked
# (one bar per sample on a time axis, split into groups that add to 100; EA2, owner review 2026-11-19).
# "also": series offered for download with the view but not drawn.
CHART_VIEWS: dict[str, list[dict]] = {
    "ED1": [
        {"label": "Level", "kind": "level", "series": ["labor_share_nfb", "profit_share"]},
        {"label": "Change over time", "kind": "change", "series": ["labor_share_nfb", "profit_share"], "windows": [1, 3, 5]},
    ],
    "EA1": [
        {"label": "All firms", "kind": "level", "series": ["btos_ai_use"]},
        {"label": "By firm size", "kind": "multi", "series": ["btos_ai_use_by_size"]},
    ],
    "EA2": [
        {"label": "Collaboration patterns", "kind": "stacked", "series": ["aei_patterns"],
         "also": ["aei_automation_share", "aei_augmentation_share", "aei_uncategorized_share"],
         # Shown in the data table only, on its own denominator (percent of all conversations).
         "leftOut": {"series": "aei_uncategorized_share", "heading": "Left out",
                     "label": "Not categorized",
                     "note": "Not categorized: the percent of conversations that fit none of the five "
                             "patterns, as Anthropic publishes it. They are left out of every other column, "
                             "which is why the patterns add up to 100."},
         "families": [
             {"name": "Automation", "groups": ["directive", "feedback_loop"]},
             {"name": "Augmentation", "groups": ["task_iteration", "learning", "validation"]},
         ],
         "groupNames": {"directive": "Directive", "feedback_loop": "Feedback loop",
                        "task_iteration": "Task iteration", "learning": "Learning", "validation": "Validation"},
         # Where the full method-group definitions are (the "Method groups" content section).
         "groupsLink": "#method-groups",
         # Footnotes on data-table rows, by sample date (owner, 2026-11-19; checked against the release
         # README, the Handa et al. paper and Anthropic's blog chart).
         "footnotes": {
             "2024-12-16": "The first release's table is incomplete. In the December 2024 file, the five "
                           "patterns and “none” add up to 84.2 percent. Anthropic does not say what the "
                           "rest is. KEEL's figures for that sample, like Anthropic's own published chart, use "
                           "only the five patterns, so they are unaffected if the missing rows lie outside the five "
                           "patterns; the “Not categorized” figure "
                           "for that sample is as published and may be understated.",
         },
         # One per segment (method group); text checked against Anthropic's data documentation, 2026-11-19.
         "methodGroups": [
             {"name": "A", "tip": "Group A: Anthropic's first two reports. KEEL reads the summary table each "
                                  "published. Claude.ai Free and Pro plans."},
             {"name": "B", "tip": "Group B: from September 2025 Anthropic published the underlying data, and "
                                  "KEEL computes the shares from the five pattern rows. One-week samples, "
                                  "Free and Pro plans."},
             {"name": "C", "tip": "Group C: as group B, but Claude.ai now includes the Max plan as well as "
                                  "Free and Pro. One-week sample."},
             {"name": "D", "tip": "Group D: whole calendar months, from conversations sampled every day. "
                                  "Claude.ai now includes Cowork."},
         ]},
    ],
    "GD1": [
        {"label": "Level", "kind": "level",
         "series": ["us_labor_tax_share", "oecd_labor_tax_share_usa", "oecd_labor_tax_share_avg"]},
        {"label": "Change over time", "kind": "change", "windows": [1, 3, 5],
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
# Shown above the chart while the first view's data are still downloading and another view is the default.
PRIMARY_PENDING_NOTE = {
    "CD1": "The Stack Overflow index will appear here once its data download is complete. "
           "The Wikipedia view is shown meanwhile.",
}
# Legend labels for multi-series views (grouped series are labelled by group).
SERIES_LABELS = {
    "aei_automation_share": "Automation",
    "aei_augmentation_share": "Augmentation",
    "so_questions_monthly": "Stack Overflow",
}
# Last line of every indicator page (owner, 2026-11-19: at the very bottom, after the downloads).
FEEDBACK_LINE = ('**Feedback.** [Report an error](https://github.com/richardsonlj12/keel/issues/new?template=error-report.md) · [Join the discussion](https://github.com/richardsonlj12/keel/discussions) · [Send private feedback](https://docs.google.com/forms/d/e/1FAIpQLSdJn9K0revpwU1sWM-WPmqlPtw80JVSuR9lIzcPktXqY7e3Tg/viewform)')
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


def compare_sentence(ind: reg.Indicator) -> str:
    """What a reading will compare the latest value with (owner, 2026-11-19): a long-running series is
    read by its change, an AI-native one against its own recent path."""
    what = "its change" if ind.comparison == "structural" else "it"
    return f"Readings will compare {what} with {baseline_text(ind)}."


# Markdown spans left alone when linking indicator codes: links (text and target), inline code,
# and attribute blocks such as {#id .class}.
_PROTECTED = re.compile(r"!?\[[^\]]*\]\([^)]*\)|`[^`]*`|\{[^}]*\}")


def link_codes(md: str, hrefs: dict[str, str], self_id: str | None = None) -> str:
    """Link the first mention of each indicator code (EA1, ED1 ...) in every section to that
    indicator's page, where its summary table is (owner, 2026-11-20: readers get lost in the codes).
    A section starts at any heading. Skipped: headings, code fences, a page's own code, codes with no
    page yet, and mentions inside an existing link, which also count as the section's first."""
    if not hrefs:
        return md
    code_re = re.compile(r"\b(" + "|".join(map(re.escape, sorted(hrefs, key=len, reverse=True))) + r")\b")
    out, linked, fenced = [], set(), False
    for line in md.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        if fenced or line.lstrip().startswith("```"):
            out.append(line)
            continue
        if re.match(r"#{1,6} ", line):
            linked = set()
            out.append(line)
            continue
        pieces, pos = [], 0
        for m in _PROTECTED.finditer(line):
            pieces.append((line[pos:m.start()], False))
            pieces.append((m.group(0), True))
            pos = m.end()
        pieces.append((line[pos:], False))
        new = []
        for text, protected in pieces:
            if protected:
                if text.startswith("["):  # an existing link counts as the first mention; code and attributes do not
                    linked.update(code_re.findall(text))
                new.append(text)
                continue

            def repl(m):
                code = m.group(1)
                if code == self_id or code in linked:
                    return code
                linked.add(code)
                return f"[{code}]({hrefs[code]})"
            new.append(code_re.sub(repl, text))
        out.append("".join(new))
    return "\n".join(out)


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
    unknown = [s for s in sections if s not in SECTIONS + OPTIONAL_SECTIONS]
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


def _latest(frame) -> tuple[float, str, str | None] | None:
    """(value, ISO date, period label or None). Series sampled over a stated window (EA2) carry a
    `period` column naming it, which is shown instead of the date."""
    if frame is None or frame.empty or "group" in frame.columns:
        return None
    row = frame.sort_values("date").iloc[-1]
    label = row["period"] if "period" in frame.columns and row["period"] else None
    return float(row["value"]), row["date"].date().isoformat(), label


def _when(latest: tuple, meta: SeriesMeta) -> str:
    return latest[2] or fmt_period(latest[1], meta.frequency)


# ------------------------------------------------------------------ pieces

NO_VALUE = "Latest value not yet available (data still being collected)"


def latest_value_text(ind: reg.Indicator, series: dict) -> str:
    """'[series title], latest value: X (period)', naming the series so multi-series pages are clear."""
    primary = series.get(ind.primary_series)
    latest = _latest(primary[0]) if primary else None
    if latest is None:
        return NO_VALUE
    meta = primary[1]
    return f"{meta.title}, latest value: {fmt_value(latest[0], meta.units)} ({_when(latest, meta)})"


def latest_value_parts(ind: reg.Indicator, series: dict) -> list[str]:
    """[series title, value, period] for the summary grid (one per line), or [NO_VALUE]."""
    primary = series.get(ind.primary_series)
    latest = _latest(primary[0]) if primary else None
    if latest is None:
        return [NO_VALUE]
    meta = primary[1]
    return [meta.title, fmt_value(latest[0], meta.units), _when(latest, meta)]


def reading_parts(ind: reg.Indicator, reading: reg.Reading, series: dict) -> tuple[str, str, str | None]:
    """(bold state label, magnitude, interpretation or None) for the summary table. The magnitude names
    the baseline (no baseline clause while there is no value) and goes in the Latest data row; the
    label and any interpretation go in the Current reading row. The AI link has its own row."""
    label = f"**{reg.STATE_LABELS[reading.state]}**"
    value = latest_value_text(ind, series)
    magnitude = reading.magnitude or (value if value == NO_VALUE else f"{value}. {compare_sentence(ind)}")
    return label, magnitude, reading.interpretation or None


def _data_link(name: str, url: str, cites: bibliography.Citations, prefix: str) -> str:
    """A data source's name linked to its Sources entry (the URL must be in the bibliography)."""
    return f"[{name}]({cites.anchor(cites.key_for_url(url), prefix)})"


def summary_table(ind, front, reading, series, cites: bibliography.Citations) -> str:
    primary = series.get(ind.primary_series)
    through = (f"data through {fmt_period(primary[1].data_through, primary[1].frequency)}"
               if primary else "data through: not yet available (data still being collected)")
    label, magnitude, interpretation = reading_parts(ind, reading, series)
    current = "<br>".join(_cell(x) for x in (label, interpretation) if x)
    latest = _latest(primary[0]) if primary else None
    if latest is None:
        latest_data = _cell(magnitude)
    else:  # series name / value against the baseline / when KEEL last fetched it (owner, 2026-11-19)
        meta = primary[1]
        value = reading.magnitude or (f"{fmt_value(latest[0], meta.units)} ({_when(latest, meta)}). "
                                      f"{compare_sentence(ind)}")
        latest_data = "<br>".join(_cell(x) for x in (meta.title, value, f"Data last fetched {fmt_date(meta.fetched_at)}"))
    sources = "<br>".join(_data_link(_cell(s["name"]), s["url"], cites, "../") for s in front["data_sources"])
    timing_value, timing_text = (s[:1].upper() + s[1:] for s in TIMING[ind.timing].split(": ", 1))
    # Row order and names: owner review, 2026-11-19. Each row ends with a "More" link to the section that
    # expands on it (none for Grid position or Leading or lagging). Values are Markdown-safe cells.
    rows = [
        ("What it measures", _cell(reg.content_summary(front)), "#what-it-shows"),
        ("Current reading", current, "#reading-history", "History", "<br>"),
        ("Why it matters", _cell(front["warning_sign"]), "#why-this-matters-for-gradual-disempowerment"),
        ("Grid position", f"**{reg.layer_label(ind.layer)} · {ind.domain.capitalize()}**", None),
        ("AI link", f"**{ind.ai_link.capitalize()}**<br>A draft rating on four criteria, to be reviewed in Stage 2.",
         "#method"),
        ("Leading or lagging", f"**{timing_value}**<br>{timing_text}.", None),
        ("Latest data", latest_data, "#data-and-calculation"),  # owner, 2026-11-19
        ("Calculation", _cell(front["calculation"]), "#data-and-calculation"),
        ("Coverage", _cell(f"{front['coverage']} · {through}"), "#method"),
        ("Data sources", sources, "#data-and-calculation", "More", "<br>"),
    ]
    lines = ["::: {.keel-summary}", "", "|   |   |", "|:----------|:--------------------------------------------|"]
    def cell(value, target=None, text="More", sep=" "):
        return f"{value}{sep}[{text}]({target})" if target else value
    lines += [f"| {row[0]} | {cell(*row[1:])} |" for row in rows]
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
    # One "Disclosure" box holding the headline caveat (bold) and the disclosure (owner, 2026-11-19).
    parts = []
    if ind.headline_caveat:
        caveat = ind.headline_caveat.rstrip()
        parts.append(f"**{caveat if caveat[-1:] in '.!?' else caveat + '.'}**")
    if ind.disclosure:
        parts.append(ind.disclosure)
    if parts:
        out.append('::: {.callout-note title="Disclosure"}\n' + " ".join(parts) + "\n:::")
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
        left_out = [v["leftOut"]["series"]] if v.get("leftOut") else []
        for sid in v["series"] + v.get("band", []) + left_out:
            if sid in spec_series:
                continue
            entry = {"available": sid in series, "file": f"{sid}.csv", "label": SERIES_LABELS.get(sid)}
            if sid in series:
                meta = series[sid][1]
                entry.update(title=meta.title, units=meta.units, frequency=meta.frequency, breaks=meta.breaks)
            spec_series[sid] = entry
    # Only the labels for groups that appear in a plotted series (CD1's sites); other pages get none.
    used = set()
    for sid in spec_series:
        if sid in series and "group" in series[sid][0].columns:
            used.update(series[sid][0]["group"].dropna().unique())
    default = next((v["label"] for v in views if v.get("available")), views[0]["label"])
    return {
        "id": ind.id,
        "chartTitle": ind.chart_title or ind.name,
        "dataBase": "../data/",
        "views": views,
        "defaultView": default,
        "series": spec_series,
        "markers": markers,
        "groupLabels": {g: n for g, n in group_labels.items() if g in used},
        "seNote": SE_NOTE,
    }


def chart_block(spec: dict, change_files: set[str]) -> str:
    for sid, entry in spec["series"].items():
        entry["changeFile"] = f"{sid}_changes.csv" if sid in change_files else None
    payload = json.dumps(spec, ensure_ascii=False, indent=1)
    return "\n".join([
        "```{ojs}",
        "//| echo: false",
        'import { timeframeInput, loadData, themeChanges, viewInput, seriesInput, windowInput, logInput, renderChart } from "../js/charts.js"',
        f"keelSpec = ({payload})",
        "keelData = loadData(d3, keelSpec)",
        "keelTheme = themeChanges()",
        "viewof keelView = viewInput(Inputs, keelSpec)",
        "viewof keelTimeframe = timeframeInput(Inputs, keelSpec)",
        "viewof keelSeries = seriesInput(Inputs, keelSpec, keelView)",
        "viewof keelWindow = windowInput(Inputs, keelSpec, keelView)",
        "viewof keelLog = logInput(Inputs, keelSpec, keelView)",
        "renderChart(Plot, d3, keelSpec, keelData, {view: keelView, timeframe: keelTimeframe, "
        "series: keelSeries, window: keelWindow, log: keelLog, theme: keelTheme, width})",
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


def method_section(ind, series, markers, cites: bibliography.Citations, marker_keys: dict | None = None) -> str:
    lines = [f"- **Comparison and baseline.** {COMPARISON[ind.comparison].format(baseline=baseline_text(ind))}",
             "- **Threshold rule and sensitivity table.** Stage 2.",
             f"- **AI link: {ind.ai_link.capitalize()}** (draft, to be reviewed in Stage 2), judged on four criteria:"]
    for key, question in AI_LINK_QUESTIONS:
        lines.append(f"    - *{question}* {ind.ai_link_criteria.get(key, 'Not yet assessed.')}")
    grouped: dict[tuple, list[str]] = {}
    for _, meta in series.values():
        for b in meta.breaks:
            titles = grouped.setdefault((b["date"], b["note"]), [])
            if meta.title not in titles:
                titles.append(meta.title)
    if grouped:
        joined = ("The chart groups the points between breaks; compare only within a group."
                  if all(v.get("kind") == "stacked" for v in CHART_VIEWS.get(ind.id, []))
                  else "The chart does not join the line across a break.")
        lines.append(f"- **Series breaks.** {joined}")
        for (d, note), titles in sorted(grouped.items()):
            lines.append(f"    - {fmt_date(d)} ({_and(sorted(titles))}): {note}")
    else:
        lines.append("- **Series breaks.** None recorded.")
    if markers:
        lines.append("- **Chart markers.** Dated events marked on the chart without splitting the line.")
        for m in markers:
            key = (marker_keys or {}).get((m["date"], m["label"]))
            cite = f" {cites.cite(key, '../')}" if key else ""
            lines.append(f"    - {fmt_date(m['date'])}: {m['label']}{cite}")
    return "\n".join(lines)


def latest_data_bullet(ind, series) -> str:
    """Generated 'Latest data' bullet for Data and calculation (owner, 2026-11-19): the primary series'
    latest value and the one before it, from the data, so it never goes stale. A standard error is
    given when the source publishes one; a break between the two values is named."""
    primary = series.get(ind.primary_series)
    frame = primary[0] if primary else None
    if _latest(frame) is None:
        return f"- **Latest data.** {NO_VALUE}."
    meta = primary[1]
    rows = frame.sort_values("date")
    latest, prev = rows.iloc[-1], (rows.iloc[-2] if len(rows) > 1 else None)
    when = lambda r: (r["period"] if "period" in rows.columns and r["period"]
                      else fmt_period(r["date"].date().isoformat(), meta.frequency))
    text = f"- **Latest data.** {meta.title}: {fmt_value(float(latest['value']), meta.units)} ({when(latest)})"
    if "se" in rows.columns and pd.notna(latest["se"]):
        text += f", standard error {float(latest['se']):.1f} points"
    if prev is not None:
        broke = "segment" in rows.columns and prev["segment"] != latest["segment"]
        text += (f". The value before it was {fmt_value(float(prev['value']), meta.units)} ({when(prev)})"
                 + (", before a series break, so the two are not directly comparable" if broke else ""))
    return text + "."


def sources_and_dates(ind, series, cites: bibliography.Citations) -> str:
    """Generated end of 'Data and calculation': each source with its license, then when KEEL last
    fetched each series (moved from Method, owner decision 2026-11-19, so they sit together)."""
    lines = ["- **Sources and licenses.**"]
    for s in ind.sources:
        lines.append(f"    - {_data_link(s['name'], s['url'], cites, '../')}. License: {s['license']}.")
    if series:
        lines.append("- **Last fetched.**")
        for _, meta in series.values():
            lines.append(f"    - {meta.title}: fetched {fmt_date(meta.fetched_at)}, data through "
                         f"{fmt_period(meta.data_through, meta.frequency)}.")
    return "\n".join(lines)


def downloads(views, series, change_files) -> str:
    wanted = []
    for v in views:
        for sid in v["series"] + v.get("band", []) + v.get("also", []):
            if sid not in wanted:
                wanted.append(sid)
    lines = []
    for sid in wanted:
        if sid not in series:
            continue
        title = series[sid][1].title
        lines.append(f"- [{title}](../data/{sid}.csv) (CSV) · [metadata](../data/{sid}.meta.json) (JSON)")
        if sid in change_files:
            lines.append(f"- [{title}: changes over 1, 3, and 5 years, with the 2010–19 average and spread of "
                         f"same-length changes](../data/{sid}_changes.csv) (CSV)")
    if any(sid not in series for sid in wanted):
        lines.append("- Some series are still being collected and will be listed here when available.")
    return "\n".join(lines)


# ------------------------------------------------------------------ pages

def write_change_csv(frame, meta: SeriesMeta, out_dir: Path, years) -> None:
    if "segment" not in frame.columns:
        frame = assign_segments(frame, meta.breaks)
    change_bands(frame, years=tuple(years)).to_csv(out_dir / f"{meta.series_id}_changes.csv", index=False,
                                                 date_format="%Y-%m-%d", lineterminator="\n")


def indicator_page(template: str, ind, front, sections, reading, history, views, series, markers,
                   group_labels, change_files, today, cites: bibliography.Citations,
                   marker_keys: dict | None = None) -> str:
    title = f"{ind.name} ({ind.id})"
    fm = yaml.safe_dump({"title": title, "pagetitle": f"{title} · {SITE_NAME}"}, allow_unicode=True,
                        sort_keys=False, width=1000).strip()
    spec = chart_spec(ind, views, series, markers, group_labels)
    note = ""
    if ind.id in PRIMARY_PENDING_NOTE and not views[0]["available"] and spec["defaultView"] != views[0]["label"]:
        note = f"*{PRIMARY_PENDING_NOTE[ind.id]}*\n\n"
    chart = f"**{ind.chart_title or ind.name}**\n\n{note}{chart_block(spec, change_files)}"

    def section(name):
        return f"## {name}\n\n{sections[name]}"

    replacements = {
        "%%FRONT_MATTER%%": fm,
        "%%SUMMARY_TABLE%%": summary_table(ind, front, reading, series, cites),
        "%%NOTICES%%": notices(ind, views, series, today),
        "%%WHY%%": section(SECTIONS[0]),
        "%%CHART%%": chart,
        "%%READING_HISTORY%%": reading_history(history),
        "%%SHOWS%%": section(SECTIONS[1]),
        "%%DOESNT_SHOW%%": section(SECTIONS[2]),
        "%%CHANGE%%": section(SECTIONS[3]),
        "%%DATA_AND_CALCULATION%%": (section(SECTIONS[4]).rstrip() + "\n" + latest_data_bullet(ind, series)
                                     + "\n" + sources_and_dates(ind, series, cites)),
        "%%METHOD%%": method_section(ind, series, markers, cites, marker_keys) + "".join(
            f"\n\n### {name} {{#{OPTIONAL_ANCHORS[name]}}}\n\n{sections[name]}"
            for name in OPTIONAL_SECTIONS if name in sections),
        "%%CAVEATS%%": section(SECTIONS[5]),
        "%%DOWNLOADS%%": downloads(views, series, change_files),
        "%%FEEDBACK%%": FEEDBACK_LINE,
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


def _item_source(item: dict, cites: bibliography.Citations) -> str:
    """A curated item's source: a dataset's name linked to its entry, or the source named and cited."""
    key = item["source_key"]
    if cites.entries[key]["type"] == "dataset":
        return f"[{item['source_name']}]({cites.anchor(key)})"
    return f"{item['source_name']} {cites.cite(key, locator=item.get('locator'))}"


def _caveat_lines(items: list[dict], indent: str) -> list[str]:
    """Any curated item's `caveat` field, as an italic line (its own paragraph) under the item."""
    out = []
    for item in items:
        if str(item.get("caveat", "")).strip():
            out += ["", f"{indent}*{' '.join(str(item['caveat']).split())}*"]
    return out


def summary_page(indicators, grid, oversight, readings, latest_text, oversight_items, counter_header,
                 counter_items, about, cites: bibliography.Citations, intro: str) -> str:
    by_id = {i.id: i for i in indicators}
    cells = {(c.layer, c.domain): c for c in grid}
    # Opening paragraph: owner's welcome text (2026-11-19), in content/ so it can be edited directly.
    out = [intro.strip(), ""]

    about = about.strip()
    out += ["## Indicators {#indicators}", "",
            "::: {#about-the-indicators .callout-note collapse=\"true\" title=\"About the indicators\"}", about,
            ":::", "", "::::: {.keel-grid}", "::: {.keel-corner}", "&nbsp;", ":::"]
    for d in DOMAINS:
        out += [f"::: {{.keel-colhead}}\n**{d.capitalize()}**\n:::"]
    for layer in LAYERS:
        out += [_rowhead(reg.layer_label(layer), reg.LAYER_DEFINITIONS[layer])]
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
        cite.append(f"Nearest evidence: {item['label']}, {item['source_name']}, {fmt_date(item['date'])} "
                    f"{cites.cite(item['source_key'], locator=item.get('locator'))}. "
                    f"{item['metric']}: {item['value']} {item['unit']}. One study, not a time series.")
    out += [_rowhead(reg.CROSS_CUTTING_LABEL, reg.CROSS_CUTTING_DEFINITION),
            "::: {.keel-oversight}",
            f"**{oversight['row_label']}**", "", oversight["label"], "", *cite,
            *_caveat_lines(oversight_items, ""), ":::"]

    out += [":::: {.keel-counter}", "## Counter-evidence", "",
            "Signals that point away from disempowerment, held to the same standard as the indicators.", ""]
    for item in counter_items:
        value = item["value"]
        measured = "" if isinstance(value, dict) else f" {item['metric']}: {value} {item['unit']}."
        out.append(f"- **{item['label']}** ({item['domain'].capitalize()}; "
                   f"{KIND_LABELS.get(item.get('kind'), 'Item')}; dated {fmt_date(item['date'])}).{measured} "
                   f"Source: {_item_source(item, cites)}.")
        out += _caveat_lines([item], "  ")
    panel_note = str(counter_header.get("panel_note", "")).strip()
    if panel_note:
        out += ["", f"*{panel_note}*"]
    out += ["", "::: {#inclusion-criteria .callout-note collapse=\"true\" title=\"Inclusion criteria\"}",
            " ".join(str(counter_header["inclusion_criteria"]).split()), ":::", "::::", ":::::", "",
            "Earlier snapshots and superseded rules will be kept in the [Archive](archive.qmd).", ""]
    return "\n".join(out)


def _tip_id(label: str) -> str:
    return "tip-" + re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")


def _rowhead(label: str, definition: str) -> str:
    """Row header with a hover/focus tooltip: a focusable label plus a described-by tooltip span."""
    tip_id = _tip_id(label)
    return (f"::: {{.keel-rowhead}}\n[**{label}**]{{.keel-tip tabindex=\"0\" aria-describedby=\"{tip_id}\"}}"
            f"[{definition}]{{#{tip_id} .keel-tipbody role=\"tooltip\"}}\n:::")


def _and(ids: list[str]) -> str:
    if len(ids) <= 2:
        return " and ".join(ids)
    return ", ".join(ids[:-1]) + ", and " + ids[-1]


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
    cites = bibliography.Citations(bibliography.load(root / bibliography.BIB_PATH))
    marker_keys = {(str(m["date"]), m["label"]): m["source_key"]
                   for rows in chart_markers.values() for m in rows or [] if m.get("source_key")}

    for sub in ("data", "config", "indicators", "_generated"):
        _reset(site / sub)
    for f in data_dir.iterdir():
        if f.is_file() and f.suffix in (".csv", ".json"):
            shutil.copy2(f, site / "data" / f.name)
    for rel in PUBLIC_CONFIG:
        dest = site / "config" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(config / rel, dest)
    codes = [i.id for i in indicators]
    (site / "_generated" / "methodology.md").write_text(
        link_codes((root / "content" / "methodology.md").read_text(encoding="utf-8"),
                   {c: f"indicators/{c}.qmd" for c in codes}), encoding="utf-8")

    template = (site / "_indicator_template.qmd").read_text(encoding="utf-8")
    latest_text = {}
    for ind in indicators:
        views = [dict(v) for v in CHART_VIEWS.get(ind.id, [{"label": "Level", "kind": "level", "series": ind.series}])]
        drawn = [s for v in views for s in v["series"] + v.get("also", [])]
        series = _load_series(data_dir, list(dict.fromkeys(ind.series + drawn)))
        for v in views:
            v["available"] = all(s in series for s in v["series"] + v.get("band", []))
        change_files = set()
        for v in (v for v in views if v["kind"] == "change"):
            for sid in v["series"]:
                if sid in series and "group" not in series[sid][0].columns and sid not in change_files:
                    write_change_csv(series[sid][0], series[sid][1], site / "data", v["windows"])
                    change_files.add(sid)
        front, sections = split_content((root / "content" / "indicators" / f"{ind.id}.md").read_text(encoding="utf-8"))
        sections = {name: link_codes(text, {c: f"{c}.qmd" for c in codes}, ind.id) for name, text in sections.items()}
        markers = reg.markers_for(chart_markers, ind.id)
        page = indicator_page(template, ind, front, sections, reg.current_reading(readings, ind.id),
                              readings.get(ind.id, []), views, series, markers, group_labels, change_files, today,
                              cites, marker_keys)
        (site / "indicators" / f"{ind.id}.qmd").write_text(page, encoding="utf-8")
        latest_text[ind.id] = latest_value_parts(ind, series)

    summary = summary_page(indicators, grid, oversight, readings, latest_text,
                           [i for i in published(oversight_items) if i["id"] == oversight.get("citation_ref")],
                           counter_header, published(counter_items),
                           (root / "content" / "summary-about-indicators.md").read_text(encoding="utf-8"), cites,
                           (root / "content" / "summary-intro.md").read_text(encoding="utf-8"))
    (site / "_generated" / "summary.md").write_text(summary, encoding="utf-8")
    bibliography.write_sources_page(root)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    build(Path(argv[0]) if argv else Path.cwd())
    return 0


if __name__ == "__main__":
    sys.exit(main())
