"""C1: monthly new-question counts on Stack Overflow and owner-approved comparison sites.

Keyless Stack Exchange API (anonymous quota: 300 requests a day per IP). The API has no
aggregate-by-month route, so each site-month costs one `/2.3/questions` call with
`fromdate`/`todate` set to the calendar month in UTC and a filter that returns only `total`
(plus `quota_remaining`, `backoff`, `has_more`). `/2.3/info` gives only the all-time total.

Full history is about 1,000 calls (about 980 month calls plus one all-time call per site per run), so the first fetch spans several days. Every completed month
is cached in `[data_dir]/_cache/stackexchange/[site].json` as it arrives. A run stops with a
`SourceError` as soon as the quota reaches zero with work left; the next run resumes from the
cache. The current month is never requested or cached. Each run refetches the last two complete
months (questions are deleted after the fact) and any month not yet cached.

Throttle guard: a throttled API response can silently ignore `fromdate`/`todate` and return the
site's ALL-TIME question total. Once per run and site the all-time total is fetched, and any
monthly count that is at least 99 percent of it, or above the plausibility bound below, is
rejected: it is not cached, the request is retried once after a pause, and a second rejection
stops the run with a `SourceError` (completed months stay cached; the next run resumes).
The bound for a site is min(ABSOLUTE_BOUND, max(3 x the largest monthly count already cached for
that site, BOUND_FLOOR)): 400,000 (floor 50,000) for Stack Overflow and 10,000 (floor 5,000) for a
comparison site. The floor keeps a young site's fast early growth from being rejected.

Request pacing: the API's `backoff` value is recorded from every response that carries it (errors
included) per method; both the all-time and month calls hit `/2.3/questions`, so they share one
backoff, and the next call to that method waits until it has passed. The earliest allowed next-call
time is persisted in `[data_dir]/_cache/stackexchange-throttle.json`, so a later process honours it
too (a wait over MAX_WAIT_SECONDS ends the run cleanly with a `SourceError` instead). Any two
requests are also at least MIN_REQUEST_INTERVAL_SECONDS (0.2 s) apart, well inside the limit of 30
requests per second. Error 502 (throttle_violation) stops the run at once, with no retry and
nothing cached for the failing month.

Every accepted fetch is also appended to `[data_dir]/_archive/stackexchange/[YYYY-MM-DD].csv`
(site, month, count, fetched_at) so that deletions accruing after the fact can be measured later.

Seven series are returned: the Stack Overflow and comparison-site counts; the relative-activity
index (2019 = 100) with its leave-one-out minimum and maximum (the band); the percent change since
ChatGPT's release (November 2022); and the year-over-year contrast, kept as an alternative view.
The index series need the full history (2019 base year, November 2022 reference) and are left out
of a short smoke run started with `start_month` after those months.
"""

from __future__ import annotations

import calendar
import json
import os
import tempfile
import time
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

from indicators import http
from indicators.http import SourceError
from indicators.sources import utc_now_iso
from indicators.store import SeriesMeta
from indicators.trend import (
    change_since,
    index_to_base_year,
    leave_one_out_band,
    relative_log_level,
    relative_yoy,
    rolling_total,
)

API = "https://api.stackexchange.com/2.3/questions"
DOCS_URL = "https://api.stackexchange.com/docs/questions"
# Created with /2.3/filters/create?base=none&include=.total;.quota_remaining;.backoff;.has_more
TOTAL_FILTER = "!-0ttWpIkt-bj4Nx"
SO_SITE = "stackoverflow"
SO_START = (2008, 9)  # Stack Overflow public launch month
REFRESH_MONTHS = 2
ABSOLUTE_BOUND = {SO_SITE: 400_000}
DEFAULT_ABSOLUTE_BOUND = 10_000
BOUND_FLOOR = {SO_SITE: 50_000}
DEFAULT_BOUND_FLOOR = 5_000
RELATIVE_BOUND = 3
ALL_TIME_SHARE = 0.99
RETRY_PAUSE_SECONDS = 30
LICENSE = "CC BY-SA"
DEFAULT_SITES_PATH = Path(__file__).resolve().parents[3] / "config" / "c1_comparison_sites.yaml"

_clock = time.time  # patched in tests
_sleep = time.sleep  # patched in tests


def month_bounds(year: int, month: int) -> tuple[int, int]:
    """Unix times of the first and last second of a calendar month, UTC."""
    last_day = calendar.monthrange(year, month)[1]
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    end = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)
    return int(start.timestamp()), int(end.timestamp())


