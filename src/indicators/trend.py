"""Trend and year-over-year comparison calculations."""

import numpy as np
import pandas as pd


def pre_ai_trend(df, start="2010-01-01", end="2019-12-31"):
    """Add `trend` (OLS line fitted on the window, extended over all dates) and
    `deviation`. Chart view only; this is not the threshold rule."""
    out = df.copy()
    # Time in calendar months (fractional within a month), so monthly series
    # step by exactly 1 and irregular gaps are still spaced correctly.
    d = out["date"]
    t = (d.dt.year * 12 + d.dt.month + (d.dt.day - 1) / d.dt.days_in_month).to_numpy(dtype=float)
    in_window = (out["date"] >= pd.Timestamp(start)) & (out["date"] <= pd.Timestamp(end))
    mask = (in_window & out["value"].notna()).to_numpy()
    if mask.sum() < 2:
        out["trend"] = np.nan
    else:
        slope, intercept = np.polyfit(t[mask], out["value"].to_numpy(dtype=float)[mask], 1)
        out["trend"] = slope * t + intercept
    out["deviation"] = out["value"] - out["trend"]
    return out


def yoy_change(df, periods_per_year):
    """Percent change versus the same period one year earlier (index kept)."""
    return df["value"].pct_change(periods=periods_per_year, fill_method=None) * 100


def _yoy_by_date(df, periods_per_year):
    df = df.sort_values("date")
    return pd.Series(yoy_change(df, periods_per_year).to_numpy(), index=df["date"].to_numpy())


def relative_yoy(treated, comparison, periods_per_year):
    """Treated YoY % minus the mean comparison YoY % (per group, then across
    groups), for dates where both are defined. Columns: date, value."""
    t_yoy = _yoy_by_date(treated, periods_per_year)
    if "group" in comparison.columns:
        parts = [_yoy_by_date(g, periods_per_year) for _, g in comparison.groupby("group")]
    else:
        parts = [_yoy_by_date(comparison, periods_per_year)]
    c_mean = pd.concat(parts, axis=1).mean(axis=1, skipna=True)
    joined = pd.concat([t_yoy.rename("t"), c_mean.rename("c")], axis=1).dropna()
    result = pd.DataFrame({"date": joined.index, "value": (joined["t"] - joined["c"]).to_numpy()})
    return result.sort_values("date").reset_index(drop=True)
