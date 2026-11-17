import json
from datetime import date

import pandas as pd

from indicators import refresh
from indicators.store import SeriesMeta, read_series


def _meta(series_id="s1", through="2026-09-30"):
    return SeriesMeta(
        series_id=series_id, indicator_id="E1", title="t", units="u", frequency="quarterly",
        source_name="src", source_url="https://example.org", license="CC0",
        fetched_at="2026-11-17T00:00:00Z", data_through=through, max_lag_days=100,
    )


def _frame(values=(1.0, 2.0)):
    return pd.DataFrame({"date": pd.to_datetime(["2026-06-30", "2026-09-30"]), "value": list(values)})


def _health(tmp_path):
    return json.loads((tmp_path / "_health.json").read_text())["sources"]


def test_refresh_isolates_source_failure(tmp_path):
    def boom():
        raise RuntimeError("upstream down")

    out = refresh.run(tmp_path, sources={"bad": boom, "good": lambda: [(_frame(), _meta())]},
                      today=date(2026, 11, 17))
    assert out["sources"]["bad"]["status"] == "failed"
    assert "upstream down" in out["sources"]["bad"]["error"]
    assert out["sources"]["good"] == {"status": "ok", "data_through": "2026-09-30"}
    df, _ = read_series("s1", tmp_path)
    assert len(df) == 2
    assert _health(tmp_path)["good"]["status"] == "ok"


def test_refresh_attaches_chart_markers_without_splitting(tmp_path):
    refresh.run(tmp_path, sources={"a": lambda: [(_frame(), _meta())]}, today=date(2026, 11, 17))
    _, meta = read_series("s1", tmp_path)  # indicator E1: only the all-indicator ChatGPT marker
    assert meta.annotations == [{"date": "2022-11-30", "label": "ChatGPT released to the public"}]
    assert meta.breaks == []


def test_refresh_keeps_last_good_on_invalid_payload(tmp_path):
    refresh.run(tmp_path, sources={"a": lambda: [(_frame(), _meta())]}, today=date(2026, 11, 1))
    before = (tmp_path / "s1.csv").read_text()
    bad = _frame().assign(value=[1.0, float("nan")])
    # a valid first series plus an invalid second one: nothing from this source may be written
    out = refresh.run(
        tmp_path,
        sources={"a": lambda: [(_frame((9.0, 9.0)), _meta()), (bad, _meta("s2"))]},
        today=date(2026, 11, 2),
    )
    assert out["sources"]["a"]["status"] == "failed"
    assert (tmp_path / "s1.csv").read_text() == before
    assert not (tmp_path / "s2.csv").exists()


def test_failure_since_date_persists(tmp_path):
    def boom():
        raise RuntimeError("x")

    refresh.run(tmp_path, sources={"a": boom}, today=date(2026, 11, 1))
    out = refresh.run(tmp_path, sources={"a": boom}, today=date(2026, 11, 5))
    assert out["sources"]["a"]["since"] == "2026-11-01"
    # recovery clears it; a new failure starts a new streak
    refresh.run(tmp_path, sources={"a": lambda: [(_frame(), _meta())]}, today=date(2026, 11, 6))
    assert "since" not in _health(tmp_path)["a"]
    out = refresh.run(tmp_path, sources={"a": boom}, today=date(2026, 11, 9))
    assert out["sources"]["a"]["since"] == "2026-11-09"


def test_main_exit_code_and_only_flag(tmp_path, monkeypatch):
    def boom():
        raise RuntimeError("x")

    monkeypatch.setattr(refresh, "default_sources",
                        lambda data_dir, full: {"a": boom, "b": lambda: [(_frame(), _meta())]})
    assert refresh.main(["--data-dir", str(tmp_path)]) == 1
    assert refresh.main(["--data-dir", str(tmp_path), "--only", "b"]) == 0
    assert set(_health(tmp_path)) == {"a", "b"}  # a's earlier failure is retained


def test_default_sources_pass_data_dir_and_full(tmp_path):
    srcs = refresh.default_sources(tmp_path, full=True)
    assert set(srcs) == {"fred", "oecd", "btos", "aei", "stackexchange", "wikimedia"}
    assert refresh.default_data_dir().is_absolute()
