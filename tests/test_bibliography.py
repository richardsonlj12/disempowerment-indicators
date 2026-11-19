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
CSL = ROOT / "references" / "chicago-author-date.csl"
REFERENCE_KEY = re.compile(r"^[a-z]+\d{4}[a-z]?$")
LEGAL_KEY = re.compile(r"^eo\d+$")  # an executive order: "eo" and its number, e.g. eo14434
DATASET_KEY = re.compile(r"^[a-z0-9_]+$")


@pytest.fixture(scope="module")
def entries():
    return bib.load(BIB)


# ------------------------------------------------------------------ the bibliography file

def test_bibliography_and_style_files_exist():
    assert BIB.exists()
    assert CSL.exists()
    assert "Chicago Manual of Style 18th edition (author-date)" in CSL.read_text(encoding="utf-8")
    assert not (ROOT / "references" / "chicago-author-date-17th-edition.csl").exists()


def test_keys_unique_and_well_formed(entries):
    keys = [e["id"] for e in entries]
    assert len(keys) == len(set(keys)), "duplicate keys"
    for e in entries:
        pattern = {"dataset": DATASET_KEY, "legislation": LEGAL_KEY}.get(e["type"], REFERENCE_KEY)
        assert pattern.match(e["id"]), e["id"]


def _stem(word):
    return re.sub(r"[^a-z]", "", word.lower().translate(str.maketrans("ğçşıöüé", "gcsioue")))


def test_reference_key_is_first_author_surname_and_year(entries):
    for e in entries:
        if e["type"] in ("dataset", "legislation"):
            continue
        year = str(e["issued"]["date-parts"][0][0])
        if not e.get("author"):  # no author: consecutive words of the title, e.g. stackoverflow2023
            words = [_stem(w) for w in e["title"].split()]
            stems = ["".join(words[i:j]) for i in range(len(words)) for j in range(i + 1, len(words) + 1)]
        elif "literal" in e["author"][0]:  # an organization: one word of its name, or its initials
            name = e["author"][0]["literal"]
            stems = [_stem(w) for w in name.split()]
            stems.append("".join(w[0].lower() for w in name.split() if w[0].isupper() and w != "U.S."))
        else:
            stems = [_stem(e["author"][0]["family"])]
        assert any(re.fullmatch(rf"{re.escape(s)}{year}[a-z]?", e["id"]) for s in stems if s), (e["id"], stems, year)


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


# ------------------------------------------------------------------ formatting (Chicago author-date, 18th ed.)

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


def test_names_up_to_six_listed_seven_or_more_first_three_then_et_al():
    """CMOS 18: up to six authors are all listed; seven or more, the first three and "et al."
    (CSL chicago-author-date 18th ed.: et-al-min 7, et-al-use-first 3)."""
    six = [_person(f"Name{i}", "B") for i in range(6)]
    assert bib.format_names(six).endswith("and B Name5.")
    seven = [_person(f"Name{i}", "A.") for i in range(7)]
    out = bib.format_names(seven)
    assert out == "Name0, A., A. Name1, A. Name2, et al."


@pytest.mark.parametrize("pages,expected", [
    ("3-10", "3–10"), ("71-72", "71–72"), ("96-117", "96–117"), ("100-104", "100–104"),
    ("101-108", "101–8"), ("1100-1113", "1100–1113"), ("107-109", "107–9"), ("321-328", "321–28"),
    ("498-532", "498–532"), ("1087-1089", "1087–89"), ("1496-1504", "1496–504"), ("2787-2816", "2787–816"),
    ("227-236", "227–36"), ("323-359", "323–59"),
])
def test_chicago_page_ranges(pages, expected):
    """CMOS 9.64 (abbreviating, or condensing, inclusive numbers)."""
    assert bib.page_range(pages) == expected


def test_month_day_does_not_repeat_the_year():
    """CMOS 18 author-date: the year follows the author; a month and day follow later without the year."""
    assert bib.month_day({"date-parts": [[2026, 10, 27]]}) == "October 27"
    assert bib.month_day({"date-parts": [[2026, 8]]}) is None
    assert bib.month_day({"date-parts": [[2026]]}) is None


def test_preprint_format():
    e = {"id": "doe2025", "type": "article", "author": [_person("Doe", "Jane")], "title": "A Title",
         "genre": "Preprint", "publisher": "arXiv", "number": "arXiv:2501.00001",
         "issued": {"date-parts": [[2025, 1, 28]]}, "DOI": "10.48550/arXiv.2501.00001",
         "URL": "https://arxiv.org/abs/2501.00001"}
    assert bib.format_entry(e) == (
        "Doe, Jane. 2025. “A Title.” Preprint, arXiv, January 28. "
        "[https://doi.org/10.48550/arXiv.2501.00001](https://doi.org/10.48550/arXiv.2501.00001).")


