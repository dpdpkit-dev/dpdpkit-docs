# dpdpkit-policies

Versioned DPDP policy packs, sector overlays, and the JSON Schema that validates them. It holds data only; every legal number dpdpkit uses (the 48-hour pre-erasure warning, the one-year log floor, the 90-day grievance ceiling) lives here and nowhere in code. [`dpdpkit-core`](dpdpkit-core.md) installs it, so install it on its own only to validate your own packs or read the rules.

| | |
| --- | --- |
| Install | `pip install --pre dpdpkit-policies` |
| Version | 2026.11.0a1 (CalVer, released on its own schedule) |
| Requires | Python 3.10+, `pyyaml`, `jsonschema` |
| Source | [dpdpkit-policies](https://github.com/dpdpkit-dev/dpdpkit-policies) · [Changelog](https://github.com/dpdpkit-dev/dpdpkit-policies/blob/main/CHANGELOG.md) |

The four sector overlays are covered on [Policy overlays](policy-overlays.md). Background is in
[Policy packs](../concepts/policy-packs.md) and [Rule to code](../reference/rule-to-code.md).

!!! warning "Not legal advice"
    A pack is an engineering reading of a legal text, not the text itself. Overlays are still marked draft. Have a
    lawyer check every number against the official notification before you rely on it.

## Install

```bash
pip install --pre dpdpkit-policies
```

No extras. The package ships one pack, `dpdp-rules-2025.v1` (source: G.S.R. 846(E), the DPDP Rules, 2025), and
four overlays.

## Quickstart

1. List what ships.

    ```bash
    dpdpkit-policies list
    ```

    ```text
    pack     dpdp-rules-2025.v1
    overlay  cert-in-2022
    overlay  education
    overlay  health-abdm
    overlay  rbi-kyc
    ```

2. Validate everything, or your own file.

    ```bash
    dpdpkit-policies validate                 # the shipped packs and overlays
    dpdpkit-policies validate my-pack.yaml    # exit 1 if the file does not match the schema
    ```

3. Load a pack in Python.

    ```python
    import dpdpkit_policies as policies

    pack = policies.load_pack("dpdp-rules-2025.v1", overlays=["cert-in-2022"])
    print(pack["overlays"])   # ['cert-in-2022']
    ```

4. Print the rule-to-code map, which is also how the [Rule to code](../reference/rule-to-code.md) page is built.

    ```bash
    dpdpkit-policies rule-map                 # Markdown table
    dpdpkit-policies rule-map --format json
    ```

To use a pack in an application, name it in `dpdpkit.yaml` (`policy: dpdp-rules-2025.v1`) and read values through
`dpdpkit.policy.Policy` rather than loading the YAML yourself.

## Configuration

The package has no settings. You choose a pack and overlays in `dpdpkit.yaml`:

| Key | Default | What it does |
| --- | --- | --- |
| `policy` | none, **required** | A shipped pack id such as `dpdp-rules-2025.v1`. |
| `overlays` | `[]` | Overlay ids, merged in the order listed. |

Inspect the result before deploying:

```bash
dpdpkit policy show --overlay cert-in-2022
dpdpkit policy diff dpdp-rules-2025.v1 my-pack.yaml
```

To write your own pack or overlay, copy a shipped file and validate it against the schema. Get the schema from
`dpdpkit_policies.schema("pack")` or `schema("overlay")`; both are also shipped as `pack.schema.json` and
`overlay.schema.json` inside the package.

### CLI

| Command | What it does |
| --- | --- |
| `dpdpkit-policies list` | List shipped pack and overlay ids. |
| `dpdpkit-policies validate [PATH...]` | Validate shipped files, or the given files. A file with `kind: overlay` is checked as an overlay, anything else as a pack. |
| `dpdpkit-policies rule-map [--format md\|json]` | Each pack key with its legal source and the code that uses it. |

## API reference

::: dpdpkit_policies
    options:
      members: [list_packs, list_overlays, load_pack, load_overlay, merge_overlays, read_policy_file, schema, validate_pack, validate_overlay, load_rule_map, PolicyValidationError, UnknownPolicyError]

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `UnknownPolicyError: unknown pack 'x'; available: dpdp-rules-2025.v1` | The id is misspelled, or the pack is newer than the installed package. | Run `dpdpkit-policies list`; upgrade the package. Through core, this surfaces as `PolicyError`. |
| `UnknownPolicyError: unknown overlay 'x'; available: ...` | Same, for an overlay. | Use one of the listed ids. |
| `PolicyValidationError: <id>: does not apply to pack ... (applies to [...])` | The overlay's `applies_to` prefixes do not match the pack id. | Use an overlay written for that pack, or change `applies_to` in your own overlay. |
| `FAILED  pack my-pack.yaml` followed by `path.to.key: ...` lines | The file does not match the schema. The path names the key. | Fix the key and run `dpdpkit-policies validate` again. |
| `PolicyValidationError: ... top level must be a mapping` | The file is empty or is a list. | Start from a copy of a shipped file. |
| dpdpkit refuses to start with a policy error | A missing or invalid pack stops the kit by design; there are no built-in defaults. | Fix the pack. Do not work around it. |
| An overlay value does not change behaviour | Core reads only some overlay keys today (see [Policy overlays](policy-overlays.md)). | Check which code reads the key on [Rule to code](../reference/rule-to-code.md). |

## Upgrading

`dpdpkit-policies` versions by month (`2026.11`), not with the code release train, because the rules change on
their own schedule. The pack id carries its own version (`v1`), and `list_packs()` returns every pack in the
release. Before changing `policy` in `dpdpkit.yaml`, run `dpdpkit policy diff OLD NEW` and review each changed key
with counsel. Pin `dpdpkit-policies` if you need the same numbers on every install.

Every changelog entry that adds or changes a pack cites the official notification. `0.1`-series core accepts
`dpdpkit-policies>=2026.11.0a1`.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
