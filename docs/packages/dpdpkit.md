# dpdpkit

The meta-package: one name to install that pulls in [`dpdpkit-core`](dpdpkit-core.md) and, through extras, the adapters and optional features. Use it when you want a single pinned entry in `requirements.txt`; it contains no code of its own.

| | |
| --- | --- |
| Install | `pip install --pre dpdpkit` |
| Version | 0.1.0a2 (always equal to `dpdpkit-core`) |
| Requires | Python 3.10+ |
| Source | [dpdpkit-dev](https://github.com/dpdpkit-dev) · [Changelog](https://github.com/dpdpkit-dev/dpdpkit-core/blob/main/CHANGELOG.md) |

Other packages in the same stack are listed in the [package index](index.md).

!!! warning "Not legal advice"
    dpdpkit is software that helps you implement obligations under the DPDP Act, 2023 and the DPDP Rules, 2025. It
    does not provide legal advice and does not guarantee compliance.

## Install

```bash
pip install --pre "dpdpkit[fastapi]"
```

| Extra | Installs | Use it for |
| --- | --- | --- |
| none | `dpdpkit-core` (and `dpdpkit-policies`) | Library, CLI and CI checks |
| `fastapi` | `dpdpkit-fastapi>=0.1.0a2,<0.2` | A FastAPI service. Add `dpdpkit-fastapi[scheduler]` for the retention scheduler. |
| `ses` | `dpdpkit-core[ses]` | Email through Amazon SES |
| `workbook` | `dpdpkit-core[workbook]` | The data-mapping workbook |

The meta-package pins core exactly (`dpdpkit-core==0.1.0a2`). Extras for Django, the server image and the PII
scanner are added once those packages are published through the meta-package; install them by name from the
[package index](index.md) until then.

## Quickstart

1. Install and write a config.

    ```bash
    pip install --pre dpdpkit
    dpdpkit init
    ```

2. Check that it works.

    ```bash
    dpdpkit --version      # dpdpkit-core 0.1.0a2
    dpdpkit policy list    # dpdp-rules-2025.v1
    dpdpkit lint
    ```

3. Continue with the [FastAPI quickstart](../getting-started/fastapi.md) or the [`dpdpkit-core`](dpdpkit-core.md) page.

## Configuration

None. The meta-package has no settings; configure [`dpdpkit-core`](dpdpkit-core.md) and the adapter you installed.

## API reference

None. `import dpdpkit` gives you the API of `dpdpkit-core`. See the [Python API](../reference/python/index.md).

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ERROR: Could not find a version that satisfies the requirement dpdpkit` | Only pre-releases exist, and pip skips them. | Add `--pre`. |
| `dpdpkit-core ... conflicts with` another requirement | Core is pinned exactly, so another pin on core disagrees. | Drop the other pin, or upgrade both together. |
| `WARNING: dpdpkit 0.1.0a2 does not provide the extra 'django'` | There is no such extra yet. | `pip install --pre dpdpkit-django`. |
| `dpdpkit --version` shows an old version after upgrading | Another environment's `dpdpkit` is first on `PATH`. | Run `python -m pip show dpdpkit-core` in the active environment. |

## Upgrading

`dpdpkit` and `dpdpkit-core` always share a version, so `pip install --pre -U dpdpkit` moves both. If you also
install an adapter by name, upgrade it in the same command. Release notes are in the
[`dpdpkit-core` changelog](https://github.com/dpdpkit-dev/dpdpkit-core/blob/main/CHANGELOG.md).

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
