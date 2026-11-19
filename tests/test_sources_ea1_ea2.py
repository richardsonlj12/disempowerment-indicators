"""Tests for the BTOS (EA1) and Anthropic Economic Index (EA2) source modules."""

import io
import json
import re
from pathlib import Path
from urllib.parse import quote

import openpyxl
import pandas as pd
import pytest
import responses

from indicators.http import SourceError
from indicators.sources import aei, btos
from indicators.store import FREQUENCIES, ROLES, validate_frame

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def isolated_cwd(tmp_path, monkeypatch):
    """Default data dir is relative; keep offline tests away from any committed data/."""
    monkeypatch.chdir(tmp_path)


def _by_id(results):
    return {meta.series_id: (df, meta) for df, meta in results}


# ---------------------------------------------------------------- BTOS


def _btos_bytes(name: str) -> bytes:
    return (FIXTURES / "btos" / name).read_bytes()


def _mock_btos(national: bytes | None = None, core: bytes | None = None, size: bytes | None = None):
    xlsx = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    responses.add(
        responses.GET,
        "https://www.census.gov/hfp/btos/downloads/National.xlsx",
        body=national or _btos_bytes("National.xlsx"),
        content_type=xlsx,
    )
    responses.add(
        responses.GET,
        "https://www.census.gov/hfp/btos/downloads/" + quote("AI Core Questions.xlsx"),
        body=core or _btos_bytes("AI_Core_Questions.xlsx"),
        content_type=xlsx,
    )
    responses.add(
        responses.GET,
        "https://www.census.gov/hfp/btos/downloads/" + quote("Employment Size Class.xlsx"),
        body=size or _btos_bytes("Employment_Size_Class.xlsx"),
        content_type=xlsx,
    )


def _btos_series():
    df, meta = _by_id(btos.fetch())["btos_ai_use"]
    return df, meta


@responses.activate
def test_btos_by_size_class_series():
    _mock_btos()
    df, meta = _by_id(btos.fetch())["btos_ai_use_by_size"]
    validate_frame(df)
    assert meta.indicator_id == "EA1" and meta.role == "context" and meta.frequency == "biweekly"
    assert meta.units == "percent" and meta.breaks == []
    assert set(df["group"]) == {
        "1 to 4 employees", "5 to 9 employees", "10 to 19 employees", "20 to 49 employees",
        "50 to 99 employees", "100 to 249 employees", "250 or more employees",
    }
    small = df[df["group"] == "1 to 4 employees"].set_index("date")
    large = df[df["group"] == "250 or more employees"].set_index("date")
    # First period 202524 (collection ends 2025-11-30) and latest 202622 (ends 2026-11-01).
    assert small.index.min() == pd.Timestamp("2025-11-30") and small.index.max() == pd.Timestamp("2026-11-01")
    assert small.loc["2025-11-30", "value"] == 17.0 and small.loc["2026-11-01", "value"] == 22.8
    assert large.loc["2026-11-01", "value"] == 44.1
    assert (df["se"] >= 0).all() and len(small) == 25
    assert meta.data_through == "2026-11-01"
    assert "202524 to 202622" in meta.notes and "202319" not in meta.notes
    assert "Firm-weighted" in meta.notes and "Employment Size Class.xlsx" in meta.notes


@responses.activate
def test_btos_by_size_unknown_wording_raises():
    changed = _rewrite_question(
        _btos_bytes("Employment_Size_Class.xlsx"), "Response Estimates", "in any of its business functions", "somewhere else"
    )
    _mock_btos(size=changed)
    with pytest.raises(SourceError):
        btos.fetch()


@responses.activate
def test_btos_break_assigned():
    _mock_btos()
    df, meta = _btos_series()
    validate_frame(df)
    assert meta.breaks == [
        {
            "date": "2025-11-17",
            "note": "Question changed from AI use 'in producing goods or services' to 'in any business function'",
        }
    ]
    before = df[df["date"] < "2025-11-17"]
    after = df[df["date"] >= "2025-11-17"]
    assert len(before) and len(after)
    assert (before["segment"] == 0).all()
    assert (after["segment"] == 1).all()


