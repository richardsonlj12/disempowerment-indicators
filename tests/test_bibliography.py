"""Bibliography (references/keel.json) and the Sources page generated from it."""

import json
import re
import shutil
from pathlib import Path

import pytest
import responses
import yaml

from indicators import bibliography as bib

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "references" / "keel.json"
CSL = ROOT / "references" / "chicago-author-date-17th-edition.csl"
REFERENCE_KEY = re.compile(r"^[a-z]+\d{4}[a-z]?$")
DATASET_KEY = re.compile(r"^[a-z0-9_]+$")


@pytest.fixture(scope="module")
def entries():
    return bib.load(BIB)


# ------------------------------------------------------------------ the bibliography file

def test_bibliography_and_style_files_exist():
    assert BIB.exists()
    assert CSL.exists()
    assert "Chicago Manual of Style 17th edition (author-date)" in CSL.read_text(encoding="utf-8")


def test_keys_unique_and_well_formed(entries):
    keys = [e["id"] for e in entries]
    assert len(keys) == len(set(keys)), "duplicate keys"
    for e in entries:
        pattern = DATASET_KEY if e["type"] == "dataset" else REFERENCE_KEY
        assert pattern.match(e["id"]), e["id"]


def test_reference_key_is_first_author_surname_and_year(entries):
    for e in entries:
        if e["type"] == "dataset":
            continue
        first = e["author"][0]
        year = str(e["issued"]["date-parts"][0][0])
        if "literal" in first:  # an organization: one word of its name, e.g. census2025
            stems = [re.sub(r"[^a-z]", "", w) for w in first["literal"].lower().split()]
        else:
            stems = [re.sub(r"[^a-z]", "", first["family"].lower().translate(str.maketrans("ğçşıöüé", "gcsioue")))]
        assert any(re.fullmatch(rf"{re.escape(s)}{year}[a-z]?", e["id"]) for s in stems), (e["id"], stems, year)


def test_key_letter_matches_displayed_year_suffix(entries):
    """kulveit2025 shows 2025; herdagdelen2026a shows 2026a. A key letter appears only when needed."""
    suffixes = bib.year_suffixes(entries)
    for e in entries:
        if e["type"] == "dataset":
            continue
        letter = e["id"][-1] if e["id"][-1].isalpha() else ""
        assert suffixes.get(e["id"], "") == letter, e["id"]


@pytest.mark.parametrize("entry", json.loads(BIB.read_text(encoding="utf-8")), ids=lambda e: e["id"])
def test_entry_has_required_fields_for_its_type(entry):
    assert bib.missing_fields(entry) == [], entry["id"]


def test_types_are_supported(entries):
    assert {e["type"] for e in entries} <= set(bib.REQUIRED)


def test_every_entry_has_url_or_doi_except_books(entries):
    for e in entries:
        if e["type"] == "book":
            assert e.get("publisher") and e.get("issued"), e["id"]
        else:
            assert e.get("URL") or e.get("DOI"), e["id"]


def test_urls_are_https(entries):
    for e in entries:
        if e.get("URL"):
            assert e["URL"].startswith("https://"), e["id"]


def test_datasets_have_access_date_and_license(entries):
    datasets = [e for e in entries if e["type"] == "dataset"]
    assert datasets
    for e in datasets:
        assert e.get("accessed") and e.get("license"), e["id"]


def _front_matter_sources():
    urls = []
    for page in sorted((ROOT / "content" / "indicators").glob("*.md")):
        front = yaml.safe_load(page.read_text(encoding="utf-8").split("---\n", 2)[1])
        urls += [s["url"] for s in front.get("data_sources", [])]
    return urls


def test_registry_and_page_data_sources_are_in_the_bibliography(entries):
    """Every data source a page or the registry links is a Data sources entry."""
    urls = {e.get("URL") for e in entries if e["type"] == "dataset"}
    reg = yaml.safe_load((ROOT / "config" / "indicators.yaml").read_text(encoding="utf-8"))
    registry = [s["url"] for i in reg["indicators"] for s in i.get("sources", [])]
    for url in registry + _front_matter_sources():
        assert url in urls, url


def test_oversight_citation_is_in_the_bibliography(entries):
    items = yaml.safe_load((ROOT / "config" / "curated" / "oversight.yaml").read_text(encoding="utf-8"))["items"]
    urls = {e.get("URL") for e in entries}
    for item in items:
        assert item["source_url"] in urls, item["source_url"]


# ------------------------------------------------------------------ formatting (Chicago author-date, 17th ed.)

def _person(family, given):
    return {"family": family, "given": given}


