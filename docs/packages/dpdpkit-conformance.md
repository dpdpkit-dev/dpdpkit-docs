# dpdpkit-conformance

The OpenAPI 3.1 contract for the dpdpkit REST API, and a black-box pytest suite that checks a server against it. Use it if you write your own backend or adapter that must behave like [`dpdpkit-fastapi`](dpdpkit-fastapi.md), [`dpdpkit-django`](dpdpkit-django.md) or the [server image](dpdpkit-server.md), or if you want to check a deployment of one of them.

| | |
| --- | --- |
| Install | `pip install --pre "dpdpkit-conformance[asgi]"` |
| Version | 0.1.0a2 |
| Requires | Python 3.10+, pytest 8, httpx; `starlette` for the `asgi` extra |
| Source | [dpdpkit-spec](https://github.com/dpdpkit-dev/dpdpkit-spec) · [Changelog](https://github.com/dpdpkit-dev/dpdpkit-spec/blob/main/CHANGELOG.md) |
| Demo | [Try it on the demo site](https://demo.dpdpkit.dev/packages/ci) (fictional data) |

See the [package index](index.md) for the other packages.

!!! warning "Not legal advice"
    Passing the suite shows that a server follows the dpdpkit API. It does not show that your notice, purposes or
    retention periods meet the DPDP Act, 2023 or the DPDP Rules, 2025, and using the package does not guarantee
    compliance.

## Install

```bash
pip install --pre "dpdpkit-conformance[asgi]"
```

| Extra | Adds |
| --- | --- |
| `asgi` | Starlette, so the suite can run in-process against an ASGI app. Not needed to test a running server. |

The wheel includes `openapi.yaml`, which the `@dpdpkit/client` types are generated from. The REST contract is
described on the [REST contract](../reference/rest.md) page.

## Quickstart

1. Prepare the app under test (see [What the app must do](#what-the-app-must-do)).
2. Run the suite against a running server, giving the base URL including the dpdpkit prefix:

    ```bash
    DPDPKIT_BASE_URL=http://localhost:8000/dpdp dpdpkit-conformance
    ```

    or in-process against an ASGI app, as `module:attribute` importable from the current folder:

    ```bash
    DPDPKIT_ASGI_APP=app:app DPDPKIT_PREFIX=/dpdp dpdpkit-conformance
    ```

3. The run is a normal pytest run and ends with a pytest summary such as `N passed`. Any extra arguments go to pytest, for
   example `dpdpkit-conformance -x -k consent`.

### What the app must do

1. Publish a notice with at least one consent-based purpose. Without a consent purpose the consent tests are skipped.
2. Run in **conformance mode**: take the principal from the `X-DPDP-Test-Principal` header and the admin role
   (`viewer`, `handler` or `admin`) from `X-DPDP-Test-Role`. Turn this on only in a test configuration, because it
   lets any caller choose their identity.
3. Register at least one erasure handler. The suite does not trigger erasure, but a production-like setup has one.

The suite creates records with principals named `conf-...`, so run it against a test database, not production.

### Upgrade check

To check that a release keeps data written by the previous one:

```bash
dpdpkit-conformance upgrade seed --state seed.json     # app on the previous release
# install the new release and run its migrations
dpdpkit-conformance upgrade verify --state seed.json   # checks the data, then re-runs the suite
```

Add `--no-suite` to `verify` to check the seeded data only.

## Configuration

| Variable | Default | Meaning |
| --- | --- | --- |
| `DPDPKIT_BASE_URL` | none | Base URL of a running server, including the prefix. Used when `DPDPKIT_ASGI_APP` is not set. |
| `DPDPKIT_ASGI_APP` | none | `module:attribute` of an ASGI app to run in-process. Needs the `asgi` extra. |
| `DPDPKIT_PREFIX` | `/dpdp` | Path prefix the app is mounted on, for in-process runs. |

Set one of `DPDPKIT_BASE_URL` or `DPDPKIT_ASGI_APP`. The command line is `dpdpkit-conformance [pytest args]` or
`dpdpkit-conformance upgrade (seed|verify) --state FILE [--no-suite] [pytest args]`.

### Using it in CI

Adapter CI installs the suite from git, or from PyPI, and runs it against the example app:

```bash
pip install --pre "dpdpkit-conformance[asgi]"
DPDPKIT_ASGI_APP=app:app dpdpkit-conformance
```

dpdpkit adapters do not release if this fails. The same rule is a good one for your own backend.

### Changing the contract

Additive changes, such as a new optional field or endpoint, are minor releases. Removing or renaming anything is a
breaking change and is deprecated first. See [Versioning and deprecation](../reference/deprecation.md).

## API reference

The REST contract is documented in the [REST contract](../reference/rest.md). The package also exposes a few helpers
for writing your own tests: `openapi()`, `schema_errors(instance, schema_name)`, `assert_schema(instance, schema_name)`,
`PRINCIPAL_HEADER` and `ROLE_HEADER`, all from `dpdpkit_conformance`. They have no generated reference page.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `set DPDPKIT_BASE_URL (e.g. http://localhost:8000/dpdp) or DPDPKIT_ASGI_APP` and exit code 4 | Neither variable is set. | Set one. |
| `app under test must publish a notice before conformance runs` | `GET /notices/current` did not return 200. | Publish a notice, and check the base URL includes the prefix. |
| Many 404 responses | The base URL or `DPDPKIT_PREFIX` is wrong. | The URL must end at the dpdpkit prefix, for example `/dpdp`. |
| Many 401 or 403 responses on admin tests | Conformance mode is off, so the test headers are ignored. | Enable the `X-DPDP-Test-Principal` and `X-DPDP-Test-Role` headers in the test configuration. |
| `ModuleNotFoundError` for your app | The module is not importable from the current folder. | Run from the folder that contains it, or install your app. |
| `No module named 'starlette'` | The `asgi` extra is missing. | `pip install --pre "dpdpkit-conformance[asgi]"`. |
| `upgrade check failed: ...` | Data seeded before the upgrade is missing or changed. | Check the migration, then run `verify` again. |
| Consent tests are skipped | The notice has no consent-based purpose. | Add one to the test notice. |

## Upgrading

Upgrade `dpdpkit-conformance` with the adapter you test: a newer suite can check endpoints an older adapter lacks.
Check the [changelog](https://github.com/dpdpkit-dev/dpdpkit-spec/blob/main/CHANGELOG.md) for contract changes first.

There are no breaking changes to report yet: `0.1.0a2` is part of the first alpha series.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
