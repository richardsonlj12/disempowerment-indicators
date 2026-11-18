"""Page generator (Task 10): builds the Quarto sources in a copy of the repository."""

import re
import shutil
from datetime import date
from pathlib import Path

import pandas as pd
import pytest
import yaml

from indicators import pages

ROOT = Path(__file__).resolve().parent.parent
RELEASE1 = {"E1", "E2", "E3", "G1", "C1"}
TABLE_ROWS = ["Summary", "Current reading", "Grid position", "AI link", "Leading or lagging",
              "Warning sign", "Data source(s)", "Calculation", "Coverage"]
INTERNAL_KEYS = ["structural", "ai_native", "exposure", "erosion", "lockin", "tier"]
TODAY = date(2026, 11, 18)

SYNTHETIC_PAGE = """---
summary: Neutral summary text.
warning_sign: Neutral warning text.
data_sources:
  - name: Source one
    url: https://example.org/one
calculation: Neutral calculation text.
coverage: Somewhere · monthly · from 2000
---

## Why this matters for gradual disempowerment

Neutral.

## What it shows

Neutral.

## What it doesn't show

Neutral.

## What would change our reading

### Warning sign

Neutral.

### Alternative explanations

Neutral.

## Data and calculation

Neutral.

## Caveats

Neutral.
"""


def _copy_site_sources(dest: Path) -> None:
    generated = {"_site", ".quarto", "data", "config", "indicators", "_generated"}
    shutil.copytree(ROOT / "site", dest, ignore=lambda d, names: [
        n for n in names if Path(d) == ROOT / "site" and n in generated])


@pytest.fixture
def repo(tmp_path):
    """A copy of config/, the top-level data/ files, content/ and the site sources."""
    shutil.copytree(ROOT / "config", tmp_path / "config")
    shutil.copytree(ROOT / "content", tmp_path / "content")
    (tmp_path / "data").mkdir()
    for f in (ROOT / "data").iterdir():
        if f.is_file():
            shutil.copy(f, tmp_path / "data" / f.name)
    _copy_site_sources(tmp_path / "site")
    return tmp_path


def _page(repo, ind_id):
    return (repo / "site" / "indicators" / f"{ind_id}.qmd").read_text(encoding="utf-8")


def _front_matter(text):
    return yaml.safe_load(text.split("---\n", 2)[1])


def _table(text):
    rows = []
    for line in text.splitlines():
        m = re.match(r"^\| ([^|]+?) \| (.*) \|$", line)
        if m and not set(m.group(1)) <= set("-: "):
            rows.append((m.group(1), m.group(2)))
    return rows


def _index(repo):
    site = repo / "site"
    return (site / "index.qmd").read_text(encoding="utf-8") + (site / "_generated" / "summary.md").read_text(encoding="utf-8")


def _cells(index_text):
    """Grid cells as {(row, domain): body} from the fenced divs in the summary."""
    cells = {}
    for m in re.finditer(r'^::: \{\.keel-cell row="([^"]+)" domain="([^"]+)"\}\n(.*?)\n:::$',
                         index_text, re.M | re.S):
        cells[(m.group(1), m.group(2))] = m.group(3)
    return cells


def test_build_writes_release1_pages_only(repo):
    reg = yaml.safe_load((repo / "config" / "indicators.yaml").read_text())
    extra = dict(reg["indicators"][0], id="E9", release=2)
    reg["indicators"].append(extra)
    (repo / "config" / "indicators.yaml").write_text(yaml.safe_dump(reg, sort_keys=False))
    pages.build(repo, today=TODAY)
    written = {p.stem for p in (repo / "site" / "indicators").glob("*.qmd")}
    assert written == RELEASE1


def test_title_contains_full_indicator_name(repo):
    pages.build(repo, today=TODAY)
    assert _front_matter(_page(repo, "C1"))["title"] == "C1 · Human knowledge-commons activity"
    assert _front_matter(_page(repo, "E1"))["title"] == "E1 · Labor share of income, nonfarm business"


def test_summary_table_has_nine_rows_in_order(repo):
    pages.build(repo, today=TODAY)
    for ind_id in RELEASE1:
        assert [r for r, _ in _table(_page(repo, ind_id))][:9] == TABLE_ROWS, ind_id