def _ym(value) -> tuple[int, int]:
    if isinstance(value, (date, datetime)):
        return value.year, value.month
    year, month = str(value)[:7].split("-")
    return int(year), int(month)


def _key(ym: tuple[int, int]) -> str:
    return f"{ym[0]:04d}-{ym[1]:02d}"


def _first_full_month(open_beta_date) -> tuple[int, int]:
    """The opening month if the beta opened on day 1, else the next month."""
    ym = _ym(open_beta_date)
    if isinstance(open_beta_date, (date, datetime)):
        day = open_beta_date.day
    else:
        day = int(str(open_beta_date)[8:10])
    if day == 1:
        return ym
    return (ym[0] + 1, 1) if ym[1] == 12 else (ym[0], ym[1] + 1)


def _months(first: tuple[int, int], last: tuple[int, int]) -> list[tuple[int, int]]:
    out, (y, m) = [], first
    while (y, m) <= last:
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def _previous(ym: tuple[int, int]) -> tuple[int, int]:
    return (ym[0] - 1, 12) if ym[1] == 1 else (ym[0], ym[1] - 1)


def load_sites(path: Path | str | None = None) -> dict:
    """Read the comparison-site config; refuse to proceed unless the owner approved it."""
    config = yaml.safe_load(Path(path or DEFAULT_SITES_PATH).read_text(encoding="utf-8"))
    if config.get("approved_by_owner") is not True or not config.get("approved_on"):
        raise SourceError("C1 comparison sites are not owner-approved (approved_by_owner and approved_on); nothing fetched")
    return config


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _read_cache(path: Path) -> dict[str, int]:
    return {k: int(v) for k, v in json.loads(path.read_text()).items()} if path.exists() else {}


def _write_cache(path: Path, cache: dict[str, int]) -> None:
    _atomic_write(path, json.dumps(dict(sorted(cache.items())), indent=0) + "\n")


METHOD = "questions"  # the API method both the all-time and the month calls hit
MIN_REQUEST_INTERVAL_SECONDS = 0.2  # spacing between any two requests (API limit: 30 per second per IP)
MAX_WAIT_SECONDS = 300  # a backoff longer than this ends the run cleanly instead of sleeping


def _throttle_path(data_dir: Path) -> Path:
    # A sibling of the cache directory, so that `_cache/stackexchange/*.json` holds only month caches.
    return Path(data_dir) / "_cache" / "stackexchange-throttle.json"


def _read_throttle_state(data_dir: Path) -> dict[str, float]:
    path = _throttle_path(data_dir)
    try:
        return {k: float(v) for k, v in json.loads(path.read_text()).items()}
    except (OSError, ValueError, AttributeError):
        return {}


def _write_throttle_state(data_dir: Path, state: dict[str, float]) -> None:
    _atomic_write(_throttle_path(data_dir), json.dumps(state) + "\n")


class _Throttle:
    """Per-method `backoff` plus a minimum spacing, persisted so a later process honours both."""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.allowed_at = _read_throttle_state(self.data_dir)  # method -> earliest epoch time of the next call
        self.last_request = 0.0

    def wait(self, method: str = METHOD) -> None:
        delay = max(self.allowed_at.get(method, 0.0), self.last_request + MIN_REQUEST_INTERVAL_SECONDS) - _clock()
        if delay > MAX_WAIT_SECONDS:
            raise SourceError(
                f"Stack Exchange asked for a backoff of {delay:.0f}s on /{method}; stopping cleanly. "
                "Completed months are cached; run again later."
            )
        if delay > 0:
            _sleep(delay)
        self.last_request = _clock()

    def record(self, body, method: str = METHOD) -> None:
        backoff = body.get("backoff") if isinstance(body, dict) else None
        if backoff:
            self.allowed_at[method] = max(self.allowed_at.get(method, 0.0), _clock() + float(backoff))
            _write_throttle_state(self.data_dir, self.allowed_at)


_throttle: _Throttle | None = None


def _api_get(params: dict, what: str) -> dict:
    """One API call, spaced and backoff-aware. Returns the JSON body; raises SourceError on an API error.

    `backoff` is recorded from every response that carries it, errors included. Error 502
    (throttle_violation) is never retried: it raises straight away."""
    _throttle.wait()
    try:
        body = http.get(API, params=params, expect="json").json()
    except SourceError as error:
        try:
            _throttle.record(json.loads(getattr(error, "body", "")))
        except ValueError:
            pass
        raise
    _throttle.record(body)
    if "error_id" in body:
        raise SourceError(f"Stack Exchange {what}: {body.get('error_name')} {body.get('error_message')}")
    return body


