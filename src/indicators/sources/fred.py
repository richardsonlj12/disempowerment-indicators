"""ED1 and GD1 US series.

Keyless sources only:
- FRED `fredgraph.csv` for NIPA series (profit share, labor-based tax share).
- BLS public API v1 for the labor share *level in percent* (FRED carries only the index).
"""

from __future__ import annotations

import io
from datetime import date
from pathlib import Path

import pandas as pd
import requests

from indicators import http
from indicators.http import SourceError
from indicators.sources import utc_now_iso
from indicators.store import SeriesMeta

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv"
BLS_API = "https://api.bls.gov/publicAPI/v1/timeseries/data/"

BLS_LABOR_SHARE = "PRS85006174"  # Nonfarm business labor share, percent of current-dollar output
BLS_FIRST_YEAR = 1947
# BLS Productivity and Costs and BEA NIPA publish a quarter about 1 to 2 months after it ends:
# next quarter (about 90 days) + about 60 days to publication + 30 days slack, from quarter end.
QUARTERLY_LAG_DAYS = 180
BLS_CHUNK_YEARS = 10  # API v1 returns at most 10 years per request
BLS_MIN_FULL_QUARTERS = 300  # 1947Q1 onward is ~315+; fewer means a truncated fetch

PROFIT_NUMERATOR = "CPATAX"
PROFIT_DENOMINATOR = "GDP"
PERSONAL_TAXES = "W055RC1Q027SBEA"
CONTRIBUTIONS = "W782RC1Q027SBEA"
TAX_RECEIPTS = "W054RC1Q027SBEA"

PUBLIC_DOMAIN = "US government work, public domain"


def _fred_series(series_id: str) -> pd.Series:
    response = http.get(FRED_CSV, params={"id": series_id}, expect="csv")
    frame = pd.read_csv(io.StringIO(response.text))
    if "observation_date" not in frame.columns or series_id not in frame.columns:
        raise SourceError(f"FRED {series_id}: unexpected columns {list(frame.columns)}")
    values = pd.to_numeric(frame[series_id], errors="coerce")  # FRED marks gaps with "."
    out = pd.Series(values.to_numpy(dtype=float), index=pd.to_datetime(frame["observation_date"]), name=series_id)
    return out.dropna().sort_index()


def _bls_post(start: int, end: int) -> dict:
    """The v1 API honours startyear/endyear only in a POST body; on GET it silently
    returns its default (latest ~3 years) for every request."""
    body = {"seriesid": [BLS_LABOR_SHARE], "startyear": str(start), "endyear": str(end)}
    for attempt in range(http.RETRIES + 1):
        response = requests.post(BLS_API, json=body, headers={"User-Agent": http.USER_AGENT}, timeout=60)
        if (response.status_code == 429 or response.status_code >= 500) and attempt < http.RETRIES:
            http._sleep(http.BACKOFF_SECONDS * (2**attempt))
            continue
        break
    if response.status_code >= 400:
        raise SourceError(f"BLS {BLS_LABOR_SHARE}: HTTP {response.status_code}: {response.text[:200]}")
    try:
        return response.json()
    except ValueError as exc:
        raise SourceError(f"BLS {BLS_LABOR_SHARE}: response was not JSON") from exc


def _bls_labor_share(starts: list[int], min_quarters: int = 0) -> pd.Series:
    rows: dict[pd.Timestamp, float] = {}
    seen_year_sets: list[frozenset[int]] = []
    for start in starts:
        end = min(start + BLS_CHUNK_YEARS - 1, date.today().year)
        payload = _bls_post(start, end)
        if payload.get("status") != "REQUEST_SUCCEEDED":
            raise SourceError(f"BLS {BLS_LABOR_SHARE}: {payload.get('status')} {payload.get('message')}")
        years: set[int] = set()
        for series in payload["Results"]["series"]:
            for obs in series["data"]:
                period = obs["period"]
                if not (period.startswith("Q") and period != "Q05"):  # Q05 is the annual average
                    continue
                year = int(obs["year"])
                years.add(year)
                month = (int(period[1:]) - 1) * 3 + 1
                rows[pd.Timestamp(year=year, month=month, day=1)] = float(obs["value"])
        if years and not years <= set(range(start, end + 1)):
            raise SourceError(
                f"BLS {BLS_LABOR_SHARE}: requested {start}-{end} but got {min(years)}-{max(years)}; "
                f"the year range was ignored (message: {payload.get('message')})"
            )
        if years and frozenset(years) in seen_year_sets:
            raise SourceError(f"BLS {BLS_LABOR_SHARE}: identical year ranges returned for different chunks")
        seen_year_sets.append(frozenset(years))
    if not rows:
        raise SourceError(f"BLS {BLS_LABOR_SHARE}: no observations returned")
    if len(rows) < min_quarters:
        raise SourceError(
            f"BLS {BLS_LABOR_SHARE}: full history returned only {len(rows)} quarters (< {min_quarters}); "
            "the year range may have been truncated"
        )
    return pd.Series(rows, dtype=float).sort_index()