def test_reading_rendered_in_three_lines(repo):
    pages.build(repo, today=TODAY)
    rows = dict(_table(_page(repo, "E1")))
    lines = rows["Current reading"].split("<br>")
    assert len(lines) == 3
    assert "Not yet reviewed" in lines[0]
    assert "2010 to 2019 baseline" in lines[1] and "percent" in lines[1]
    assert lines[2].strip().startswith("AI link: Weak")
    e2_lines = dict(_table(_page(repo, "E2")))["Current reading"].split("<br>")
    assert "own recent path" in e2_lines[1]


def test_data_sources_render_as_links(repo):
    pages.build(repo, today=TODAY)
    cell = dict(_table(_page(repo, "C1")))["Data source(s)"]
    assert "[Stack Exchange API (new questions per month)](https://api.stackexchange.com/docs/questions)" in cell
    assert "(https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/)" in cell


def test_grid_position_and_coverage_filled_automatically(repo):
    pages.build(repo, today=TODAY)
    rows = dict(_table(_page(repo, "G1")))
    assert rows["Grid position"] == "Displacement · Government"
    assert "data through 2026 Q2" in rows["Coverage"]
    assert dict(_table(_page(repo, "E2")))["Grid position"] == "Adoption · Economic"


def test_e3_page_has_caveat_and_disclosure(repo):
    pages.build(repo, today=TODAY)
    text = _page(repo, "E3")
    assert "One vendor, one product: Claude usage only" in text
    assert "This data is published by Anthropic" in text


def test_stale_badge_rendered_when_stale(repo):
    pages.build(repo, today=TODAY)
    assert "Stale since" not in _page(repo, "E2")
    pages.build(repo, today=date(2030, 1, 1))
    assert "Stale since 16 December 2026" in _page(repo, "E2")


def test_all_pages_show_not_yet_reviewed(repo):
    pages.build(repo, today=TODAY)
    for ind_id in RELEASE1:
        assert "Not yet reviewed" in _page(repo, ind_id)
        assert "No reviewed readings yet" in _page(repo, ind_id)
    cells = _cells(_index(repo))
    for (row, _), body in cells.items():
        if row in ("Adoption", "Displacement") and "indicators/" in body:
            assert "Not yet reviewed" in body


def test_trend_csv_for_structural_only(repo):
    pages.build(repo, today=TODAY)
    data = repo / "site" / "data"
    for sid in ("labor_share_nfb", "us_labor_tax_share"):
        frame = pd.read_csv(data / f"{sid}_trend.csv")
        assert list(frame.columns) == ["date", "value", "trend", "deviation", "segment"]
    for sid in ("btos_ai_use", "btos_ai_use_by_size", "aei_automation_share", "aei_augmentation_share"):
        assert not (data / f"{sid}_trend.csv").exists()
    assert (data / "btos_ai_use.csv").exists() and (data / "btos_ai_use.meta.json").exists()


def test_index_lockin_row_says_no_public_measure(repo):
    pages.build(repo, today=TODAY)
    cells = _cells(_index(repo))
    lockin = {d: body for (r, d), body in cells.items() if r == "Lock-in"}
    assert set(lockin) == {"Economic", "Government", "Cultural"}
    assert all("No public measure yet" in body for body in lockin.values())
    assert "No public measure yet" in cells[("Adoption", "Government")]
    assert "indicators/E2.qmd" in cells[("Adoption", "Economic")]


def test_index_has_oversight_row_with_citation(repo):
    pages.build(repo, today=TODAY)
    text = _index(repo)
    block = text[text.index("Human deferral and oversight"):]
    block = block[:block.index("\n:::\n")]
    assert "No public measure yet" in block
    assert "https://www.anthropic.com/research/agents-judgment-calls" in block
    assert "Herdağdelen, Joren and Tamkin (2026)" in block


def test_index_has_scales_note_placeholder_counter_evidence_and_archive(repo):
    pages.build(repo, today=TODAY)
    text = _index(repo)
    assert "Low, Rising" in text and "Within baseline" in text
    assert "Readings begin after the threshold rule is reviewed and frozen" in text
    assert "Labor-based taxes remain about half of OECD tax revenue" in text
    assert "Written before items were added." in text
    assert "archive.qmd" in text


def test_unverified_curated_items_absent(repo):
    path = repo / "config" / "curated" / "counter_evidence.yaml"
    data = yaml.safe_load(path.read_text())
    data["items"].append(dict(data["items"][0], id="unverified_x", label="UNVERIFIED TEST ITEM",
                              verified=False, verified_on=None))
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    opath = repo / "config" / "curated" / "oversight.yaml"
    odata = yaml.safe_load(opath.read_text())
    odata["items"].append(dict(odata["items"][0], id="unverified_o", label="UNVERIFIED OVERSIGHT ITEM",
                               verified=False, verified_on=None))
    opath.write_text(yaml.safe_dump(odata, sort_keys=False, allow_unicode=True))
    pages.build(repo, today=TODAY)
    text = _index(repo)
    assert "UNVERIFIED TEST ITEM" not in text
    assert "UNVERIFIED OVERSIGHT ITEM" not in text
    assert "Labor-based taxes remain about half of OECD tax revenue" in text