def test_names_one_two_three():
    assert bib.format_names([_person("Krueger", "David Scott")]) == "Krueger, David Scott."
    assert bib.format_names([_person("Moon", "Alvin"), _person("Boudreaux", "Benjamin")]) == \
        "Moon, Alvin, and Benjamin Boudreaux."
    assert bib.format_names([_person("Brynjolfsson", "Erik"), _person("Chandar", "Bharat"), _person("Chen", "Ruyu")]) == \
        "Brynjolfsson, Erik, Bharat Chandar, and Ruyu Chen."
    assert bib.format_names([{"literal": "U.S. Census Bureau"}]) == "U.S. Census Bureau."
    assert bib.format_names([_person("Allen", "Jeffrey S.")]) == "Allen, Jeffrey S."


def test_names_more_than_ten_list_seven_then_et_al():
    people = [_person(f"Name{i}", "A.") for i in range(11)]
    out = bib.format_names(people)
    assert out.endswith("Name6, et al.")
    assert "Name7" not in out
    ten = [_person(f"Name{i}", "B") for i in range(10)]
    assert bib.format_names(ten).endswith("and B Name9.")


@pytest.mark.parametrize("pages,expected", [
    ("3-10", "3–10"), ("71-72", "71–72"), ("96-117", "96–117"), ("100-104", "100–104"),
    ("101-108", "101–8"), ("1100-1113", "1100–1113"), ("107-109", "107–9"), ("321-328", "321–28"),
    ("498-532", "498–532"), ("1087-1089", "1087–89"), ("1496-1504", "1496–504"), ("2787-2816", "2787–816"),
    ("227-236", "227–36"),
])
def test_chicago_page_ranges(pages, expected):
    """CMOS 17, 9.64 (abbreviating, or condensing, inclusive numbers)."""
    assert bib.page_range(pages) == expected


def test_full_date_repeats_the_year():
    assert bib.full_date({"date-parts": [[2026, 10, 27]]}) == "October 27, 2026"
    assert bib.full_date({"date-parts": [[2026, 8]]}) == "August 2026"
    assert bib.full_date({"date-parts": [[2026]]}) is None


def test_preprint_format():
    e = {"id": "doe2025", "type": "article", "author": [_person("Doe", "Jane")], "title": "A Title",
         "genre": "Preprint", "publisher": "arXiv", "number": "arXiv:2501.00001",
         "issued": {"date-parts": [[2025, 1, 28]]}, "DOI": "10.48550/arXiv.2501.00001",
         "URL": "https://arxiv.org/abs/2501.00001"}
    assert bib.format_entry(e) == (
        "Doe, Jane. 2025. “A Title.” Preprint, arXiv:2501.00001, January 28, 2025. "
        "[https://doi.org/10.48550/arXiv.2501.00001](https://doi.org/10.48550/arXiv.2501.00001).")


def test_blog_post_format_italic_blog_name_and_full_date():
    e = {"id": "doe2026", "type": "post-weblog", "author": [_person("Doe", "Jane")], "title": "Has It?",
         "container-title": "Some Newsletter", "issued": {"date-parts": [[2026, 9, 29]]},
         "URL": "https://example.substack.com/p/has-it"}
    assert bib.format_entry(e) == (
        "Doe, Jane. 2026. “Has It?” *Some Newsletter* (blog). September 29, 2026. "
        "[https://example.substack.com/p/has-it](https://example.substack.com/p/has-it).")


def test_blog_name_containing_blog_gets_no_label_and_publisher_follows():
    e = {"id": "doe2025", "type": "post-weblog", "author": [_person("Doe", "Jo")], "title": "T",
         "container-title": "Jo's Blog", "publisher": "Org", "issued": {"date-parts": [[2025, 11, 23]]},
         "URL": "https://example.org/t"}
    assert "*Jo's Blog*, Org. November 23, 2025." in bib.format_entry(e)


def test_webpage_format_roman_site_name():
    e = {"id": "doe2026", "type": "webpage", "author": [_person("Doe", "Jane")], "title": "Page",
         "container-title": "Example Research", "issued": {"date-parts": [[2026, 10, 27]]},
         "URL": "https://example.com/page"}
    assert bib.format_entry(e).startswith("Doe, Jane. 2026. “Page.” Example Research. October 27, 2026. [")


def test_report_format():
    e = {"id": "moon2026", "type": "report", "author": [_person("Moon", "Alvin"), _person("Boudreaux", "Benjamin")],
         "title": "A Formal Model", "number": "RR-A4817-1", "publisher": "RAND Corporation",
         "publisher-place": "Santa Monica, CA", "issued": {"date-parts": [[2026, 4, 20]]},
         "DOI": "10.7249/RRA4817-1", "URL": "https://www.rand.org/x.html"}
    assert bib.format_entry(e) == (
        "Moon, Alvin, and Benjamin Boudreaux. 2026. *A Formal Model*. RR-A4817-1. Santa Monica, CA: "
        "RAND Corporation, April 20, 2026. [https://doi.org/10.7249/RRA4817-1](https://doi.org/10.7249/RRA4817-1).")