def test_blog_post_format_italic_blog_name_then_month_day():
    e = {"id": "doe2026", "type": "post-weblog", "author": [_person("Doe", "Jane")], "title": "Has It?",
         "container-title": "Some Newsletter", "issued": {"date-parts": [[2026, 9, 29]]},
         "URL": "https://example.substack.com/p/has-it"}
    assert bib.format_entry(e) == (
        "Doe, Jane. 2026. “Has It?” *Some Newsletter* (blog), September 29. "
        "[https://example.substack.com/p/has-it](https://example.substack.com/p/has-it).")


def test_blog_name_containing_blog_gets_no_label_and_publisher_follows():
    e = {"id": "doe2025", "type": "post-weblog", "author": [_person("Doe", "Jo")], "title": "T",
         "container-title": "Jo’s Blog", "publisher": "Org", "issued": {"date-parts": [[2025, 11, 23]]},
         "URL": "https://example.org/t"}
    assert "“T.” *Jo’s Blog*, Org, November 23. [" in bib.format_entry(e)


def test_webpage_format_roman_site_name():
    e = {"id": "doe2026", "type": "webpage", "author": [_person("Doe", "Jane")], "title": "Page",
         "container-title": "Example Research", "issued": {"date-parts": [[2026, 10, 27]]},
         "URL": "https://example.com/page"}
    assert bib.format_entry(e).startswith("Doe, Jane. 2026. “Page.” Example Research, October 27. [")


def test_webpage_without_author_starts_with_title():
    """CMOS 18: with no author, the title takes the author's place, and the in-text citation uses it."""
    e = {"id": "dear2023", "type": "webpage", "title": "Dear Stack Overflow, Inc.", "container-title": "Open letter",
         "issued": {"date-parts": [[2023, 6, 5]]}, "URL": "https://example.org/letter"}
    assert bib.missing_fields(e) == []
    assert bib.format_entry(e) == ("“Dear Stack Overflow, Inc.” 2023. Open letter, June 5. "
                                   "[https://example.org/letter](https://example.org/letter).")
    assert bib.in_text(e) == "“Dear Stack Overflow, Inc.” 2023"


def test_report_format_without_place_of_publication():
    """CMOS 18 no longer requires the place of publication; it is omitted even when recorded."""
    e = {"id": "moon2026", "type": "report", "author": [_person("Moon", "Alvin"), _person("Boudreaux", "Benjamin")],
         "title": "A Formal Model", "number": "RR-A4817-1", "publisher": "RAND Corporation",
         "publisher-place": "Santa Monica, CA", "issued": {"date-parts": [[2026, 4, 20]]},
         "DOI": "10.7249/RRA4817-1", "URL": "https://www.rand.org/x.html"}
    assert bib.format_entry(e) == (
        "Moon, Alvin, and Benjamin Boudreaux. 2026. *A Formal Model*. RR-A4817-1. "
        "RAND Corporation, April 20. [https://doi.org/10.7249/RRA4817-1](https://doi.org/10.7249/RRA4817-1).")


def test_report_in_series_without_publisher():
    e = {"id": "x2025", "type": "report", "author": [{"literal": "Agency"}], "title": "Updates",
         "collection-title": "Notes", "issued": {"date-parts": [[2025, 12, 3]]}, "URL": "https://example.gov/a%20b.pdf"}
    assert bib.format_entry(e) == ("Agency. 2025. *Updates*. Notes, December 3. "
                                   "[https://example.gov/a%20b.pdf](https://example.gov/a%20b.pdf).")


def test_report_with_month_only_shows_the_year_only():
    e = {"id": "x2026", "type": "report", "author": [_person("A", "B")], "title": "Paper",
         "publisher": "Lab", "issued": {"date-parts": [[2026, 8]]}, "URL": "https://example.edu/p.pdf"}
    assert bib.format_entry(e) == "A, B. 2026. *Paper*. Lab. [https://example.edu/p.pdf](https://example.edu/p.pdf)."


def test_conference_paper_format_with_editors():
    e = {"id": "chooi2026", "type": "paper-conference", "author": [_person("Chooi", "Jay")], "title": "Measuring",
         "container-title": "Proceedings of the Workshop", "page": "227-236",
         "editor": [_person(f"Ed{i}", "E.") for i in range(9)],
         "publisher": "Association for Computational Linguistics", "publisher-place": "San Diego, CA",
         "issued": {"date-parts": [[2026, 7]]}, "DOI": "10.18653/v1/x"}
    assert bib.format_entry(e) == (
        "Chooi, Jay. 2026. “Measuring.” In *Proceedings of the Workshop*, edited by E. Ed0, E. Ed1, E. Ed2, et al., "
        "227–36. Association for Computational Linguistics. [https://doi.org/10.18653/v1/x](https://doi.org/10.18653/v1/x).")


