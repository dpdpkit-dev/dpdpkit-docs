# dpdpkit-admin

The self-hosted admin dashboard: a static web app where your team works the rights request queue, watches consent and retention, records incidents and downloads the audit evidence pack. You do not install it on its own: it ships inside [`dpdpkit-fastapi`](dpdpkit-fastapi.md), [`dpdpkit-django`](dpdpkit-django.md) and the [server image](dpdpkit-server.md), so read this page if you run one of them and want to know what the dashboard does and who can use it.

| | |
| --- | --- |
| Install | None. It is bundled into the backend packages. |
| Version | 0.1.0-alpha.2 |
| Requires | A dpdpkit backend that serves the admin endpoints, and a modern browser |
| Source | [dpdpkit-admin](https://github.com/dpdpkit-dev/dpdpkit-admin) · [Changelog](https://github.com/dpdpkit-dev/dpdpkit-admin/blob/main/CHANGELOG.md) |
| Demo | [Try it on the demo site](https://demo.dpdpkit.dev/packages/admin) (fictional data) |

See the [package index](index.md) for the other packages.

!!! warning "Not legal advice"
    The dashboard shows what dpdpkit has recorded and drafts reports for you to review. Request handling, breach
    reporting and retention are decisions for you and your counsel, and using the package does not guarantee
    compliance with the DPDP Act, 2023 or the DPDP Rules, 2025. dpdpkit never submits a report to any authority.

## Install

There is nothing to install. Each backend package adds the dashboard bundle to its release build:

| Backend | Where the dashboard is |
| --- | --- |
| `dpdpkit-fastapi` | `<prefix>/admin/ui/`, for example `/dpdp/admin/ui/`. A source checkout serves a placeholder page; the PyPI wheel has the real dashboard. |
| `dpdpkit-django` | `<prefix>/admin/ui/`, once the app's URLs are included. |
| `dpdpkit-server` | `http://localhost:8000/dpdp/admin/ui/` in the Docker image. |

Each backend pins a dashboard version in its `admin-bundle.version` file. Every `vX.Y.Z` tag of dpdpkit-admin also
publishes `dpdpkit-admin-X.Y.Z.tar.gz` and a `.sha256` file on its GitHub release, with `index.html` at the top
of the archive.

## Quickstart

1. Run a backend with an admin guard. For FastAPI, the [FastAPI quickstart](../getting-started/fastapi.md) sets one up:

    ```python
    dpdp.install(app, prefix="/dpdp")
    ```

    with `admin_guard` set on `DPDPKit`, for example `admin_guard=lambda request: "admin" if request.state.user.is_staff else None`.
    Without a guard every admin endpoint is refused.

2. Open `/dpdp/admin/ui/` in a browser where you are signed in as staff.
3. The **Overview** screen shows open and overdue requests, upcoming erasures and items needing attention. If it
   shows numbers instead of an error, the dashboard is talking to your backend.

The dashboard takes its API address from the page address: `/dpdp/admin/ui/` calls `/dpdp`. It sends your session
cookie and, for Django sessions, the CSRF token on writes.

## Configuration

The dashboard has no config file or environment variables. Who may do what is set in the backend, with
`admin_guard` (FastAPI) or `ADMIN_GUARD` (Django), and with the admin password or OIDC settings of the server image.

### Screens and roles

Each action needs the role shown. A guard returns `viewer`, `handler` or `admin`; a higher role includes the lower ones.

| Screen | What it does | Role |
| --- | --- | --- |
| Overview | Counts of open and overdue requests, upcoming erasures and items needing attention. | `viewer` |
| Request queue | Lists rights requests with status and due date. Per request: assign, start, mark identity verified or not (not verified rejects), respond or reject with a message. | `viewer` to read, `handler` to change |
| Consent analytics | Grants, denials and withdrawals per purpose and notice version. Contains no personal data. | `viewer` |
| Retention monitor | Upcoming warnings and erasures, and schedules that need attention with the reason. See [Retention](../concepts/retention.md). | `viewer` |
| Incident register | Lists incidents with their report deadlines, records a new incident, and shows a draft report. | `viewer` to read, `handler` to record or draft |
| Audit export | Downloads the evidence pack (a zip of CSV and PDF) and verifies both ledger hash chains. See [Ledger](../concepts/ledger.md). | `admin` for the pack, `viewer` to verify |
| Settings | Shows the current notice, its version, languages and purposes (read-only), and the API base path. | `viewer` |

### API base path

Under **Settings → Connection**, **API base path** changes where the dashboard sends its calls. It is saved in the
browser's local storage, so it applies only to that browser. Leave it empty to go back to the path taken from the
page address. Reload the screen after saving.

### Not here yet

Editing the notice and purposes, webhooks, API keys, team roles, templated responses and failed-notification counts
need backend support first. Change the notice in your configuration, and see [Webhooks](../guides/webhooks.md) for
delivery handling.

## API reference

The dashboard has no public code API. It calls the `/admin/...` endpoints and `GET /notices/current`, which are
documented in the [REST contract](../reference/rest.md).

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| A page that says the UI is a placeholder | You run a source checkout of the backend, which does not include the bundle. | Install the released wheel or use the Docker image. |
| Screens show `... failed (401)` or `(403)` | No `admin_guard`, the guard returned no role, or your role is too low. | Return `viewer`, `handler` or `admin` from the guard. Django: set `ADMIN_GUARD`, since the default gives staff `handler` and only superusers `admin`. |
| Download evidence pack fails with 403 | The pack needs the `admin` role. | Sign in as an admin, or have the guard return `admin`. |
| Screens call the wrong address | The dashboard is served from a path without `/admin/ui/`, or a saved base path is stale. | Set **API base path** under Settings, or clear it to use the default. |
| Write actions fail on Django | The CSRF cookie is missing. | Sign in through Django in the same browser, so `csrftoken` is set. |
| `This screen could not be displayed. The backend may be a different version from this dashboard.` | The backend returned a response this version does not expect. | Upgrade the backend and the dashboard together. |
| The incident register shows an error | The backend does not support incidents. | Use a backend release that includes the incident endpoints. |

## Upgrading

The dashboard version is chosen by the backend you install, so upgrade the backend package or pull a newer server
image. The pinned version is in the backend's changelog. Upgrade the backend and dashboard as one: a dashboard
newer than the backend can show a screen error for endpoints the backend lacks.

There are no breaking changes to report yet: `0.1.0-alpha.2` is part of the first alpha series. Read the
[changelog](https://github.com/dpdpkit-dev/dpdpkit-admin/blob/main/CHANGELOG.md) before each upgrade.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
