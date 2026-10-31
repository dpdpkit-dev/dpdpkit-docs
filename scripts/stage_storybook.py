"""Copy the @dpdpkit/react Storybook build into docs/storybook, so mkdocs publishes it with each docs version.

Build it first in a dpdpkit-react checkout: ``npm ci && npm run build-storybook`` (writes storybook-static/).
Usage: python scripts/stage_storybook.py [checkouts-dir]   (default: the folder containing this repo)
"""

import shutil
import sys
from pathlib import Path

docs = Path(__file__).resolve().parents[1]
checkouts = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else docs.parent
source = checkouts / "dpdpkit-react" / "storybook-static"
target = docs / "docs" / "storybook"
if not (source / "index.html").is_file():
    sys.exit(f"no Storybook build at {source}: run `npm ci && npm run build-storybook` in dpdpkit-react first")
shutil.rmtree(target, ignore_errors=True)
shutil.copytree(source, target)
print(f"staged {target}")
