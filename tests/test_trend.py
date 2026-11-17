import pandas as pd
import pytest

from indicators.trend import pre_ai_trend, relative_yoy, yoy_change


def monthly(values, start="2024-01-01", **extra):
    dates = pd.date_range(start, periods=len(values), freq="MS")
    return pd.DataFrame({"date": dates, "value": values, **extra})


def test_pre_ai_trend_exact_on_linear_series():
    df = monthly([2 * t + 1 for t in range(120)], start="2010-01-01")
    out = pre_ai_trend(df)
    assert out["deviation"].abs().max() < 1e-6


def test_pre_ai_trend_extends_over_all_dates():
    df = monthly([2.0 * t + 1 for t in range(150)], start="2010-01-01")
    out = pre_ai_trend(df)
    assert len(out) == 150
    assert out["deviation"].abs().max() < 1e-6


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
