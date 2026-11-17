"""Source modules: each exposes fetch() -> list[tuple[DataFrame, SeriesMeta]]."""

from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
