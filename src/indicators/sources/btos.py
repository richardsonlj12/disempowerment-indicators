"""E2: share of US firms using AI, from the Census Business Trends and Outlook Survey (BTOS).

Keyless: public Census workbooks.
- `National.xlsx` (current): question 7 (use "in any business function"), from the 2025-11-17 collection.
- `AI Core Questions.xlsx` (archived original): question 7 (use "in producing goods or services"),
  collections 2023-09-11 to 2025-10-05.

- `Employment Size Class.xlsx`: question 7 by firm employment size class (the series `btos_ai_use_by_size`,
  new wording only, from the 2025-11-17 collection).

The first two carry the national, firm-weighted estimate and its standard error for each biweekly period
(column headers are Census sample dates, for example 202609). Dates come from the
"Collection and Reference Dates" sheet of National.xlsx; each estimate is dated by the END of its
collection fortnight.
"""

from __future__ import annotations

import io
from datetime import datetime
from urllib.parse import quote

import openpyxl
import pandas as pd

from indicators import http
from indicators.http import SourceError
from indicators.sources import utc_now_iso
from indicators.store import SeriesMeta, assign_segments

BASE = "https://www.census.gov/hfp/btos/downloads/"
CURRENT_URL = BASE + "National.xlsx"
CORE_URL = BASE + quote("AI Core Questions.xlsx")

SIZE_URL = BASE + quote("Employment Size Class.xlsx")
# Census Data Dictionary sheet of Employment Size Class.xlsx.
SIZE_CLASSES = {
    "A": "1 to 4 employees",
    "B": "5 to 9 employees",
    "C": "10 to 19 employees",
    "D": "20 to 49 employees",
    "E": "50 to 99 employees",
    "F": "100 to 249 employees",
    "G": "250 or more employees",
}

QUESTION_ID = "7"
ANSWER_YES = "1"
OLD_WORDING = "in producing goods or services"
NEW_WORDING = "in any of its business functions"

BREAKS = [
    {
        "date": "2025-11-17",
        "note": "Question changed from AI use 'in producing goods or services' to 'in any business function'",
    }
]


def _workbook(url: str) -> openpyxl.Workbook:
    response = http.get(url, expect="any")
    try:
        return openpyxl.load_workbook(io.BytesIO(response.content), read_only=True, data_only=True)
    except Exception as exc:  # not a workbook (for example an HTML error page)
        raise SourceError(f"{url}: not a readable xlsx workbook ({exc})") from exc


def _sheet(wb: openpyxl.Workbook, name: str, url: str) -> list[tuple]:
    if name not in wb.sheetnames:
        raise SourceError(f"{url}: sheet {name!r} not found; sheets are {wb.sheetnames}")
    return list(wb[name].iter_rows(values_only=True))


def _percent(cell) -> float:
    """'17.3%' -> 17.3; Census suppression marks ('.', 'S', blanks) -> NaN."""
    if cell is None:
        return float("nan")
    text = str(cell).strip().rstrip("%")
    try:
        return float(text)
    except ValueError:
        return float("nan")


def _yes_row(rows: list[tuple], url: str, wording: str) -> tuple[tuple, str]:
    """Find question 7, answer 'Yes', check the wording, and return (row, question text)."""
    header = [str(c) if c is not None else "" for c in rows[0][:4]]
    if header != ["Question ID", "Question", "Answer ID", "Answer"]:
        raise SourceError(f"{url}: unexpected header {header}")
    for row in rows[1:]:
        if str(row[0]) == QUESTION_ID and str(row[2]) == ANSWER_YES:
            question = str(row[1])
            if wording not in question or str(row[3]).strip().lower() != "yes":
                raise SourceError(f"{url}: question {QUESTION_ID} no longer reads {wording!r}: {question!r}")
            return row, question
    raise SourceError(f"{url}: question {QUESTION_ID} answer {ANSWER_YES} not found")


def _collection_ends(rows: list[tuple], url: str) -> dict[str, pd.Timestamp]:
    header = [str(c) for c in rows[0][:8]]
    if header[3] != "Smpdt" or header[5] != "Col End":
        raise SourceError(f"{url}: unexpected collection-dates header {header}")
    out = {}
    for row in rows[1:]:
        if row[3] is None or row[5] is None:
            continue
        end = row[5] if isinstance(row[5], datetime) else pd.to_datetime(row[5])
        out[str(row[3])] = pd.Timestamp(end).normalize()
    return out


