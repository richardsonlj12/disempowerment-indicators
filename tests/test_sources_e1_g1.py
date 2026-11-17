"""Tests for the FRED/BLS (E1, G1) and OECD (G1) source modules."""

import re
from datetime import date
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import pytest
import responses

from indicators.sources import fred, oecd
from indicators.store import ROLES, FREQUENCIES, SeriesMeta, validate_frame

FIXTURES = Path(__file__).parent / "fixtures"


def _fixture(*parts: str) -> str:
    return (FIXTURES.joinpath(*parts)).read_text(encoding="utf-8")


def _mock_fred():
    for sid in ["CPATAX", "GDP", "W054RC1Q027SBEA", "W055RC1Q027SBEA", "W782RC1Q027SBEA"]:
        responses.add(
            responses.GET,
            "https://fred.stlouisfed.org/graph/fredgraph.csv",
            body=_fixture("fred", f"{sid}.csv"),
            match=[responses.matchers.query_param_matcher({"id": sid}, strict_match=False)],
        )
    # The BLS fixture is returned for every chunked request; duplicates are merged by date.
    responses.add(
        responses.GET,
        re.compile(r"https://api\.bls\.gov/publicAPI/v1/timeseries/data/PRS85006174.*"),
        body=_fixture("fred", "bls_PRS85006174.json"),
        content_type="application/json",
    )


def _mock_oecd():
    responses.add(
        responses.GET,
        re.compile(r"https://sdmx\.oecd\.org/public/rest/data/.*"),
        body=_fixture("oecd", "revenue_statistics.csv"),
        content_type="application/vnd.sdmx.data+csv",
    )


@pytest.fixture(autouse=True)
def isolated_cwd(tmp_path, monkeypatch):
    """Default data dir is relative; keep offline tests away from any committed data/."""
    monkeypatch.chdir(tmp_path)


def _bls_calls():
    return [c for c in responses.calls if "api.bls.gov" in c.request.url]


def _by_id(results):
    return {meta.series_id: (df, meta) for df, meta in results}


@responses.activate
def test_labor_share_parses_percent():
    _mock_fred()
    df, meta = _by_id(fred.fetch())["labor_share_nfb"]
    validate_frame(df)
    assert meta.units == "percent"
    assert meta.indicator_id == "E1" and meta.role == "primary"
    # Percent level, not an index: every value sits in a plausible percent band.
    assert df["value"].between(40, 70).all()
    row = df[df["date"] == "2026-04-01"]
    assert len(row) == 1
    assert row["value"].iloc[0] == pytest.approx(53.3)
    assert df["date"].is_unique and df["date"].is_monotonic_increasing


@responses.activate
def test_profit_share_formula():
    _mock_fred()
    df, meta = _by_id(fred.fetch())["profit_share"]
    row = df[df["date"] == "2026-04-01"]["value"].iloc[0]
    # CPATAX 3877.434 / GDP 32563.030 * 100, hand-computed
    assert row == pytest.approx(11.9075, abs=1e-3)
    assert meta.role == "context" and meta.indicator_id == "E1"


@responses.activate
def test_tax_share_formula():
    _mock_fred()
    df, meta = _by_id(fred.fetch())["us_labor_tax_share"]
    validate_frame(df)
    # (personal current taxes 3374.645 + contributions 1993.336)
    #   / (government current tax receipts 6358.949 + contributions 1993.336) * 100
    row = df[df["date"] == "2025-07-01"]["value"].iloc[0]
    assert row == pytest.approx(64.2706, abs=1e-3)
    # Receipts for 2026Q3 are not yet published, so that quarter must be absent.
    assert df["date"].max() == pd.Timestamp("2026-04-01")
    assert meta.data_through == "2026-04-01"
    for sid in ("W055RC1Q027SBEA", "W782RC1Q027SBEA", "W054RC1Q027SBEA"):
        assert sid in meta.notes
    assert meta.indicator_id == "G1" and meta.role == "primary"


@responses.activate
def test_oecd_labor_share_formula():
    _mock_oecd()
    out = _by_id(oecd.fetch())
    usa, usa_meta = out["oecd_labor_tax_share_usa"]
    avg, avg_meta = out["oecd_labor_tax_share_avg"]
    validate_frame(usa)
    validate_frame(avg)
    # PIT 39.968453 + SSC 23.506054
    assert usa[usa["date"] == "2023-01-01"]["value"].iloc[0] == pytest.approx(63.474507, abs=1e-5)
    # PIT 23.736387 + SSC 25.46347
    assert avg[avg["date"] == "2023-01-01"]["value"].iloc[0] == pytest.approx(49.199857, abs=1e-5)
    assert usa_meta.role == avg_meta.role == "context"
    assert usa_meta.frequency == "annual"
    assert "1100" in usa_meta.notes and "2000" in usa_meta.notes


