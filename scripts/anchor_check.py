"""Check where every internal link lands in a built site, in a real browser.

Usage: python scripts/anchor_check.py [site_dir]   (default site/_site; needs Playwright and Chrome)

For every link to a section or other anchor (same page or another page), on a desktop and a phone
screen, it follows the link the way a reader does and checks that the target is visible and sits
just below the top bar: not hidden under it, and without a large gap above it. The top bar hides
and shows as you scroll, so it checks against wherever the bar is at that moment. A target near the
end of a page may sit lower, because the page cannot scroll further; that passes.

The owner found headings hidden under the bar, or far below it, three times (2026-11-20); this
check exists so that class of problem is found before release, not by a reader. Exits 1 and prints
each failure.
"""
from __future__ import annotations

import functools
import http.server
import sys
import threading
from pathlib import Path
from urllib.parse import urljoin, urldefrag

GAP_MAX = 48  # px allowed between the bar (or the top of the screen) and the target
# Anchors readers never follow: Quarto's hidden code-line anchors, the skip link, empty "#".
SKIP_PREFIXES = ("cb", "quarto-")
SCREENS = {"desktop": {"viewport": {"width": 1280, "height": 900}}, "phone": "iPhone 13"}

MEASURE = """f => {
  let el = document.getElementById(f);
  if (!el) return {missing: true};
  if (el.matches('section')) el = el.querySelector('h1,h2,h3,h4,h5,h6') || el;
  const r = el.getBoundingClientRect();
  const bar = document.getElementById('quarto-header');
  const end = document.documentElement.scrollHeight - innerHeight - scrollY <= 2;
  return {top: Math.round(r.top), height: Math.round(r.height),
          bar: bar ? Math.max(0, Math.round(bar.getBoundingClientRect().bottom)) : 0, end};
}"""
SETTLE = """async () => {  // wait until scrolling has stopped (the landing script repeats while charts load)
  let last = -1, still = 0;
  for (let i = 0; i < 60 && still < 8; i++) {
    await new Promise(r => setTimeout(r, 100));
    still = scrollY === last ? still + 1 : 0; last = scrollY;
  }
}"""
LINKS = """() => [...document.querySelectorAll('a[href*="#"]')].map(a => a.getAttribute('href'))"""


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def _serve(site: Path) -> tuple[http.server.ThreadingHTTPServer, str]:
    handler = functools.partial(_Quiet, directory=str(site))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/"


def _verdict(m: dict) -> str | None:
    if m.get("missing"):
        return "target not found"
    if m["height"] == 0:
        return "target is hidden (inside a closed section or box)"
    if m["top"] < m["bar"] - 1:
        return f"hidden under the top bar ({m['bar'] - m['top']}px)"
    if m["top"] > m["bar"] + GAP_MAX and not m["end"]:
        return f"lands {m['top'] - m['bar']}px below the bar"
    return None


def check(site: Path, counts: dict | None = None) -> list[str]:
    from playwright.sync_api import sync_playwright

    server, base = _serve(site)
    pages = sorted(p.relative_to(site).as_posix() for p in site.rglob("*.html") if "site_libs" not in p.parts)
    failures: list[str] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel="chrome")
            for screen, spec in SCREENS.items():
                ctx = browser.new_context(**(pw.devices[spec] if isinstance(spec, str) else spec))
                page = ctx.new_page()
                page.on("pageerror", lambda e, s=screen: failures.append(f"{s}: script error: {e}"))
                cross: set[str] = set()
                for rel in pages:
                    page.goto(base + rel)
                    page.wait_for_load_state("networkidle")
                    page.evaluate(SETTLE)
                    same: list[str] = []
                    for href in page.evaluate(LINKS):
                        url, frag = urldefrag(urljoin(base + rel, href))
                        if not frag or frag.startswith(SKIP_PREFIXES) or not url.startswith(base):
                            continue
                        if url == base + rel:
                            if frag not in same:
                                same.append(frag)
                        else:
                            cross.add(f"{url}#{frag}")
                    for frag in same:  # follow the link on the page, as a reader does
                        page.evaluate("f => { const a = [...document.querySelectorAll('a')].find(x => "
                                      "x.getAttribute('href') === '#' + f); a ? a.click() : (location.hash = f); }", frag)
                        page.evaluate(SETTLE)
                        why = _verdict(page.evaluate(MEASURE, frag))
                        if counts is not None:
                            counts[screen] = counts.get(screen, 0) + 1
                        if why:
                            failures.append(f"{screen}: {rel}#{frag} (link on the same page): {why}")
                for target in sorted(cross):  # arrive from another page
                    page.goto(target)
                    page.wait_for_load_state("networkidle")
                    page.evaluate(SETTLE)
                    why = _verdict(page.evaluate(MEASURE, urldefrag(target)[1]))
                    if counts is not None:
                        counts[screen] = counts.get(screen, 0) + 1
                    if why:
                        failures.append(f"{screen}: {target[len(base):]} (link from another page): {why}")
                ctx.close()
            browser.close()
    finally:
        server.shutdown()
    return failures


if __name__ == "__main__":
    site_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "site/_site")
    counts: dict = {}
    found = check(site_dir, counts)
    for line in found:
        print(line)
    print(f"links followed: {counts}; {len(found)} problem(s)")
    sys.exit(1 if found else 0)
