"""Fail on broken links in the built site.

mkdocs build --strict already fails on internal links to pages and anchors that don't exist. This checks the
external http(s) links in the HTML under site/: a 404 or 410, or a host that can't be reached after retries,
fails. Other 4xx and 5xx answers (rate limits, bot blocks) only warn, because they say little about the link.
Usage: python scripts/check_links.py [site-dir]   (default: site)
"""

import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlparse

# Hosts not to probe. dpdpkit.dev isn't registered yet (SETUP-05). The demo sleeps on its free plan and can outlast
# the timeout here; its own smoke-live workflow checks it every six hours.
NOT_LIVE = {"dpdpkit.dev", "dpdpkit-demo.onrender.com"}
# Example and placeholder hosts used in code samples.
EXAMPLE = re.compile(r"(^|\.)(example\.(com|org|net)|localhost|127\.0\.0\.1|0\.0\.0\.0)$")
HEADERS = {"User-Agent": "dpdpkit-docs-link-check (+https://github.com/dpdpkit-dev/dpdpkit-docs)"}


class Hrefs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href") or ""
            if href.startswith(("http://", "https://")):
                self.urls.add(urldefrag(href)[0])


def probe(url: str):
    """Return (url, verdict) where verdict is None when fine, ('fail'|'warn', reason) otherwise."""
    reason = "unknown"
    for attempt in range(3):
        for method in ("HEAD", "GET"):
            req = urllib.request.Request(url, method=method, headers=HEADERS)
            try:
                with urllib.request.urlopen(req, timeout=20):
                    return url, None
            except urllib.error.HTTPError as e:
                if e.code in (404, 410):
                    if method == "GET":
                        return url, ("fail", f"HTTP {e.code}")
                    continue  # some servers answer HEAD wrongly: confirm with GET
                reason = f"HTTP {e.code}"
                if method == "GET":
                    return url, ("warn", reason)
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                reason = str(getattr(e, "reason", e))
                break
        time.sleep(2 * (attempt + 1))
    return url, ("fail", f"unreachable: {reason}")


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "site")
    if not site.is_dir():
        sys.exit(f"no built site at {site}: run `mkdocs build --strict` first")
    where: dict[str, set[str]] = {}
    for html in site.rglob("*.html"):
        if "storybook" in html.relative_to(site).parts:
            continue  # the vendored Storybook build is not ours to check
        parser = Hrefs()
        parser.feed(html.read_text(encoding="utf-8", errors="replace"))
        for url in parser.urls:
            host = urlparse(url).hostname or ""
            if host in NOT_LIVE or EXAMPLE.search(host):
                continue
            where.setdefault(url, set()).add(html.relative_to(site).as_posix())
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(probe, sorted(where)))
    failed = 0
    for url, verdict in results:
        if verdict:
            level, reason = verdict
            pages = ", ".join(sorted(where[url])[:3])
            print(f"{level.upper():4} {url} ({reason}) in {pages}", file=sys.stderr)
            failed += level == "fail"
    print(f"checked {len(results)} external links, {failed} broken")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
