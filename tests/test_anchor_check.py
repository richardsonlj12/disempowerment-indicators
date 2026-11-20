"""Where internal links land (scripts/anchor_check.py). The owner found linked headings hidden under
the top bar, or far below it, three times before release (2026-11-20)."""
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import anchor_check  # noqa: E402


@pytest.mark.parametrize("m, problem", [
    ({"top": 72, "height": 30, "bar": 61, "end": False}, None),           # just below a showing bar
    ({"top": 12, "height": 30, "bar": 0, "end": False}, None),            # bar hidden, near the top
    ({"top": -20, "height": 30, "bar": 61, "end": False}, "hidden under"),
    ({"top": 200, "height": 30, "bar": 61, "end": False}, "below the bar"),
    ({"top": 346, "height": 30, "bar": 61, "end": True}, None),           # end of page: cannot scroll further
    ({"top": 100, "height": 0, "bar": 61, "end": False}, "hidden"),
    ({"missing": True}, "not found"),
])
def test_landing_rules(m, problem):
    why = anchor_check._verdict(m)
    assert (why is None) if problem is None else (problem in why), why


@pytest.mark.release_gate
def test_every_internal_link_lands_below_the_top_bar():
    """Blocks release: follow every internal link on a desktop and a phone screen in Chrome. Needs a
    full build first: cd site && quarto render."""
    if importlib.util.find_spec("playwright") is None:
        pytest.fail("Playwright is not installed: pip install -e '.[dev,browser]'")
    site = ROOT / "site" / "_site"
    assert (site / "index.html").is_file(), "build the site first: cd site && quarto render"
    counts: dict = {}
    problems = anchor_check.check(site, counts)
    assert counts.get("desktop", 0) > 50 and counts.get("phone", 0) > 50, counts
    assert not problems, "\n".join(problems)
