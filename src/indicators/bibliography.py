"""Bibliography: references/keel.json (CSL-JSON) rendered as the Sources page, and its link check.

Entries are formatted in Chicago author-date style, 18th edition (2024), by `format_entry`; in-text
citations come from `in_text`. Rules applied (sources in references/README.md):

- Authors in the reference list: first author inverted; up to six authors all listed; seven or more,
  the first three and "et al." (CMOS 18; CSL chicago-author-date: et-al-min 7, et-al-use-first 3).
  Editors of a proceedings volume follow the same rule. Repeated authors are written out, not replaced
  by a 3-em dash, so each entry stands alone when reached through its anchor.
- In-text citations: one author "Krueger 2025"; two "Moon and Boudreaux 2026"; three or more, the
  first author and "et al." ("Chooi et al. 2026"; CSL: et-al-min 3, et-al-use-first 1).
- Same in-text citation (same first author or authors, same year): letter suffixes (2026a, 2026b) in
  reference-list order (authors, then title), so "a" is listed first and every in-text citation points
  to one entry.
- Dates: the year follows the authors. Where the source gives a month and day (preprints, web pages,
  blog posts and reports), the month and day follow the container without repeating the year:
  "2026. ... Anthropic Research, October 27." A month without a day is not shown.
- Place of publication is omitted (no longer required in the 18th edition), even when recorded.
- Preprints: "Preprint, [repository], [month day]." Blog names in italics, with "(blog)" unless the
  name says so, then a comma and any publisher.
- Titles of standalone works (reports, books) in italics; titles of parts (articles, posts, chapters,
  datasets) in quotation marks. A work with no author starts with its title.
- Executive orders in Bluebook legal form (the CSL style follows Bluebook): "Exec. Order No. 14,434,
  91 Fed. Reg. 63,129 (Oct. 2, 2026)."
- A web page revised after publication may carry ", last modified [Month Day, Year]" after its date.
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
    "article": ["author", "title", "issued", "publisher"],
    "paper-conference": ["author", "title", "issued", "container-title", "publisher"],
    "article-journal": ["author", "title", "issued", "container-title", "volume"],
    "report": ["author", "title", "issued"],
    "chapter": ["author", "title", "issued", "container-title", "publisher"],
    "book": ["author", "title", "issued", "publisher"],
    "post-weblog": ["author", "title", "issued", "container-title"],
    "webpage": ["title", "issued", "container-title"],  # author optional: a work with no author
    "legislation": ["title", "issued", "container-title", "volume", "page"],
    "dataset": ["author", "title", "accessed", "license"],
}
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December")
SECTIONS = (("References", "references"), ("Data sources", "data-sources"))
BLUEBOOK_MONTHS = ("Jan.", "Feb.", "Mar.", "Apr.", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec.")
ET_AL_MIN, ET_AL_USE_FIRST = 7, 3  # reference list (CMOS 18)

OK = "OK"
BROKEN = "broken"
OWNER_CHECK = "owner browser check"
# URLs that block scripted requests and that the owner has opened in a browser and confirmed. The
# release-gate link check passes a blocked URL only if it is listed here. Date: when the owner checked.
OWNER_BROWSER_CHECKED: dict[str, str] = {
    "https://www.bls.gov/productivity/home.htm": "2026-11-18",
    "https://fred.stlouisfed.org/series/CPATAX": "2026-11-18",
    "https://fred.stlouisfed.org/series/GDP": "2026-11-18",
    "https://fred.stlouisfed.org/series/W055RC1Q027SBEA": "2026-11-18",
    "https://fred.stlouisfed.org/series/W054RC1Q027SBEA": "2026-11-18",
    "https://fred.stlouisfed.org/series/W782RC1Q027SBEA": "2026-11-18",
    "https://www.bls.gov/opub/ted/2026/labor-share-at-its-lowest-level-52-8-percent-in-second-quarter-2026.htm":
        "2026-11-18",
    "https://meta.stackoverflow.com/questions/421831/policy-generative-ai-e-g-chatgpt-is-banned": "2026-11-18",
    "https://www.cbo.gov/publication/58848": "2026-11-20",  # owner confirmed (checklist b9)
}
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
    """Authors for the reference list: all up to six; seven or more, the first three and "et al."."""
    if len(people) >= ET_AL_MIN:
        shown = [_name(p, i == 0) for i, p in enumerate(people[:ET_AL_USE_FIRST])]
        return _end(", ".join(shown) + ", et al.")
    names = [_name(p, i == 0) for i, p in enumerate(people)]
    if len(names) == 1:
        return _end(names[0])
    return _end(", ".join(names[:-1]) + ", and " + names[-1])


def format_editors(people: list[dict]) -> str:
    """Editors after "edited by", not inverted, with the same "et al." rule as authors."""
    names = [_name(p, False) for p in people]
    if len(names) >= ET_AL_MIN:
        return ", ".join(names[:ET_AL_USE_FIRST]) + ", et al."
    if len(names) <= 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + ", and " + names[-1]


def page_range(pages: str) -> str:
    """Condense an inclusive page range (CMOS 9.64)."""
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
    """'October 27, 2026' or 'August 2026'; None when only a year is known (used for access dates)."""
    parts = (issued or {}).get("date-parts", [[None]])[0]
    if len(parts) >= 3:
        return f"{MONTHS[parts[1] - 1]} {parts[2]}, {parts[0]}"
    if len(parts) == 2:
        return f"{MONTHS[parts[1] - 1]} {parts[0]}"
    return None


def month_day(issued: dict | None) -> str | None:
    """'October 27' when the source gives a month and day; the year is not repeated (CMOS 18)."""
    parts = (issued or {}).get("date-parts", [[None]])[0]
    if len(parts) >= 3:
        return f"{MONTHS[parts[1] - 1]} {parts[2]}"
    return None


def bluebook_date(issued: dict) -> str:
    """'Oct. 2, 2026' (Bluebook month abbreviations), or the year when no day is known."""
    parts = issued["date-parts"][0]
    if len(parts) >= 3:
        return f"{BLUEBOOK_MONTHS[parts[1] - 1]} {parts[2]}, {parts[0]}"
    return str(parts[0])


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
    """The publisher, without the place of publication (not required in CMOS 18)."""
    return _md(entry["publisher"]) if entry.get("publisher") else None


def _join(*items: str | None) -> str:
    return ", ".join(x for x in items if x)


# ------------------------------------------------------------------ in-text citations

def _family(person: dict) -> str:
    return person.get("literal") or person["family"]


def in_text_author(entry: dict) -> str:
    """The author part of an in-text citation (CMOS 18): one or two names; three or more, "et al."."""
    if entry["type"] == "legislation":
        return entry["title"]
    people = entry.get("author") or []
    if not people:
        return f"“{entry['title']}”"
    if len(people) == 1:
        return _family(people[0])
    if len(people) == 2:
        return f"{_family(people[0])} and {_family(people[1])}"
    return f"{_family(people[0])} et al."


def in_text(entry: dict, suffixes: dict[str, str] | None = None) -> str:
    """The text of a parenthetical citation without the parentheses: "Kulveit et al. 2025". An
    executive order is cited by its title alone ("Exec. Order No. 14434")."""
    if entry["type"] == "legislation":
        return entry["title"]
    return f"{in_text_author(entry)} {_year(entry)}{(suffixes or {}).get(entry['id'], '')}"


def year_suffixes(entries: list[dict]) -> dict[str, str]:
    """Letter suffixes for works that would share an in-text citation, in reference-list order."""
    groups: dict[tuple, list[dict]] = {}
    for e in entries:
        if e["type"] in ("dataset", "legislation") or not e.get("issued"):
            continue
        groups.setdefault((in_text_author(e), _year(e)), []).append(e)
    out = {}
    for group in groups.values():
        if len(group) > 1:
            for i, e in enumerate(sorted(group, key=lambda x: sort_text(f"{format_names(x['author'])} {x['title']}"))):
                out[e["id"]] = "abcdefghijklmnopqrstuvwxyz"[i]
    return out


class Citations:
    """In-text citations linked to the Sources page, for generated page text. `prefix` is the path from
    the page to the site root ("" for top-level pages, "../" for indicator pages)."""

    def __init__(self, entries: list[dict]):
        self.entries = {e["id"]: e for e in entries}
        self.suffixes = year_suffixes(entries)
        self.by_url = {u: e["id"] for e in entries for u in entry_urls(e)}

    def key_for_url(self, url: str) -> str:
        if url not in self.by_url:
            raise ValueError(f"{url} is not in the bibliography (references/keel.json)")
        return self.by_url[url]

    def anchor(self, key: str, prefix: str = "") -> str:
        if key not in self.entries:
            raise ValueError(f"{key} is not in the bibliography (references/keel.json)")
        return f"{prefix}sources.qmd#{key}"

    def cite(self, key: str, prefix: str = "", locator: str | None = None) -> str:
        """'[(Kulveit et al. 2025)](sources.qmd#kulveit2025)', with an optional page or part locator."""
        target = self.anchor(key, prefix)
        text = in_text(self.entries[key], self.suffixes) + (f", {locator}" if locator else "")
        return f"[({text})]({target})"


# ------------------------------------------------------------------ entries

def format_entry(entry: dict, suffixes: dict[str, str] | None = None) -> str:
    """One reference-list entry in Chicago author-date style (18th ed.), as Pandoc Markdown."""
    t = entry["type"]
    link = entry_urls(entry)[:1]
    title = _md(entry["title"])
    quoted = f"“{_end(title)}”"

    if t == "legislation":
        text = (f"{title}, {_md(entry['volume'])} {_md(entry['container-title'])} {entry['page']} "
                f"({bluebook_date(entry['issued'])}).")
        return text + (f" {_link(link[0])}." if link else "")

    year = _year(entry) + (suffixes or {}).get(entry["id"], "")
    if entry.get("author"):
        parts = [_md(format_names(entry["author"])), _end(year)]
        title_shown = False
    else:  # no author: the title takes the author's place
        parts = [quoted, _end(year)]
        title_shown = True
    md = month_day(entry.get("issued"))

    if t == "article":
        parts.append(quoted)
        parts.append(_end(_join(entry.get("genre", "Preprint"), _md(entry["publisher"]), md)))
    elif t in ("post-weblog", "webpage"):
        if not title_shown:
            parts.append(quoted)
        site = _md(entry["container-title"])
        if t == "post-weblog":
            site = f"*{site}*" + ("" if "blog" in entry["container-title"].lower() else " (blog)")
        modified = full_date(entry.get("last-modified"))
        parts.append(_end(_join(site, _md(entry["publisher"]) if entry.get("publisher") else None, md,
                                f"last modified {modified}" if modified else None)))
    elif t == "report":
        parts.append(f"*{title}*.")
        elements = [_md(entry[f]) for f in ("collection-title", "number") if entry.get(f)]
        if _publisher(entry):
            elements.append(_publisher(entry))
        if elements:
            parts += [_end(x) for x in elements[:-1]] + [_end(_join(elements[-1], md))]
        elif md:
            parts.append(_end(md))
    elif t == "paper-conference":
        parts.append(quoted)
        container = f"In *{_md(entry['container-title'])}*"
        if entry.get("editor"):
            container += f", edited by {_md(format_editors(entry['editor']))}"
        if entry.get("page"):
            container += f", {page_range(entry['page'])}"
        parts.append(_end(container))
        parts.append(_end(_publisher(entry)))
    elif t == "chapter":
        parts.append(quoted)
        chap = f"Chap. {entry['chapter-number']} in " if entry.get("chapter-number") else "In "
        container = f"{chap}*{_md(entry['container-title'])}*"
        if entry.get("page"):
            container += f", {page_range(entry['page'])}"
        parts.append(_end(container))
        parts.append(_end(_publisher(entry)))
    elif t == "article-journal":  # CMOS 18: Journal Volume (Issue): pages.
        parts.append(quoted)
        container = f"*{_md(entry['container-title'])}* {entry['volume']}"
        if entry.get("issue"):
            container += f" ({entry['issue']})"
        if entry.get("page"):
            container += f": {page_range(entry['page'])}"
        parts.append(_end(container))
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
    "Works and datasets cited on KEEL. Each entry has a stable "
    "link: for example, `sources.html#kulveit2025`. Data sources give the date KEEL last checked "
    "the page and the license of the data. Every entry was checked against the original publication "
    "before it was added. KEEL is built with assistance from Claude (see [Disclosure](about.qmd#disclosure))."
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
        detail = r.detail
        if r.status == OWNER_CHECK and r.url in OWNER_BROWSER_CHECKED:
            detail = f"{detail}; owner checked in a browser on {OWNER_BROWSER_CHECKED[r.url]}".lstrip("; ")
        lines.append(f"| {r.key} | <{url}> | {r.status} | {r.code if r.code is not None else '-'} | {detail} |")
    lines += ["", "## Owner browser checks", "",
              "URLs that block scripts and that the owner opened in a browser (`OWNER_BROWSER_CHECKED` in "
              "`src/indicators/bibliography.py`). The release-gate link test passes a blocked URL only if it is "
              "listed here.", "", "| URL | date checked |", "|---|---|"]
    lines += [f"| <{u}> | {d} |" for u, d in OWNER_BROWSER_CHECKED.items()]
    pending = [r for r in results if r.status == OWNER_CHECK and r.url not in OWNER_BROWSER_CHECKED]
    lines += ["", "Waiting for an owner browser check: " +
              ("; ".join(f"<{r.url}> ({r.key}, {r.code or r.detail})" for r in pending) if pending else "none") + "."]
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
