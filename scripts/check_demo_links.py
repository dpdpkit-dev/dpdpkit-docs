"""Fail unless every package page links to its page on the demo site.

The demo site (dpdpkit-demo) has one page per demo: /packages/<slug>. Packages that share a demo
(for example @dpdpkit/react runs on the FastAPI page) map to the same slug. Add new package pages to DEMO.
Usage: python scripts/check_demo_links.py
"""

import re
import sys
from pathlib import Path

DEMO_BASE = "https://demo.dpdpkit.dev"  # placeholder until the host is chosen (DEMO-10); also in check_links.py

# package page -> demo slug ("" is the demo home page)
DEMO = {
    "dpdpkit": "",
    "dpdpkit-core": "core",
    "dpdpkit-policies": "core",
    "policy-overlays": "core",
    "dpdpkit-fastapi": "fastapi",
    "dpdpkit-react": "fastapi",
    "dpdpkit-django": "django",
    "dpdpkit-server": "server",
    "dpdpkit-embed": "server",
    "dpdpkit-client": "client",
    "dpdpkit-admin": "admin",
    "dpdpkit-pii": "pii",
    "dpdpkit-conformance": "ci",
    "dpdpkit-lint-action": "ci",
}
NOT_PACKAGE_PAGES = {"index", "template"}

pages = Path(__file__).resolve().parents[1] / "docs" / "packages"
problems = []
names = {p.stem for p in pages.glob("*.md")} - NOT_PACKAGE_PAGES
for name in sorted(names - DEMO.keys()):
    problems.append(f"{name}.md: no demo page is listed for it in scripts/check_demo_links.py")
for name in sorted(DEMO.keys() - names):
    problems.append(f"{name}: listed in scripts/check_demo_links.py but docs/packages/{name}.md does not exist")
for name, slug in sorted(DEMO.items()):
    page = pages / f"{name}.md"
    if not page.is_file():
        continue
    url = f"{DEMO_BASE}/packages/{slug}" if slug else f"{DEMO_BASE}/"
    if not re.search(rf"\]\({re.escape(url)}\)", page.read_text(encoding="utf-8")):
        problems.append(f"{page.name}: no link to its demo page {url}")

if problems:
    sys.exit("\n".join(problems))
print(f"{len(DEMO)} package pages link to their demo page")
