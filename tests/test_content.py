"""Checks on the page prose in content/ (owner requests, Batch C)."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
INDICATOR_PAGES = sorted((CONTENT / "indicators").glob("*.md"))
METHODOLOGY = CONTENT / "methodology.md"
CLOSING_PAGES = INDICATOR_PAGES + [METHODOLOGY]
ABOUT = ROOT / "site" / "about.qmd"
ALL_CONTENT = sorted(CONTENT.rglob("*.md"))

CLOSING = (
    "These indicators show whether the conditions for disempowerment are present. "
    "They do not show whether it is happening."
)
RETIRED_CLOSING_PHRASES = ["that it is happening", "or that it is not"]

REPORT_ERROR = "[Report an error](https://github.com/richardsonlj12/keel/issues/new?template=error-report.md)"
JOIN_DISCUSSION = "[Join the discussion](https://github.com/richardsonlj12/keel/discussions)"
SEND_PRIVATE = ("[Send private feedback](https://docs.google.com/forms/d/e/1FAIpQLSdJn9K0revpwU1sWM-WPmqlPtw80JVSuR9lIzcPktXqY7e3Tg/viewform)")
FORM_PLACEHOLDER = "[feedback form link]"


def _ids(paths):
    return [p.relative_to(CONTENT).as_posix() for p in paths]


def test_content_pages_exist():
    assert {p.stem for p in INDICATOR_PAGES} >= {"ED1", "EA1", "EA2", "GD1", "CD1"}
    assert METHODOLOGY.exists(), "content/methodology.md must exist with a lowercase name"


@pytest.mark.parametrize("path", CLOSING_PAGES, ids=_ids(CLOSING_PAGES))
def test_page_has_standard_closing_line(path):
    assert CLOSING in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", ALL_CONTENT, ids=_ids(ALL_CONTENT))
def test_no_retired_closing_wording(path):
    text = path.read_text(encoding="utf-8")
    for phrase in RETIRED_CLOSING_PHRASES:
        assert phrase not in text, f"{path.name} still contains {phrase!r}"


@pytest.mark.parametrize("path", INDICATOR_PAGES + [ABOUT], ids=_ids(INDICATOR_PAGES) + ["about.qmd"])
def test_page_links_feedback_channels(path):
    """All three feedback channels are linked (link text may vary by page)."""
    text = path.read_text(encoding="utf-8")
    assert "https://github.com/richardsonlj12/keel/issues/new?template=error-report.md" in text
    assert "https://github.com/richardsonlj12/keel/discussions" in text
    assert "https://docs.google.com/forms/d/e/1FAIpQLSdJn9K0revpwU1sWM-WPmqlPtw80JVSuR9lIzcPktXqY7e3Tg/viewform" in text


@pytest.mark.parametrize("path", INDICATOR_PAGES, ids=_ids(INDICATOR_PAGES))
def test_indicator_page_ends_with_feedback_line(path):
    """Owner decision (2026-11-18): one line, sentence-case labels, same URLs and order."""
    last = path.read_text(encoding="utf-8").rstrip().splitlines()[-1]
    assert last == f"**Feedback.** {REPORT_ERROR} · {JOIN_DISCUSSION} · {SEND_PRIVATE}"


def test_ea2_has_no_inline_disclosure_paragraph():
    """Owner decision (2026-11-18): the generated Disclosure callout is the only disclosure on EA2."""
    assert "**Disclosure.**" not in (CONTENT / "indicators" / "EA2.md").read_text(encoding="utf-8")


PLURAL_DATA_PAGES = ALL_CONTENT + sorted((ROOT / "site").glob("*.qmd")) + [ROOT / "config" / "indicators.yaml"]


@pytest.mark.parametrize("path", PLURAL_DATA_PAGES, ids=lambda p: p.relative_to(ROOT).as_posix())
def test_data_is_plural(path):
    """Owner wording rule: "these data", plural verbs ("the data are"). Fixed phrases such as "data source"
    are not affected."""
    text = path.read_text(encoding="utf-8").lower()
    assert "this data " not in text and "this data." not in text
    for singular in ("data is ", "data says ", "data shows ", "data does ", "data was ", "data has "):
        assert singular not in text, (path.name, singular)


@pytest.mark.release_gate
@pytest.mark.parametrize("path", ALL_CONTENT, ids=_ids(ALL_CONTENT))
def test_feedback_form_link_supplied(path):
    """Blocks release (Task 12) until the owner supplies the Google Form URL."""
    assert FORM_PLACEHOLDER not in path.read_text(encoding="utf-8")


@pytest.mark.release_gate
@pytest.mark.parametrize("path", ALL_CONTENT, ids=_ids(ALL_CONTENT))
def test_no_unapproved_drafts(path):
    """Blocks release until the owner approves or removes every [DRAFT FOR OWNER] passage."""
    assert "[DRAFT FOR OWNER]" not in path.read_text(encoding="utf-8")


METHODOLOGY_H2_IDS = ["what-keel-measures", "how-to-read-an-indicator", "how-readings-are-made",
                      "guards", "roadmap", "sources"]


def test_methodology_sections_and_index():
    """Exactly six H2 sections with explicit ids, in order, all linked from the "On this page" index."""
    import re

    text = METHODOLOGY.read_text(encoding="utf-8")
    h2 = re.findall(r"^## .*$", text, flags=re.M)
    ids = [m.group(1) if (m := re.search(r"\{#([\w-]+)\}\s*$", h)) else None for h in h2]
    assert ids == METHODOLOGY_H2_IDS, h2
    index = next(line for line in text.splitlines() if line.startswith("**On this page:**"))
    assert re.findall(r"\]\(#([\w-]+)\)", index) == METHODOLOGY_H2_IDS
    assert text.index(index) < text.index(h2[0])


def test_methodology_feedback_points_to_about():
    """The methodology page links the About page's feedback section, which carries the three channels."""
    assert "about.qmd#report-an-error-or-give-feedback" in METHODOLOGY.read_text(encoding="utf-8")
    assert "## Report an error or give feedback" in ABOUT.read_text(encoding="utf-8")
