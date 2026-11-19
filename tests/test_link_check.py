"""scripts/link_check.py: broken internal links in a built site."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "link_check", Path(__file__).resolve().parents[1] / "scripts" / "link_check.py")
link_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(link_check)


def _site(tmp_path, pages: dict[str, str], files: tuple[str, ...] = ()) -> Path:
    for rel, html in pages.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html, encoding="utf-8")
    for rel in files:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x\n", encoding="utf-8")
    return tmp_path


def test_link_check_flags_missing_csv(tmp_path):
    site = _site(tmp_path, {"index.html": '<a href="data/gone.csv">csv</a><a href="data/here.csv">ok</a>'},
                 files=("data/here.csv",))
    broken = link_check.check(site)
    assert len(broken) == 1
    assert "data/gone.csv" in broken[0] and "index.html" in broken[0]


def test_link_check_accepts_relative_links_under_base_path(tmp_path):
    site = _site(
        tmp_path,
        {"index.html": '<a href="about.html#top">a</a><a href="data/s.csv">c</a>'
                       '<a href="indicators/EA1.html">i</a>',
         "about.html": '<a href="index.html">home</a><img src="site_libs/x.png">',
         "indicators/EA1.html": '<a href="../index.html">up</a><script src="../site_libs/a.js"></script>'},
        files=("data/s.csv", "site_libs/a.js", "site_libs/x.png"))
    assert link_check.check(site, "/keel/") == []


def test_link_check_flags_root_absolute_links_even_when_they_resolve(tmp_path):
    site = _site(tmp_path, {"index.html": '<a href="/keel/about.html">a</a><a href="/about.html">b</a>',
                            "about.html": ""})
    broken = link_check.check(site)
    assert len(broken) == 2
    assert all("root-absolute" in b for b in broken)


def test_link_check_ignores_external_and_fragments_but_flags_wrong_base(tmp_path):
    site = _site(tmp_path, {"index.html": '<a href="https://example.org/x">e</a><a href="mailto:a@b.c">m</a>'
                                          '<a href="#sec">f</a><a href="/other/about.html">bad</a>',
                            "about.html": ""})
    broken = link_check.check(site)
    assert len(broken) == 1 and "/other/about.html" in broken[0]
