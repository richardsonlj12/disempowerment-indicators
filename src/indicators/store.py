"""Series store: the shared data contract between source modules and the site."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

FREQUENCIES = ("weekly", "biweekly", "monthly", "quarterly", "annual", "irregular")
ROLES = ("primary", "context", "comparison")


@dataclass
class SeriesMeta:
    series_id: str
    indicator_id: str
    title: str
    units: str
    frequency: str  # weekly|biweekly|monthly|quarterly|annual|irregular
    source_name: str
    source_url: str
    license: str
    fetched_at: str  # ISO UTC
    data_through: str  # ISO date
    # Days after the END of the latest period (see period_end) by which newer data are expected:
    # one more period plus the source's usual publication lag, with slack. Drives the stale badge.
    max_lag_days: int
    breaks: list[dict] = field(default_factory=list)  # {"date": "YYYY-MM-DD", "note": str}; split lines
    annotations: list[dict] = field(default_factory=list)  # {"date": "YYYY-MM-DD", "label": str}; markers only
    notes: str = ""
    role: str = "primary"  # primary|context|comparison


def validate_frame(df: pd.DataFrame) -> None:
    """Raise ValueError with a specific message if df violates the contract."""
    for col in ("date", "value"):
        if col not in df.columns:
            raise ValueError(f"missing required column: {col}")
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        raise ValueError("date column must be datetime")
    if not pd.api.types.is_float_dtype(df["value"]):
        raise ValueError("value column must be float")
    if df["value"].isna().any():
        raise ValueError("value column must not contain NaN")

    if "group" in df.columns:
        if df.duplicated(subset=["group", "date"]).any():
            raise ValueError("date must be unique within each group")
        for _, sub in df.groupby("group", sort=False):
            if not sub["date"].is_monotonic_increasing:
                raise ValueError("date must be ascending within each group")
    else:
        if df["date"].duplicated().any():
            raise ValueError("date must be unique")
        if not df["date"].is_monotonic_increasing:
            raise ValueError("date must be ascending")

    if "segment" in df.columns and not pd.api.types.is_integer_dtype(df["segment"]):
        raise ValueError("segment column must be int")
    if "se" in df.columns:
        if not pd.api.types.is_float_dtype(df["se"]):
            raise ValueError("se column must be float")
        if (df["se"] < 0).any():
            raise ValueError("se must be >= 0")
    if "group" in df.columns and not all(isinstance(g, str) for g in df["group"]):
        raise ValueError("group column must be str")


def assign_segments(df: pd.DataFrame, breaks: list[dict]) -> pd.DataFrame:
    """Add a `segment` column that increments at each break date (on or after)."""
    out = df.copy()
    segment = pd.Series(0, index=out.index)
    for b in breaks:
        segment += (out["date"] >= pd.Timestamp(b["date"])).astype(int)
    out["segment"] = segment.astype(int)
    return out


def _atomic_write(path: Path, text: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def write_series(df: pd.DataFrame, meta: SeriesMeta, data_dir: Path) -> None:
    """Validate, then write `[series_id].csv` and `.meta.json` atomically."""
    validate_frame(df)
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    csv_text = df.to_csv(index=False, date_format="%Y-%m-%d", lineterminator="\n")
    meta_text = json.dumps(asdict(meta), indent=2, ensure_ascii=False) + "\n"
    _atomic_write(data_dir / f"{meta.series_id}.csv", csv_text)
    _atomic_write(data_dir / f"{meta.series_id}.meta.json", meta_text)


def read_series(series_id: str, data_dir: Path) -> tuple[pd.DataFrame, SeriesMeta]:
    data_dir = Path(data_dir)
    # Only numeric columns may be NA; group labels like "NA"/"None" must stay literal.
    df = pd.read_csv(
        data_dir / f"{series_id}.csv",
        parse_dates=["date"],
        dtype={"group": str},
        keep_default_na=False,
        na_values={"value": [""], "se": [""]},
    )
    meta = SeriesMeta(**json.loads((data_dir / f"{series_id}.meta.json").read_text(encoding="utf-8")))
    return df, meta


def period_end(data_through: str, frequency: str) -> date:
    """Last day of the period that `data_through` labels. Quarterly, annual and monthly series are
    dated by the period's first day; weekly, biweekly and irregular dates are taken as they are."""
    d = date.fromisoformat(str(data_through)[:10])
    if frequency == "annual":
        return date(d.year, 12, 31)
    if frequency in ("quarterly", "monthly"):
        months = 3 if frequency == "quarterly" else 1
        first = d.month if frequency == "monthly" else 3 * ((d.month - 1) // 3) + 1
        year, month = divmod(first - 1 + months, 12)
        return date(d.year + year, month + 1, 1) - timedelta(days=1)
    return d


def stale_since(meta: SeriesMeta) -> date:
    """Date by which newer data were expected: the end of the latest period plus max_lag_days
    (one more period plus the source's usual publication lag, with some slack)."""
    return period_end(meta.data_through, meta.frequency) + timedelta(days=meta.max_lag_days)


def staleness(meta: SeriesMeta, today: date) -> int | None:
    """Days past stale_since(meta), or None if not overdue."""
    late = (today - stale_since(meta)).days
    return late if late > 0 else None
