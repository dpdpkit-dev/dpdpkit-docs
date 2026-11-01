# FastAPI quickstart

By the end of this page your FastAPI app will show a consent notice, record per-purpose consent in a
tamper-evident ledger, block a feature until the user consents, take rights requests and run erasure
schedules. Allow about 30 minutes.

You need Python 3.10+ and an existing FastAPI app. Any SQLAlchemy database works: SQLite for trying it
out, Postgres or MySQL in production.

## 1. Install

```bash
pip install --pre "dpdpkit[fastapi]" "dpdpkit-fastapi[scheduler]"
```

`--pre` is needed while dpdpkit is in alpha. Add `dpdpkit-fastapi[postgres]` or `[mysql]` for a database
driver.

## 2. Describe your purposes

```bash
dpdpkit init
```

This writes `dpdpkit.yaml`. Open it and change three things:

- **`contact`**: your organisation's name, privacy email and rights page. They appear in every notice
  and every response to a rights request.
- **`purposes`**: one entry per reason you process personal data. Each lists the `data_items` it
  uses and, optionally, a `retention` rule. The starter file has `account` (required to run the service,
  erased after 3 years of inactivity) and `marketing` (optional, erased when consent is withdrawn).
  For ed-tech, health, e-commerce, fintech or SaaS, start from a fuller file with
  `dpdpkit init --template <sector>` (see [Industry purpose templates](../guides/purpose-templates.md)).
- **`notice`**: the title, body and links shown with the consent form. Add `translations` for each
  language you serve.

!!! warning "These are legal decisions"
    Which purposes need consent, what the notice says and how long data is kept are decisions for you
    and your counsel. dpdpkit records and enforces what you configure.

The `policy:` line pins the rules pack (deadlines, warning periods, log retention). See
[Policy packs](../concepts/policy-packs.md).

## 3. Wire it into your app

```python title="main.py"
import os

from fastapi import Depends, FastAPI, Request

from dpdpkit import ConsoleNotifier, Contact
from dpdpkit.fastapi import DPDPKit, require_consent

app = FastAPI()


def current_user(request: Request) -> str | None:
    # Return a stable, non-personal id for the signed-in user (a primary key, not an email).
    return request.headers.get("X-User")  # stand-in: replace with your auth


def staff_role(request: Request) -> str | None:
    # "viewer", "handler" or "admin" for staff; None for everyone else.
    return "admin" if request.headers.get("X-User") == "staff" else None


def contact_for(user_id: str) -> Contact | None:
    # Where to send pre-erasure warnings. Look the user up in your own tables.
    return Contact(email=f"{user_id}@example.in")


dpdp = DPDPKit(
    db_url=os.environ.get("DATABASE_URL", "sqlite:///./app.db"),
    config="dpdpkit.yaml",
    principal_resolver=current_user,
    admin_guard=staff_role,
    contact_resolver=contact_for,
    notifier=ConsoleNotifier(),  # prints messages; use SmtpNotifier in production
    signing_key=os.environ.get("DPDPKIT_SIGNING_KEY", "dev-only"),
    migrate_on_startup=True,
)
dpdp.install(app, prefix="/dpdp")
```

`install()` adds the REST endpoints under `/dpdp`, error handlers, a middleware that records user
activity (which resets inactivity clocks), and the admin dashboard mount.

`principal_resolver` and `admin_guard` may be sync or async and receive the FastAPI `Request`, so they
can read whatever your auth layer puts on it (`request.state.user`, a session or a JWT).

`migrate_on_startup=True` creates and upgrades dpdpkit's tables (all prefixed `dpdp_`). In production
you may prefer to run migrations as a deploy step instead:

```bash
dpdpkit migrate --kit main:dpdp       # or: --db-url "$DATABASE_URL"
dpdpkit migrate --sql --db-url postgresql://   # print the SQL for review
```

Start the app:

```bash
uvicorn main:app --reload
```

## 4. Show the notice and record consent

Your frontend fetches the current notice and posts the user's choices. Nothing is pre-ticked; each
optional purpose is a separate decision.

```bash
curl "localhost:8000/dpdp/notices/current?locale=hi"

curl -X POST localhost:8000/dpdp/consents -H "X-User: u_42" -H "content-type: application/json" \
     -d '{"decisions": [{"purpose": "account", "granted": true}, {"purpose": "marketing", "granted": true}]}'

curl localhost:8000/dpdp/consents/me -H "X-User: u_42"
curl localhost:8000/dpdp/consents/me/receipt -H "X-User: u_42"     # signed receipt
```

Every decision is written to the hash-chained ledger with the notice version and content hash the user
saw.

