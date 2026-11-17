"""Tests for the Stack Exchange and Wikimedia source modules (C1)."""

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd
import pytest
import responses

from indicators import http
from indicators.http import SourceError
from indicators.sources import stackexchange, wikimedia
from indicators.store import FREQUENCIES, ROLES, validate_frame

FIXTURES = Path(__file__).parent / "fixtures" / "wikimedia"
ROOT = Path(__file__).resolve().parent.parent
SITES_YAML = ROOT / "config" / "c1_comparison_sites.yaml"
SE_URL = "https://api.stackexchange.com/2.3/questions"

TODAY = date(2024, 6, 15)  # complete months: up to 2024-05; current month 2024-06
START = "2023-01"  # 17 complete months, enough for year-over-year


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(http, "_sleep", lambda s: None)
    monkeypatch.setattr(stackexchange, "_sleep", lambda s: None)


def _by_id(results):
    return {meta.series_id: (df, meta) for df, meta in results}


def _ts(year, month, day=1, h=0, m=0, s=0):
    return int(datetime(year, month, day, h, m, s, tzinfo=timezone.utc).timestamp())


# ---------------------------------------------------------------- Stack Exchange


def _default_count(site, year, month):
    if site == "stackoverflow":
        return int(1000 * (1.10 if year == 2024 else 1.0))  # +10% year over year
    return 100  # flat everywhere else


def _mock_se(count=_default_count, quota_start=300, backoff=None):
    state = {"quota": quota_start, "calls": []}

    def callback(request):
        qs = parse_qs(urlparse(request.url).query)
        site = qs["site"][0]
        start = datetime.fromtimestamp(int(qs["fromdate"][0]), tz=timezone.utc)
        state["calls"].append((site, start.year, start.month))
        state["quota"] -= 1
        body = {"total": count(site, start.year, start.month), "has_more": False,
                "quota_remaining": max(state["quota"], 0)}
        if backoff:
            body["backoff"] = backoff
        return (200, {}, json.dumps(body))

    responses.add_callback(responses.GET, SE_URL, callback=callback)
    return state


def test_so_month_bounds():
    # Leap-year February, a 31-day month, and a December that rolls the year over.
    assert stackexchange.month_bounds(2024, 2) == (_ts(2024, 2, 1), _ts(2024, 2, 29, 23, 59, 59))
    assert stackexchange.month_bounds(2023, 7) == (_ts(2023, 7, 1), _ts(2023, 7, 31, 23, 59, 59))
    assert stackexchange.month_bounds(2023, 12) == (_ts(2023, 12, 1), _ts(2023, 12, 31, 23, 59, 59))
    # Consecutive months tile the calendar with no gap and no overlap.
    assert stackexchange.month_bounds(2023, 12)[1] + 1 == stackexchange.month_bounds(2024, 1)[0]


@responses.activate
def test_request_uses_month_bounds_total_filter_and_user_agent():
    _mock_se()
    stackexchange.fetch(start_month="2024-03", today=date(2024, 4, 20))
    request = responses.calls[0].request
    qs = parse_qs(urlparse(request.url).query)
    assert (int(qs["fromdate"][0]), int(qs["todate"][0])) == stackexchange.month_bounds(2024, 3)
    assert qs["filter"][0] == stackexchange.TOTAL_FILTER
    assert request.headers["User-Agent"].startswith("disempowerment-indicators/0.1 (+https://github.com/")


def _write_sites(tmp_path, approved):
    text = SITES_YAML.read_text().replace("approved_by_owner: true", f"approved_by_owner: {str(approved).lower()}")
    path = tmp_path / "sites.yaml"
    path.write_text(text)
    return path


@responses.activate
def test_comparison_requires_owner_approval(tmp_path):
    _mock_se()
    with pytest.raises(SourceError, match="approv"):
        stackexchange.fetch(sites_path=_write_sites(tmp_path, False), start_month=START, today=TODAY)
    assert len(responses.calls) == 0  # nothing was requested, including Stack Overflow


