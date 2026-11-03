"""Merge the dpdpkit namespace from sibling checkouts into build/api-src for mkdocstrings.

dpdpkit-core, dpdpkit-fastapi, dpdpkit-django and dpdpkit-pii all ship parts of the ``dpdpkit`` package, and griffe stops at the
first ``dpdpkit/__init__.py`` it finds, so the API reference is built from one merged copy.
Usage: python scripts/stage_api_src.py [checkouts-dir]   (default: the folder containing this repo)
"""

import shutil
import sys
from pathlib import Path

docs = Path(__file__).resolve().parents[1]
checkouts = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else docs.parent
target = docs / "build" / "api-src" / "dpdpkit"
shutil.rmtree(target, ignore_errors=True)
skip = shutil.ignore_patterns("__pycache__", "*.pyc")
shutil.copytree(checkouts / "dpdpkit-core" / "src" / "dpdpkit", target, ignore=skip)
shutil.copytree(checkouts / "dpdpkit-fastapi" / "src" / "dpdpkit" / "fastapi", target / "fastapi", ignore=skip)
shutil.copytree(checkouts / "dpdpkit-django" / "src" / "dpdpkit" / "django", target / "django", ignore=skip)
shutil.copytree(checkouts / "dpdpkit-pii" / "src" / "dpdpkit" / "pii", target / "pii", ignore=skip)
print(f"staged {target}")
