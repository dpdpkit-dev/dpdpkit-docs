# dpdpkit-docs

Source for the dpdpkit documentation site (MkDocs Material, versioned with `mike`, deployed to GitHub Pages).

> dpdpkit helps implement obligations under India's DPDP Act, 2023 and DPDP Rules, 2025. It does not
> provide legal advice and does not guarantee compliance.

```bash
pip install -r requirements.txt
python scripts/gen_rule_map.py
mkdocs serve
```

Deploys: `main` → `/dev/`, tag `vX.Y.Z` → `/X.Y/` plus the `latest` alias.
