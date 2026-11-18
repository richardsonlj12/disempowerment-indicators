"""G1 comparison series: OECD Revenue Statistics via the keyless SDMX endpoint.

Labor-based share = (personal income tax 1100 + social security contributions 2000)
as a percentage of total tax revenue, general government, annual.
"""

from __future__ import annotations

import io

import pandas as pd

from indicators import http
from indicators.http import SourceError
from indicators.sources import utc_now_iso
from indicators.store import SeriesMeta

DATAFLOW = "OECD.CTP.TPS,DSD_REV_COMP_OECD@DF_RSOECD,2.0"
# Key order: REF_AREA.MEASURE.SECTOR.STANDARD_REVENUE.CTRY_SPECIFIC_REVENUE.UNIT_MEASURE.FREQ
KEY = "USA+OECD_REP.TAX_REV.S13.T_1100+T_2000._T.PT_OTR_SECTOR.A"
URL = f"https://sdmx.oecd.org/public/rest/data/{DATAFLOW}/{KEY}"
START_YEAR = "1965"

PIT, SSC = "T_1100", "T_2000"
# Revenue Statistics appears each December. The United States is published for year t in December
# t+1, the OECD average for year t in December t+2. Lag from the end of the latest year to the next
# release that should add a year, plus about 45 days slack.
LAG_DAYS = {"oecd_labor_tax_share_usa": 790, "oecd_labor_tax_share_avg": 1140}

SERIES = (
    ("USA", "oecd_labor_tax_share_usa", "United States"),
    ("OECD_REP", "oecd_labor_tax_share_avg", "OECD average"),
)


# Ruling R15: the DF_RSOECD dataflow metadata carries no licence or restriction annotation
# (checked 2026-11-18), so the series are published with this attribution.
ATTRIBUTION = (
    "Source: OECD, Revenue Statistics 2025. "
    "OECD terms and conditions: https://www.oecd.org/en/about/terms-conditions.html"
)


def _labor_share(rows: pd.DataFrame, area: str) -> pd.DataFrame:
    sub = rows[rows["REF_AREA"] == area]
    wide = sub.pivot_table(index="TIME_PERIOD", columns="STANDARD_REVENUE", values="OBS_VALUE", aggfunc="first")
    if PIT not in wide.columns or SSC not in wide.columns:
        raise SourceError(f"OECD {area}: missing PIT or SSC rows")
    wide = wide[[PIT, SSC]].dropna()  # a year missing either component is dropped, not under-counted
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(wide.index.astype(int).astype(str) + "-01-01"),
            "value": (wide[PIT] + wide[SSC]).to_numpy(dtype=float),
        }
    )
    return out.sort_values("date").reset_index(drop=True)


def fetch() -> list[tuple[pd.DataFrame, SeriesMeta]]:
    response = http.get(URL, params={"format": "csvfilewithlabels", "startPeriod": START_YEAR}, expect="csv")
    rows = pd.read_csv(io.StringIO(response.text))
    needed = {"REF_AREA", "STANDARD_REVENUE", "TIME_PERIOD", "OBS_VALUE"}
    if not needed <= set(rows.columns):
        raise SourceError(f"OECD: unexpected columns {list(rows.columns)}")
    rows["OBS_VALUE"] = pd.to_numeric(rows["OBS_VALUE"], errors="coerce")

    fetched_at = utc_now_iso()
    out = []
    for area, series_id, label in SERIES:
        df = _labor_share(rows, area)
        meta = SeriesMeta(
            series_id=series_id,
            indicator_id="G1",
            title=f"Labor-based share of tax revenue, {label}",
            units="percent",
            frequency="annual",
            source_name="OECD Revenue Statistics",
            source_url="https://data-explorer.oecd.org/?df[ds]=DisseminateFinalDMZ&df[id]=DSD_REV_COMP_OECD%40DF_RSOECD&df[ag]=OECD.CTP.TPS",
            license=ATTRIBUTION,
            fetched_at=fetched_at,
            data_through=df["date"].max().strftime("%Y-%m-%d"),
            max_lag_days=LAG_DAYS[series_id],
            role="context",
            notes=(
                f"Formula: (revenue category {PIT[2:]} taxes on income of individuals + {SSC[2:]} social "
                "security contributions) as a percentage of total tax revenue, general government, from "
                f"dataflow {DATAFLOW}. The OECD average is the published OECD_REP aggregate "
                "(each category's percentage of total tax revenue is as published, not recomputed)."
            ),
        )
        out.append((df, meta))
    return out
