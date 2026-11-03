# Package index

dpdpkit is a set of small packages. Install the ones for your stack; each row links to the page that
covers it once that page is published.

All packages are in alpha (`0.1.0a2`, `0.1.0-alpha.2` for npm), so pip needs `--pre`.

## What to install for each stack

| Your stack | Install | Then |
| --- | --- | --- |
| FastAPI | `pip install --pre "dpdpkit[fastapi]" "dpdpkit-fastapi[scheduler]"` | [FastAPI quickstart](../getting-started/fastapi.md), [`dpdpkit-fastapi`](dpdpkit-fastapi.md) |
| Django | `pip install --pre dpdpkit-django` (add `[drf]` for Django REST framework) | [`dpdpkit-django`](dpdpkit-django.md) |
| Node, PHP, Java, Go, Ruby or anything else | Run the `ghcr.io/dpdpkit-dev/server` Docker image | [Any other stack](../getting-started/other-stacks.md) |
| React frontend | `npm install @dpdpkit/react` | [`@dpdpkit/react`](dpdpkit-react.md), [React components](../reference/react.md) |
| Plain HTML, a CMS, Vue, Svelte or Angular | `npm install @dpdpkit/embed`, or one `<script>` tag | [`@dpdpkit/embed`](dpdpkit-embed.md) |
| Other JavaScript frontend or Node backend | `npm install @dpdpkit/client` | [`@dpdpkit/client`](dpdpkit-client.md), [REST contract](../reference/rest.md) |
| Checking a build or a notice only | `pip install --pre dpdpkit-core` (gives the `dpdpkit` and `dpdp-lint` commands) | [Notice review](../guides/notice-review.md) |

Pick **one** backend: the FastAPI adapter, the Django app or the server image. The frontend packages talk
to whichever you chose over the [REST contract](../reference/rest.md).

## Python packages

| Package | What it is | Version | Python | Extras |
| --- | --- | --- | --- | --- |
| [`dpdpkit`](dpdpkit.md) | Meta-package. Installs `dpdpkit-core`; extras pull in adapters. Its version always equals `dpdpkit-core`. | 0.1.0a2 | 3.10+ | `fastapi`, `ses`, `workbook` |
| [`dpdpkit-core`](dpdpkit-core.md) | The kit: consent, notices, rights requests, retention, ledger, events, export, and the `dpdpkit` CLI. | 0.1.0a2 | 3.10+ | `ses`, `workbook` |
| [`dpdpkit-policies`](dpdpkit-policies.md) | Versioned DPDP policy packs and [sector overlays](policy-overlays.md). Installed by core. | 2026.11.0a1 | 3.10+ | none |
| [`dpdpkit-fastapi`](dpdpkit-fastapi.md) | FastAPI adapter: REST endpoints, SQLAlchemy storage, migrations, scheduler. | 0.1.0a3 | 3.10+ | `scheduler`, `celery`, `arq`, `postgres`, `mysql` |
| [`dpdpkit-django`](dpdpkit-django.md) | Django app: models, REST endpoints, admin request queue. | 0.1.0a3 | 3.10+ | `drf`, `celery`, `postgres`, `mysql` |
| [`dpdpkit-server`](dpdpkit-server.md) | The REST API as a self-hosted server and Docker image, built on `dpdpkit-fastapi`. | 0.1.0a3 | 3.10+ | `postgres` |
| `dpdpkit-pii` | Finds personal data in your databases and files: Indian PII recognizers and a read-only scanner. Adds `dpdpkit scan`. | 0.1.0a2 | 3.10+ | `excel`, `s3` |
| `dpdpkit-conformance` | The OpenAPI contract and black-box test suite every adapter passes. | 0.1.0a2 | 3.10+ | `asgi` |

## JavaScript packages

| Package | What it is | Version | Requires |
| --- | --- | --- | --- |
| [`@dpdpkit/client`](dpdpkit-client.md) | Typed client for the REST API. | 0.1.0-alpha.2 | Node 18+ |
| [`@dpdpkit/react`](dpdpkit-react.md) | `<ConsentNotice>`, `<PreferenceCenter>`, `<RightsRequestForm>`. | 0.1.0-alpha.2 | React 18+ |
| [`@dpdpkit/embed`](dpdpkit-embed.md) | Framework-free web components: `<dpdp-consent>`, `<dpdp-preferences>`, `<dpdp-rights-form>`. | 0.1.0-alpha.2 | none |

The admin dashboard ([`dpdpkit-admin`](dpdpkit-admin.md)) is bundled with the backend packages and is not installed on its own.

## Supported versions

| Dependency | Supported | Tested in CI |
| --- | --- | --- |
| Python | 3.10 or later | 3.10 and 3.13 |
| FastAPI | 0.110 or later | current release |
| Django | 4.2 or later | 4.2 and 5.x |
| SQLAlchemy | 2.0.25 or later | current 2.x release |
| Databases | SQLite, PostgreSQL, MySQL | SQLite, PostgreSQL 16, MySQL 8.4 |
| Node (`@dpdpkit/client`) | 18 or later | 22 and 24, plus a smoke test on older runtimes |
| React (`@dpdpkit/react`) | 18 or later | 18 |

Use SQLite for trying things out and PostgreSQL or MySQL in production.

### Keeping versions compatible

- Adapters and the server accept `dpdpkit-core` in the same minor series (`>=0.1.0a2,<0.2`). Upgrade
  core and the adapter together.
- `dpdpkit-policies` is versioned by month (`2026.11`) because the rules it holds change on their own
  schedule. See [Policy packs](../concepts/policy-packs.md).
- Breaking changes follow [Versioning and deprecation](../reference/deprecation.md).

!!! note "Versions change"
    The numbers above are the current alpha. Each package's changelog is the authority on what a
    release supports.

## Package pages

Every package page follows one [page template](template.md): install, quickstart, configuration, API
reference, troubleshooting and upgrading, always in that order.
