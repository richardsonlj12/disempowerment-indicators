"""Checks on the page prose in content/ (owner requests, Batch C)."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
INDICATOR_PAGES = sorted((CONTENT / "indicators").glob("*.md"))
METHODOLOGY = CONTENT / "methodology.md"
CLOSING_PAGES = INDICATOR_PAGES + [METHODOLOGY]
ALL_CONTENT = sorted(CONTENT.rglob("*.md"))

CLOSING = (
    "These indicators show whether the conditions for disempowerment are present. "
    "They do not show whether it is happening."
)
RETIRED_CLOSING_PHRASES = ["that it is happening", "or that it is not"]

REPORT_ERROR = "[Report an error](https://github.com/richardsonlj12/keel/issues/new?template=error-report.md)"
GIVE_FEEDBACK = "[Give feedback](https://github.com/richardsonlj12/keel/discussions)"
FORM_PLACEHOLDER = "[feedback form link]"


def _ids(paths):
    return [p.relative_to(CONTENT).as_posix() for p in paths]


def test_content_pages_exist():
    assert {p.stem for p in INDICATOR_PAGES} >= {"E1", "E2", "E3", "G1", "C1"}
    assert METHODOLOGY.exists(), "content/methodology.md must exist with a lowercase name"


@pytest.mark.parametrize("path", CLOSING_PAGES, ids=_ids(CLOSING_PAGES))
def test_page_has_standard_closing_line(path):
    assert CLOSING in path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", ALL_CONTENT, ids=_ids(ALL_CONTENT))
def test_no_retired_closing_wording(path):
    text = path.read_text(encoding="utf-8")
    for phrase in RETIRED_CLOSING_PHRASES:
        assert phrase not in text, f"{path.name} still contains {phrase!r}"


@pytest.mark.parametrize("path", CLOSING_PAGES, ids=_ids(CLOSING_PAGES))
def test_page_links_feedback_channels(path):
    text = path.read_text(encoding="utf-8")
    assert REPORT_ERROR in text
    assert GIVE_FEEDBACK in text
    assert "Feedback form" in text


@pytest.mark.parametrize("path", INDICATOR_PAGES, ids=_ids(INDICATOR_PAGES))
def test_indicator_page_ends_with_feedback_line(path):
    last = path.read_text(encoding="utf-8").rstrip().splitlines()[-1]
    assert last.startswith("**Feedback.**") and REPORT_ERROR in last


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
