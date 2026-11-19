"""Change-distribution, year-over-year and relative-activity calculations."""

import numpy as np
import pandas as pd


def change_bands(df, years=(1, 3, 5), start="2010-01-01", end="2019-12-31"):
    """KEEL's method for long-running series (owner decision, 2026-11-19): the change over each
    window, and the spread of same-length changes in the baseline period.

    For each window of `years` years, `change` is the value minus the value exactly that many years
    earlier (matched by date, so gaps simply drop a change), skipped where a series break (`segment`)
    lies between the two. The baseline is every such change with BOTH ends inside [start, end]:
    `base_mean`, `base_sd` (sample standard deviation) and `base_n` repeat on each row of the window
    (NaN mean and sd when fewer than two baseline changes exist). Chart view and candidate-rule input
    only; the window and the bands that count are fixed in Stage 2.

    Columns: date, window_years, change, segment, base_mean, base_sd, base_n."""
    d = df.sort_values("date")
    value = dict(zip(d["date"], d["value"].astype(float)))
    segment = dict(zip(d["date"], d["segment"] if "segment" in d.columns else [0] * len(d)))
    lo, hi = pd.Timestamp(start), pd.Timestamp(end)
    frames = []
    for y in years:
        rows = []
        for date in d["date"]:
            then = date - pd.DateOffset(years=y)
            if then in value and segment[then] == segment[date]:
                rows.append({"date": date, "window_years": y, "change": value[date] - value[then],
                             "segment": int(segment[date]), "_base": then >= lo and date <= hi})
        w = pd.DataFrame(rows, columns=["date", "window_years", "change", "segment", "_base"])
        base = w.loc[w["_base"].astype(bool), "change"]
        w["base_n"] = len(base)
        w["base_mean"] = base.mean() if len(base) >= 2 else np.nan
        w["base_sd"] = base.std(ddof=1) if len(base) >= 2 else np.nan
        frames.append(w.drop(columns="_base"))
    out = pd.concat(frames, ignore_index=True)
    return out[["date", "window_years", "change", "segment", "base_mean", "base_sd", "base_n"]]


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


# ---------------------------------------------------------------- relative-activity index (CD1)
#
# Stack Overflow (the treated site) against a set of comparison sites, all on 12-month rolling
# totals so seasonality and day-count noise drop out. R is a log ratio, so a constant gap between
# the sites is a constant R; the index and change views are re-expressions of R, nothing more.
# This is a relative-activity measure, not a causal estimate of AI's effect.


def _month_number(df):
    return (df["date"].dt.year * 12 + df["date"].dt.month - 1).to_numpy()


def _rolling_one(df, window):
    full = pd.Series(df["value"].to_numpy(dtype=float), index=_month_number(df))
    full = full.reindex(range(full.index.min(), full.index.max() + 1))  # a gap leaves NaN
    totals = full.rolling(window, min_periods=window).sum().dropna()
    dates = pd.to_datetime([f"{i // 12:04d}-{i % 12 + 1:02d}-01" for i in totals.index])
    return pd.DataFrame({"date": dates, "value": totals.to_numpy(dtype=float)})


def rolling_total(df, window=12):
    """Sum of the last `window` months, labelled by the window-end month, only where all
    `window` consecutive months exist. A frame with a `group` column is done per group."""
    if "group" not in df.columns:
        return _rolling_one(df.sort_values("date"), window)
    parts = []
    for name, sub in df.groupby("group", sort=False):
        part = _rolling_one(sub.sort_values("date"), window)
        part.insert(1, "group", name)
        parts.append(part)
    return pd.concat(parts, ignore_index=True)


def relative_log_level(treated_totals, comparison_totals_grouped):
    """R(m) = ln T_treated(m) - mean over comparison groups of ln T_group(m), only for months
    where the treated series and EVERY comparison group have a value. Columns: date, value."""
    t = treated_totals.set_index("date")["value"].astype(float)
    wide = comparison_totals_grouped.pivot(index="date", columns="group", values="value").astype(float)
    joined = wide.join(t.rename("__treated__"), how="inner").dropna()
    r = np.log(joined["__treated__"]) - np.log(joined.drop(columns="__treated__")).mean(axis=1)
    return pd.DataFrame({"date": r.index, "value": r.to_numpy(dtype=float)}).sort_values("date").reset_index(drop=True)


def index_to_base_year(R, year=2019):
    """I(m) = 100 x exp(R(m) - mean of R over the calendar year). Needs all 12 months of `year`."""
    base = R[R["date"].dt.year == year]
    if len(base) != 12:
        raise ValueError(f"base year {year} needs 12 monthly values of R, found {len(base)}")
    out = R.copy()
    out["value"] = 100 * np.exp(R["value"] - base["value"].mean())
    return out


def change_since(R, month="2022-11-01"):
    """Percent change D(m) = 100 x (exp(R(m) - R(month)) - 1) for months from `month` on."""
    ref = R[R["date"] == pd.Timestamp(month)]
    if ref.empty:
        raise ValueError(f"R has no value for the reference month {month}")
    out = R[R["date"] >= pd.Timestamp(month)].copy()
    out["value"] = 100 * (np.exp(out["value"] - ref["value"].iloc[0]) - 1)
    return out.reset_index(drop=True)


def leave_one_out_band(treated_totals, comparison_totals_grouped, year=2019):
    """For each comparison group j, the index using only the other groups; returns
    (min_df, max_df) across the leave-one-out indices, on the months of the full index
    (all groups present). The full index is the geometric mean of these, so it lies inside."""
    full = relative_log_level(treated_totals, comparison_totals_grouped)
    frames = []
    for g in comparison_totals_grouped["group"].unique():
        rest = comparison_totals_grouped[comparison_totals_grouped["group"] != g]
        idx = index_to_base_year(relative_log_level(treated_totals, rest), year)
        frames.append(idx.set_index("date")["value"].reindex(full["date"]))
    wide = pd.concat(frames, axis=1)
    lo = pd.DataFrame({"date": wide.index, "value": wide.min(axis=1).to_numpy()})
    hi = pd.DataFrame({"date": wide.index, "value": wide.max(axis=1).to_numpy()})
    return lo, hi