def test_report_in_series_without_publisher():
    e = {"id": "x2025", "type": "report", "author": [{"literal": "Agency"}], "title": "Updates",
         "collection-title": "Notes", "issued": {"date-parts": [[2025, 12, 3]]}, "URL": "https://example.gov/a%20b.pdf"}
    assert bib.format_entry(e) == ("Agency. 2025. *Updates*. Notes. December 3, 2025. "
                                   "[https://example.gov/a%20b.pdf](https://example.gov/a%20b.pdf).")


def test_conference_paper_format():
    e = {"id": "chooi2026", "type": "paper-conference", "author": [_person("Chooi", "Jay")], "title": "Measuring",
         "container-title": "Proceedings of the Workshop", "page": "227-236",
         "publisher": "Association for Computational Linguistics", "publisher-place": "San Diego, CA",
         "issued": {"date-parts": [[2026, 7]]}, "DOI": "10.18653/v1/x"}
    assert bib.format_entry(e) == (
        "Chooi, Jay. 2026. “Measuring.” In *Proceedings of the Workshop*, 227–36. San Diego, CA: "
        "Association for Computational Linguistics. [https://doi.org/10.18653/v1/x](https://doi.org/10.18653/v1/x).")


def test_chapter_format():
    e = {"id": "a2026", "type": "chapter", "author": [_person("A", "B")], "title": "Policy",
         "chapter-number": "8", "container-title": "The Report", "publisher": "Inst", "publisher-place": "Stanford, CA",
         "issued": {"date-parts": [[2026, 4]]}, "URL": "https://example.edu/ch8.pdf"}
    assert bib.format_entry(e) == ("A, B. 2026. “Policy.” Chap. 8 in *The Report*. Stanford, CA: Inst. "
                                   "[https://example.edu/ch8.pdf](https://example.edu/ch8.pdf).")


def test_book_format():
    e = {"id": "a2020", "type": "book", "author": [_person("A", "B")], "title": "Book",
         "publisher": "Press", "publisher-place": "City", "issued": {"date-parts": [[2020]]}}
    assert bib.format_entry(e) == "A, B. 2020. *Book*. City: Press."


def test_dataset_format_with_access_date_and_license():
    e = {"id": "fred_gdp", "type": "dataset", "author": [{"literal": "U.S. Bureau of Economic Analysis"}],
         "title": "Gross Domestic Product [GDP]", "publisher": "FRED, Federal Reserve Bank of St. Louis",
         "accessed": {"date-parts": [[2026, 11, 18]]}, "license": "US government work, public domain",
         "URL": "https://fred.stlouisfed.org/series/GDP"}
    assert bib.format_entry(e) == (
        "U.S. Bureau of Economic Analysis. n.d. “Gross Domestic Product \\[GDP\\].” FRED, Federal Reserve Bank of "
        "St. Louis. Accessed November 18, 2026. [https://fred.stlouisfed.org/series/GDP](https://fred.stlouisfed.org/series/GDP). "
        "License: US government work, public domain.")


def test_markdown_specials_are_escaped():
    e = {"id": "oecd", "type": "dataset", "author": [{"literal": "OECD"}], "title": "Stats [A@B]",
         "accessed": {"date-parts": [[2026, 11, 18]]}, "license": "Terms",
         "URL": "https://data.example.org/?df[ds]=X&df[id]=A%40B"}
    out = bib.format_entry(e)
    assert "“Stats \\[A\\@B\\].”" in out
    assert "(https://data.example.org/?df%5Bds%5D=X&df%5Bid%5D=A%40B)" in out
    assert "[https://data.example.org/?df\\[ds\\]=X&df\\[id\\]=A%40B]" in out


def test_title_ending_in_question_mark_takes_no_period():
    e = {"id": "a2026", "type": "webpage", "author": [_person("A", "B")], "title": "Why?",
         "container-title": "Site", "issued": {"date-parts": [[2026, 1, 2]]}, "URL": "https://e.org/"}
    assert "“Why?” Site." in bib.format_entry(e)


def test_same_authors_same_year_get_letter_suffixes():
    a = {"id": "doe2026a", "type": "webpage", "author": [_person("Doe", "Jane")], "title": "Alpha",
         "container-title": "S", "issued": {"date-parts": [[2026, 10, 27]]}, "URL": "https://e.org/a"}
    b = {"id": "doe2026b", "type": "report", "author": [_person("Doe", "Jane")], "title": "Beta",
         "issued": {"date-parts": [[2026]]}, "URL": "https://e.org/b"}
    suffixes = bib.year_suffixes([b, a])
    assert suffixes == {"doe2026a": "a", "doe2026b": "b"}
    assert bib.format_entry(a, suffixes).startswith("Doe, Jane. 2026a.")


