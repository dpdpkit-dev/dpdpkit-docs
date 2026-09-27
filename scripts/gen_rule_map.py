"""Write docs/reference/rule-to-code.md from the installed dpdpkit-policies package."""

import contextlib
import io
from pathlib import Path

from dpdpkit_policies.cli import main

buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    main(["rule-map", "--format", "md"])
page = Path(__file__).resolve().parents[1] / "docs" / "reference" / "rule-to-code.md"
page.write_text(
    "# Rule to code\n\nGenerated from `dpdpkit-policies`. Each row shows a pack key, its value, the legal "
    "source and the dpdpkit module that reads it.\n\n" + buf.getvalue(),
    encoding="utf-8",
)
print(f"wrote {page}")