@responses.activate
def test_stackexchange_partial_quota_not_written(tmp_path):
    state = _mock_se(quota_start=12)  # the 12th response reports quota_remaining 0
    with pytest.raises(SourceError, match="quota"):
        stackexchange.fetch(start_month=START, today=TODAY)
    assert len(state["calls"]) == 12  # stopped at the call that exhausted the quota
    assert not (tmp_path / "data" / "so_questions_monthly.csv").exists()
    assert not (tmp_path / "data" / "so_vs_comparison_yoy.csv").exists()
    cache = tmp_path / "data" / "_cache" / "stackexchange"
    cached = json.loads((cache / "stackoverflow.json").read_text())
    assert len(cached) == 12  # every month that came back complete is kept
    assert "2024-06" not in cached  # the current month is never cached
    assert sorted(cached) == [f"2023-{m:02d}" for m in range(1, 13)]
    # The next run resumes from the cache and asks only for what is missing.
    responses.reset()
    state2 = _mock_se()
    stackexchange.fetch(start_month=START, today=TODAY)
    so_requests = {(y, m) for (s, y, m) in state2["calls"] if s == "stackoverflow"}
    assert so_requests == {(2024, m) for m in range(1, 6)}  # the 5 missing months, which include the last two


@responses.activate
def test_current_month_is_never_requested_or_cached(tmp_path):
    state = _mock_se()
    results = _by_id(stackexchange.fetch(start_month=START, today=TODAY))
    assert ("stackoverflow", 2024, 6) not in state["calls"]
    for path in (tmp_path / "data" / "_cache" / "stackexchange").glob("*.json"):
        assert "2024-06" not in json.loads(path.read_text())
    df, meta = results["so_questions_monthly"]
    assert df["date"].max() == pd.Timestamp("2024-05-01")
    assert meta.data_through == "2024-05-01"


@responses.activate
def test_rerun_refetches_only_last_two_months_plus_uncached(tmp_path):
    _mock_se()
    stackexchange.fetch(start_month=START, today=TODAY)
    responses.reset()
    state = _mock_se()
    stackexchange.fetch(start_month=START, today=TODAY)
    months = {(y, m) for (_, y, m) in state["calls"]}
    assert months == {(2024, 4), (2024, 5)}
    assert len(state["calls"]) == 2 * 8  # Stack Overflow plus seven other sites
    # A month later: the new complete month and the one before it are refreshed.
    responses.reset()
    state = _mock_se()
    stackexchange.fetch(start_month=START, today=date(2024, 7, 3))
    assert {(y, m) for (_, y, m) in state["calls"]} == {(2024, 5), (2024, 6)}


@responses.activate
def test_relative_yoy_written(tmp_path):
    _mock_se()
    results = _by_id(stackexchange.fetch(start_month=START, today=TODAY))
    assert set(results) == {
        "so_questions_monthly",
        "se_comparison_questions_monthly",
        "se_robustness_questions_monthly",
        "so_vs_comparison_yoy",
    }
    yoy, meta = results["so_vs_comparison_yoy"]
    validate_frame(yoy)
    assert meta.indicator_id == "C1" and meta.role == "primary"
    assert meta.frequency == "monthly" and meta.units == "percentage points"
    # SO is +10% year over year, the comparison sites are flat, so the difference is 10.
    assert yoy["date"].min() == pd.Timestamp("2024-01-01") and yoy["date"].max() == pd.Timestamp("2024-05-01")
    assert yoy["value"].tolist() == pytest.approx([10.0] * 5)
    assert (tmp_path / "data" / "_cache" / "stackexchange").is_dir()


@responses.activate
def test_comparison_and_robustness_series_shape():
    # The robustness-only sites are wild on purpose: the year-over-year contrast must ignore them.
    def counts(site, year, month):
        if site in ("gaming", "worldbuilding", "judaism"):
            return 100 * (1 + (year - 2023) * 5)
        return _default_count(site, year, month)

    _mock_se(counts)
    results = _by_id(stackexchange.fetch(start_month=START, today=TODAY))
    comp, comp_meta = results["se_comparison_questions_monthly"]
    robust, robust_meta = results["se_robustness_questions_monthly"]
    for df, meta in ((comp, comp_meta), (robust, robust_meta)):
        validate_frame(df)
        assert meta.indicator_id == "C1" and meta.role == "comparison"
        assert meta.frequency in FREQUENCIES and meta.role in ROLES
        assert meta.license == "CC BY-SA"
    assert set(comp["group"]) == {"diy", "travel", "rpg", "scifi"}
    assert set(robust["group"]) == {"gaming", "worldbuilding", "judaism"}
    assert len(comp) == 4 * 17 and len(robust) == 3 * 17
    yoy, _ = results["so_vs_comparison_yoy"]
    assert yoy["value"].tolist() == pytest.approx([10.0] * 5)
    so, so_meta = results["so_questions_monthly"]
    assert so_meta.role == "context" and "group" not in so.columns
    assert so["value"].dtype == float