@responses.activate
def test_btos_value_is_percent():
    _mock_btos()
    df, meta = _btos_series()
    assert meta.units == "percent" and meta.frequency == "biweekly"
    assert meta.indicator_id == "EA1" and meta.role == "primary"
    assert df["value"].between(0, 100).all()
    # Dated by collection end; values are percent, not fractions.
    by_date = df.set_index("date")["value"]
    assert by_date[pd.Timestamp("2023-09-24")] == pytest.approx(3.7)  # 202319, old wording
    assert by_date[pd.Timestamp("2025-10-05")] == pytest.approx(10.0)  # 202520, last old-wording period
    assert by_date[pd.Timestamp("2025-11-30")] == pytest.approx(17.3)  # 202524, first new-wording period
    assert by_date[pd.Timestamp("2026-05-03")] == pytest.approx(19.8)  # 202609
    assert df["date"].is_unique and df["date"].is_monotonic_increasing


@responses.activate
def test_btos_se_nonnegative_when_present():
    _mock_btos()
    df, _ = _btos_series()
    assert "se" in df.columns and pd.api.types.is_float_dtype(df["se"])
    present = df["se"].dropna()
    assert len(present) == len(df)
    assert (present >= 0).all()
    assert df.set_index("date")["se"][pd.Timestamp("2026-05-03")] == pytest.approx(0.24)


@responses.activate
def test_btos_meta_records_questions_and_sources():
    _mock_btos()
    _, meta = _btos_series()
    assert meta.source_url == "https://www.census.gov/hfp/btos"
    assert "in producing goods or services" in meta.notes
    assert "in any of its business functions" in meta.notes
    assert "202520" in meta.notes and "202524" in meta.notes
    assert meta.frequency in FREQUENCIES and meta.role in ROLES
    assert meta.data_through == "2026-11-01"


def _rewrite_question(data: bytes, sheet: str, old: str, new: str) -> bytes:
    wb = openpyxl.load_workbook(io.BytesIO(data))
    for row in wb[sheet].iter_rows(min_row=2):
        for cell in row[:3]:  # the question text is in column B (national) or C (size class)
            if isinstance(cell.value, str) and old in cell.value:
                cell.value = cell.value.replace(old, new)
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


@responses.activate
def test_btos_unknown_question_wording_raises():
    changed = _rewrite_question(
        _btos_bytes("National.xlsx"), "Response Estimates", "in any of its business functions", "somewhere else"
    )
    _mock_btos(national=changed)
    with pytest.raises(SourceError):
        btos.fetch()


@pytest.mark.live
def test_live_btos_may_2026_near_19_8():
    df, _ = _btos_series()
    may = df[(df["date"] >= "2026-05-01") & (df["date"] <= "2026-05-31")]
    assert len(may) > 0
    assert may["value"].between(19.3, 20.3).any()


# ---------------------------------------------------------------- Economic Index

EXPECTED = {
    # sample start: (automation, augmentation); classifiable denominator, hand-computed in the
    # fixtures' units. April and May 2026 come from the five pattern rows (Anthropic's rounded
    # totals are 48.98 and 48.62).
    "2024-12-16": (42.55375, 57.44625),
    "2025-02-01": (43.06188, 56.93812),
    "2025-08-04": (51.06977, 48.93023),
    "2025-11-13": (46.73940, 53.26060),
    "2026-02-05": (45.54558, 54.45442),
    "2026-04-01": (48.97875, 51.02125),
    "2026-05-01": (48.61895, 51.38105),
}
EXPECTED_PERIODS = {
    "2024-12-16": ("16–23 Dec 2024", "2025-02-10"),
    "2025-02-01": ("Feb–Mar 2025", "2025-03-27"),
    "2025-08-04": ("4–11 Aug 2025", "2025-09-15"),
    "2025-11-13": ("13–20 Nov 2025", "2026-01-15"),
    "2026-02-05": ("5–12 Feb 2026", "2026-03-24"),
    "2026-04-01": ("April 2026", "2026-06-26"),
    "2026-05-01": ("May 2026", "2026-06-26"),
}

HF = "https://huggingface.co/datasets/Anthropic/EconomicIndex/resolve/main/"
TREE = "https://huggingface.co/api/datasets/Anthropic/EconomicIndex/tree/main"