# ------------------------------------------------------------------ the Sources page

@pytest.fixture
def sources_md(tmp_path, entries):
    (tmp_path / "references").mkdir()
    shutil.copy(BIB, tmp_path / "references" / "keel.json")
    (tmp_path / "site" / "_generated").mkdir(parents=True)
    bib.write_sources_page(tmp_path)
    return (tmp_path / "site" / "_generated" / "sources.md").read_text(encoding="utf-8")


def _anchors(text):
    return re.findall(r"^::: \{#([\w-]+) \.keel-ref\}$", text, flags=re.M)


def test_every_key_renders_an_anchor(sources_md, entries):
    assert sorted(_anchors(sources_md)) == sorted(e["id"] for e in entries)


def test_two_sections_in_order_with_datasets_last(sources_md, entries):
    h2 = re.findall(r"^## (.+)$", sources_md, flags=re.M)
    assert h2 == ["References {#references}", "Data sources {#data-sources}"]
    refs, data = sources_md.split("## Data sources", 1)
    datasets = {e["id"] for e in entries if e["type"] == "dataset"}
    assert set(_anchors(data)) == datasets
    assert not set(_anchors(refs)) & datasets


def test_sections_are_alphabetical(sources_md):
    for section in sources_md.split("## Data sources", 1):
        bodies = re.findall(r"^::: \{#[\w-]+ \.keel-ref\}\n(.+)$", section, flags=re.M)
        keys = [bib.sort_text(b) for b in bodies]
        assert keys == sorted(keys)


def test_every_url_and_doi_is_a_clickable_link(sources_md, entries):
    for e in entries:
        for url in bib.entry_urls(e)[:1]:  # the displayed one: DOI when present, else URL
            assert f"]({bib.link_target(url)})" in sources_md, e["id"]


def test_sources_qmd_includes_generated_page():
    text = (ROOT / "site" / "sources.qmd").read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---\n", 2)[1])
    assert front["title"] == "Sources" and front["pagetitle"] == "Sources · KEEL"
    assert "{{< include _generated/sources.md >}}" in text


# ------------------------------------------------------------------ link check

def test_entry_urls_lists_doi_first_then_url():
    e = {"DOI": "10.1/x", "URL": "https://e.org/"}
    assert bib.entry_urls(e) == ["https://doi.org/10.1/x", "https://e.org/"]


@responses.activate
def test_classify_ok_blocked_broken():
    responses.add(responses.GET, "https://ok.example/", status=200)
    responses.add(responses.GET, "https://redir.example/", status=301, headers={"Location": "https://ok.example/"})
    responses.add(responses.GET, "https://blocked.example/", status=403)
    responses.add(responses.GET, "https://gone.example/", status=404)
    assert bib.check_url("https://ok.example/").status == "OK"
    assert bib.check_url("https://redir.example/").status == "OK"
    blocked = bib.check_url("https://blocked.example/")
    assert blocked.status == bib.OWNER_CHECK and blocked.code == 403
    assert bib.check_url("https://gone.example/").status == "broken"


@responses.activate
def test_connection_failure_is_owner_check_not_pass():
    import requests

    responses.add(responses.GET, "https://slow.example/", body=requests.exceptions.ReadTimeout("timed out"))
    result = bib.check_url("https://slow.example/")
    assert result.status == bib.OWNER_CHECK and result.code is None


def test_link_check_report_lists_every_url(entries):
    results = [bib.LinkResult(key=e["id"], url=u, status="OK", code=200, detail="")
               for e in entries for u in bib.entry_urls(e)]
    report = bib.link_check_report(results, "2026-11-18")
    for r in results:
        assert r.url in report
    assert "OK: " in report and "owner browser check: 0" in report and "broken: 0" in report


@pytest.mark.live
@pytest.mark.release_gate
def test_live_every_bibliography_url_resolves(entries):
    """Owner requirement: every URL on the Sources page resolves. Sites that block scripts are listed
    for an owner browser check (review/sources-link-check.md), never passed silently."""
    results = bib.check_all(entries)
    broken = [(r.key, r.url, r.code, r.detail) for r in results if r.status == "broken"]
    assert not broken, broken
    unchecked = {r.url for r in results if r.status == bib.OWNER_CHECK}
    assert unchecked <= bib.OWNER_BROWSER_CHECKED, sorted(unchecked - bib.OWNER_BROWSER_CHECKED)
