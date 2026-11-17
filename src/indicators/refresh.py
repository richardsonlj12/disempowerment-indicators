"""Run every source independently, write what succeeded, record health, exit 1 on any failure."""
from __future__ import annotations

import argparse
import inspect
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable

from indicators.sources import aei, btos, fred, oecd, stackexchange, wikimedia
from indicators.store import validate_frame, write_series

MODULES = {
    "fred": fred,
    "oecd": oecd,
    "btos": btos,
    "aei": aei,
    "stackexchange": stackexchange,
    "wikimedia": wikimedia,
}


def default_data_dir() -> Path:
    """`data/` at the repository root, independent of the working directory."""
    return Path(__file__).resolve().parents[2] / "data"


def default_sources(data_dir: Path | str, full: bool = False) -> dict[str, Callable]:
    """Zero-argument fetchers; data_dir (and full) are passed to sources whose fetch() takes them."""
    out: dict[str, Callable] = {}
    for name, module in MODULES.items():
        params = inspect.signature(module.fetch).parameters
        kwargs = {}
        if "data_dir" in params:
            kwargs["data_dir"] = Path(data_dir)
        if "full" in params:
            kwargs["full"] = full
        out[name] = (lambda m=module, kw=kwargs: m.fetch(**kw))
    return out


def _load_health(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("sources", {})
    except (OSError, ValueError, AttributeError):
        return {}


def run(data_dir: Path | str, sources: dict[str, Callable] | None = None,
        today: date | None = None, full: bool = False) -> dict:
    """Fetch each source; one failing never stops or partly writes another.

    Returns {"updated": ISO date, "sources": {name: record}}, also written to _health.json.
    Sources not run this time keep their previous record.
    """
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    today = today or datetime.now(timezone.utc).date()
    if sources is None:
        sources = default_sources(data_dir, full)
    health_path = data_dir / "_health.json"
    records = _load_health(health_path)

    for name, fetch in sources.items():
        previous = records.get(name, {})
        try:
            results = fetch()
            for df, _ in results:  # validate everything before writing anything
                validate_frame(df)
            for df, meta in results:
                write_series(df, meta, data_dir)
            records[name] = {"status": "ok", "data_through": max(m.data_through for _, m in results)}
        except Exception as exc:  # noqa: BLE001 - any failure must be isolated per source
            since = previous.get("since") if previous.get("status") == "failed" else None
            records[name] = {
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
                "since": since or today.isoformat(),
            }
            print(f"{name}: FAILED: {records[name]['error']}", file=sys.stderr)

    health = {"updated": today.isoformat(), "sources": records}
    health_path.write_text(json.dumps(health, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return health


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m indicators.refresh")
    parser.add_argument("--data-dir", type=Path, default=None, help="default: data/ at the repository root")
    parser.add_argument("--only", action="append", metavar="SOURCE", help="run only this source (repeatable)")
    parser.add_argument("--full", action="store_true", help="deep refresh for sources that support it")
    args = parser.parse_args(argv)

    data_dir = args.data_dir or default_data_dir()
    sources = default_sources(data_dir, args.full)
    if args.only:
        unknown = [n for n in args.only if n not in sources]
        if unknown:
            parser.error(f"unknown source(s) {unknown}; choose from {sorted(sources)}")
        sources = {n: sources[n] for n in args.only}
    health = run(data_dir, sources=sources)
    failed = [n for n in sources if health["sources"][n]["status"] == "failed"]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