def test_about_has_claude_disclosure():
    text = (ROOT / "site" / "about.qmd").read_text(encoding="utf-8")
    assert "built with assistance from Claude (Anthropic)" in text


def test_about_has_author_section_and_acronym():
    text = (ROOT / "site" / "about.qmd").read_text(encoding="utf-8")
    assert "## About the author" in text
    assert "Jeremy Richardson, Ph.D." in text
    assert "[OWNER TO EDIT]" in text
    assert "https://richardsonlj.substack.com/" in text
    assert text.count("Key Evidence on Eroding Leverage") == 1
    assert "https://github.com/richardsonlj12/keel/issues/new?template=error-report.md" in text
    assert "https://github.com/richardsonlj12/keel/discussions" in text


def test_footer_and_substack_link_on_every_page():
    config = yaml.safe_load((ROOT / "site" / "_quarto.yml").read_text(encoding="utf-8"))
    footer = config["website"]["page-footer"]
    footer_text = yaml.safe_dump(footer)
    assert "by Jeremy Richardson" in footer_text
    assert "[Substack](https://richardsonlj.substack.com/)" in footer_text
    for qmd in (ROOT / "site").glob("*.qmd"):
        assert "page-footer" not in qmd.read_text(encoding="utf-8"), qmd.name


def test_site_url_uses_keel_base_path():
    config = yaml.safe_load((ROOT / "site" / "_quarto.yml").read_text(encoding="utf-8"))
    assert config["website"]["site-url"] == "https://richardsonlj12.github.io/keel/"
    assert config["website"]["navbar"]["title"] == "KEEL"
    for qmd in (ROOT / "site").glob("[!_]*.qmd"):
        assert "pagetitle:" in qmd.read_text(encoding="utf-8") and " · KEEL" in qmd.read_text(encoding="utf-8"), qmd.name
    assert config["project"]["output-dir"] == "_site"


def test_no_angle_bracket_placeholders_in_generated_qmd(repo):
    pages.build(repo, today=TODAY)
    generated = list((repo / "site" / "indicators").glob("*.qmd")) + [repo / "site" / "_generated" / "summary.md"]
    for path in generated:
        text = path.read_text(encoding="utf-8")
        tags = set(re.findall(r"<([^<>\s/]+)[^<>]*>", text))
        assert tags <= {"br"}, (path.name, tags)
        assert "%%" not in text, path.name


def test_no_internal_keys_in_generated_text(repo):
    for ind_id in RELEASE1:
        (repo / "content" / "indicators" / f"{ind_id}.md").write_text(SYNTHETIC_PAGE, encoding="utf-8")
    pages.build(repo, today=TODAY)
    generated = list((repo / "site" / "indicators").glob("*.qmd")) + [repo / "site" / "_generated" / "summary.md"]
    for path in generated:
        text = re.sub(r"```\{ojs\}.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
        for key in INTERNAL_KEYS:
            assert not re.search(rf"\b{key}\b", text, re.I), (path.name, key)
        assert "AI-specificity" not in text, path.name


def test_c1_says_data_still_being_collected_when_series_absent(repo):
    for f in (repo / "data").glob("s[oe]_*"):
        f.unlink()
    pages.build(repo, today=TODAY)
    text = _page(repo, "C1")
    assert "Data still being collected" in text
    assert "Wikipedia" in text


def test_c1_views_listed_in_chart_spec(repo):
    pages.build(repo, today=TODAY)
    text = _page(repo, "C1")
    for label in ("Relative activity index (2019 = 100)", "Change since November 2022",
                  "Year-over-year gap (alternative view)", "Monthly questions", "Wikipedia"):
        assert label in text
    assert "By firm size" in _page(repo, "E2")
    assert "Deviation from 2010–19 trend" in _page(repo, "E1")


def test_csv_links_relative(repo):
    pages.build(repo, today=TODAY)
    text = _page(repo, "E1")
    assert "](../data/labor_share_nfb.csv)" in text
    assert "](../data/labor_share_nfb_trend.csv)" in text
    assert "](../archive.qmd)" in text