def _series(est_rows, se_rows, url, wording, ends) -> tuple[dict[pd.Timestamp, tuple[float, float]], str, list[str]]:
    est, question = _yes_row(est_rows, url, wording)
    se, _ = _yes_row(se_rows, url, wording)
    est_hdr, se_hdr = est_rows[0], se_rows[0]
    if [str(h) for h in est_hdr[4:]] != [str(h) for h in se_hdr[4:]]:
        raise SourceError(f"{url}: estimate and standard-error sheets list different periods")
    out, periods = {}, []
    for period, e, s in zip(est_hdr[4:], est[4:], se[4:]):
        value = _percent(e)
        if pd.isna(value):
            continue
        key = str(period)
        if key not in ends:
            raise SourceError(f"{url}: period {key} has no collection dates")
        out[ends[key]] = (value, _percent(s))
        periods.append(key)
    if not out:
        raise SourceError(f"{url}: no estimates for question {QUESTION_ID}")
    return out, question, periods


def _size_rows(rows: list[tuple], url: str) -> dict[str, tuple]:
    """Question 7, answer Yes, per size class; the sheet's columns are Empsize, then the usual four."""
    header = [str(c) if c is not None else "" for c in rows[0][:5]]
    if header != ["Empsize", "Question ID", "Question", "Answer ID", "Answer"]:
        raise SourceError(f"{url}: unexpected header {header}")
    out = {}
    for row in rows[1:]:
        if str(row[1]) == QUESTION_ID and str(row[3]) == ANSWER_YES:
            question = str(row[2])
            if NEW_WORDING not in question or str(row[4]).strip().lower() != "yes":
                raise SourceError(f"{url}: question {QUESTION_ID} no longer reads {NEW_WORDING!r}: {question!r}")
            out[str(row[0])] = row
    if set(out) != set(SIZE_CLASSES):
        raise SourceError(f"{url}: size classes {sorted(out)} differ from {sorted(SIZE_CLASSES)}")
    return out


def _by_size(wb: openpyxl.Workbook, fetched_at: str) -> tuple[pd.DataFrame, SeriesMeta]:
    ends = _collection_ends(_sheet(wb, "Collection and Reference Dates", SIZE_URL), SIZE_URL)
    est_rows = _sheet(wb, "Response Estimates", SIZE_URL)
    se_rows = _sheet(wb, "Response Standard Errors", SIZE_URL)
    if [str(h) for h in est_rows[0][5:]] != [str(h) for h in se_rows[0][5:]]:
        raise SourceError(f"{SIZE_URL}: estimate and standard-error sheets list different periods")
    est, se = _size_rows(est_rows, SIZE_URL), _size_rows(se_rows, SIZE_URL)
    periods = [str(h) for h in est_rows[0][5:]]
    records, kept = [], set()
    for code, label in SIZE_CLASSES.items():
        for i, period in enumerate(periods):
            value = _percent(est[code][5 + i])
            if pd.isna(value):
                continue
            if period not in ends:
                raise SourceError(f"{SIZE_URL}: period {period} has no collection dates")
            records.append((label, ends[period], value, _percent(se[code][5 + i])))
            kept.add(period)
    if not records:
        raise SourceError(f"{SIZE_URL}: no estimates for question {QUESTION_ID}")
    df = pd.DataFrame(records, columns=["group", "date", "value", "se"])
    df["group"] = pd.Categorical(df["group"], categories=list(SIZE_CLASSES.values()), ordered=True)
    df = df.sort_values(["group", "date"]).reset_index(drop=True)
    df["group"] = df["group"].astype(str)
    df = df[["date", "group", "value", "se"]]
    df["value"] = df["value"].astype(float)
    df["se"] = df["se"].astype(float)
    question = str(next(iter(est.values()))[2])
    meta = SeriesMeta(
        series_id="btos_ai_use_by_size",
        indicator_id="E2",
        title="Share of US firms using AI, by firm employment size class (firm-weighted)",
        units="percent",
        frequency="biweekly",
        source_name="Census Business Trends and Outlook Survey (BTOS), by employment size class",
        source_url="https://www.census.gov/hfp/btos",
        license="US government work, public domain",
        fetched_at=fetched_at,
        data_through=df["date"].max().strftime("%Y-%m-%d"),
        max_lag_days=45,
        role="context",
        notes=(
            "Firm-weighted share answering Yes (question 7) within each employment size class, with Census "
            "standard errors (column se, percentage points), from Employment Size Class.xlsx (sheets Response "
            "Estimates and Response Standard Errors). Size classes: " + "; ".join(SIZE_CLASSES.values()) + ". "
            "Each estimate is dated by the end of its two-week collection period. The file holds only the "
            f"new-wording series, from the 2025-11-17 collection (sample dates {min(kept)} to {max(kept)}). Question: {question} "
            "Census published no estimate for sample dates 202521 to 202523. The workbook prints the SI label "
            "for every period; the relabel from 'AI' to 'Super Intelligence or SI' began with the collection "
            "fielded from 2026-10-19 (shown as a chart marker, not a break)."
        ),
    )
    return df, meta


