"""E2: share of US firms using AI, from the Census Business Trends and Outlook Survey (BTOS).

Keyless: two public Census workbooks.
- `National.xlsx` (current): question 7 (use "in any business function"), from the 2025-11-17 collection.
- `AI Core Questions.xlsx` (archived original): question 7 (use "in producing goods or services"),
  collections 2023-09-11 to 2025-10-05.

Both carry the national, firm-weighted estimate and its standard error for each biweekly period
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
            "directly comparable; the break date is the first collection of the new wording."
        ),
    )
    return [(df, meta)]