For React, [`@dpdpkit/react`](https://www.npmjs.com/package/@dpdpkit/react) provides `<ConsentNotice>`,
`<PreferenceCenter>` and `<RightsRequestForm>` that call these endpoints. Other frontends can use
[`@dpdpkit/client`](https://www.npmjs.com/package/@dpdpkit/client).

## 5. Gate features on consent

```python title="main.py"
@app.post("/offers/send", dependencies=[Depends(require_consent("marketing"))])
def send_offer() -> dict[str, bool]:
    return {"sent": True}
```

Without consent the endpoint returns `403` with `{"error": {"code": "consent_required", ...}}` naming the
purpose, so the frontend can ask for it. In background jobs, check directly:

```python
if dpdp.kit.consent.check(user_id, "marketing"):
    ...
```

Withdrawal is one call, and it takes effect immediately:

```bash
curl -X POST localhost:8000/dpdp/consents/marketing/withdraw -H "X-User: u_42"
curl -X POST localhost:8000/offers/send -H "X-User: u_42"     # 403 consent_required
```

### Async apps

If your app uses async SQLAlchemy, give dpdpkit the same URL or engine:

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("postgresql+asyncpg://app:secret@db/app")
dpdp = DPDPKit(engine=engine, ...)          # or db_url="postgresql+asyncpg://..."
```

dpdpkit's core is synchronous, so it connects with the matching sync driver (asyncpg → psycopg,
aiosqlite → sqlite, aiomysql/asyncmy → PyMySQL) through its own small connection pool. Install it with
`dpdpkit-fastapi[postgres]` or `[mysql]`. The REST endpoints already run in a threadpool. In your own
`async def` code, call kit methods through `dpdp.run()` so the event loop is never blocked:

```python
@app.post("/newsletter")
async def newsletter(user=Depends(current_user)):
    if await dpdp.run(dpdp.kit.consent.check, user.id, "marketing"):
        ...
```

## 6. Tell dpdpkit how to erase and export your data

dpdpkit never touches your own tables. You register two kinds of function:

```python title="main.py"
@dpdp.kit.retention.register_handler
def erase_user_data(user_id: str, purposes: list[str]) -> None:
    # Delete or anonymise this user's rows for these purposes. Raise if anything fails.
    if "account" in purposes:
        ...  # e.g. db.execute(delete(User).where(User.id == user_id))
    if "marketing" in purposes:
        ...  # e.g. remove them from your mailing list


dpdp.kit.export.register_collector("orders", lambda user_id: {"orders": []})  # your data for access requests
```

If a handler raises, the erasure is marked `needs_attention` and nothing is retried until a person
resolves it. See [Retention and erasure](../concepts/retention.md) for every fail-safe.

## 7. Rights requests

Users open requests; staff work them through the admin API (or the admin dashboard from v0.4).

```bash
curl -X POST localhost:8000/dpdp/requests -H "X-User: u_42" -H "content-type: application/json" \
     -d '{"kind": "erasure", "details": {}}'

curl "localhost:8000/dpdp/admin/requests?open=true" -H "X-User: staff"

curl -X PATCH localhost:8000/dpdp/admin/requests/<id> -H "X-User: staff" -H "content-type: application/json" \
     -d '{"action": "respond", "message": "Your account data has been erased."}'
```

Deadlines come from the policy pack. Responding to an erasure request calls your erasure handlers,
respecting legal holds and purposes kept under a legal obligation.

## 8. Run the scheduler

Retention warnings and erasures run on a schedule. In **one** process (not every web worker):

```python
dpdp.start_scheduler(retention_minutes=15)
```

This runs retention every 15 minutes, verifies the ledger daily, exports the ledger root hash daily and
sends any queued [webhooks](../guides/webhooks.md).
Without APScheduler, call the CLI from cron instead:

```bash
dpdpkit retention run --kit main:dpdp
dpdpkit ledger verify --kit main:dpdp
```

## 9. Check it works

```bash
dpdpkit ledger verify --kit main:dpdp              # ok: N rows verified
dpdpkit retention preview --kit main:dpdp          # what will be warned or erased this week
curl localhost:8000/dpdp/me/export -H "X-User: u_42"   # what an access request returns
```

The full contract is tested by the conformance suite. Point it at your app to check nothing is missing:

```bash
pip install --pre "dpdpkit-conformance[asgi]"
DPDPKIT_ASGI_APP=main:app dpdpkit-conformance
```

The suite authenticates with test headers, so your resolvers must honour them while it runs. See
[`examples/fastapi_shop`](https://github.com/dpdpkit-dev/dpdpkit-fastapi/tree/main/examples/fastapi_shop)
for the pattern.

## Before production

- [ ] Replace the stand-in `current_user` and `staff_role` with your real auth.
- [ ] Set `DPDPKIT_SIGNING_KEY` to a long random secret, kept out of source control.
- [ ] Use `SmtpNotifier`, `SesNotifier` or your own notifier so pre-erasure warnings are actually
  delivered. See [Email delivery](../guides/email.md).
- [ ] Register erasure handlers for every purpose that has a retention rule, and test them.
- [ ] Run the scheduler in exactly one process.
- [ ] Export the ledger root hash somewhere you cannot rewrite. See [Anchoring](../guides/anchoring.md).
- [ ] If other systems must act on erasures or withdrawals, configure [webhooks](../guides/webhooks.md).
- [ ] Have counsel review `dpdpkit.yaml`: purposes, notice text, translations and retention periods.
