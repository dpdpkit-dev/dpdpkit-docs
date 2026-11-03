# dpdpkit-server

The server image: `dpdpkit-fastapi` packaged as a Docker container that runs the dpdpkit REST API and admin dashboard with its own database. Your backend, in any language, calls it over HTTP. Use it if your stack is not Python; for FastAPI or Django see [`dpdpkit-fastapi`](dpdpkit-fastapi.md) or [`dpdpkit-django`](dpdpkit-django.md).

| | |
| --- | --- |
| Install | `docker pull ghcr.io/dpdpkit-dev/server` |
| Version | 0.1.0a3 |
| Requires | Docker (or any OCI runtime) and PostgreSQL for anything beyond a trial. Images are `linux/amd64` and `linux/arm64`. |
| Source | [dpdpkit-server](https://github.com/dpdpkit-dev/dpdpkit-server) · [Changelog](https://github.com/dpdpkit-dev/dpdpkit-server/blob/main/CHANGELOG.md) |
| Demo | [Try it on the demo site](https://dpdpkit-demo.onrender.com/packages/server) (fictional data; can take a minute or more to wake) |

The image is also published as a Python package, `dpdpkit-server` (`pip install --pre "dpdpkit-server[postgres]"`), which
runs the same server with `python -m dpdpkit.server`. It installs [`dpdpkit-core`](dpdpkit-core.md) and
[`dpdpkit-fastapi`](dpdpkit-fastapi.md). Pick one backend: this image, the FastAPI adapter or the Django app. See the
[package index](index.md).

!!! warning "Not legal advice"
    dpdpkit-server records and enforces what you configure. Notice wording, purposes and retention periods are
    decisions for you and your counsel, and using the package does not guarantee compliance with the DPDP Act, 2023
    or the DPDP Rules, 2025.

## How it fits together

```text
browser ── @dpdpkit/embed ──(end-user token)──► dpdpkit-server ◄──(API key)── your backend
                                                  │      ▲
                                      signed webhook    └── confirmation
                                                  ▼
                                              your backend ── erases or exports your own data
```

- Your backend holds an **API key** and calls the server to mint end-user tokens and to confirm webhook events.
- Your front end loads `@dpdpkit/embed`, which calls the server with the short-lived **end-user token** your backend minted.
- When data must be erased or exported, the server sends a signed `erasure.due` or `export.requested` webhook. Your
  backend acts on its own data, then confirms. A request that is never confirmed stays open and shows as overdue.

## Install

```bash
docker pull ghcr.io/dpdpkit-dev/server:0.1.0a3
```

Pin a version in production. The tag `latest` follows the newest release. Images carry an SBOM and build provenance and
are signed with cosign. Verify before you run:

```bash
cosign verify ghcr.io/dpdpkit-dev/server:0.1.0a3 \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity-regexp '^https://github.com/dpdpkit-dev/dpdpkit-server/\.github/workflows/release-image\.yml@refs/tags/v'
```

The container runs as the non-root user `10001:10001` and works on a read-only file system, so start it with
`--read-only --tmpfs /tmp`. It needs no writable path other than `/tmp`.

## Quickstart

Docker Compose runs Postgres, the API and one worker. From a clone of
[dpdpkit-server](https://github.com/dpdpkit-dev/dpdpkit-server):

1. Create the secrets file.

    ```bash
    cp .env.example .env
    ```

2. Make an API key. The key goes to your backend; only its hash goes in `.env`.

    ```bash
    docker run --rm ghcr.io/dpdpkit-dev/server new-api-key
    ```

3. Fill in `.env`: `POSTGRES_PASSWORD`, `DPDPKIT_SIGNING_KEY` (for example `openssl rand -hex 32`),
   `DPDPKIT_API_KEY_HASHES` and `APP_WEBHOOK_SECRET`. Compose refuses to start while a required value is empty.

4. Edit `dpdpkit.example.yaml`: purposes, notice and the `webhooks:` list for your app. Then start everything.

    ```bash
    docker compose up -d
    curl localhost:8000/healthz
    curl localhost:8000/readyz
    ```

`/healthz` answers once the server is up, and `/readyz` answers `200` once the database responds. The consent API is
under `/dpdp` (same contract as the [REST contract](../reference/rest.md)) and the admin dashboard is at
`http://localhost:8000/dpdp/admin/ui/`.

### Compose file

The compose file in the repository is the reference. Its shape:

```yaml title="docker-compose.yml (abridged)"
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: dpdpkit
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD in .env}
      POSTGRES_DB: dpdpkit
    volumes: [pgdata:/var/lib/postgresql/data]

  server:
    image: ghcr.io/dpdpkit-dev/server:${DPDPKIT_VERSION:-latest}
    read_only: true
    tmpfs: [/tmp]
    ports: ["127.0.0.1:8000:8000"]
    volumes: ["./dpdpkit.example.yaml:/etc/dpdpkit/dpdpkit.yaml:ro"]
    environment:
      DPDPKIT_CONFIG: /etc/dpdpkit/dpdpkit.yaml
      DPDPKIT_DATABASE_URL: postgresql://dpdpkit:${POSTGRES_PASSWORD}@postgres:5432/dpdpkit
      DPDPKIT_SIGNING_KEY: ${DPDPKIT_SIGNING_KEY}
      DPDPKIT_API_KEY_HASHES: ${DPDPKIT_API_KEY_HASHES}
      APP_WEBHOOK_SECRET: ${APP_WEBHOOK_SECRET}
      DPDPKIT_MIGRATE_ON_STARTUP: "true"
    depends_on:
      postgres: {condition: service_healthy}

  worker:                       # run exactly one
    image: ghcr.io/dpdpkit-dev/server:${DPDPKIT_VERSION:-latest}
    command: ["worker"]
    # same read_only, tmpfs, volumes and environment as server, without DPDPKIT_MIGRATE_ON_STARTUP
    ports: ["127.0.0.1:8001:8000"]
    depends_on:
      server: {condition: service_healthy}

volumes:
  pgdata:
```

The ports are bound to `127.0.0.1`. Put a reverse proxy with TLS in front before exposing the API, and keep
`/healthz`, `/readyz` and `/metrics` off the public internet: they take no credentials.

### The worker

The periodic jobs (retention, daily ledger verification, root-hash export and webhook delivery) run in a separate
container from the same image:

```bash
docker run --read-only --tmpfs /tmp -p 8001:8000 -e DPDPKIT_DATABASE_URL=... ghcr.io/dpdpkit-dev/server worker
```

Run **exactly one** worker. Two workers would run retention and deliver webhooks twice. The worker serves its own
`/healthz`, `/readyz` and `/metrics`.

## Node example

[`examples/node-express`](https://github.com/dpdpkit-dev/dpdpkit-server/tree/main/examples/node-express) is an Express app
(Node 18+) with a small client that has no dependencies. It does the two jobs your backend has:

- `POST /api/privacy-token` mints a short-lived end-user token for the consent widget. The API key stays on the backend.
- `POST /dpdpkit/webhook` verifies `X-DPDPKit-Signature` over the **raw** body, acts on the event and confirms it.

```js title="dpdpkit.js (excerpt)"
export class DpdpkitClient {
  constructor({ baseUrl, apiKey, fetchImpl = fetch }) { /* ... */ }

  // A short-lived token for the consent widget, bound to one of your users.
  createUserToken(subject, { scope = "", ttlSeconds = 900 } = {}) {
    return this.#post("/v1/tokens", { subject, scope, ttl_seconds: ttlSeconds });
  }

  // Tell the server that you acted on an erasure.due or export.requested event.
  confirm({ eventType, eventId, subjectId, status = "completed", message = "" }) {
    return this.#post("/v1/webhooks/confirmations", {
      event_type: eventType, event_id: eventId, subject_id: subjectId, status, message,
    });
  }
}
```

Run it against the Compose stack, with the API key whose hash you put in `.env` and the same webhook secret:

```bash
cd examples/node-express
npm install
DPDPKIT_API_KEY=dpk_... APP_WEBHOOK_SECRET=... npm start
curl -X POST localhost:3000/api/privacy-token -H 'x-demo-user: user-1'
```

The example config points the `app` webhook at `http://host.docker.internal:3000/dpdpkit/webhook`, which is this app
running on your machine. The demo identifies the user by an `x-demo-user` header; replace `currentUser` with your own
session. `npm test` runs the signature, token and confirmation tests.

## Laravel example

[`examples/laravel`](https://github.com/dpdpkit-dev/dpdpkit-server/blob/main/examples/laravel/README.md) is a snippet for
Laravel 10+ (PHP 8.1+) that uses the built-in HTTP client. It is a snippet to copy, not a package, and it has not been
run against a live server. Treat it as a starting point and test it.

Configuration in `config/services.php`:

```php
'dpdpkit' => [
    'url' => env('DPDPKIT_URL', 'http://localhost:8000'),
    'api_key' => env('DPDPKIT_API_KEY'),               // dpk_..., from `new-api-key`; backend only
    'webhook_secret' => env('DPDPKIT_WEBHOOK_SECRET'), // same value as APP_WEBHOOK_SECRET on the server
],
```

Verifying a webhook. The signature is `t=<unix>,v1=<hex hmac-sha256 of "<t>.<raw body>">`:

```php
public static function verifySignature(string $secret, string $rawBody, ?string $header, int $tolerance = 300): bool
{
    $parts = [];
    foreach (explode(',', (string) $header) as $part) {
        [$key, $value] = array_pad(explode('=', $part, 2), 2, null);
        $parts[$key] = $value;
    }
    if (! isset($parts['t'], $parts['v1']) || ! ctype_digit($parts['t'])) {
        return false;
    }
    if (abs(time() - (int) $parts['t']) > $tolerance) {
        return false;
    }

    return hash_equals(hash_hmac('sha256', $parts['t'].'.'.$rawBody, $secret), $parts['v1']);
}
```

Handling the webhook in a controller:

```php
public function webhook(Request $request, Dpdpkit $dpdpkit)
{
    // The signature covers the exact bytes: use getContent(), not the parsed input.
    $raw = $request->getContent();
    if (! Dpdpkit::verifySignature(config('services.dpdpkit.webhook_secret'), $raw, $request->header('X-DPDPKit-Signature'))) {
        abort(401, 'bad signature');
    }

    $event = json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
    $data = $event['data'] ?? [];

    if ($event['type'] === 'erasure.due') {
        // Erase $data['purpose'] data of $data['principal'] in your own tables here.
        $dpdpkit->confirm($event['type'], $event['id'], $data['schedule_id']);
    } elseif ($event['type'] === 'export.requested') {
        // Build and deliver the export for $data['principal'] here.
        $dpdpkit->confirm($event['type'], $event['id'], $data['request_id']);
    }

    return response()->noContent();
}
```

The repository snippet also has the `Dpdpkit` service class (`userToken`, `confirm`) and the routes. Exempt
`dpdpkit/webhook` from CSRF: in Laravel 11 use `$middleware->validateCsrfTokens(except: ['dpdpkit/webhook']);` in
`bootstrap/app.php`, and in Laravel 10 add the path to `VerifyCsrfToken::$except`.

## Webhooks and confirmations

The server sends `erasure.due` and `export.requested`, signed in the `X-DPDPKit-Signature` header and retried with
backoff. Declare the receivers under `webhooks:` in `dpdpkit.yaml`; the signing secret is read from the environment
variable named by `secret_env`. See [Webhooks](../guides/webhooks.md) for the event payloads.

After your app has acted on its own data, confirm with the event `id`:

```bash
curl -X POST http://localhost:8000/v1/webhooks/confirmations \
  -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
  -d '{"event_type": "export.requested", "event_id": "ev_...", "subject_id": "<request_id>", "status": "completed"}'
```

`subject_id` is the `schedule_id` for `erasure.due` and the `request_id` for `export.requested`, both taken from the
event data. Confirmations are idempotent on the event id, so a retried webhook is safe. Return a non-2xx status from
your endpoint to make the server retry. Failed deliveries are listed at `GET /admin/webhooks/dead-letters` and can be
queued again with `POST /admin/webhooks/redeliver`.

## Configuration

Settings come from environment variables or the `server:` section of a mounted `dpdpkit.yaml`. The environment wins.
They are loaded and checked at start-up, and a bad value stops the container with a `configuration error`.

| Setting | Variable | `server:` key | Default |
| --- | --- | --- | --- |
| Config file | `DPDPKIT_CONFIG` | not allowed | `/etc/dpdpkit/dpdpkit.yaml`, then `./dpdpkit.yaml`, if present |
| Bind address | `DPDPKIT_HOST` | `host` | `0.0.0.0` |
| Port | `DPDPKIT_PORT` | `port` | `8000` |
| Log level | `DPDPKIT_LOG_LEVEL` | `log_level` | `info` |
| Migrate on start | `DPDPKIT_MIGRATE_ON_STARTUP` | `migrate_on_startup` | `false` |
| Database URL (secret) | `DPDPKIT_DATABASE_URL` or `DPDPKIT_DATABASE_URL_FILE` | not allowed | none, **required** |
| Signing key (secret) | `DPDPKIT_SIGNING_KEY` or `DPDPKIT_SIGNING_KEY_FILE` | not allowed | none, **required** in production |
| API key hashes | `DPDPKIT_API_KEY_HASHES` | `api_key_hashes` | none; comma-separated, **required** for your backend to call the API |
| Admin password hash (secret) | `DPDPKIT_ADMIN_PASSWORD_HASH` or `_FILE` | not allowed | none; enables `POST /admin/login` |
| Admin emails | `DPDPKIT_ADMIN_EMAILS` | `admin_emails` | none; who may sign in through OIDC |
| OIDC | `DPDPKIT_OIDC_ISSUER`, `_CLIENT_ID`, `_REDIRECT_URI` | `oidc_issuer`, `oidc_client_id`, `oidc_redirect_uri` | none |
| OIDC client secret (secret) | `DPDPKIT_OIDC_CLIENT_SECRET` or `_FILE` | not allowed | none |

Secrets cannot be put in the file: the server refuses to start if `server:` contains one. Use the `_FILE` form with
Docker or Kubernetes secrets, and set only one of the two forms. Make the values with the image's own commands:

| Command | What it does |
| --- | --- |
| `docker run --rm ghcr.io/dpdpkit-dev/server new-api-key` | Prints an API key (`dpk_...`) and its SHA-256 hash. Give the key to your backend and put the hash in `DPDPKIT_API_KEY_HASHES`. |
| `docker run --rm -it ghcr.io/dpdpkit-dev/server hash-password` | Makes an admin password hash. Single-quote it in `.env`, because it contains `$`. |
| `docker run ... ghcr.io/dpdpkit-dev/server worker` | Runs the periodic jobs instead of the API. |

The purposes, notice, contact details, retention and overlays live in `dpdpkit.yaml`, the same file the other
backends use: see the [`dpdpkit-core` configuration](dpdpkit-core.md#configuration).

### Endpoints the server adds

| Endpoint | Auth | What it does |
| --- | --- | --- |
| `POST /v1/tokens` | API key | Mints a short-lived end-user token for the widgets (`subject`, `scope`, `ttl_seconds`). |
| `POST /v1/webhooks/confirmations` | API key | Records that your app acted on a webhook event. |
| `POST /admin/login` | admin password | Returns an admin session token. |
| `GET /admin/webhooks/deliveries`, `/admin/webhooks/dead-letters`, `POST /admin/webhooks/redeliver` | admin | Inspect and re-queue webhook deliveries. |
| `/dpdp/...` | end-user token | The consent and rights API, the same contract as in the [REST contract](../reference/rest.md). |
| `/healthz`, `/readyz`, `/metrics` | none | Liveness, readiness (503 until the database responds) and Prometheus metrics. |

## API reference

The server has no Python API of its own to import. Its HTTP endpoints are in the [REST contract](../reference/rest.md),
and the code behind the `/dpdp` routes is in the [FastAPI adapter](../reference/python/fastapi.md) reference. The shared
conformance suite runs against the built image in CI.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `set POSTGRES_PASSWORD in .env` (or another variable) when running `docker compose up` | A required value in `.env` is empty. | Fill in `.env`; see the comments in `.env.example`. |
| `dpdpkit-server: configuration error: DPDPKIT_DATABASE_URL needs a dpdpkit.yaml (set DPDPKIT_CONFIG or mount it)` | A database was set but no config file was found. | Mount `dpdpkit.yaml` at `/etc/dpdpkit/dpdpkit.yaml`. |
| `configuration error: the worker needs DPDPKIT_DATABASE_URL` | The worker started without a database. | Give it the same environment as the server. |
| `configuration error: DPDPKIT_CONFIG points to ..., which is not a file` | The path is wrong or the volume is not mounted. | Check the mount and the path inside the container. |
| `configuration error: ...: server.database_url is a secret; set DPDPKIT_DATABASE_URL instead` | A secret was put in the `server:` section. | Move it to the environment or a `_FILE` secret. |
| `configuration error: set only one of DPDPKIT_DATABASE_URL and DPDPKIT_DATABASE_URL_FILE` | Both forms are set. | Remove one. |
| `/readyz` returns 503 | The database is unreachable or not ready. | Check the URL, the network and that Postgres is up. Compose waits for the Postgres health check. |
| API calls return 401 | The API key is missing or its hash is not in `DPDPKIT_API_KEY_HASHES`. | Send `Authorization: Bearer dpk_...` and re-check the hash from `new-api-key`. |
| Webhook endpoint rejects the signature | The raw body was parsed first, the secret differs, or the clock is off by more than 300 seconds. | Verify over the raw bytes, use the value of `APP_WEBHOOK_SECRET` and keep clocks in sync. |
| Webhooks never reach a local app | The container cannot reach `localhost` of the host. | Use `http://host.docker.internal:3000/...` as in the example config; Compose adds the host mapping. |
| Requests stay open and show as overdue | Your app never confirmed the event. | Call `/v1/webhooks/confirmations` with the event `id`; redeliver from the dead-letter list if needed. |
| Retention and webhooks run twice | More than one worker is running. | Run exactly one `worker` container. |
| Read-only file system errors | The container was started without `--tmpfs /tmp`. | Add `--read-only --tmpfs /tmp`. |

## Upgrading

Change the image tag, pull it and restart. Upgrade the server and the worker together, and pin the tag
(`DPDPKIT_VERSION` in Compose). With `DPDPKIT_MIGRATE_ON_STARTUP=true` the API container applies new database
migrations when it starts; the worker should start after it, which is what the compose `depends_on` does. Take a
database backup first.

There are no breaking changes to report yet: `0.1.0a3` is part of the first alpha series, and APIs can still change
between pre-releases. Read the
[changelog](https://github.com/dpdpkit-dev/dpdpkit-server/blob/main/CHANGELOG.md) before each upgrade.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