def _month_total(site: str, ym: tuple[int, int]) -> tuple[int, int | None]:
    """One API call: (question count, quota_remaining or None)."""
    from_ts, to_ts = month_bounds(*ym)
    body = _api_get({"site": site, "fromdate": from_ts, "todate": to_ts, "filter": TOTAL_FILTER}, f"{site} {_key(ym)}")
    if "total" not in body:
        raise SourceError(f"Stack Exchange {site} {_key(ym)}: response has no total")
    return int(body["total"]), body.get("quota_remaining")


def _all_time_total(site: str) -> tuple[int, int | None]:
    """One API call without dates: the site's all-time question total (and quota_remaining)."""
    body = _api_get({"site": site, "filter": TOTAL_FILTER}, f"{site} all-time total")
    if "total" not in body:
        raise SourceError(f"Stack Exchange {site} all-time total: response has no total")
    return int(body["total"]), body.get("quota_remaining")


def plausibility_bound(site: str, cache: dict[str, int], key: str) -> int:
    """Largest monthly count accepted for `site` (see the module docstring)."""
    # Exclude the month being (re)fetched: its own cached value must not widen the bound for the new value.
    seen = max((v for k, v in cache.items() if k != key), default=0)
    absolute = ABSOLUTE_BOUND.get(site, DEFAULT_ABSOLUTE_BOUND)
    floor = BOUND_FLOOR.get(site, DEFAULT_BOUND_FLOOR)
    return min(absolute, max(RELATIVE_BOUND * seen, floor))


def _rejection(site: str, ym: tuple[int, int], total: int, all_time: int, bound: int) -> str | None:
    if all_time > 0 and total >= ALL_TIME_SHARE * all_time:
        return f"count {total} matches the site's all-time total {all_time} (throttled response ignoring the month)"
    if total > bound:
        return f"count {total} exceeds the plausibility bound {bound}"
    return None


def _validated_month(site: str, ym: tuple[int, int], all_time: int, cache: dict[str, int]) -> tuple[int, int | None]:
    """Fetch one month; reject an implausible count, retry once after a pause, then raise."""
    key = _key(ym)
    bound = plausibility_bound(site, cache, key)
    for attempt in (0, 1):
        total, quota = _month_total(site, ym)
        problem = _rejection(site, ym, total, all_time, bound)
        if problem is None:
            return total, quota
        if attempt == 0:
            _sleep(RETRY_PAUSE_SECONDS)
    raise SourceError(
        f"Stack Exchange {site} {key}: {problem}; rejected twice and not cached. "
        "Completed months are cached; run again later."
    )


def _archive(data_dir: Path, today: date, fetched_at: str, site: str, ym: tuple[int, int], total: int) -> None:
    """Append one accepted fetch to the day's append-only archive (site, month, count, fetched_at)."""
    path = Path(data_dir) / "_archive" / "stackexchange" / f"{today.isoformat()}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with path.open("a", encoding="utf-8", newline="") as f:
        if new:
            f.write("site,month,count,fetched_at\n")
        f.write(f"{site},{_key(ym)},{total},{fetched_at}\n")


INDEX_BASE_YEAR = 2019
CHATGPT_MONTH = "2022-11-01"


def _index_series(so_df, comparison, partial):
    """(index, loo_min, loo_max, change_since_chatgpt) from 12-month rolling totals, or {} when a
    short smoke run does not span the base year and reference month."""
    so_total, comparison_total = rolling_total(so_df), rolling_total(comparison)
    try:
        R = relative_log_level(so_total, comparison_total)
        index = index_to_base_year(R, INDEX_BASE_YEAR)
        change = change_since(R, CHATGPT_MONTH)
        lo, hi = leave_one_out_band(so_total, comparison_total, INDEX_BASE_YEAR)
    except ValueError:
        if partial:
            return {}
        raise
    return {"index": index, "loo_min": lo, "loo_max": hi, "change": change}


def _frame(rows: list[tuple[str, tuple[int, int], int]], grouped: bool) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime([f"{y:04d}-{m:02d}-01" for _, (y, m), _ in rows]),
            "value": [float(v) for _, _, v in rows],
        }
    )
    if grouped:
        df.insert(1, "group", [site for site, _, _ in rows])
    return df


