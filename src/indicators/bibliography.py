"""Bibliography: references/keel.json (CSL-JSON) rendered as the Sources page, and its link check.

Entries are formatted in Chicago author-date style (17th ed.) by `format_entry`. Rules applied:

- Authors: first author inverted, all authors listed up to ten; more than ten, the first seven and
  "et al." (CMOS 15.9). Repeated authors are written out, not replaced by a 3-em dash, so each entry
  stands alone when reached through its anchor.
- Same authors and same year: letter suffixes (2026a, 2026b), in title order (CMOS 15.19).
- Dates: the year follows the authors. Where the source gives a month or a day (preprints, web pages,
  blog posts, reports), the full date follows the title and container, with the year repeated:
  "2026. ... October 27, 2026." (CMOS 17 author-date, as shown in university library guides to
  the 17th edition: "repeat the year with the month and day to avoid any confusion").
- Titles of standalone works (reports, books) in italics; titles of parts (articles, posts, chapters,
  datasets) in quotation marks; blog names in italics with "(blog)" unless the name says so.
- Page ranges condensed per CMOS 9.64. A DOI, when present, is the link shown; otherwise the URL.
- Datasets (the Data sources section) carry "n.d.", the access date and the license.

CLI: `python -m indicators.bibliography [repo_root]` writes the Sources page;
`python -m indicators.bibliography check-links [repo_root]` writes review/sources-link-check.md.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import requests

BIB_PATH = Path("references") / "keel.json"
SOURCES_MD = Path("site") / "_generated" / "sources.md"
LINK_REPORT = Path("review") / "sources-link-check.md"

REQUIRED = {
    "article": ["author", "title", "issued", "publisher", "number"],
    "paper-conference": ["author", "title", "issued", "container-title", "publisher"],
    "report": ["author", "title", "issued"],
    "chapter": ["author", "title", "issued", "container-title", "publisher"],
    "book": ["author", "title", "issued", "publisher"],
    "post-weblog": ["author", "title", "issued", "container-title"],
    "webpage": ["author", "title", "issued", "container-title"],
    "dataset": ["author", "title", "accessed", "license"],
}
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December")
SECTIONS = (("References", "references"), ("Data sources", "data-sources"))

OK = "OK"
BROKEN = "broken"
OWNER_CHECK = "owner browser check"
# URLs that block scripted requests and that the owner has opened in a browser and confirmed. The
# release-gate link check passes a blocked URL only if it is listed here.
OWNER_BROWSER_CHECKED: set[str] = set()
BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/130.0 Safari/537.36")
BLOCKING_CODES = {401, 403, 429}


# ------------------------------------------------------------------ loading and validation

def load(path: Path) -> list[dict]:
    entries = json.loads(Path(path).read_text(encoding="utf-8"))
    problems = {e.get("id", "?"): missing_fields(e) for e in entries}
    problems = {k: v for k, v in problems.items() if v}
    if problems:
        raise ValueError(f"bibliography entries missing fields: {problems}")
    keys = [e["id"] for e in entries]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate bibliography keys")
    return entries


def missing_fields(entry: dict) -> list[str]:
    if entry.get("type") not in REQUIRED:
        return [f"unsupported type {entry.get('type')!r}"]
    missing = [f for f in ["id"] + REQUIRED[entry["type"]] if not entry.get(f)]
    if entry["type"] != "book" and not (entry.get("URL") or entry.get("DOI")):
        missing.append("URL or DOI")
    return missing


# ------------------------------------------------------------------ formatting pieces

def _md(text: str) -> str:
    """Escape characters that Pandoc Markdown would read as markup (links, citations, emphasis)."""
    return re.sub(r"([\\\[\]@*_`<>])", r"\\\1", str(text))


def _end(text: str) -> str:
    """Close an element with a period unless it already ends in terminal punctuation."""
    return text if text[-1:] in ".?!" else text + "."


def _name(person: dict, inverted: bool) -> str:
    if "literal" in person:
        return person["literal"]
    if inverted:
        return f"{person['family']}, {person['given']}"
    return f"{person['given']} {person['family']}"


def format_names(people: list[dict]) -> str:
    if len(people) > 10:
        shown = [_name(p, i == 0) for i, p in enumerate(people[:7])]
        return _end(", ".join(shown) + ", et al.")
    names = [_name(p, i == 0) for i, p in enumerate(people)]
    if len(names) == 1:
        return _end(names[0])
    return _end(", ".join(names[:-1]) + ", and " + names[-1])


def page_range(pages: str) -> str:
    """Condense an inclusive page range (CMOS 17, 9.64)."""
    first, _, last = pages.replace("–", "-").partition("-")
    if not last:
        return first
    a = int(first)
    if a < 100 or a % 100 == 0 or len(first) != len(last):
        return f"{first}–{last}"
    common = 0
    while common < len(first) and first[common] == last[common]:
        common += 1
    changed = last[common:]
    if a % 100 < 10:  # 101 to 109 in each hundred: the changed part only
        return f"{first}–{changed.lstrip('0') or '0'}"
    return f"{first}–{last[-max(2, len(changed)):]}"  # otherwise two digits, or more as needed


def full_date(issued: dict | None) -> str | None:
    """'October 27, 2026' or 'August 2026'; None when only a year is known."""
    parts = (issued or {}).get("date-parts", [[None]])[0]
    if len(parts) >= 3:
        return f"{MONTHS[parts[1] - 1]} {parts[2]}, {parts[0]}"
    if len(parts) == 2:
        return f"{MONTHS[parts[1] - 1]} {parts[0]}"
    return None


def _year(entry: dict) -> str:
    issued = entry.get("issued")
    return str(issued["date-parts"][0][0]) if issued else "n.d."


def entry_urls(entry: dict) -> list[str]:
    """The URLs an entry carries, the displayed one first: its DOI link when present, then its URL."""
    urls = []
    if entry.get("DOI"):
        urls.append(f"https://doi.org/{entry['DOI']}")
    if entry.get("URL"):
        urls.append(entry["URL"])
    return urls


def link_target(url: str) -> str:
    return url.replace("[", "%5B").replace("]", "%5D")


def _link(url: str) -> str:
    return f"[{_md(url)}]({link_target(url)})"


def _publisher(entry: dict) -> str | None:
    pub = entry.get("publisher")
    place = entry.get("publisher-place")
    if pub and place:
        return f"{_md(place)}: {_md(pub)}"
    return _md(pub) if pub else None


def year_suffixes(entries: list[dict]) -> dict[str, str]:
    """Letter suffixes for works by the same authors in the same year, in title order."""
    groups: dict[tuple, list[dict]] = {}
    for e in entries:
        if e["type"] == "dataset" or not e.get("issued"):
            continue
        groups.setdefault((format_names(e["author"]), _year(e)), []).append(e)
    out = {}
    for group in groups.values():
        if len(group) > 1:
            for i, e in enumerate(sorted(group, key=lambda x: sort_text(x["title"]))):
                out[e["id"]] = "abcdefghijklmnopqrstuvwxyz"[i]
    return out


# ------------------------------------------------------------------ entries

def format_entry(entry: dict, suffixes: dict[str, str] | None = None) -> str:
    """One reference-list entry in Chicago author-date style, as Pandoc Markdown."""
    t = entry["type"]
    year = _year(entry) + (suffixes or {}).get(entry["id"], "")
    parts = [_md(format_names(entry["author"])), _end(year)]
    title = _md(entry["title"])
    quoted = f"“{_end(title)}”"
    date_full = full_date(entry.get("issued"))
    link = entry_urls(entry)[:1]

    if t == "article":
        parts.append(quoted)
        detail = ", ".join(x for x in (entry.get("genre", "Preprint"), _md(entry["number"]), date_full) if x)
        parts.append(_end(detail))
    elif t in ("post-weblog", "webpage"):
        parts.append(quoted)
        site = _md(entry["container-title"])
        if t == "post-weblog":
            site = f"*{site}*" + ("" if "blog" in entry["container-title"].lower() else " (blog)")
        if entry.get("publisher"):
            site += f", {_md(entry['publisher'])}"
        parts.append(_end(site))
        if date_full:
            parts.append(_end(date_full))
    elif t == "report":
        parts.append(f"*{title}*.")
        for field in ("collection-title", "number"):
            if entry.get(field):
                parts.append(_end(_md(entry[field])))
        tail = ", ".join(x for x in (_publisher(entry), date_full) if x)
        if tail:
            parts.append(_end(tail))
    elif t == "paper-conference":
        parts.append(quoted)
        container = f"In *{_md(entry['container-title'])}*"
        if entry.get("page"):
            container += f", {page_range(entry['page'])}"
        parts.append(_end(container))
        parts.append(_end(_publisher(entry)))
    elif t == "chapter":
        parts.append(quoted)
        chap = f"Chap. {entry['chapter-number']} in " if entry.get("chapter-number") else "In "
        parts.append(_end(f"{chap}*{_md(entry['container-title'])}*"))
        parts.append(_end(_publisher(entry)))
    elif t == "book":
        parts.append(f"*{title}*.")
        parts.append(_end(_publisher(entry)))
    elif t == "dataset":
        parts.append(quoted)
        if entry.get("publisher"):
            parts.append(_end(_md(entry["publisher"])))
        parts.append(_end(f"Accessed {full_date(entry['accessed'])}"))
    else:
        raise ValueError(f"unsupported type {t!r}")

    if link:
        parts.append(_link(link[0]) + ".")
    if t == "dataset":
        parts.append(_end(f"License: {_md(entry['license'])}"))
    return " ".join(parts)


def sort_text(text: str) -> str:
    """Alphabetizing key: accents removed, markup and punctuation ignored, case folded."""
    plain = unicodedata.normalize("NFKD", text)
    plain = "".join(c for c in plain if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", "", plain.lower())


# ------------------------------------------------------------------ the Sources page

INTRO = (
    "Works and datasets cited on KEEL, in Chicago author-date style. Each entry has a stable "
    "link: for example, `sources.html#kulveit2025`. Data sources give the date KEEL last checked "
    "the page and the license of the data."
)


def sources_markdown(entries: list[dict]) -> str:
    suffixes = year_suffixes(entries)
    groups = {"references": [e for e in entries if e["type"] != "dataset"],
              "data-sources": [e for e in entries if e["type"] == "dataset"]}
    out = [INTRO, ""]
    for heading, anchor in SECTIONS:
        out += [f"## {heading} {{#{anchor}}}", ""]
        rendered = [(format_entry(e, suffixes), e["id"]) for e in groups[anchor]]
        for text, key in sorted(rendered, key=lambda r: sort_text(r[0])):
            out += [f"::: {{#{key} .keel-ref}}", text, ":::", ""]
    return "\n".join(out)


def write_sources_page(repo_root: Path) -> None:
    root = Path(repo_root)
    entries = load(root / BIB_PATH)
    (root / SOURCES_MD).write_text(sources_markdown(entries), encoding="utf-8")


# ------------------------------------------------------------------ link check

@dataclass
class LinkResult:
    key: str
    url: str
    status: str
    code: int | None
    detail: str


def check_url(url: str, key: str = "", timeout: float = 30) -> LinkResult:
    """GET the URL with a browser-like User-Agent, following redirects. 2xx/3xx is OK; 401, 403, 429,
    5xx and connection failures (sites that block scripts) need an owner browser check; any other
    4xx is broken."""
    headers = {"User-Agent": BROWSER_UA, "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
               "Accept-Language": "en-US,en;q=0.9"}
    try:
        r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, stream=True)
        r.close()
    except requests.RequestException as e:
        return LinkResult(key, url, OWNER_CHECK, None, type(e).__name__)
    code = r.status_code
    final = r.url if r.url != url else ""
    if 200 <= code < 400:
        return LinkResult(key, url, OK, code, f"redirected to {final}" if final else "")
    if code in BLOCKING_CODES or code >= 500:
        return LinkResult(key, url, OWNER_CHECK, code, "blocked or unavailable to scripts")
    return LinkResult(key, url, BROKEN, code, "")


def check_all(entries: list[dict]) -> list[LinkResult]:
    return [check_url(u, e["id"]) for e in entries for u in entry_urls(e)]


def link_check_report(results: list[LinkResult], checked_on: str) -> str:
    counts = {s: sum(r.status == s for r in results) for s in (OK, OWNER_CHECK, BROKEN)}
    lines = [
        "# Sources link check",
        "",
        f"Every URL and DOI in `references/keel.json`, requested on {checked_on} with a browser-like "
        "User-Agent, following redirects (`python -m indicators.bibliography check-links`). "
        "\"Owner browser check\" means the site refused or did not answer a scripted request; the "
        "owner must open it in a browser.",
        "",
        f"Summary: OK: {counts[OK]} · owner browser check: {counts[OWNER_CHECK]} · broken: {counts[BROKEN]}",
        "",
        "| key | URL | status | HTTP | notes |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        url = r.url.replace("|", "%7C")
        lines.append(f"| {r.key} | <{url}> | {r.status} | {r.code if r.code is not None else '-'} | {r.detail} |")
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ CLI

def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "check-links":
        root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
        results = check_all(load(root / BIB_PATH))
        (root / LINK_REPORT).write_text(link_check_report(results, date.today().isoformat()), encoding="utf-8")
        for r in results:
            print(f"{r.status:20} {r.code!s:5} {r.key:36} {r.url}")
        return 1 if any(r.status == BROKEN for r in results) else 0
    write_sources_page(Path(argv[0]) if argv else Path.cwd())
    return 0


if __name__ == "__main__":
    sys.exit(main())
