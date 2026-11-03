"""Run the package-page code samples against the published packages.

A fenced block runs when the line before it is ``<!-- sample: run -->``. Python blocks run with the
interpreter, shell blocks with bash -e. Blocks on one page share a scratch folder and run in page order, so
``dpdpkit init`` can create the file a later block reads. Any non-zero exit fails the check.

Install the published packages into a clean environment first, then pass that environment's Python:
    python -m venv _samples_venv && _samples_venv/bin/pip install --pre dpdpkit-core dpdpkit-policies
    python scripts/check_samples.py --python _samples_venv/bin/python
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MARKER = re.compile(r"^\s*<!--\s*sample:\s*run\s*-->\s*$")
FENCE = re.compile(r"^(\s*)```(\w+)")
# On Windows, plain "bash" can be the WSL launcher; prefer Git for Windows' bash when it is installed.
GIT_BASH = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git" / "bin" / "bash.exe"
BASH = str(GIT_BASH) if os.name == "nt" and GIT_BASH.is_file() else "bash"


def samples(page: Path):
    """Yield (line number, language, dedented code) for each marked block on the page."""
    lines = page.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if not MARKER.match(line):
            continue
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        m = FENCE.match(lines[j]) if j < len(lines) else None
        if not m:
            sys.exit(f"{page}:{i + 1}: 'sample: run' must be followed by a fenced code block")
        indent, lang = m.groups()
        body = []
        k = j + 1
        while k < len(lines) and not lines[k].strip().startswith("```"):
            body.append(lines[k][len(indent):] if lines[k].startswith(indent) else lines[k].lstrip())
            k += 1
        yield j + 1, lang, "\n".join(body) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--python", default=sys.executable, help="Python of the environment with the published packages")
    parser.add_argument("--pages", default="docs/packages", help="folder of package pages")
    args = parser.parse_args()

    python = Path(args.python).resolve()
    bin_dir = str(python.parent)
    env = {**os.environ, "PATH": bin_dir + os.pathsep + os.environ["PATH"], "PYTHONIOENCODING": "utf-8"}
    failures = ran = 0
    for page in sorted(Path(args.pages).glob("*.md")):
        found = list(samples(page))
        if not found:
            continue
        scratch = tempfile.mkdtemp(prefix="docs-sample-")
        try:
            for line_no, lang, code in found:
                if lang in ("python", "py"):
                    cmd = [str(python), "-I", "-c", code]
                elif lang in ("bash", "sh", "shell"):
                    cmd = [BASH, "-e", "-c", code]
                else:
                    sys.exit(f"{page}:{line_no}: cannot run a '{lang}' block")
                ran += 1
                result = subprocess.run(cmd, cwd=scratch, env=env, capture_output=True, text=True, timeout=300)
                if result.returncode:
                    failures += 1
                    print(f"FAIL {page}:{line_no} ({lang}) exit {result.returncode}\n{code}\n"
                          f"{result.stdout[-1500:]}{result.stderr[-1500:]}", file=sys.stderr)
                else:
                    print(f"ok   {page}:{line_no} ({lang})")
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    if not ran:
        sys.exit("no samples are marked 'sample: run'; nothing was checked")
    print(f"{ran - failures}/{ran} samples passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
