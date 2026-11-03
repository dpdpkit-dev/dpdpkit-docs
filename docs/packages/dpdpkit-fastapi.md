# dpdpkit-fastapi

The FastAPI adapter: it adds the dpdpkit REST endpoints, SQLAlchemy storage, database migrations, a consent dependency and a job scheduler to your app. Install it if your backend is FastAPI; for other Python stacks see [`dpdpkit-django`](dpdpkit-django.md) or the [server image](../getting-started/other-stacks.md).

| | |
| --- | --- |
| Install | `pip install --pre "dpdpkit[fastapi]" "dpdpkit-fastapi[scheduler]"` |
| Version | 0.1.0a3 |
| Requires | Python 3.10+, `dpdpkit-core>=0.1.0a2,<0.2`, `fastapi>=0.110`, `sqlalchemy>=2.0.25`, `alembic>=1.13` |
| Source | [dpdpkit-fastapi](https://github.com/dpdpkit-dev/dpdpkit-fastapi) · [Changelog](https://github.com/dpdpkit-dev/dpdpkit-fastapi/blob/main/CHANGELOG.md) |
| Demo | [Try it on the demo site](https://demo.dpdpkit.dev/packages/fastapi) (fictional data) |

Installing `dpdpkit-fastapi` also installs [`dpdpkit-core`](dpdpkit-core.md). The `dpdpkit[fastapi]` extra on the
[`dpdpkit` meta-package](dpdpkit.md) installs the same pair. Pick one backend: this adapter, the Django app or
the server image. See the [package index](index.md).

!!! warning "Not legal advice"
    dpdpkit-fastapi records and enforces what you configure. Notice wording, purposes and retention periods are
    decisions for you and your counsel, and using the package does not guarantee compliance with the DPDP Act, 2023
    or the DPDP Rules, 2025.

## Install

```bash
pip install --pre "dpdpkit-fastapi[scheduler,postgres]"
```

| Extra | Adds | Needed for |
| --- | --- | --- |
| `scheduler` | `apscheduler>=3.10,<4` | `DPDPKit.start_scheduler()` |
| `celery` | `celery>=5.3` | Running the jobs from Celery beat (`register_celery`) |
| `arq` | `arq>=0.25` | Running the jobs from arq (`arq_functions`, `arq_cron_jobs`) |
| `postgres` | `psycopg[binary]>=3.1` | PostgreSQL, including `postgresql+asyncpg://` URLs |
| `mysql` | `pymysql>=1.1` | MySQL, including `mysql+aiomysql://` and `mysql+asyncmy://` URLs |

SQLite needs no extra. Use it to try things out, and PostgreSQL or MySQL in production.

## Quickstart

The full walkthrough is the [FastAPI quickstart](../getting-started/fastapi.md). The shortest working version:

1. Write a starter configuration.

    ```bash
    dpdpkit init
    ```

2. Create the adapter and install it on your app.

    ```python title="main.py"
    import os

    from fastapi import Depends, FastAPI, Request

    from dpdpkit.fastapi import DPDPKit, require_consent

    app = FastAPI()


    def current_user(request: Request) -> str | None:
        return request.headers.get("X-User")  # stand-in: return your signed-in user's primary key


    dpdp = DPDPKit(
        db_url=os.environ.get("DATABASE_URL", "sqlite:///./app.db"),
        config="dpdpkit.yaml",
        principal_resolver=current_user,
        signing_key=os.environ.get("DPDPKIT_SIGNING_KEY", "dev-only"),
        migrate_on_startup=True,
    )
    dpdp.install(app, prefix="/dpdp")


    @app.post("/offers/send", dependencies=[Depends(require_consent("marketing"))])
    def send_offer() -> dict[str, bool]:
        return {"sent": True}
    ```

3. Run it, record a consent and check the ledger.

    ```bash
    uvicorn main:app --reload
    curl -X POST localhost:8000/dpdp/consents -H "X-User: u_42" -H "content-type: application/json" \
         -d '{"decisions": [{"purpose": "marketing", "granted": true}]}'
    dpdpkit ledger verify --kit main:dpdp
    ```

Without consent, `/offers/send` returns `403` with the error code `consent_required`. The endpoints are described
in the [REST contract](../reference/rest.md).

## Configuration

Everything is a keyword argument to `DPDPKit(...)`. Give it either `config` or `policy`, and one of `db_url`,
`engine` or `repository`.

| Argument | Type | Default | What it does |
| --- | --- | --- | --- |
| `principal_resolver` | `callable(request)` | none, **required** | Returns a stable, non-personal id for the signed-in user (a primary key, not an email), or `None`. May be `async`. |
| `admin_guard` | `callable(request)` | `None` | Returns `viewer`, `handler` or `admin` for staff, `True` for admin, or `None`. With no guard every admin endpoint is refused. May be `async`. |
| `db_url` / `engine` / `repository` | URL string / SQLAlchemy engine / `Repository` | none, one is **required** | Where dpdpkit stores its tables (prefixed `dpdp_`). Async URLs are accepted and connect with the matching sync driver. |
| `config` | path or mapping | `None` | A [`dpdpkit.yaml`](dpdpkit-core.md#configuration). The notice is published if its text changed. |
| `policy`, `overlays` | string, list | `None`, `()` | Use these instead of `config` to name a [policy pack](dpdpkit-policies.md) and [overlays](policy-overlays.md) directly. |
| `registry` | `Registry` | built from `config` | A purposes registry you assembled in code. |
| `notifier` | `Notifier` | none | Delivers pre-erasure warnings and other messages. Use `SmtpNotifier` or `SesNotifier` in production; see [Email delivery](../guides/email.md). |
| `contact`, `contact_resolver` | mapping, `callable(user_id)` | none | Organisation contact for notices, and the per-user address for warnings. |
| `identity_verifier`, `guardian_verifiers` | objects | none | Hooks to verify the requester's identity, and a guardian's, for child accounts. |
| `signing_key` | string or bytes | none | Signs consent receipts. Set a long random secret before production. |
| `tenant_id` | string | `default` | Separates ledgers when one database serves several tenants. |
| `webhooks` | list of `WebhookEndpoint` | from `webhooks:` in `config` | Outbound events, sent through a database outbox. See [Webhooks](../guides/webhooks.md). |
| `migrate_on_startup` | bool | `False` | Create and upgrade dpdpkit's tables when the object is created. |
| `create_tables` | bool | `False` | Create tables without migrations. For tests; prefer migrations. |

`install(app, prefix="/dpdp", admin_path=None, track_activity=True)` adds the routes, error handlers, an
activity middleware and the admin dashboard at `<prefix>/admin/ui/`. The middleware records signed-in activity
(throttled to once per five minutes per user), which restarts inactivity clocks.

`start_scheduler()` takes `retention_minutes` (15), `verify_hour` (2), `root_export_hour` (3, UTC, `None` turns it off),
`root_sinks` and `webhook_seconds` (30). Run it in exactly one process. To use a worker you already run, call
`register_celery(celery_app, dpdp)` or `arq_functions(dpdp)` and `arq_cron_jobs(dpdp)` from `dpdpkit.fastapi.tasks`.

### Commands

The adapter adds to the `dpdpkit` command line from [`dpdpkit-core`](dpdpkit-core.md#commands).

| Command | What it does |
| --- | --- |
| `dpdpkit migrate [--kit main:dpdp \| --db-url URL] [--revision head] [--sql]` | Apply the database migrations, or print the SQL for review. |
| `dpdpkit webhooks list\|dead\|send\|retry --kit main:dpdp` | Inspect the outbox, send due deliveries, redeliver dead ones (`--id`, `--all`). |

## API reference

The Python API is generated from the docstrings in `dpdpkit-fastapi`: see the
[FastAPI adapter](../reference/python/fastapi.md) page for `DPDPKit`, `require_consent`, `SqlAlchemyRepository`
and the webhook outbox. The HTTP endpoints are in the [REST contract](../reference/rest.md).

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ConfigError: pass db_url, engine or repository` | `DPDPKit(...)` has no storage. | Pass `db_url="sqlite:///./app.db"` or your engine. |
| `ConfigError: pass config= (a dpdpkit.yaml) or policy=` | Neither a configuration nor a policy pack was given. | Pass `config="dpdpkit.yaml"` (run `dpdpkit init` to create it). |
| `ConfigError: create a DPDPKit before using require_consent()` | `require_consent(...)` ran before any `DPDPKit` existed. | Create the `DPDPKit` object at import time, before routes are used. |
| `ConfigError: install the scheduler extra` | `start_scheduler()` needs APScheduler. | `pip install --pre "dpdpkit-fastapi[scheduler]"`, or run `dpdpkit retention run --kit main:dpdp` from cron. |
| `ConfigError: durable webhooks need the SQLAlchemy repository` | Webhooks were given with a custom `repository`. | Use `db_url` or `engine`, or drop the webhooks. |
| Every `/dpdp/admin/...` call returns 401 or 403 | There is no `admin_guard`, or it returned no role. | Pass `admin_guard`. Return `viewer`, `handler` or `admin`. |
| Endpoints answer 401 `unauthenticated` | `principal_resolver` returned `None`. | Check how your auth puts the user on the request. |
| `no such table: dpdp_...` or a migration error | The tables were never created or are out of date. | Set `migrate_on_startup=True`, or run `dpdpkit migrate --kit main:dpdp`. |
| Erasure warnings never arrive | There is no `notifier`, or no contact for the user. | Pass a real `notifier` and a `contact_resolver`. |
| Retention runs several times, or not at all | The scheduler runs in every web worker, or in none. | Start it in one process only, or use cron or a Celery or arq worker. |
| `database is locked` on SQLite | Several processes write to one file. | Use PostgreSQL or MySQL for anything beyond a single process. |

## Upgrading

Upgrade `dpdpkit-fastapi` and `dpdpkit-core` in the same step: the adapter accepts core in the same minor series
only (`>=0.1.0a2,<0.2`). After upgrading, apply the new migrations with `dpdpkit migrate --kit main:dpdp`, or leave
`migrate_on_startup=True` to do it on start. Use `--sql` to review the change first.

There are no breaking changes to report yet: `0.1.0a3` is part of the first alpha series, and it adds the bundled
admin dashboard at `<prefix>/admin/ui/`. Read the
[changelog](https://github.com/dpdpkit-dev/dpdpkit-fastapi/blob/main/CHANGELOG.md) before each upgrade.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