@responses.activate
def test_site_starts_at_first_full_month_after_open_beta():
    state = _mock_se()
    stackexchange.fetch(start_month="2010-06", today=date(2010, 10, 20))
    first = {}
    for site, y, m in state["calls"]:
        first[site] = min(first.get(site, (y, m)), (y, m))
    assert first["stackoverflow"] == (2010, 6)
    assert first["diy"] == (2010, 8)  # open beta 2010-07-28 is a partial month
    assert first["gaming"] == (2010, 8)  # open beta 2010-07-14
    assert first["rpg"] == (2010, 9)  # open beta 2010-08-26
    assert "travel" not in first  # beta opened 2011-06


def test_first_full_month_helper():
    assert stackexchange._first_full_month(date(2010, 7, 28)) == (2010, 8)
    assert stackexchange._first_full_month(date(2010, 12, 31)) == (2011, 1)
    assert stackexchange._first_full_month(date(2011, 3, 1)) == (2011, 3)


@responses.activate
def test_yoy_starts_when_all_four_primary_sites_have_a_year(tmp_path):
    # Latest primary start is travel (beta 2011-06-28, first full month 2011-07), so the contrast
    # starts 2012-07; the partial opening months never enter it.
    state = _mock_se()
    results = _by_id(stackexchange.fetch(start_month="2010-06", today=date(2013, 1, 15)))
    assert ("travel", 2011, 6) not in state["calls"] and ("diy", 2010, 7) not in state["calls"]
    yoy, meta = results["so_vs_comparison_yoy"]
    assert yoy["date"].min() == pd.Timestamp("2012-07-01")
    assert yoy["value"].tolist() == pytest.approx([0.0] * len(yoy))
    assert "2012-07" in meta.notes and "same four sites" in meta.notes


@responses.activate
def test_yoy_comparison_mean_uses_four_sites_throughout():
    # diy grows 50% a year, the others are flat; with all four in the mean the contrast is -12.5
    # from 2012-07 on, and no earlier month (where fewer sites would be averaged) is published.
    def counts(site, year, month):
        if site == "diy":
            return int(100 * 1.5 ** (year - 2010))
        return 100

    _mock_se(counts)
    results = _by_id(stackexchange.fetch(start_month="2010-06", today=date(2013, 1, 15)))
    yoy, _ = results["so_vs_comparison_yoy"]
    assert yoy["date"].min() == pd.Timestamp("2012-07-01")
    jan = yoy[yoy["date"] == "2012-12-01"]["value"].iloc[0]
    assert jan == pytest.approx(-12.5)  # 0 - (50 + 0 + 0 + 0) / 4


@responses.activate
def test_backoff_field_is_honoured(monkeypatch):
    slept = []
    monkeypatch.setattr(stackexchange, "_sleep", slept.append)
    _mock_se(backoff=5)
    stackexchange.fetch(start_month="2024-04", today=date(2024, 5, 20))
    assert slept and set(slept) == {5}


@responses.activate
def test_throttle_error_from_api_raises_source_error():
    body = {"error_id": 502, "error_name": "throttle_violation", "error_message": "too many requests"}
    responses.add(responses.GET, SE_URL, status=400, json=body)
    with pytest.raises(SourceError, match="throttle_violation"):
        stackexchange.fetch(start_month=START, today=TODAY)


# ---------------------------------------------------------------- Wikimedia

WM = "https://wikimedia.org/api/rest_v1/metrics/"