FIXTURE_FOR = {
    "release_2025_02_10": "release_2025_02_10_automation_vs_augmentation.csv",
    "release_2025_03_27": "release_2025_03_27_automation_vs_augmentation_v2.csv",
    "release_2025_09_15": "release_2025_09_15_raw_claude_ai.csv",
    "release_2026_01_15": "release_2026_01_15_raw_claude_ai.csv",
    "release_2026_03_24": "release_2026_03_24_raw_claude_ai.csv",
    "release_2026_06_26": "release_2026_06_26_claude_ai.csv",
}


def _aei_text(release: str) -> str:
    return (FIXTURES / "aei" / FIXTURE_FOR[release]).read_text(encoding="utf-8")


def _mock_aei(overrides: dict[str, str] | None = None, extra_dirs: tuple[str, ...] = ()):
    overrides = overrides or {}
    listing = [{"type": "directory", "path": r} for r in aei.RELEASE_SCHEMAS]
    listing += [{"type": "directory", "path": d} for d in ("labor_market_impacts", "robot_exposure") + extra_dirs]
    listing += [{"type": "file", "path": "README.md"}]
    responses.add(responses.GET, TREE, body=json.dumps(listing), content_type="application/json")
    for release, schema in aei.RELEASE_SCHEMAS.items():
        responses.add(
            responses.GET,
            HF + schema["path"],
            body=overrides.get(release, _aei_text(release)),
            content_type="text/csv",
        )


def _aei():
    return _by_id(aei.fetch())


def _hf_calls():
    return [c for c in responses.calls if c.request.url.startswith(HF)]


@responses.activate
def test_aei_release_schema_mapping():
    _mock_aei()
    out = _aei()
    auto, auto_meta = out["aei_automation_share"]
    aug, aug_meta = out["aei_augmentation_share"]
    assert set(aei.RELEASE_SCHEMAS) == set(FIXTURE_FOR)
    for df in (auto, aug):
        validate_frame(df)
    assert set(auto["date"].dt.strftime("%Y-%m-%d")) == set(EXPECTED)
    for date, (a, g) in EXPECTED.items():
        assert auto.set_index("date")["value"][pd.Timestamp(date)] == pytest.approx(a, abs=1e-4)
        assert aug.set_index("date")["value"][pd.Timestamp(date)] == pytest.approx(g, abs=1e-4)
    assert auto_meta.indicator_id == aug_meta.indicator_id == "EA2"
    assert auto_meta.role == "primary" and aug_meta.role == "context"
    assert auto_meta.frequency == aug_meta.frequency == "irregular"
    assert auto_meta.units == "percent"
    # Each mapping is listed in the notes.
    for release in aei.RELEASE_SCHEMAS:
        assert release in auto_meta.notes
    assert "directive" in auto_meta.notes and "feedback loop" in auto_meta.notes
    assert "learning" in auto_meta.notes and "validation" in auto_meta.notes


@responses.activate
def test_aei_points_dated_by_sample_window_with_period_and_release():
    _mock_aei()
    auto, _ = _aei()["aei_automation_share"]
    for _, row in auto.iterrows():
        key = row["date"].strftime("%Y-%m-%d")
        assert (row["period"], row["release"]) == EXPECTED_PERIODS[key]
        assert row["sample_end"] >= key


@responses.activate
def test_aei_patterns_add_up_to_the_totals():
    _mock_aei()
    out = _aei()
    patterns, meta = out["aei_patterns"]
    validate_frame(patterns)
    assert meta.role == "context" and meta.indicator_id == "EA2"
    assert set(patterns["group"]) == {"directive", "feedback_loop", "task_iteration", "learning", "validation"}
    wide = patterns.pivot(index="date", columns="group", values="value")
    assert (wide.sum(axis=1) - 100).abs().max() < 1e-9
    auto = out["aei_automation_share"][0].set_index("date")["value"]
    assert ((wide["directive"] + wide["feedback_loop"]) - auto).abs().max() < 1e-9
    # Hand-checked pattern share: August 2025 directive, 38.7798 of 96.1391 classifiable
    # (38.7798 + 10.3182 + 22.2233 + 20.3381 + 4.4797).
    assert wide.loc[pd.Timestamp("2025-08-04"), "directive"] == pytest.approx(40.3372, abs=1e-3)


