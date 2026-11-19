import pandas as pd
import pytest

import numpy as np

from indicators.trend import (
    change_bands, change_since, index_to_base_year, leave_one_out_band, relative_log_level,
    relative_yoy, rolling_total, yoy_change,
)


def monthly(values, start="2024-01-01", **extra):
    dates = pd.date_range(start, periods=len(values), freq="MS")
    return pd.DataFrame({"date": dates, "value": values, **extra})


def quarterly(values, start="2008-01-01", **extra):
    dates = pd.date_range(start, periods=len(values), freq="QS")
    return pd.DataFrame({"date": dates, "value": values, **extra})


def test_change_bands_changes_and_baseline_spread():
    # Quarterly, rising 1 point a quarter: every 1-year change is +4, every 3-year change +12.
    df = quarterly([float(t) for t in range(80)])  # 2008 Q1 .. 2027 Q4
    out = change_bands(df, years=(1, 3))
    one = out[out["window_years"] == 1]
    assert set(out.columns) == {"date", "window_years", "change", "segment", "base_mean", "base_sd", "base_n"}
    assert (one["change"] == 4.0).all() and one["date"].min() == pd.Timestamp("2009-01-01")
    # Baseline: changes with BOTH ends in 2010-2019. 1-year: ends 2011 Q1 .. 2019 Q4 = 36 changes.
    assert one["base_n"].iloc[0] == 36 and one["base_mean"].iloc[0] == 4.0 and one["base_sd"].iloc[0] == 0.0
    three = out[out["window_years"] == 3]
    assert three["base_n"].iloc[0] == 28 and (three["change"] == 12.0).all()


def test_change_bands_baseline_sd_matches_hand_calculation():
    # Annual series 2010..2019 with 1-year changes +1, -1 alternating: mean 1/9, sample sd known.
    values = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    df = pd.DataFrame({"date": pd.date_range("2010-01-01", periods=10, freq="YS"), "value": [float(v) for v in values]})
    one = change_bands(df, years=(1,))
    changes = np.diff(values)
    assert one["base_n"].iloc[0] == 9
    assert one["base_mean"].iloc[0] == pytest.approx(changes.mean())
    assert one["base_sd"].iloc[0] == pytest.approx(changes.std(ddof=1))


def test_change_bands_skip_changes_across_a_break_and_missing_dates():
    df = quarterly([float(t) for t in range(80)], segment=[0] * 60 + [1] * 20)
    df = df[df["date"] != pd.Timestamp("2012-01-01")]  # a gap: no change ends or starts there
    one = change_bands(df, years=(1,))
    dates = set(one["date"])
    assert pd.Timestamp("2012-01-01") not in dates and pd.Timestamp("2013-01-01") not in dates
    # The break is at row 60 = 2023 Q1: changes ending 2023 Q1 .. 2023 Q4 start before it.
    assert not any(pd.Timestamp(f"2023-{m:02d}-01") in dates for m in (1, 4, 7, 10))
    assert pd.Timestamp("2024-01-01") in dates
    assert set(one["segment"]) == {0, 1}


def test_change_bands_without_baseline_data_gives_no_band():
    df = quarterly([float(t) for t in range(12)], start="2022-01-01")
    one = change_bands(df, years=(1,))
    assert one["base_n"].eq(0).all() and one["base_mean"].isna().all() and one["base_sd"].isna().all()


def test_yoy_change_monthly():
    df = monthly([100.0] * 12 + [80.0])
    out = yoy_change(df, 12)
    assert out.iloc[12] == pytest.approx(-20.0)
    assert out.iloc[:12].isna().all()


def test_relative_yoy():
    treated = monthly([100.0] * 12 + [70.0])
    comparison = pd.concat(
        [
            monthly([100.0] * 12 + [80.0], group="a"),
            monthly([100.0] * 12 + [100.0], group="b"),
        ]
    )
    # comparison mean YoY = (-20 + 0) / 2 = -10 ; treated = -30
    out = relative_yoy(treated, comparison, 12)
    assert list(out.columns) == ["date", "value"]
    assert len(out) == 1
    assert out["value"].iloc[0] == pytest.approx(-20.0)


# ---------------------------------------------------------------- relative-activity index


def test_rolling_total_sums_twelve_months_labelled_by_window_end():
    df = monthly([float(i) for i in range(1, 15)])  # 1..14 from 2024-01
    out = rolling_total(df, 12)
    assert list(out.columns) == ["date", "value"]
    assert out["date"].iloc[0] == pd.Timestamp("2024-12-01")  # window-end month
    assert out["value"].tolist() == [78.0, 90.0, 102.0]  # 1..12, 2..13, 3..14


