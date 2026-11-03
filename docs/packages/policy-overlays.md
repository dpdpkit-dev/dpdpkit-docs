# Policy overlays

Sector overlays add rules from other regulations on top of the base DPDP pack. They ship inside [`dpdpkit-policies`](dpdpkit-policies.md) and are switched on by name in `dpdpkit.yaml`; use one when a regulator outside the DPDP Rules also governs your records.

| | |
| --- | --- |
| Install | Included in `pip install --pre dpdpkit-policies` |
| Version | 2026.11.0a1 |
| Overlays | `cert-in-2022`, `rbi-kyc`, `health-abdm`, `education` |
| Source | [overlays folder](https://github.com/dpdpkit-dev/dpdpkit-policies/tree/main/src/dpdpkit_policies/overlays) |
| Demo | [Try it on the demo site](https://demo.dpdpkit.dev/packages/core) (fictional data) |

!!! warning "Drafts, not legal advice"
    All four overlays are marked **draft**. Periods, clause numbers and scope follow the usual reading of each
    text and have not been checked by a lawyer. Several values carry open questions listed in the
    [changelog](https://github.com/dpdpkit-dev/dpdpkit-policies/blob/main/CHANGELOG.md). Whether an overlay
    applies to you, and which period is right, is a decision for you and your counsel.

## Install

Nothing extra to install. Check they are present:

```bash
dpdpkit-policies list
```

## Quickstart

1. Name the overlays in `dpdpkit.yaml`. They merge in the order listed.

    ```yaml
    policy: dpdp-rules-2025.v1
    overlays: [cert-in-2022]
    ```

2. See what changed against the base pack.

    ```bash
    dpdpkit policy show --overlay cert-in-2022
    ```

    The output now lists `overlays: [cert-in-2022]` and `breach.cert_in_report_hours: 6`.

3. Or load it from Python.

    <!-- sample: run -->
    ```python
    from dpdpkit import Policy

    policy = Policy.load("dpdp-rules-2025.v1", overlays=["cert-in-2022"])
    print(policy.overlays, policy.get("breach.cert_in_report_hours"))   # ['cert-in-2022'] 6
    ```

## Configuration

Each overlay sets a few keys, deep-merged into the pack, so an overlay value replaces the pack's value for the same key.

| Overlay | Keys it sets | Value | Source |
| --- | --- | --- | --- |
| `cert-in-2022` | `breach.cert_in_report_hours` | 6 | CERT-In Directions No. 20(3)/2022-CERT-In, 28 April 2022 |
| | `retention.log_retention_in_india_days` | 180 | same. A location-bound minimum; the base `retention.min_log_retention_days` (365) still governs |
| `rbi-kyc` | `retention.kyc_record_retention_years` | 5 | RBI Master Direction on KYC, 2016, as amended; PMLA 2002 s.12 |
| | `retention.legal_hold_reasons` | 7 starter codes | same. Codes are dpdpkit's own, not statutory |
| `health-abdm` | `retention.health_record_retention_years` | 3 | Indian Medical Council Regulations, 2002, reg. 1.3.1; ABDM Health Data Management Policy |
| | `consent.external_consent_reference_types` | 3 reference types | ABDM consent manager. Type names are dpdpkit's own |
| `education` | `children.fourth_schedule_exemption_codes` | 3 codes, no numbers | DPDP Rules, 2025, rule 12 and Fourth Schedule. Codes are dpdpkit's own and carry no item numbers yet |

### What core enforces today

Setting an overlay records its values in the policy, and `dpdpkit policy show` displays them. Core acts on them
unevenly:

| Key | Used by core? |
| --- | --- |
| `breach.cert_in_report_hours` | **Yes.** `kit.incidents` counts a CERT-In clock and drafts the report. Without this key, a CERT-In report cannot be created. |
| `retention.log_retention_in_india_days` | Recorded only. |
| `retention.kyc_record_retention_years`, `retention.legal_hold_reasons` | Recorded only. Core does not yet read them. |
| `retention.health_record_retention_years`, `consent.external_consent_reference_types` | Recorded only. |
| `children.fourth_schedule_exemption_codes` | Recorded only. Core does not yet bypass guardian checks for these codes. |

"Recorded only" means the value is in the merged policy and available through `policy.get(...)`, but no dpdpkit
code changes its behaviour for it. Set the matching retention periods and legal holds in your own purposes until
that changes. [Rule to code](../reference/rule-to-code.md) lists which code reads each key.

### Writing your own overlay

```yaml
id: my-overlay
kind: overlay
source: "Name and date of the instrument"
applies_to: [dpdp-rules-2025]   # pack id prefixes
set:                            # deep-merged into the pack; the result must validate
  breach:
    cert_in_report_hours: 6
```

Check it with `dpdpkit-policies validate my-overlay.yaml`. The merged pack is validated against `pack.schema.json`,
so a key the schema does not know is rejected.

## API reference

The overlay functions are on the [`dpdpkit-policies`](dpdpkit-policies.md#api-reference) page:
`list_overlays`, `load_overlay`, `merge_overlays` and `validate_overlay`. In core, see
[`Policy`](../reference/python/kit.md).

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `unknown overlay 'x'; available: cert-in-2022, education, health-abdm, rbi-kyc` | Misspelled id. | Use one of the listed ids. |
| `does not apply to pack ... (applies to ['dpdp-rules-2025'])` | The overlay targets a pack id prefix your pack does not start with. | Use a matching pack. |
| The merged policy fails validation | A custom overlay sets a key the schema rejects, or a wrong type. | Run `dpdpkit-policies validate` and fix the key named in the error. |
| `cert_in_report_hours` is missing and a CERT-In report cannot be created | `cert-in-2022` is not in `overlays`. | Add it to `dpdpkit.yaml`. |
| An overlay is listed but retention behaviour did not change | The key is recorded only. See the table above. | Set the period in your own retention rules. |
| `dpdpkit policy diff` shows no differences | `diff` compares two packs, not overlays. | Use `dpdpkit policy show --overlay ID` for the merged result. |

## Upgrading

Overlays release with `dpdpkit-policies` and are versioned with it (`2026.11.0a1`). They are drafts, so a value or key
can change between releases. After each upgrade, run `dpdpkit policy show --overlay ID` for every overlay you use and
review the result with counsel. The [changelog](https://github.com/dpdpkit-dev/dpdpkit-policies/blob/main/CHANGELOG.md)
lists each overlay's sources and open questions.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
