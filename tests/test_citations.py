"""In-text citations on the pages: every link to a Sources entry resolves, and works in the bibliography
are cited through the Sources page, not linked directly (Sources batch, Part 2)."""

import re
import shutil
from pathlib import Path

import pytest
import yaml

from indicators import bibliography as bib
from indicators import pages

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "references" / "keel.json"
SOURCE_LINK = re.compile(r"\]\((?:\.\./)?sources\.qmd#([A-Za-z0-9_-]+)\)")
MD_LINK_TARGET = re.compile(r"\]\((https?://[^)\s]+)\)")
HAND_WRITTEN = sorted((ROOT / "content").rglob("*.md")) + sorted((ROOT / "site").glob("*.qmd"))
CURATED = ROOT / "config" / "curated"


@pytest.fixture(scope="module")
def entries():
    return {e["id"]: e for e in bib.load(BIB)}


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """The generated pages (indicator pages, summary, methodology, Sources) from a copy of the repo."""
    root = tmp_path_factory.mktemp("repo")
    for d in ("config", "content", "references"):
        shutil.copytree(ROOT / d, root / d)
    (root / "data").mkdir()
    for f in (ROOT / "data").iterdir():
        if f.is_file():
            shutil.copy(f, root / "data" / f.name)
    skip = {"_site", ".quarto", "data", "config", "indicators", "_generated"}
    shutil.copytree(ROOT / "site", root / "site",
                    ignore=lambda d, names: [n for n in names if Path(d) == ROOT / "site" and n in skip])
    pages.build(root)
    out = sorted((root / "site" / "indicators").glob("*.qmd")) + sorted((root / "site" / "_generated").glob("*.md"))
    return {p.relative_to(root).as_posix(): p.read_text(encoding="utf-8") for p in out}


def _rel(p):
    return p.relative_to(ROOT).as_posix()


def _bibliography_urls(entries):
    return {u: key for key, e in entries.items() for u in bib.entry_urls(e)}


@pytest.mark.parametrize("path", HAND_WRITTEN, ids=_rel)
def test_citation_links_resolve(path, entries):
    for key in SOURCE_LINK.findall(path.read_text(encoding="utf-8")):
        assert key in entries, f"{_rel(path)} links sources.qmd#{key}, which is not in the bibliography"


def test_generated_citation_links_resolve(built, entries):
    found = 0
    for name, text in built.items():
        for key in SOURCE_LINK.findall(text):
            found += 1
            assert key in entries, f"{name} links sources.qmd#{key}"
    assert found > 20


def test_indicator_pages_use_the_right_relative_path(built):
    for name, text in built.items():
        if name.startswith("site/indicators/"):
            assert "](sources.qmd#" not in text, name
    for path in (ROOT / "content" / "indicators").glob("*.md"):
        assert "](sources.qmd#" not in path.read_text(encoding="utf-8"), path.name
    assert "](../sources.qmd#" not in (ROOT / "content" / "methodology.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("path", HAND_WRITTEN, ids=_rel)
def test_no_bare_links_to_works_in_the_bibliography(path, entries):
    """A work or dataset in the bibliography is cited through its Sources entry, not linked directly."""
    urls = _bibliography_urls(entries)
    for target in MD_LINK_TARGET.findall(path.read_text(encoding="utf-8")):
        assert target not in urls, f"{_rel(path)} links {target} directly; cite {urls[target]} instead"


def test_no_bare_links_to_works_in_generated_pages(built, entries):
    urls = _bibliography_urls(entries)
    for name, text in built.items():
        if name.endswith("_generated/sources.md"):
            continue
        for target in MD_LINK_TARGET.findall(text):
            assert bib.link_target(target) not in {bib.link_target(u) for u in urls}, (name, target)


def test_no_known_old_source_links_in_content():
    """The links replaced by citations in Part 2 (arXiv and RAND landing pages are not the displayed links)."""
    for path in HAND_WRITTEN:
        text = path.read_text(encoding="utf-8")
        for old in ("](https://arxiv.org/abs/", "](https://www.rand.org/pubs/", "](https://aclanthology.org/",
                    "](https://intelligence-curse.ai/"):
            assert old not in text, (_rel(path), old)


def test_curated_items_cite_a_bibliography_entry_with_the_same_url(entries):
    for name in ("oversight.yaml", "counter_evidence.yaml"):
        for item in yaml.safe_load((CURATED / name).read_text(encoding="utf-8"))["items"]:
            key = item["source_key"]
            assert key in entries, (name, key)
            if entries[key]["type"] != "dataset":  # a dataset item may link a specific data request
                assert item["source_url"] in bib.entry_urls(entries[key]), (name, key)


def test_chart_markers_cite_a_bibliography_entry_with_the_same_url(entries):
    markers = yaml.safe_load((ROOT / "config" / "chart_markers.yaml").read_text(encoding="utf-8"))["markers"]
    for rows in markers.values():
        for m in rows:
            assert m["source_key"] in entries, m
            assert m["source_url"] in bib.entry_urls(entries[m["source_key"]]), m


def test_methodology_sources_section_points_to_the_sources_page():
    text = (ROOT / "content" / "methodology.md").read_text(encoding="utf-8")
    section = text[text.index("## Sources and disclosure {#sources}"):]
    assert "<!-- SOURCES" not in text
    assert "[Sources](sources.qmd)" in section
    assert "\n- [" not in section, "the list of sources is replaced by the Sources page"
    assert "KEEL is built with assistance from Claude (Anthropic)." in section
    assert "Every entry was checked against the original publication before it was added. KEEL is built with assistance from Claude (see [Disclosure](about.qmd#disclosure))." in section
    assert "about.qmd#report-an-error-or-give-feedback" in section
