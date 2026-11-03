# dpdpkit-lint-action

A GitHub Action that fails your CI when your `dpdpkit.yaml` has no usable notice or a purpose has no retention rule. Use it on pull requests so a change to your configuration cannot quietly drop one. It runs the same check as `dpdpkit lint` and `dpdp-lint` from [`dpdpkit-core`](dpdpkit-core.md).

| | |
| --- | --- |
| Install | `uses: dpdpkit-dev/dpdpkit-lint-action@v1` |
| Version | `v1` |
| Requires | A GitHub Actions runner with `bash`; it sets up Python itself |
| Source | [dpdpkit-lint-action](https://github.com/dpdpkit-dev/dpdpkit-lint-action) |

See the [package index](index.md) for the other packages.

!!! warning "Not legal advice"
    The action checks that the configuration is complete. It does not decide whether your purposes, wording or
    retention periods are lawful, and a pass does not guarantee compliance with the DPDP Act, 2023 or the DPDP Rules,
    2025. That is for you and your counsel.

## Install

There is nothing to install. Add a step to a workflow:

```yaml
- uses: dpdpkit-dev/dpdpkit-lint-action@v1
```

The action installs Python and `dpdpkit-core` on the runner. It needs no database and no network access beyond
installing the package.

## Quickstart

1. Add `.github/workflows/dpdp-lint.yml`:

    ```yaml
    name: dpdp-lint
    on: [pull_request]

    permissions:
      contents: read

    jobs:
      dpdp-lint:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v7
          - uses: dpdpkit-dev/dpdpkit-lint-action@v1
            with:
              config: dpdpkit.yaml
    ```

2. Open a pull request. A passing run shows a green check. A failing run adds annotations on the pull request, each
   pointing at the file, and the job fails.

What it checks:

- The **notice** is configured and passes the automated notice checks: required links, itemised data and purposes,
  translations and contact details. Placeholder text is a warning.
- Every **purpose has a retention rule**: `retention.period_days` or `retention.third_schedule_class`.

To run the same check on your machine:

```bash
pip install --pre dpdpkit-core
dpdpkit lint dpdpkit.yaml
```

Exit code 1 means a failure, or a warning with `--strict`. See [Notice review](../guides/notice-review.md) for the
notice checks and [Retention](../concepts/retention.md) for retention rules.

## Configuration

| Input | Default | Meaning |
| --- | --- | --- |
| `config` | `dpdpkit.yaml` | Paths to lint, separated by spaces or newlines. |
| `strict` | `false` | Also fail on warnings, such as placeholder text left in the notice. |
| `version` | latest | `dpdpkit-core` version to install, for example `0.1.0a2`. Pin it for reproducible builds. |
| `python-version` | `3.12` | Python used to run the linter. |

Lint several files:

```yaml
- uses: dpdpkit-dev/dpdpkit-lint-action@v1
  with:
    config: |
      dpdpkit.yaml
      services/billing/dpdpkit.yaml
    strict: "true"
    version: "0.1.0a2"
```

Set `permissions: contents: read` as shown, since the action needs nothing more. Pin `@v1` to a full commit SHA if
your organisation requires it.

## API reference

The action has no code API. Its inputs are listed above. The checks run in `dpdpkit lint`; see the
[`dpdpkit-core`](dpdpkit-core.md) page for its command-line options (`--strict`, `--format text|github`).

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `FAIL ... no retention rule (period_days or third_schedule_class) for: <ids>` | A purpose has no retention rule. | Add `retention.period_days` or `retention.third_schedule_class` to each purpose listed. |
| `cannot lint <path>: ...` | The file is missing, or is not valid `dpdpkit.yaml`. | Check the `config` path relative to the repository root, and that `actions/checkout` ran first. |
| `dpdp-lint: failed` | At least one check failed. | Read the annotations on the pull request, or the step log. |
| A run fails only with `strict: "true"` | Warnings, such as placeholder text in the notice. | Replace the placeholder text, or turn `strict` off. |
| `No matching distribution found for dpdpkit-core` | The `version` input names a release that does not exist, or only alpha releases are available. | Check the version on PyPI. |
| A path with spaces is split in two | `config` is split on spaces. | Put each path on its own line, and avoid spaces in paths. |
| No annotations on a pull request from a fork | GitHub limits what a forked run may write. | Read the step log instead. |

## Upgrading

Pointing at `@v1` follows the action's major version. Pin `version` to the
`dpdpkit-core` release you tested if you want repeatable results; a newer `dpdpkit-core` can add checks that fail a
configuration that passed before.

There are no breaking changes to report yet.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