def _mock_wikimedia():
    responses.add(
        responses.GET,
        re.compile(re.escape(WM + "pageviews/aggregate/en.wikipedia/all-access/user/monthly/") + r"2015070100/\d+"),
        body=(FIXTURES / "pageviews_user_monthly.json").read_text(),
        content_type="application/json",
    )
    for level, name in (("5..24-edits", "editors_5_24"), ("25..99-edits", "editors_25_99"), ("100..-edits", "editors_100_")):
        responses.add(
            responses.GET,
            re.compile(re.escape(WM + f"editors/aggregate/en.wikipedia/user/all-page-types/{level}/monthly/") + r"20100101/\d+"),
            body=(FIXTURES / f"{name}.json").read_text(),
            content_type="application/json",
        )


@responses.activate
def test_wikimedia_user_agent_set():
    _mock_wikimedia()
    wikimedia.fetch(today=date(2026, 11, 17))
    assert len(responses.calls) == 4  # pageviews plus three editor activity levels
    for call in responses.calls:
        assert call.request.headers["User-Agent"] == (
            "disempowerment-indicators/0.1 (+https://github.com/richardsonlj12/disempowerment-indicators)"
        )


@responses.activate
def test_wikimedia_break_assigned():
    _mock_wikimedia()
    results = _by_id(wikimedia.fetch(today=date(2026, 11, 17)))
    df, meta = results["wiki_user_pageviews_en"]
    validate_frame(df)
    assert len(meta.breaks) == 1 and meta.breaks[0]["date"] == "2025-03-01"
    assert "https://diff.wikimedia.org/2025/10/17/new-user-trends-on-wikipedia/" in meta.breaks[0]["note"]
    assert "March" in meta.breaks[0]["note"] and "August 2025" in meta.breaks[0]["note"]
    before, after = df[df["date"] < "2025-03-01"], df[df["date"] >= "2025-03-01"]
    assert len(before) and len(after)
    assert (before["segment"] == 0).all() and (after["segment"] == 1).all()
    assert df["date"].iloc[0] == pd.Timestamp("2015-07-01")
    assert df["value"].iloc[0] == 7665421980.0 and df["value"].dtype == float
    assert meta.indicator_id == "C1" and meta.role == "context" and meta.frequency == "monthly"
    assert "agent=user" in meta.notes or "agent user" in meta.notes


@responses.activate
def test_wikimedia_active_editors_sum_five_plus_edit_levels():
    _mock_wikimedia()
    results = _by_id(wikimedia.fetch(today=date(2026, 11, 17)))
    df, meta = results["wiki_active_editors_en"]
    validate_frame(df)
    by_date = df.set_index("date")["value"]
    assert by_date[pd.Timestamp("2015-01-01")] == 26434 + 8000 + 3500
    assert by_date[pd.Timestamp("2010-01-01")] == 26000 + 9000 + 4000
    assert meta.breaks == [] and "segment" not in df.columns or (df["segment"] == 0).all()
    assert meta.indicator_id == "C1" and meta.role == "context"


@responses.activate
def test_wikimedia_html_instead_of_json_raises():
    responses.add(responses.GET, re.compile(".*"), body="<html>blocked</html>", content_type="text/html")
    with pytest.raises(SourceError):
        wikimedia.fetch(today=date(2026, 11, 17))


# ---------------------------------------------------------------- live


@pytest.mark.live
def test_live_stackexchange_few_months(tmp_path):
    results = _by_id(stackexchange.fetch(data_dir=tmp_path, start_month="2022-01", today=date(2022, 6, 15)))
    so, _ = results["so_questions_monthly"]
    assert len(so) == 5 and (so["value"] > 10000).all()
    diy = results["se_comparison_questions_monthly"][0].query("group == 'diy'")
    assert len(diy) == 5 and (diy["value"] > 100).all()


@pytest.mark.live
def test_live_wikimedia():
    results = _by_id(wikimedia.fetch())
    views, _ = results["wiki_user_pageviews_en"]
    assert views["date"].iloc[0] == pd.Timestamp("2015-07-01") and views["value"].iloc[0] == 7665421980.0
    editors, _ = results["wiki_active_editors_en"]
    assert editors["date"].iloc[0] == pd.Timestamp("2010-01-01")
