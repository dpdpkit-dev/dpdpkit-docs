# dpdpkit-core

The rules engine: consent ledger, versioned notices, rights requests, retention and erasure, audit evidence and the `dpdpkit` command line. Install it directly to check a build or a notice, or let a framework adapter pull it in.

| | |
| --- | --- |
| Install | `pip install --pre dpdpkit-core` |
| Version | 0.1.0a2 |
| Requires | Python 3.10+, `pydantic>=2.6`, `dpdpkit-policies` |
| Source | [dpdpkit-core](https://github.com/dpdpkit-dev/dpdpkit-core) · [Changelog](https://github.com/dpdpkit-dev/dpdpkit-core/blob/main/CHANGELOG.md) |

Core has no web framework and no database driver. For a service, pick an adapter from the
[package index](index.md). Installing `dpdpkit-core` also installs [`dpdpkit-policies`](dpdpkit-policies.md), and
the [`dpdpkit` meta-package](dpdpkit.md) installs core.

!!! warning "Not legal advice"
    dpdpkit-core records and enforces what you configure. Notice wording, purposes and retention periods are
    decisions for you and your counsel, and using the package does not guarantee compliance with the DPDP Act, 2023
    or the DPDP Rules, 2025.

## Install

```bash
pip install --pre "dpdpkit-core[workbook]"
```

| Extra | Adds | Needed for |
| --- | --- | --- |
| `ses` | `boto3` | `dpdpkit.ses`, the Amazon SES email transport |
| `workbook` | `openpyxl` | `dpdpkit workbook`, the data-mapping workbook |

The base install gives you two commands: `dpdpkit` and `dpdp-lint`.

## Quickstart

1. Write a starter configuration. `dpdpkit init --template edtech` starts from an industry template instead
   (`dpdpkit init --list-templates` lists them).

    ```bash
    dpdpkit init
    ```

2. Build a kit from it, record a consent, withdraw it and verify the ledger.

    ```python
    from dpdpkit import InMemoryRepository, MemoryNotifier, kit_from_config, load_config, sync_notice

    config = load_config("dpdpkit.yaml")
    kit = kit_from_config(config, InMemoryRepository(), notifier=MemoryNotifier(), signing_key="change-me")
    sync_notice(kit, config)                  # publishes the notice if its text changed

    kit.consent.grant("u_42", "marketing")    # recorded against the current notice version
    print(kit.consent.check("u_42", "marketing"))   # True
    kit.consent.withdraw("u_42", "marketing")
    print(kit.consent.check("u_42", "marketing"))   # False
    kit.ledger.verify()                       # raises LedgerTampered if a row was edited
    ```

3. Check the notice and the configuration from the command line.

    ```bash
    dpdpkit notice check
    dpdpkit lint
    ```

`InMemoryRepository` forgets everything on exit. For a real service use the
[FastAPI adapter](../getting-started/fastapi.md) or run the [server image](../getting-started/other-stacks.md).
See [Notice review](../guides/notice-review.md) for what `dpdpkit notice` produces.

## Configuration

Core reads `dpdpkit.yaml`. The file must name a policy pack; a file without `policy` raises `ConfigError`.

| Key | Type | Default | What it does |
| --- | --- | --- | --- |
| `policy` | string | none, **required** | Id of the [policy pack](dpdpkit-policies.md), for example `dpdp-rules-2025.v1`. |
| `overlays` | list of strings | `[]` | [Sector overlays](policy-overlays.md) merged over the pack, in order. |
| `tenant_id` | string | `default` | Separates ledgers when one database serves several tenants. |
| `contact` | mapping | `{}` | Name, email and rights URL shown in the notice. Erasure warnings need a contact. |
| `data_items`, `processors`, `purposes` | lists | none | The registry: what you collect, who processes it, why, and the retention rule per purpose. |
| `notice` | mapping | none | Title, body, `links` (`withdraw`, `rights`, `board_complaint`) and `translations` per locale. |

Settings that are not in the file:

| Setting | Where | Notes |
| --- | --- | --- |
| `signing_key` | `kit_from_config(..., signing_key=...)` | Signs consent receipts. Set a real secret before production. |
| `DPDPKIT_KIT` | environment, or `--kit module:attribute` | Which kit the `ledger`, `retention` and `export` commands load. |
| `DPDPKIT_TELEMETRY`, `DPDPKIT_TELEMETRY_URL`, `DO_NOT_TRACK`, `DPDPKIT_CONFIG_DIR` | environment | Anonymous telemetry is **off** by default and sends nothing until a collector URL is set. `dpdpkit telemetry status` shows the state. |

### Commands

| Command | What it does |
| --- | --- |
| `dpdpkit init [--template ID]` | Write a starter `dpdpkit.yaml`. |
| `dpdpkit policy list` · `show [--pack ID\|FILE] [--overlay ID]` · `diff OLD NEW` | Inspect and compare policy packs. |
| `dpdpkit notice check` · `notice review` | Automated notice checks, and a review pack for counsel. |
| `dpdpkit lint [CONFIG...]` (or `dpdp-lint`) | CI check: fails when a purpose has no retention rule or the notice is missing or fails the checks. `--strict` also fails on warnings. |
| `dpdpkit ledger verify` · `root` · `check-root` | Verify the hash chain, export its root hash, check against anchored roots. Needs `--kit`. |
| `dpdpkit retention preview` · `run` | Preview or run erasure schedules. Needs `--kit`. |
| `dpdpkit export --principal ID` · `--evidence` | Export one person's data, or an evidence pack. Needs `--kit`. |
| `dpdpkit workbook new` · `import` · `report` | Data-mapping workbook. Needs the `workbook` extra. |
| `dpdpkit telemetry status\|enable\|disable\|show` | Control opt-in telemetry. |

Core never submits anything to an authority. Incident report drafts are for you to review and send.

## API reference

The Python API is generated from the docstrings in `dpdpkit-core`. Start at the [Python API](../reference/python/index.md) overview:

- [Kit and configuration](../reference/python/kit.md): `Kit`, `kit_from_config`, `sync_notice`, `Policy`, `Registry`
- [Consent and notices](../reference/python/consent.md) and [Rights requests](../reference/python/rights.md)
- [Retention and erasure](../reference/python/retention.md) and [Ledger](../reference/python/ledger.md)
- [Events and notifications](../reference/python/events.md), [Export](../reference/python/export.md) and
  [Storage](../reference/python/storage.md)
- [Models and errors](../reference/python/models.md)

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ConfigError: dpdpkit.yaml must name a policy pack (policy: dpdp-rules-2025.v1)` | The config has no `policy` key. | Add `policy: dpdp-rules-2025.v1`, or run `dpdpkit init`. |
| `PolicyError: unknown pack 'x'; available: dpdp-rules-2025.v1` | The pack id is wrong or not in the installed `dpdpkit-policies`. | Run `dpdpkit policy list`. Upgrade `dpdpkit-policies` if the pack is newer than your install. |
| `PolicyError: unknown overlay ...` or `... does not apply to pack ...` | The overlay id is misspelled, or it targets a different pack. | See [Policy overlays](policy-overlays.md). |
| `error: pass --kit module:attribute (or set DPDPKIT_KIT) to load your kit` | `ledger`, `retention` and `export` need your kit, which holds the database connection. | Pass `--kit myapp.dpdp:kit` or set `DPDPKIT_KIT`. The attribute may be a kit, an adapter object with a `.kit`, or a function that returns either. |
| `LedgerTampered` from `ledger.verify()`, or exit code 2 from `dpdpkit ledger verify` | A ledger row was edited, deleted or reordered. | Treat it as an incident. Restore from a backup and compare with anchored roots (see [Ledger anchoring](../guides/anchoring.md)). |
| Erasure does not happen and the request sits in `needs_attention` | Erasure runs only after a warning is recorded as delivered and the full warning period has passed. A missing contact, failed delivery, failing erasure handler or legal hold also stops it. | Run `dpdpkit retention preview`, fix the cause, run again. |
| Telemetry is "on" but nothing is sent | There is no default collector. | Expected. Set `DPDPKIT_TELEMETRY_URL` or run `dpdpkit telemetry disable`. |
| `ImportError: the data-mapping workbook needs openpyxl` or `SES support needs boto3` | The matching extra is not installed. | `pip install --pre "dpdpkit-core[workbook]"` or `"dpdpkit-core[ses]"`. |

## Upgrading

Upgrade `dpdpkit-core` and any adapter (`dpdpkit-fastapi`, `dpdpkit-django`, `dpdpkit-server`) in the same step.
Adapters accept core in the same minor series only (`>=0.1.0a2,<0.2`). `dpdpkit-policies` can move on its own;
run `dpdpkit policy diff OLD NEW` before adopting a new pack.

There are no breaking changes to report yet: `0.1.0a2` is the first alpha series. Repository implementations
need the methods added in that release (`TransferRepository`, `GuardianRepository`, `IncidentRepository`). Read the
[changelog](https://github.com/dpdpkit-dev/dpdpkit-core/blob/main/CHANGELOG.md) before each upgrade.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