@responses.activate
def test_aei_monthly_patterns_must_match_published_totals():
    text = _aei_text("release_2026_06_26").replace("collaboration_directive_pct,31.72", "collaboration_directive_pct,35.72")
    _mock_aei({"release_2026_06_26": text})
    with pytest.raises(SourceError, match="Anthropic's totals"):
        aei.fetch()


@responses.activate
def test_aei_unknown_schema_raises_rather_than_guessing():
    # Header of a raw release renamed: must raise, not guess a mapping.
    text = _aei_text("release_2026_01_15").replace("cluster_name", "node_name", 1)
    _mock_aei({"release_2026_01_15": text})
    with pytest.raises(SourceError, match="release_2026_01_15"):
        aei.fetch()


@responses.activate
def test_aei_unknown_collaboration_label_raises():
    text = _aei_text("release_2025_09_15").replace(",directive,", ",autonomous,")
    _mock_aei({"release_2025_09_15": text})
    with pytest.raises(SourceError, match="autonomous"):
        aei.fetch()


@responses.activate
def test_aei_new_release_without_schema_raises():
    _mock_aei(extra_dirs=("release_2026_09_30",))
    with pytest.raises(SourceError, match="release_2026_09_30"):
        aei.fetch()


@responses.activate
def test_aei_shares_bounded():
    _mock_aei()
    out = _aei()
    auto = out["aei_automation_share"][0].set_index("date")["value"]
    aug = out["aei_augmentation_share"][0].set_index("date")["value"]
    assert auto.between(0, 100).all() and aug.between(0, 100).all()
    assert ((auto + aug) <= 100 + 1e-6).all()
    assert list(auto.index) == list(aug.index)


@responses.activate
def test_aei_breaks_and_segments():
    _mock_aei()
    out = _aei()
    for sid in ("aei_automation_share", "aei_augmentation_share"):
        df, meta = out[sid]
        assert meta.breaks == aei.BREAKS
        assert {b["date"] for b in meta.breaks} == {"2025-08-04", "2026-02-05", "2026-04-01"}
        seg = df.set_index(df["date"].dt.strftime("%Y-%m-%d"))["segment"]
        assert seg["2024-12-16"] == 0 and seg["2025-02-01"] == 0 and seg["2025-08-04"] == 1
        assert seg["2025-11-13"] == 1 and seg["2026-02-05"] == 2
        assert seg["2026-04-01"] == 3 and seg["2026-05-01"] == 3


@responses.activate
def test_aei_incremental_skips_committed_releases(tmp_path):
    _mock_aei()
    first = aei.fetch(data_dir=tmp_path)
    for df, meta in first:
        df.drop(columns=["segment"]).to_csv(tmp_path / f"{meta.series_id}.csv", index=False)
    responses.calls.reset()
    second = aei.fetch(data_dir=tmp_path)
    assert _hf_calls() == []  # every release already committed: only the listing is checked
    for (a, _), (b, _) in zip(first, second):
        pd.testing.assert_frame_equal(a.reset_index(drop=True), b.reset_index(drop=True), check_dtype=False)


@responses.activate
def test_aei_full_flag_refetches(tmp_path):
    _mock_aei()
    for df, meta in aei.fetch(data_dir=tmp_path):
        df.drop(columns=["segment"]).to_csv(tmp_path / f"{meta.series_id}.csv", index=False)
    responses.calls.reset()
    aei.fetch(data_dir=tmp_path, full=True)
    assert len(_hf_calls()) == len(aei.RELEASE_SCHEMAS)


@responses.activate
def test_aei_meta_fields_complete():
    _mock_aei()
    for df, meta in aei.fetch():
        for key in ("series_id", "title", "units", "source_name", "source_url", "license", "fetched_at", "data_through"):
            assert getattr(meta, key), key
        assert meta.max_lag_days > 0
        assert meta.data_through == "2026-05-31"  # last day of the latest sample window
        assert "CC-BY" in meta.license
        assert meta.source_url == "https://huggingface.co/datasets/Anthropic/EconomicIndex"


@pytest.mark.live
def test_live_aei_release_listing_has_no_unmapped_release():
    from indicators import http

    names = {e["path"] for e in http.get(TREE, expect="json").json() if e["type"] == "directory"}
    unmapped = {n for n in names if n.startswith("release_")} - set(aei.RELEASE_SCHEMAS)
    assert not unmapped