def fetch(
    data_dir: Path | str = "data",
    sites_path: Path | str | None = None,
    start_month: str | None = None,
    today: date | None = None,
) -> list[tuple[pd.DataFrame, SeriesMeta]]:
    """Fetch (resuming from cache) and return the C1 Stack Exchange series (seven, or three on a short run).

    `start_month` ("YYYY-MM") limits how far back to fetch, for smoke tests. `today` is for tests.
    """
    config = load_sites(sites_path)  # owner gate, before any request
    today = today or datetime.now(timezone.utc).date()
    last_complete = _previous((today.year, today.month))
    refresh = {last_complete, _previous(last_complete)}
    floor = _ym(start_month) if start_month else (1, 1)
    cache_dir = Path(data_dir) / "_cache" / "stackexchange"
    global _throttle
    _throttle = _Throttle(Path(data_dir))

    plan = [(SO_SITE, SO_START)]
    # A site's opening month is partial (beta opens mid-month); start at its first full month.
    plan += [(s["api_site_name"], _first_full_month(s["open_beta_date"])) for s in config["sites"]]

    caches, todo = {}, []
    for site, beta in plan:
        caches[site] = _read_cache(cache_dir / f"{site}.json")
        for ym in _months(max(beta, floor), last_complete):
            if _key(ym) not in caches[site] or ym in refresh:
                todo.append((site, ym))

    all_time: dict[str, int] = {}
    for index, (site, ym) in enumerate(todo):
        quota = None
        if site not in all_time:
            all_time[site], quota = _all_time_total(site)
        if quota is None or quota > 0:
            total, quota = _validated_month(site, ym, all_time[site], caches[site])
            caches[site][_key(ym)] = total
            _write_cache(cache_dir / f"{site}.json", caches[site])
            _archive(Path(data_dir), today, utc_now_iso(), site, ym, total)
            remaining = len(todo) - index - 1
        else:  # the all-time call used the last of the quota; this month is still to fetch
            remaining = len(todo) - index
        if quota is not None and quota <= 0 and remaining:
            raise SourceError(
                f"Stack Exchange anonymous quota exhausted with {remaining} site-months still to fetch; "
                f"completed months are cached in {cache_dir}. Run again after the quota resets (daily)."
            )

    def rows(sites: list[str]) -> list[tuple[str, tuple[int, int], int]]:
        beta = dict(plan)
        out = []
        for site in sites:
            for ym in _months(max(beta[site], floor), last_complete):
                out.append((site, ym, caches[site][_key(ym)]))
        return out

    primary = [s["api_site_name"] for s in config["sites"]]
    so_df = _frame(rows([SO_SITE]), grouped=False)
    comparison = _frame(rows(primary), grouped=True)
    # Hold the comparison mean to the same four sites throughout: start the contrast once every
    # primary site has twelve months of history (latest first month plus one year).
    beta = dict(plan)
    latest_start = max(max(beta[s], floor) for s in primary)
    yoy_start = pd.Timestamp(year=latest_start[0] + 1, month=latest_start[1], day=1)
    yoy = relative_yoy(so_df, comparison, 12)
    yoy = yoy[yoy["date"] >= yoy_start].reset_index(drop=True)

    index_frames = _index_series(so_df, comparison, partial=start_month is not None)

    fetched_at = utc_now_iso()
    through = _key(last_complete) + "-01"
    common = dict(
        indicator_id="C1",
        frequency="monthly",
        source_name="Stack Exchange API",
        source_url=DOCS_URL,
        license=LICENSE,
        fetched_at=fetched_at,
        data_through=through,
        max_lag_days=75,
    )
    count_note = (
        "Questions created in the calendar month (UTC), counted from the /2.3/questions endpoint with "
        "filter total. Counts are as of the fetch date, so questions deleted later are not included. "
        "The current month is excluded; the last two complete months are refetched on every run."
    )
    names = {s["api_site_name"]: s["name"] for s in config["sites"]}
    primary_text = ", ".join(f"{names[s]} ({s})" for s in primary)

    index_note = (
        "Relative-activity index, not a causal estimate. Computed from 12-month rolling totals of "
        "so_questions_monthly and se_comparison_questions_monthly, labelled by the last month of each "
        "window: R = ln(Stack Overflow total) minus the mean of ln(total) across the four primary comparison "
        "sites, only for months where all four sites have a full 12 months. Values are expressed relative "
        f"to the {INDEX_BASE_YEAR} average (index {INDEX_BASE_YEAR} = 100), so the pre-AI level is the reference. "
        f"The companion series so_change_since_chatgpt is measured from the November 2022 window ({CHATGPT_MONTH[:7]}). "
        "AI also affects the comparison sites, so this is Stack Overflow's activity relative to them, "
        "not the absolute AI effect."
    )
    extra = []
    if index_frames:
        band_note = (
            " The leave-one-out band is the lowest and highest index obtained by dropping each comparison "
            "site in turn and using the other three; it is written as two series, "
            "so_relative_index_loo_min and so_relative_index_loo_max."
        )
        extra = [
            (
                index_frames["index"],
                SeriesMeta(
                    series_id="so_relative_index",
                    title=f"Stack Overflow activity relative to comparison sites (index, {INDEX_BASE_YEAR} = 100)",
                    units=f"index ({INDEX_BASE_YEAR} = 100)",
                    role="primary",
                    notes=index_note + band_note,
                    **common,
                ),
            ),
            (
                index_frames["loo_min"],
                SeriesMeta(
                    series_id="so_relative_index_loo_min",
                    title="Relative-activity index, leave-one-out minimum",
                    units=f"index ({INDEX_BASE_YEAR} = 100)",
                    role="context",
                    notes="Lower edge of the leave-one-out band around so_relative_index. " + index_note,
                    **common,
                ),
            ),
            (
                index_frames["loo_max"],
                SeriesMeta(
                    series_id="so_relative_index_loo_max",
                    title="Relative-activity index, leave-one-out maximum",
                    units=f"index ({INDEX_BASE_YEAR} = 100)",
                    role="context",
                    notes="Upper edge of the leave-one-out band around so_relative_index. " + index_note,
                    **common,
                ),
            ),
            (
                index_frames["change"],
                SeriesMeta(
                    series_id="so_change_since_chatgpt",
                    title="Stack Overflow activity relative to comparison sites, change since November 2022",
                    units="percent",
                    role="context",
                    notes=(
                        "Percent change in the same relative-activity measure since the 12-month window "
                        "ending November 2022 (ChatGPT was released on 30 November 2022, so that window is almost entirely before it): "
                        "100 x (exp(R(m) - R(2022-11)) - 1). Relative-activity index, not a causal estimate. "
                        + index_note
                    ),
                    **common,
                ),
            ),
        ]

    return extra + [
        (
            so_df,
            SeriesMeta(
                series_id="so_questions_monthly",
                title="Stack Overflow new questions per month",
                units="questions per month",
                role="context",
                notes=count_note + " Site: stackoverflow, from September 2008.",
                **common,
            ),
        ),
        (
            comparison,
            SeriesMeta(
                series_id="se_comparison_questions_monthly",
                title="New questions per month on the comparison Stack Exchange sites",
                units="questions per month",
                role="comparison",
                notes=count_note
                + f" Owner-approved primary comparison sites (selected {config['approved_on']}): {primary_text}. "
                "Each site starts at its first full month after open beta (a partial opening month would distort year-over-year changes). Selection record: "
                + config["selection_record"],
                **common,
            ),
        ),
        (
            yoy,
            SeriesMeta(
                series_id="so_vs_comparison_yoy",
                title="Stack Overflow year-over-year change minus comparison-site year-over-year change",
                units="percentage points",
                role="context",
                notes=(
                    "Alternative view to the relative-activity index. Stack Overflow's year-over-year percent change in monthly new questions minus the mean "
                    "year-over-year percent change across the primary comparison sites (each site first, "
                    "then the mean). Computed from so_questions_monthly and se_comparison_questions_monthly. "
                    f"The series starts {yoy_start:%Y-%m}, the first month in which all four primary sites have "
                    "a year-over-year change, so the comparison mean covers the same four sites throughout. "
                    "AI also affects the comparison sites, so this shows Stack Overflow relative to them, "
                    "not the absolute AI effect."
                ),
                **common,
            ),
        ),
    ]


def scan_archive_for_jumps(archive_dir: Path | str, factor: float = 2.0) -> list[str]:
    """Flag site-months whose count is more than `factor` x the previous or next month's count.

    Reads every day's archive CSV under `archive_dir` (later fetches of a month win), as a check
    against partially throttled responses. Returns human-readable lines; empty when clean."""
    latest: dict[tuple[str, str], int] = {}
    for path in sorted(Path(archive_dir).glob("*.csv")):
        frame = pd.read_csv(path, dtype={"site": str, "month": str})
        for site, month, count in zip(frame["site"], frame["month"], frame["count"]):
            latest[(site, month)] = int(count)
    flags = []
    for site in sorted({s for s, _ in latest}):
        months = sorted(m for s, m in latest if s == site)
        for m in months:
            ym = _ym(m)
            prev, nxt = _key(_previous(ym)), _key((ym[0] + 1, 1) if ym[1] == 12 else (ym[0], ym[1] + 1))
            for other in (prev, nxt):
                neighbour = latest.get((site, other))
                if neighbour and latest[(site, m)] > factor * neighbour:
                    flags.append(f"{site} {m}: {latest[(site, m)]} is more than {factor}x {other} ({neighbour})")
    return flags
