# dpdpkit-docs

Source for the dpdpkit documentation site (MkDocs Material, versioned with `mike`, deployed to GitHub Pages).

> dpdpkit helps implement obligations under India's DPDP Act, 2023 and DPDP Rules, 2025. It does not
> provide legal advice and does not guarantee compliance.

```bash
pip install -r requirements.txt
python scripts/gen_rule_map.py
python scripts/stage_api_src.py      # API reference sources, from ../dpdpkit-core and ../dpdpkit-fastapi
python scripts/stage_storybook.py    # Storybook, from ../dpdpkit-react/storybook-static
mkdocs serve
```

Build the Storybook once before staging it: `npm ci && npm run build-storybook` in `../dpdpkit-react`.

The Python API pages (`docs/reference/python/`) are generated from docstrings at build time. CI checks
out `dpdpkit-core` and `dpdpkit-fastapi` from `main`, so a docstring change shows up on the next docs build.
The same goes for the `@dpdpkit/react` Storybook: CI builds it from `dpdpkit-react` `main` and mkdocs publishes it
at `/<version>/storybook/`, linked from `docs/reference/react.md`.

Deploys: `main` → `/dev/`, tag `vX.Y.Z` → `/X.Y/` plus the `latest` alias.

## Cloud waitlist

`docs/waitlist.md` shows a signup form with its privacy notice. The site is static, so submissions go to a
third-party form service that accepts a plain HTML POST (and JSON when sent with `Accept: application/json`,
for the in-page confirmation). The form stays disabled until two repository variables are set:

| Variable | Example | Used for |
| --- | --- | --- |
| `WAITLIST_ACTION` | `https://formspree.io/f/abcdwxyz` | The form's `action` URL |
| `WAITLIST_PROCESSOR` | `Formspree` | Named in the notice as the service that stores submissions |

Locally, set `DPDPKIT_WAITLIST_ACTION` and `DPDPKIT_WAITLIST_PROCESSOR` before `mkdocs serve`.
The form sends `email`, optional `organisation`, `stack` and `interest_*` fields, `consent=yes`,
`notice_version`, and a `_gotcha` honeypot that should be empty (Formspree drops submissions that fill it).
Bump `extra.waitlist.notice_version` in `mkdocs.yml` whenever the notice text changes.

## Demo video

`demo/` holds the 5-minute demo as code: a narrated script (`demo/scenes.yaml`), the quickstart app it runs,
and `demo/demo.py`, which records every step against the real packages and renders an MP4 with captions.
See [demo/README.md](demo/README.md).