def test_rolling_total_needs_twelve_complete_months():
    df = monthly([1.0] * 20)
    df = df[df["date"] != pd.Timestamp("2024-06-01")]  # a missing month
    out = rolling_total(df, 12)
    # Only windows that avoid the gap exist: Jul 2024 - Jun 2025, and the two after it.
    assert out["date"].tolist() == list(pd.to_datetime(["2025-06-01", "2025-07-01", "2025-08-01"]))
    assert rolling_total(monthly([1.0] * 11), 12).empty


def test_rolling_total_per_group():
    df = pd.concat([monthly([1.0] * 12, group="a"), monthly([2.0] * 13, group="b")], ignore_index=True)
    out = rolling_total(df, 12)
    assert list(out.columns) == ["date", "group", "value"]
    assert out[out["group"] == "a"]["value"].tolist() == [12.0]
    assert out[out["group"] == "b"]["value"].tolist() == [24.0, 24.0]


def _totals(treated_by_month, site_levels, start="2019-01-01"):
    n = len(treated_by_month)
    treated = monthly([float(v) for v in treated_by_month], start=start)
    comp = pd.concat(
        [monthly([float(v) for v in levels], start=start, group=name) for name, levels in site_levels.items()],
        ignore_index=True,
    )
    return treated, comp


def test_constant_ratio_gives_index_100():
    n = 24
    treated, comp = _totals([1000] * n, {s: [100] * n for s in "abcd"})
    R = relative_log_level(treated, comp)
    assert R["value"].tolist() == pytest.approx([np.log(10)] * n)
    idx = index_to_base_year(R, 2019)
    assert idx["value"].tolist() == pytest.approx([100.0] * n)


def test_treated_halves_while_comparison_flat_gives_50():
    n = 24
    treated, comp = _totals([2400] * 12 + [1200] * 12, {s: [1200] * n for s in "abcd"})
    R = relative_log_level(treated, comp)
    idx = index_to_base_year(R, 2019)
    assert idx["value"].tolist() == pytest.approx([100.0] * 12 + [50.0] * 12)
    ref = change_since(R, "2020-01-01")  # from the first halved month: 0 then flat
    assert ref["value"].tolist() == pytest.approx([0.0] * 12)
    since = change_since(R, "2019-12-01")
    assert since["value"].iloc[0] == pytest.approx(0.0)
    assert since["value"].iloc[1] == pytest.approx(-50.0)  # 100 x (exp(ln 1 - ln 2) - 1)


def test_relative_log_level_requires_every_comparison_group():
    treated = monthly([100.0] * 4)
    comp = pd.concat([monthly([100.0] * 4, group="a"), monthly([100.0] * 3, group="b")], ignore_index=True)
    R = relative_log_level(treated, comp)
    assert len(R) == 3 and R["date"].max() == pd.Timestamp("2024-03-01")


def test_index_to_base_year_needs_the_whole_base_year():
    R = pd.DataFrame({"date": pd.date_range("2019-06-01", periods=12, freq="MS"), "value": [0.0] * 12})
    with pytest.raises(ValueError, match="2019"):
        index_to_base_year(R, 2019)


def test_change_since_needs_reference_month():
    R = pd.DataFrame({"date": pd.date_range("2023-01-01", periods=3, freq="MS"), "value": [0.0] * 3})
    with pytest.raises(ValueError, match="2022-11-01"):
        change_since(R, "2022-11-01")


def test_leave_one_out_band_hand_computed_and_brackets_index():
    n = 24
    # Stack Overflow and sites a, b, c flat; site d doubles from 2020 on.
    levels = {"a": [1000] * n, "b": [1000] * n, "c": [1000] * n, "d": [1000] * 12 + [2000] * 12}
    treated, comp = _totals([1000] * n, levels)
    R = relative_log_level(treated, comp)
    full = index_to_base_year(R, 2019)
    # After the doubling: mean ln over four sites = ln1000 + ln2/4, so R = -ln2/4, index 100 x 2^(-1/4).
    assert full["value"].iloc[-1] == pytest.approx(100 * 2 ** -0.25)
    lo, hi = leave_one_out_band(treated, comp, 2019)
    assert lo["date"].tolist() == full["date"].tolist()
    # Leaving out d gives 100; leaving out a, b or c gives 100 x 2^(-1/3).
    assert hi["value"].iloc[-1] == pytest.approx(100.0)
    assert lo["value"].iloc[-1] == pytest.approx(100 * 2 ** (-1 / 3))
    assert (lo["value"] <= full["value"] + 1e-9).all() and (full["value"] <= hi["value"] + 1e-9).all()