def _frame(series: pd.Series) -> pd.DataFrame:
    out = series.dropna().rename("value").rename_axis("date").reset_index()
    out["value"] = out["value"].astype(float)
    return out


def _meta(df: pd.DataFrame, fetched_at: str, **fields) -> SeriesMeta:
    return SeriesMeta(
        fetched_at=fetched_at,
        data_through=df["date"].max().strftime("%Y-%m-%d"),
        license=PUBLIC_DOMAIN,
        frequency="quarterly",
        units="percent",
        **fields,
    )


def _labor_share_history(data_dir: Path, full: bool) -> pd.Series:
    """BLS API v1 allows 25 requests/day without a key, and full history needs 8.

    With a committed CSV, fetch only the latest 10-year chunk and merge it over the
    committed history (fetched quarters win, so BLS revisions are picked up).
    """
    this_year = date.today().year
    existing_path = Path(data_dir) / "labor_share_nfb.csv"
    if full or not existing_path.exists():
        return _bls_labor_share(
            list(range(BLS_FIRST_YEAR, this_year + 1, BLS_CHUNK_YEARS)), min_quarters=BLS_MIN_FULL_QUARTERS
        )
    old = pd.read_csv(existing_path, parse_dates=["date"])
    old_series = pd.Series(old["value"].to_numpy(dtype=float), index=pd.DatetimeIndex(old["date"]))
    recent = _bls_labor_share([this_year - BLS_CHUNK_YEARS + 1])
    return pd.concat([old_series[~old_series.index.isin(recent.index)], recent]).sort_index()


def fetch(data_dir: Path | str = "data", full: bool = False) -> list[tuple[pd.DataFrame, SeriesMeta]]:
    fetched_at = utc_now_iso()

    labor = _frame(_labor_share_history(Path(data_dir), full))
    labor_meta = _meta(
        labor,
        fetched_at,
        series_id="labor_share_nfb",
        indicator_id="ED1",
        title="Labor share of income, nonfarm business sector",
        source_name="BLS Productivity and Costs",
        source_url="https://www.bls.gov/productivity/home.htm",
        max_lag_days=QUARTERLY_LAG_DAYS,
        role="primary",
        notes=(
            f"BLS series {BLS_LABOR_SHARE} (labor share, percent of current-dollar output, nonfarm "
            "business sector, seasonally adjusted), read through the keyless BLS public API v1. "
            "FRED carries only the index form (PRS85006173), so the percent level comes from BLS. "
            "BLS revises recent quarters."
        ),
    )

    profit_value = _fred_series(PROFIT_NUMERATOR) / _fred_series(PROFIT_DENOMINATOR) * 100
    profit = _frame(profit_value)
    profit_meta = _meta(
        profit,
        fetched_at,
        series_id="profit_share",
        indicator_id="ED1",
        title="Corporate profits after tax as a share of GDP",
        source_name="BEA National Income and Product Accounts, via FRED",
        source_url="https://fred.stlouisfed.org/series/CPATAX",
        max_lag_days=QUARTERLY_LAG_DAYS,
        role="context",
        notes=(
            f"Formula: {PROFIT_NUMERATOR} (corporate profits after tax with inventory valuation and "
            f"capital consumption adjustments) / {PROFIT_DENOMINATOR} (gross domestic product) x 100. "
            "Both seasonally adjusted annual rates."
        ),
    )

    personal = _fred_series(PERSONAL_TAXES)
    contributions = _fred_series(CONTRIBUTIONS)
    receipts = _fred_series(TAX_RECEIPTS)
    both = pd.concat({"p": personal, "c": contributions, "r": receipts}, axis=1).dropna()
    tax = _frame((both["p"] + both["c"]) / (both["r"] + both["c"]) * 100)
    tax_meta = _meta(
        tax,
        fetched_at,
        series_id="us_labor_tax_share",
        indicator_id="GD1",
        title="US labor-based share of tax revenue",
        source_name="BEA National Income and Product Accounts, via FRED",
        source_url="https://fred.stlouisfed.org/series/" + PERSONAL_TAXES,
        max_lag_days=QUARTERLY_LAG_DAYS,
        role="primary",
        notes=(
            f"Formula: ({PERSONAL_TAXES} personal current taxes + {CONTRIBUTIONS} contributions for "
            f"government social insurance) / ({TAX_RECEIPTS} government current tax receipts + "
            f"{CONTRIBUTIONS}) x 100. All levels, all governments (federal, state and local), "
            "seasonally adjusted annual rates. Quarters where any input is unpublished are omitted."
        ),
    )

    return [(labor, labor_meta), (profit, profit_meta), (tax, tax_meta)]
