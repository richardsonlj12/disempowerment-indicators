from datetime import date

import pandas as pd
import pytest

from indicators.store import (
    SeriesMeta,
    assign_segments,
    read_series,
    staleness,
    validate_frame,
    write_series,
)


def make_meta(**kw):
    base = dict(
        series_id="test_series",
        indicator_id="E1",
        title="Test series",
        units="percent",
        frequency="monthly",
        source_name="Test source",
        source_url="https://example.org/data",
        license="CC0",
        fetched_at="2026-11-17T00:00:00Z",
        data_through="2026-06-30",
        max_lag_days=120,
        breaks=[{"date": "2025-11-17", "note": "method change"}],
    )
    base.update(kw)
    return SeriesMeta(**base)


def make_df(dates=("2025-01-01", "2025-02-01", "2025-03-01"), values=(1.0, 2.0, 3.0)):
    return pd.DataFrame({"date": pd.to_datetime(list(dates)), "value": list(values)})


def test_write_read_roundtrip(tmp_path):
    df = make_df()
    df["segment"] = [0, 0, 1]
    df["se"] = [0.1, float("nan"), 0.3]
    meta = make_meta()
    write_series(df, meta, tmp_path)
    assert (tmp_path / "test_series.csv").exists()
    assert (tmp_path / "test_series.meta.json").exists()
    df2, meta2 = read_series("test_series", tmp_path)
    assert meta2 == meta
    assert list(df2.columns) == list(df.columns)
    pd.testing.assert_frame_equal(df2, df, check_dtype=False)


def test_grouped_roundtrip_preserves_na_like_labels(tmp_path):
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-01-01", "2025-02-01", "2025-02-01"]),
            "value": [1.0, 2.0, 3.0, 4.0],
            "se": [0.1, float("nan"), 0.3, float("nan")],
            "group": ["NA", "None", "NA", "None"],
        }
    )
    write_series(df, make_meta(), tmp_path)
    df2, _ = read_series("test_series", tmp_path)
    assert list(df2["group"]) == ["NA", "None", "NA", "None"]
    pd.testing.assert_frame_equal(df2, df, check_dtype=False)


def test_validate_rejects_duplicate_dates():
    df = make_df(dates=("2025-01-01", "2025-01-01", "2025-03-01"))
    with pytest.raises(ValueError, match="unique"):
        validate_frame(df)


def test_validate_allows_same_date_in_different_groups():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-01-01", "2025-02-01", "2025-02-01"]),
            "value": [1.0, 2.0, 3.0, 4.0],
            "group": ["a", "b", "a", "b"],
        }
    )
    validate_frame(df)
    df.loc[3, "group"] = "a"
    with pytest.raises(ValueError, match="unique"):
        validate_frame(df)


def test_validate_rejects_nan_value():
    df = make_df(values=(1.0, float("nan"), 3.0))
    with pytest.raises(ValueError, match="NaN"):
        validate_frame(df)


def test_validate_rejects_negative_se():
    df = make_df()
    df["se"] = [0.1, -0.2, 0.3]
    with pytest.raises(ValueError, match="se"):
        validate_frame(df)


def test_validate_rejects_unsorted():
    df = make_df(dates=("2025-03-01", "2025-01-01", "2025-02-01"))
    with pytest.raises(ValueError, match="ascending"):
        validate_frame(df)


def test_series_break_splits_segments():
    df = make_df(dates=("2025-11-16", "2025-11-17", "2025-11-18"))
    out = assign_segments(df, [{"date": "2025-11-17", "note": "x"}])
    assert list(out["segment"]) == [0, 1, 1]


def test_staleness():
    meta = make_meta(data_through="2026-06-30", max_lag_days=120)
    assert staleness(meta, date(2026, 11, 12)) == 15
    assert staleness(meta, date(2026, 10, 1)) is None


def test_write_is_atomic_on_invalid(tmp_path):
    df = make_df(values=(1.0, float("nan"), 3.0))
    with pytest.raises(ValueError):
        write_series(df, make_meta(), tmp_path)
    assert list(tmp_path.iterdir()) == []