def test_editors_two():
    assert bib.format_editors([_person("A", "B"), _person("C", "D")]) == "B A and D C"


def test_chapter_format_with_pages():
    e = {"id": "a2026", "type": "chapter", "author": [_person("A", "B")], "title": "Policy",
         "chapter-number": "8", "container-title": "The Report", "page": "323-359", "publisher": "Inst",
         "publisher-place": "Stanford, CA", "issued": {"date-parts": [[2026, 4]]}, "URL": "https://example.edu/ch8.pdf"}
    assert bib.format_entry(e) == ("A, B. 2026. “Policy.” Chap. 8 in *The Report*, 323–59. Inst. "
                                   "[https://example.edu/ch8.pdf](https://example.edu/ch8.pdf).")


def test_journal_article_format():
    e = {"id": "ross2001", "type": "article-journal", "author": [_person("Ross", "Michael L.")],
         "title": "Does Oil Hinder Democracy?", "container-title": "World Politics", "volume": "53",
         "issue": "3", "page": "325-361", "issued": {"date-parts": [[2001, 4]]}, "DOI": "10.1353/wp.2001.0011"}
    assert bib.format_entry(e) == (
        "Ross, Michael L. 2001. “Does Oil Hinder Democracy?” *World Politics* 53 (3): 325–61. "
        "[https://doi.org/10.1353/wp.2001.0011](https://doi.org/10.1353/wp.2001.0011).")


def test_book_format():
    e = {"id": "a2020", "type": "book", "author": [_person("A", "B")], "title": "Book",
         "publisher": "Press", "publisher-place": "City", "issued": {"date-parts": [[2020]]}}
    assert bib.format_entry(e) == "A, B. 2020. *Book*. Press."


def test_executive_order_format():
    """Bluebook legal form (the CSL 18th-edition style follows Bluebook): numbers with commas, the
    Federal Register date with an abbreviated month."""
    e = {"id": "eo14434", "type": "legislation", "title": "Exec. Order No. 14,434", "container-title": "Fed. Reg.",
         "volume": "91", "page": "63,129", "issued": {"date-parts": [[2026, 10, 2]]},
         "URL": "https://www.federalregister.gov/d/2026-20321"}
    assert bib.missing_fields(e) == []
    assert bib.format_entry(e) == ("Exec. Order No. 14,434, 91 Fed. Reg. 63,129 (Oct. 2, 2026). "
                                   "[https://www.federalregister.gov/d/2026-20321](https://www.federalregister.gov/d/2026-20321).")
    assert bib.in_text(e) == "Exec. Order No. 14,434"
    sept = dict(e, issued={"date-parts": [[2026, 9, 29]]})
    assert "(Sept. 29, 2026)" in bib.format_entry(sept)


def test_webpage_last_modified():
    e = {"id": "m2022", "type": "webpage", "author": [{"literal": "Makyen"}], "title": "Policy",
         "container-title": "Meta Stack Overflow", "issued": {"date-parts": [[2022, 12, 5]]},
         "last-modified": {"date-parts": [[2026, 10, 25]]}, "URL": "https://e.org/q"}
    assert "“Policy.” Meta Stack Overflow, December 5, last modified October 25, 2026. [" in bib.format_entry(e)


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
    assert "“Why?” Site, January 2." in bib.format_entry(e)


def test_titles_use_curly_apostrophes(entries):
    for e in entries:
        for field in ("title", "container-title"):
            assert "'" not in e.get(field, ""), (e["id"], field)


def test_licenses_carry_no_provenance_notes(entries):
    """Where a license was read is logged in review/sources-verification.md, not shown on the page."""
    for e in entries:
        if e["type"] == "dataset":
            assert "README" not in e["license"] and "section" not in e["license"], e["id"]


# ------------------------------------------------------------------ in-text citations (CMOS 18)

def test_in_text_author_forms():
    one = {"id": "a", "type": "webpage", "author": [_person("Krueger", "David")], "issued": {"date-parts": [[2025]]}}
    two = {"id": "b", "type": "report", "author": [_person("Moon", "A"), _person("Boudreaux", "B")],
           "issued": {"date-parts": [[2026]]}}
    three = {"id": "c", "type": "report", "author": [_person("Chooi", "J"), _person("Lee", "J"), _person("Li", "J")],
             "issued": {"date-parts": [[2026]]}}
    org = {"id": "d", "type": "report", "author": [{"literal": "U.S. Census Bureau"}], "issued": {"date-parts": [[2025]]}}
    assert bib.in_text(one) == "Krueger 2025"
    assert bib.in_text(two) == "Moon and Boudreaux 2026"
    assert bib.in_text(three) == "Chooi et al. 2026", "CMOS 18: three or more authors take et al. in the text"
    assert bib.in_text(org) == "U.S. Census Bureau 2025"
    assert bib.in_text(three, {"c": "b"}) == "Chooi et al. 2026b"


