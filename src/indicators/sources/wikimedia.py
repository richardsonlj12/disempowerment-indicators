"""C1 context: English Wikipedia human pageviews and active editors (keyless Wikimedia REST API).

- Pageviews: `/metrics/pageviews/aggregate/en.wikipedia/all-access/user/monthly/...` (agent `user`,
  which excludes spiders and automated traffic), available from 2015-07.
- Active editors: `/metrics/editors/aggregate/en.wikipedia/user/all-page-types/[level]/monthly/...`
  for editor type `user`, which Wikistats defines as "logged in users that are not considered a bot
  by name or group" (not in the bot user group and no "bot" in the user name). Wikimedia defines an active editor as one with 5 or
  more edits in the month, so the levels 5..24, 25..99 and 100.. are summed.

Wikimedia states that it changed its bot detection in 2025 and reclassified March to August 2025
traffic, so the human pageview series has a break at 2025-03-01.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd

from indicators import http
from indicators.http import SourceError
from indicators.sources import utc_now_iso
from indicators.store import SeriesMeta, assign_segments

BASE = "https://wikimedia.org/api/rest_v1/metrics/"
PAGEVIEWS_URL = BASE + "pageviews/aggregate/en.wikipedia/all-access/user/monthly/{start}/{end}"
EDITORS_URL = BASE + "editors/aggregate/en.wikipedia/user/all-page-types/{level}/monthly/{start}/{end}"
PAGEVIEWS_FIRST = "2015070100"
EDITORS_FIRST = "20100101"
ACTIVE_LEVELS = ("5..24-edits", "25..99-edits", "100..-edits")
LICENSE = "CC0"
DOCS_URL = "https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/"
ANNOUNCEMENT_URL = "https://diff.wikimedia.org/2025/10/17/new-user-trends-on-wikipedia/"

BREAKS = [
    {
        "date": "2025-03-01",
        "note": (
            "Wikimedia updated its bot detection and reclassified traffic for March to August 2025, moving "
            "automated traffic out of human (agent=user) pageviews; months before March 2025 keep the old "
            f"classification. Announcement: {ANNOUNCEMENT_URL}"
        ),
    }
]


def _end_of_range(today: date) -> date:
    """First day of the last complete month."""
    first = today.replace(day=1)
    return (first.replace(year=first.year - 1, month=12) if first.month == 1 else first.replace(month=first.month - 1))


def _items(url: str) -> list:
    body = http.get(url, expect="json").json()
    items = body.get("items")
    if not items:
        raise SourceError(f"{url}: no items in response")
    return items


def _pageviews(today: date) -> pd.DataFrame:
    end = _end_of_range(today).strftime("%Y%m0100")
    items = _items(PAGEVIEWS_URL.format(start=PAGEVIEWS_FIRST, end=end))
    df = pd.DataFrame(
        {
            "date": pd.to_datetime([i["timestamp"][:6] + "01" for i in items], format="%Y%m%d"),
            "value": [float(i["views"]) for i in items],
        }
    )
    return df.sort_values("date").reset_index(drop=True)


def _editors(today: date) -> pd.DataFrame:
    end = _end_of_range(today).strftime("%Y%m01")
    parts = {}
    for level in ACTIVE_LEVELS:
        results = _items(EDITORS_URL.format(level=level, start=EDITORS_FIRST, end=end))[0]["results"]
        parts[level] = pd.Series(
            [float(r["editors"]) for r in results],
            index=pd.to_datetime([r["timestamp"][:10] for r in results]),
        )
    # Keep only months published for every level, so a month never holds a partial sum.
    total = pd.concat(parts, axis=1).dropna().sum(axis=1)
    df = total.rename("value").rename_axis("date").reset_index()
    return df.sort_values("date").reset_index(drop=True)


def fetch(data_dir: Path | str = "data", today: date | None = None) -> list[tuple[pd.DataFrame, SeriesMeta]]:
    """`data_dir` is accepted for a uniform source interface; Wikimedia needs no cache."""
    today = today or datetime.now(timezone.utc).date()
    fetched_at = utc_now_iso()

    views = assign_segments(_pageviews(today), BREAKS)
    views_meta = SeriesMeta(
        series_id="wiki_user_pageviews_en",
        indicator_id="C1",
        title="English Wikipedia human pageviews per month",
        units="pageviews per month",
        frequency="monthly",
        source_name="Wikimedia Pageviews API",
        source_url=DOCS_URL,
        license=LICENSE,
        fetched_at=fetched_at,
        data_through=views["date"].max().strftime("%Y-%m-%d"),
        max_lag_days=75,
        breaks=BREAKS,
        role="context",
        notes=(
            "en.wikipedia, all-access, agent=user (Wikimedia's classification of human traffic; spiders "
            "and, since the 2025 reclassification, detected automated traffic are excluded). Available "
            "from July 2015. Wikimedia cautions that comparisons across the March 2025 break need care "
            f"because bot detection rules changed; see {ANNOUNCEMENT_URL}. Falling human pageviews may "
            "reflect AI intermediation (people reading Wikipedia content through AI tools such as chatbots and "
            "search summaries rather than visiting the site) rather than less interest in the content."
        ),
    )

    editors = _editors(today)
    editors_meta = SeriesMeta(
        series_id="wiki_active_editors_en",
        indicator_id="C1",
        title="English Wikipedia active editors per month",
        units="editors",
        frequency="monthly",
        source_name="Wikimedia Editors API",
        source_url=DOCS_URL,
        license=LICENSE,
        fetched_at=fetched_at,
        data_through=editors["date"].max().strftime("%Y-%m-%d"),
        max_lag_days=75,
        breaks=[],
        role="context",
        notes=(
            "en.wikipedia, editor type user (logged-in editors not counted as bots by bot group or by a "
            "user name containing 'bot'), all page types. Active editors are "
            "those with 5 or more edits in the month: the sum of the 5..24, 25..99 and 100.. edit "
            "activity levels."
        ),
    )
    return [(views, views_meta), (editors, editors_meta)]
