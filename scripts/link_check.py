"""Check internal links in a built site. Usage: python scripts/link_check.py [site_dir] [base_path]

Looks at every href and src in every .html file. External (http, https, mailto and other schemes)
and fragment-only links are ignored. Root-absolute paths must sit under base_path. Exits 1 and
prints each broken link when any are found.
"""
from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class _Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.urls: list[str] = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                self.urls.append(value.strip())


def _resolves(target: Path) -> bool:
    return target.is_file() or (target.is_dir() and (target / "index.html").is_file())


def check(site_dir: Path, base_path: str = "/keel/") -> list[str]:
    """Return one message per broken internal link, resolved as the deployed site would be."""
    site_dir = Path(site_dir).resolve()
    stripped = base_path.strip("/")
    base = f"/{stripped}/" if stripped else "/"
    broken: list[str] = []
    for page in sorted(site_dir.rglob("*.html")):
        parser = _Links()
        parser.feed(page.read_text(encoding="utf-8", errors="replace"))
        rel_page = page.relative_to(site_dir).as_posix()
        for url in parser.urls:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc or not parts.path:  # external, //host, or #fragment / ?query only
                continue
            path = unquote(parts.path)
            if path.startswith("/"):
                if not (path.rstrip("/") + "/").startswith(base):
                    broken.append(f"{rel_page}: {url} (outside base path {base})")
                    continue
                target = site_dir / path[len(base):]
            else:
                target = page.parent / path
            target = target.resolve()
            if site_dir not in (target, *target.parents):
                broken.append(f"{rel_page}: {url} (escapes the site)")
            elif not _resolves(target):
                broken.append(f"{rel_page}: {url} (missing)")
    return broken


def main(argv: list[str]) -> int:
    site_dir = Path(argv[0]) if argv else Path("site/_site")
    base_path = argv[1] if len(argv) > 1 else "/keel/"
    if not site_dir.is_dir():
        print(f"link_check: {site_dir} is not a directory", file=sys.stderr)
        return 2
    broken = check(site_dir, base_path)
    for line in broken:
        print(line)
    print(f"link_check: {len(broken)} broken link(s) in {site_dir}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
