# Versioning and deprecation

## Versions

The code packages (`dpdpkit-core`, `dpdpkit-fastapi`, `dpdpkit-conformance`, `@dpdpkit/client`,
`@dpdpkit/react`, and later `dpdpkit-django` and `dpdpkit-server`) are released together with one
version number. Policy packs (`dpdpkit-policies`) use calendar versions and are released on their own.

| Version change | Below 1.0 | From 1.0 |
| --- | --- | --- |
| Patch (`0.3.1`) | Fixes only | Fixes only |
| Minor (`0.4.0`) | New features; may remove APIs deprecated at least two minors earlier | New features, backwards compatible |
| Major (`2.0.0`) | n/a | May remove APIs deprecated in an earlier 1.x |

Alpha, beta and release-candidate builds (`0.3.0a1`, `0.3.0-alpha.1`) carry no compatibility promise.

## What is public

- Python: everything importable without a leading underscore from `dpdpkit`, `dpdpkit.<module>`,
  `dpdpkit.fastapi` and `dpdpkit_conformance`, as listed in the [Python API](python/index.md).
  Names starting with `_` (such as `dpdpkit._util`) may change in any release.
- JavaScript: the exports of `@dpdpkit/client`, `@dpdpkit/client/express` and `@dpdpkit/react`.
- REST: everything in [`openapi.yaml`](rest.md).
- CLI: commands, options and exit codes.
- Database: the `dpdp_*` tables belong to dpdpkit. Read them if you like, but change them only through
  `dpdpkit migrate`.

## How something is deprecated

1. The release that deprecates it lists it under **Deprecated** in the changelog, with what to use instead.
2. Every use emits a `DpdpkitDeprecationWarning` (a `DeprecationWarning`) that names the replacement and
   the release that will remove it:

    ```text
    DpdpkitDeprecationWarning: Ledger.export_roots() is deprecated since dpdpkit 0.3 and will be
    removed in 0.5; use Ledger.export_root() instead
    ```

    Deprecated functions and classes are also marked for type checkers (PEP 702), so mypy (with
    `--enable-error-code deprecated`) and pyright report callers before the code runs.
3. It keeps working, unchanged, for **at least two minor releases and at least 90 days**.
4. It is removed in the release named in the warning, and the changelog lists the removal under
   **Removed**.

Python hides `DeprecationWarning` outside test runners and `__main__`. To see these in your app:

```bash
python -W always::DeprecationWarning -m uvicorn main:app
# or in pytest (pyproject.toml): filterwarnings = ["error::dpdpkit.DpdpkitDeprecationWarning"]
```

## REST contract

- A deprecated operation or field is marked `deprecated: true` in `openapi.yaml`.
- Responses from a deprecated operation carry a `Deprecation` header ([RFC 9745](https://www.rfc-editor.org/rfc/rfc9745))
  and, once a removal date is set, a `Sunset` header ([RFC 8594](https://www.rfc-editor.org/rfc/rfc8594)).
- Removing or renaming anything in the contract is a breaking change. Pull requests to `dpdpkit-spec`
  run a breaking-change check and need the `breaking-change` label to pass it.

## Policy packs

A published pack id (for example `dpdp-rules-2025.v1`) is never changed or removed. When the Rules or
the Board's guidance change, a new pack id is published and the changelog cites the notification.
`dpdpkit policy diff` shows exactly what moved, and switching packs is a one-line config change.

## Database

Migrations only move forward and never drop consent, audit or ledger data. A column that is no longer
used stays until a major version, and the changelog says when it stopped being written.