def fetch() -> list[tuple[pd.DataFrame, SeriesMeta]]:
    fetched_at = utc_now_iso()
    current = _workbook(CURRENT_URL)
    core = _workbook(CORE_URL)
    ends = _collection_ends(_sheet(current, "Collection and Reference Dates", CURRENT_URL), CURRENT_URL)

    new, new_q, new_periods = _series(
        _sheet(current, "Response Estimates", CURRENT_URL),
        _sheet(current, "Response Standard Errors", CURRENT_URL),
        CURRENT_URL,
        NEW_WORDING,
        ends,
    )
    old, old_q, old_periods = _series(
        _sheet(core, "National Estimates", CORE_URL),
        _sheet(core, "National SE", CORE_URL),
        CORE_URL,
        OLD_WORDING,
        ends,
    )
    if set(new) & set(old):
        raise SourceError("BTOS: the old and new AI question overlap in time; the break date needs review")

    merged = {**old, **new}
    df = pd.DataFrame(
        {
            "date": list(merged),
            "value": [v for v, _ in merged.values()],
            "se": [s for _, s in merged.values()],
        }
    ).sort_values("date")
    df["value"] = df["value"].astype(float)
    df["se"] = df["se"].astype(float)
    df = assign_segments(df.reset_index(drop=True), BREAKS)

    meta = SeriesMeta(
        series_id="btos_ai_use",
        indicator_id="E2",
        title="Share of US firms using AI (firm-weighted)",
        units="percent",
        frequency="biweekly",
        source_name="Census Business Trends and Outlook Survey (BTOS), national",
        source_url="https://www.census.gov/hfp/btos",
        license="US government work, public domain",
        fetched_at=fetched_at,
        data_through=df["date"].max().strftime("%Y-%m-%d"),
        max_lag_days=45,
        breaks=list(BREAKS),
        role="primary",
        notes=(
            "National, all-sector, firm-weighted share answering Yes (question 7), with Census standard errors "
            "(column se, percentage points). Each estimate is dated by the end of its two-week collection "
            "period (Census sample date in parentheses). "
            f"Periods {old_periods[-1]} to {old_periods[0]} (AI Core Questions.xlsx): {old_q} "
            f"Periods {new_periods[-1]} to {new_periods[0]} (National.xlsx): {new_q} "
            "Census published no estimate for sample dates 202521 to 202523 (collections 2025-10-06 to "
            "2025-11-16), so the series has a gap before the wording change. The two wordings are not "
            "directly comparable; the break date is the first collection of the new wording. The workbook prints "
            "the question with the Super Intelligence (SI) label for every period; Census's wording notice of "
            "3 December 2025 shows the question as 'Artificial Intelligence (AI) ... in any of its business "
            "functions' from 2025-11-17, and the Content V5 instrument (fielded from 2026-10-19) is the first "
            "to use 'Super Intelligence or SI (formerly referred to as Artificial Intelligence or AI)'. That "
            "relabel is shown as a chart marker, not a break."
        ),
    )
    size_wb = _workbook(SIZE_URL)
    return [(df, meta), _by_size(size_wb, fetched_at)]
