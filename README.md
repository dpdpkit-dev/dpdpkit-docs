# dpdpkit-docs

Source for the dpdpkit documentation site (MkDocs Material, versioned with `mike`, deployed to GitHub Pages).

> dpdpkit helps implement obligations under India's DPDP Act, 2023 and DPDP Rules, 2025. It does not
> provide legal advice and does not guarantee compliance.

```bash
pip install -r requirements.txt
python scripts/gen_rule_map.py
python scripts/stage_api_src.py      # API reference sources, from ../dpdpkit-core and ../dpdpkit-fastapi
mkdocs serve
```

The Python API pages (`docs/reference/python/`) are generated from docstrings at build time. CI checks
out `dpdpkit-core` and `dpdpkit-fastapi` from `main`, so a docstring change shows up on the next docs build.

Deploys: `main` → `/dev/`, tag `vX.Y.Z` → `/X.Y/` plus the `latest` alias.