def test_same_authors_same_year_get_letter_suffixes():
    a = {"id": "doe2026a", "type": "webpage", "author": [_person("Doe", "Jane")], "title": "Alpha",
         "container-title": "S", "issued": {"date-parts": [[2026, 10, 27]]}, "URL": "https://e.org/a"}
    b = {"id": "doe2026b", "type": "report", "author": [_person("Doe", "Jane")], "title": "Beta",
         "issued": {"date-parts": [[2026]]}, "URL": "https://e.org/b"}
    suffixes = bib.year_suffixes([b, a])
    assert suffixes == {"doe2026a": "a", "doe2026b": "b"}
    assert bib.format_entry(a, suffixes).startswith("Doe, Jane. 2026a.")


def test_same_in_text_citation_gets_letter_suffixes_even_with_different_coauthors():
    """Two works that would both be cited "(Doe et al. 2026)" are told apart by letters, in the order they
    appear in the reference list (so "a" is listed first)."""
    a = {"id": "x", "type": "webpage", "author": [_person("Doe", "J"), _person("Roe", "K"), _person("Poe", "L")],
         "title": "Zeta", "container-title": "S", "issued": {"date-parts": [[2026, 1, 2]]}, "URL": "https://e.org/z"}
    b = {"id": "y", "type": "webpage", "author": [_person("Doe", "J"), _person("Moe", "K"), _person("Hoe", "L")],
         "title": "Alpha", "container-title": "S", "issued": {"date-parts": [[2026, 3, 4]]}, "URL": "https://e.org/a"}
    assert bib.year_suffixes([a, b]) == {"y": "a", "x": "b"}
    # list order (author names) wins over title order: "K Moe" is listed before "K Roe" whatever the titles
    a2, b2 = dict(a, title="Alpha"), dict(b, title="Zeta")
    assert bib.year_suffixes([a2, b2]) == {"y": "a", "x": "b"}


def test_letter_a_is_listed_first(sources_md, entries):
    suffixes = bib.year_suffixes(entries)
    order = re.findall(r"^::: \{#([\w-]+) \.keel-ref\}$", sources_md, flags=re.M)
    for key, letter in suffixes.items():
        if letter == "b":
            first = next(k for k, v in suffixes.items() if v == "a" and k[:-1] == key[:-1])
            assert order.index(first) < order.index(key), (first, key)


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


def test_intro_opening_and_no_style_name_on_the_page(sources_md):
    """Owner request (2026-11-18): the Sources page does not name the citation style."""
    assert sources_md.startswith("Works and datasets cited on KEEL. Each entry has a stable link")
    assert ("Every entry was checked against the original publication before it was added. KEEL is built "
            "with assistance from Claude (see [Disclosure](about.qmd#disclosure)).") in sources_md.split("\n\n")[0]
    assert "Chicago" not in sources_md
    assert "Chicago" not in (ROOT / "site" / "sources.qmd").read_text(encoding="utf-8")


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


def test_owner_browser_checks_listed_with_dates_and_shown_in_report():
    for url in ("https://www.bls.gov/productivity/home.htm", "https://fred.stlouisfed.org/series/CPATAX",
                "https://fred.stlouisfed.org/series/GDP", "https://fred.stlouisfed.org/series/W055RC1Q027SBEA",
                "https://fred.stlouisfed.org/series/W054RC1Q027SBEA", "https://fred.stlouisfed.org/series/W782RC1Q027SBEA"):
        assert bib.OWNER_BROWSER_CHECKED[url] == "2026-11-18"
    r = bib.LinkResult("fred_gdp", "https://fred.stlouisfed.org/series/GDP", bib.OWNER_CHECK, None, "ReadTimeout")
    report = bib.link_check_report([r], "2026-11-18")
    assert "owner checked in a browser on 2026-11-18" in report
    footer = report[report.index("## Owner browser checks"):]
    for url, day in bib.OWNER_BROWSER_CHECKED.items():
        assert f"| <{url}> | {day} |" in footer


@pytest.mark.live
@pytest.mark.release_gate
def test_live_every_bibliography_url_resolves(entries):
    """Owner requirement: every URL on the Sources page resolves. Sites that block scripts are listed
    for an owner browser check (review/sources-link-check.md), never passed silently."""
    results = bib.check_all(entries)
    broken = [(r.key, r.url, r.code, r.detail) for r in results if r.status == "broken"]
    assert not broken, broken
    unchecked = {r.url for r in results if r.status == bib.OWNER_CHECK}
    assert unchecked <= set(bib.OWNER_BROWSER_CHECKED), sorted(unchecked - set(bib.OWNER_BROWSER_CHECKED))