@responses.activate
def test_oecd_drops_years_missing_a_component():
    body = _fixture("oecd", "revenue_statistics.csv")
    lines = body.splitlines()
    # Remove the USA SSC row for 2023 so only PIT remains for that year.
    kept = [l for l in lines if not (l.startswith("DATAFLOW") and ",USA," in l and ",T_2000," in l and ",2023," in l)]
    assert len(kept) == len(lines) - 1
    responses.add(responses.GET, re.compile(r"https://sdmx\.oecd\.org/.*"), body="\n".join(kept) + "\n")
    usa, _ = _by_id(oecd.fetch())["oecd_labor_tax_share_usa"]
    assert pd.Timestamp("2023-01-01") not in set(usa["date"])


@responses.activate
def test_meta_fields_complete():
    _mock_fred()
    _mock_oecd()
    results = fred.fetch() + oecd.fetch()
    ids = {m.series_id: m for _, m in results}
    assert set(ids) == {
        "labor_share_nfb",
        "profit_share",
        "us_labor_tax_share",
        "oecd_labor_tax_share_usa",
        "oecd_labor_tax_share_avg",
    }
    for df, meta in results:
        assert isinstance(meta, SeriesMeta)
        for key, value in asdict(meta).items():
            if key in ("breaks", "notes"):
                continue
            assert value not in (None, ""), f"{meta.series_id}.{key} is empty"
        assert meta.frequency in FREQUENCIES
        assert meta.role in ROLES
        assert meta.indicator_id in ("E1", "G1")
        assert meta.max_lag_days > 0
        assert meta.data_through == df["date"].max().strftime("%Y-%m-%d")
        assert meta.fetched_at.endswith("Z") or "+00:00" in meta.fetched_at
        assert meta.source_url.startswith("https://")
    assert ids["profit_share"].role == "context"
    assert ids["oecd_labor_tax_share_avg"].role == "context"
    assert ids["labor_share_nfb"].role == "primary"
    assert ids["us_labor_tax_share"].role == "primary"


@responses.activate
def test_labor_share_full_when_no_existing_file(tmp_path):
    _mock_fred()
    fred.fetch(data_dir=tmp_path)
    expected = len(range(fred.BLS_FIRST_YEAR, date.today().year + 1, fred.BLS_CHUNK_YEARS))
    assert len(_bls_calls()) == expected > 1


@responses.activate
def test_labor_share_incremental_uses_one_request_and_merges(tmp_path):
    _mock_fred()
    pd.DataFrame(
        {"date": pd.to_datetime(["1950-01-01", "2026-04-01"]), "value": [60.0, 99.9]}
    ).to_csv(tmp_path / "labor_share_nfb.csv", index=False)
    df, _ = _by_id(fred.fetch(data_dir=tmp_path))["labor_share_nfb"]
    assert len(_bls_calls()) == 1
    assert df[df["date"] == "1950-01-01"]["value"].iloc[0] == 60.0  # kept from history
    assert df[df["date"] == "2026-04-01"]["value"].iloc[0] == pytest.approx(53.3)  # revised
    assert df["date"].is_unique and df["date"].is_monotonic_increasing


@responses.activate
def test_labor_share_full_flag_refetches_history(tmp_path):
    _mock_fred()
    pd.DataFrame({"date": pd.to_datetime(["1950-01-01"]), "value": [60.0]}).to_csv(
        tmp_path / "labor_share_nfb.csv", index=False
    )
    fred.fetch(data_dir=tmp_path, full=True)
    assert len(_bls_calls()) > 1


@pytest.mark.live
def test_live_labor_share_2026q2_matches_bls():
    # The plan expected 52.8, but BLS series PRS85006174 now publishes 53.3 for 2026Q2
    # (revised); see review/figure-verification.md. Assert the published value.
    df, _ = _by_id(fred.fetch())["labor_share_nfb"]
    value = df[df["date"] == "2026-04-01"]["value"].iloc[0]
    assert value == pytest.approx(53.3, abs=0.05)


@pytest.mark.live
def test_live_oecd_avg_2023():
    avg, _ = _by_id(oecd.fetch())["oecd_labor_tax_share_avg"]
    value = avg[avg["date"] == "2023-01-01"]["value"].iloc[0]
    assert value == pytest.approx(49.2, abs=0.3)
