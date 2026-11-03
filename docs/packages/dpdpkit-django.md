# dpdpkit-django

The Django app: models and migrations that keep dpdpkit's tables in your own database, the REST endpoints, consent checks for views, template tags, signals, management commands and a read-only admin request queue. Install it if your backend is Django; for FastAPI see [`dpdpkit-fastapi`](dpdpkit-fastapi.md), and for other stacks the [server image](../getting-started/other-stacks.md).

| | |
| --- | --- |
| Install | `pip install --pre dpdpkit-django` |
| Version | 0.1.0a3 |
| Requires | Python 3.10+, `django>=4.2`, `dpdpkit-core>=0.1.0a2,<0.2` |
| Source | [dpdpkit-django](https://github.com/dpdpkit-dev/dpdpkit-django) · [Changelog](https://github.com/dpdpkit-dev/dpdpkit-django/blob/main/CHANGELOG.md) |

Installing `dpdpkit-django` also installs [`dpdpkit-core`](dpdpkit-core.md). The [`dpdpkit` meta-package](dpdpkit.md)
has no `django` extra, so install this package by name. Pick one backend: this app, the FastAPI adapter or the
server image. See the [package index](index.md).

!!! warning "Not legal advice"
    dpdpkit-django records and enforces what you configure. Notice wording, purposes and retention periods are
    decisions for you and your counsel, and using the package does not guarantee compliance with the DPDP Act, 2023
    or the DPDP Rules, 2025.

## Install

```bash
pip install --pre "dpdpkit-django[drf,postgres]"
```

| Extra | Adds | Needed for |
| --- | --- | --- |
| `drf` | `djangorestframework>=3.14` | Serving the endpoints as DRF viewsets. Without it, plain JSON views are used. |
| `celery` | `celery>=5.3` | Running the jobs from Celery beat (`dpdpkit.django.tasks`) |
| `postgres` | `psycopg[binary]>=3.1` | PostgreSQL |
| `mysql` | `mysqlclient>=2.2` | MySQL |

SQLite needs no extra. Django 4.2 and 5.x are tested against SQLite, PostgreSQL and MySQL.

## Quickstart

1. Write a starter configuration next to `manage.py`.

    ```bash
    dpdpkit init
    ```

2. Add the app and the settings.

    ```python title="settings.py"
    INSTALLED_APPS = [
        # ...
        "dpdpkit.django",
    ]

    DPDPKIT = {
        "CONFIG": BASE_DIR / "dpdpkit.yaml",
        "SIGNING_KEY": os.environ["DPDPKIT_SIGNING_KEY"],
    }
    ```

3. Mount the endpoints and create the tables.

    ```python title="urls.py"
    from django.urls import include, path

    urlpatterns = [
        # ...
        path("dpdp/", include("dpdpkit.django.urls")),
    ]
    ```

    ```bash
    python manage.py migrate
    ```

4. Gate a view on consent.

    ```python title="views.py"
    from django.http import JsonResponse
    from django.views import View

    from dpdpkit.django.consent import RequiresConsentMixin, requires_consent


    @requires_consent("marketing")
    def send_offer(request):
        return JsonResponse({"sent": True})


    class OfferView(RequiresConsentMixin, View):
        consent_purposes = ("marketing",)

        def post(self, request):
            return JsonResponse({"sent": True})
    ```

5. Check that it works. Sign in, then record a consent and verify the ledger.

    ```bash
    curl -X POST localhost:8000/dpdp/consents -b cookies.txt -H "content-type: application/json" \
         -H "X-CSRFToken: $CSRF" -d '{"decisions": [{"purpose": "marketing", "granted": true}]}'
    python manage.py dpdp_verify_ledger
    ```

A caller who is not signed in gets `401 unauthenticated`. A signed-in caller without consent gets
`403 consent_required` naming the purpose, in the body shape of the [REST contract](../reference/rest.md).

### Erasure and export

dpdpkit never guesses which of your tables hold personal data. Declare them on the project-wide registry, for
example in `AppConfig.ready`, and then attach it to the kit so retention runs and erasure requests call it:

```python title="apps.py"
from dpdpkit.django.registry import registry

registry.register(
    Profile,
    principal_field="user",
    fields={"phone": "delete", "full_name": "anonymise", "pan": "retain_legal"},
    retain_reason="Income Tax Act record-keeping",
    purposes=["account"],
)
registry.register(Progress, principal_field="user", delete_rows=True)
registry.attach(get_kit())   # from dpdpkit.django.conf; do this once the app registry is ready
```

Erasure is atomic per database and raises on failure, so the schedule moves to `needs_attention` and nothing is
retried until a person resolves it. See [Retention and erasure](../concepts/retention.md). The
[`examples/django-school`](https://github.com/dpdpkit-dev/dpdpkit-django/tree/main/examples/django-school) demo
shows the whole setup, including a guardian consent flow for child accounts.

### Server-rendered pages

```django
{% load dpdpkit %}
{% dpdp_notice locale="hi" %}
<form method="post" action="/privacy/preferences/">{% csrf_token %}
  {% dpdp_preferences action="/privacy/preferences/" %}
</form>
```

Handle the post with `dpdpkit.django.consent.record_preferences(request)`. Nothing is pre-ticked. Override the
templates `dpdpkit/notice.html` and `dpdpkit/preferences.html` to restyle either tag.

## Configuration

All settings live in the `DPDPKIT` dictionary in `settings.py`. Give it `CONFIG` or `POLICY`; without either the
first request raises `ConfigError`.

| Key | Type | Default | What it does |
| --- | --- | --- | --- |
| `CONFIG` | path or mapping | none | A [`dpdpkit.yaml`](dpdpkit-core.md#configuration). The notice is published if its text changed. |
| `POLICY`, `OVERLAYS` | string, list | none, `[]` | Use these instead of `CONFIG` to name a [policy pack](dpdpkit-policies.md) and [overlays](policy-overlays.md). |
| `CONTACT` | mapping | none | Organisation contact shown in the notice. |
| `TENANT_ID` | string | `default` | Separates ledgers when one database serves several tenants. |
| `SIGNING_KEY` | string | none | Signs consent receipts. Set a long random secret, kept out of source control, before production. |
| `DATABASE` | string | Django's `default` alias | The database alias that holds the `dpdp_` tables. |
| `PRINCIPAL_RESOLVER` | dotted path | the signed-in user's primary key | `callable(request)` returning a stable, non-personal id, or `None`. |
| `ADMIN_GUARD` | dotted path | superuser is `admin`, staff is `handler` | `callable(request)` returning `viewer`, `handler` or `admin`, `True` for admin, or `None`. |
| `DRF` | bool | use DRF when installed | `True` or `False` forces or forbids the DRF viewsets. |
| `CSRF_EXEMPT` | bool | `False` | Exempt the plain JSON views from CSRF checks, for example when a separate frontend calls them with tokens. |

The settings dictionary has no key for a notifier or a contact lookup. To deliver pre-erasure warnings, build the
kit yourself and hand it over before the first request:

```python
from dpdpkit.config import kit_from_config, load_config, sync_notice
from dpdpkit.django.conf import set_kit
from dpdpkit.django.repository import DjangoRepository

config = load_config(BASE_DIR / "dpdpkit.yaml")
kit = kit_from_config(config, DjangoRepository(), notifier=my_notifier, contact_resolver=my_lookup, signing_key=KEY)
sync_notice(kit, config)
set_kit(kit)
```

See [Email delivery](../guides/email.md) for notifiers.

### Management commands

Run them from cron, or use the Celery tasks below. They are safe to repeat.

| Command | What it does |
| --- | --- |
| `manage.py dpdp_run_retention [--json]` | Send due erasure warnings and perform due erasures. |
| `manage.py dpdp_verify_ledger [--json]` | Verify the consent and audit hash chains. Exits non-zero if a row was altered or removed. |
| `manage.py dpdp_export --principal ID [--format json\|html] [-o FILE]` | Export one person's data. |
| `manage.py dpdp_export --evidence-pack -o FILE.zip` | Build the audit evidence pack. |
| `manage.py dpdp_export --root-file FILE` | Append the ledger root hash to a file. Point it at storage you cannot rewrite; see [Anchoring](../guides/anchoring.md). |

With Celery installed, add the tasks `dpdpkit.django.run_retention`, `dpdpkit.django.verify_ledger` and
`dpdpkit.django.export_root` to `CELERY_BEAT_SCHEDULE`, and run a single beat process.

### Signals

Import from `dpdpkit.django.signals`. Receivers get `event`, `tenant_id` and the event's data. A failing receiver is
logged and never blocks the state change.

| Signal | Sent when | Data |
| --- | --- | --- |
| `consent_withdrawn` | A person withdraws consent. | `principal`, `purpose` |
| `erasure_due` | A scheduled erasure is due, just before the erasure handlers run. | `principal`, `purpose` |
| `request_opened` | A person opens a rights request. | `principal`, `request_id`, `kind` |

### Admin

With `django.contrib.admin` installed, the admin gets a read-only compliance back-office: a request queue with
deadline countdowns, consent and audit ledger viewers, a retention monitor and a legal-hold list. The admin
dashboard is served at `<prefix>/admin/ui/`, for example `/dpdp/admin/ui/`.

## API reference

The Python API is generated from the docstrings in `dpdpkit-django`: see the
[Django app](../reference/python/django.md) page for `requires_consent`, `RequiresConsentMixin`,
`PersonalDataRegistry`, the settings helpers and the signals. The HTTP endpoints are in the
[REST contract](../reference/rest.md).

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ConfigError: set DPDPKIT['CONFIG'] (a dpdpkit.yaml) or DPDPKIT['POLICY'] in settings` | `settings.DPDPKIT` is missing or empty. | Add `CONFIG` pointing at your `dpdpkit.yaml`. |
| `relation "dpdp_..." does not exist` or `no such table` | The migrations have not run, or the app is missing from `INSTALLED_APPS`. | Add `"dpdpkit.django"` and run `python manage.py migrate` (with `--database ALIAS` if you set `DATABASE`). |
| `403 CSRF verification failed` on `POST /dpdp/consents` | The plain views check CSRF like any Django view. | Send the CSRF token, or set `CSRF_EXEMPT: True` if your frontend authenticates another way. |
| Every endpoint answers `401 unauthenticated` | `PRINCIPAL_RESOLVER` returned `None`: the user is not signed in, or the resolver cannot see them. | Check authentication middleware order, or point `PRINCIPAL_RESOLVER` at your own function. |
| Admin endpoints answer `403` for staff | The default guard gives `handler` to staff and `admin` to superusers only. | Set `ADMIN_GUARD` to return the role you want. |
| `ImproperlyConfigured: ... cannot be cleared (not nullable, no default)` when registering a model | A `"delete"` field cannot be emptied. | Use `"anonymise"` with a callable, make the field nullable, or `retain_legal` with a `retain_reason`. |
| `ImproperlyConfigured: ... is already registered` | The model was registered twice, often because `ready()` ran twice. | Register each model once, or call `registry.unregister(Model)` first. |
| Erasure requests do nothing to your tables | The registry was never attached to the kit. | Call `registry.attach(get_kit())` once the app is ready. |
| Warnings never arrive | `DPDPKIT` has no notifier setting. | Build the kit with a notifier and call `set_kit(kit)`, as above. |
| The DRF viewsets are used when you wanted plain views | `djangorestframework` is installed. | Set `"DRF": False`. |

## Upgrading

Upgrade `dpdpkit-django` and `dpdpkit-core` in the same step: the app accepts core in the same minor series only
(`>=0.1.0a2,<0.2`). Then run `python manage.py migrate` to apply any new migrations, and check
`python manage.py makemigrations --check` shows nothing pending for your own apps.

There are no breaking changes to report yet: `0.1.0a3` is part of the first alpha series, and it adds the bundled
admin dashboard at `<prefix>/admin/ui/`. The package is marked pre-alpha on PyPI, so read the
[changelog](https://github.com/dpdpkit-dev/dpdpkit-django/blob/main/CHANGELOG.md) before each upgrade.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
