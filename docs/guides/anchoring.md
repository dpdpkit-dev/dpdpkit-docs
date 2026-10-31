# Anchoring the ledger root hash

The hash chain proves that no row was **edited** or **removed from the middle**. On its own it cannot
prove that the newest rows were not cut off the end, or that someone with database access did not
rebuild the whole chain from scratch. A *root hash* closes that gap: it records the head of each chain
at a point in time. Keep a copy somewhere the database operator cannot rewrite, and any later
truncation or rebuild no longer matches it.

```json
{
  "tenant_id": "default",
  "consent_head": "9f2c…", "consent_seq": 1841,
  "audit_head": "41ab…",   "audit_seq": 7302,
  "root": "c07e…",
  "exported_at": "2027-06-01T03:00:00Z"
}
```

A root hash contains only hashes and counters, never personal data, so it is safe to publish.

## Exporting

=== "CLI (cron, CI, any stack)"

    ```bash
    # append today's root to a JSON-lines file
    dpdpkit ledger root --kit myapp:dpdp --out /mnt/anchors/roots.jsonl
    ```

=== "FastAPI scheduler"

    ```python
    from dpdpkit import FileRootSink

    dpdp.start_scheduler(
        root_export_hour=3,                                   # daily, 03:00 UTC (None disables)
        root_sinks=[FileRootSink("/mnt/anchors/roots.jsonl")],
    )
    ```

=== "Python"

    ```python
    root = kit.ledger.export_root(FileRootSink("roots.jsonl"))
    ```

Every export also publishes a `ledger.root_exported` event. Subscribe a webhook to it to hand each root
to a third party as it is produced (see [Where to keep it](#where-to-keep-it)).

A sink is any object with a `write(root)` method, so you can write directly to your own store:

```python
import datetime as dt

import boto3

s3 = boto3.client("s3")


class ObjectLockSink:
    def write(self, root):
        s3.put_object(
            Bucket="acme-dpdp-anchors",
            Key=f"{root.tenant_id}/{root.exported_at:%Y/%m/%d}.json",
            Body=root.model_dump_json(),
            ObjectLockMode="COMPLIANCE",
            ObjectLockRetainUntilDate=root.exported_at + dt.timedelta(days=3 * 365),
        )
```

If a sink raises, `export_root()` raises too, so a failed anchor is never skipped silently. The FastAPI
job logs the failure and tries again the next day.

## Checking

```bash
dpdpkit ledger verify     --kit myapp:dpdp                                # chain is internally consistent
dpdpkit ledger check-root --kit myapp:dpdp --anchors /mnt/anchors/roots.jsonl
```

`check-root` takes the newest root for the tenant and confirms the chains still contain a row at each
recorded sequence number with the recorded hash. Because each row includes the hash of the row before
it, matching the newest anchor also proves nothing before it changed. Exit codes: `0` ok, `1` no usable
anchor, `2` mismatch.

Run both checks on the same schedule as the export, for example right before it.

## Where to keep it

Pick at least one place you cannot quietly edit. More than one is better.

| Option | What protects it | Effort |
| --- | --- | --- |
| S3 (or compatible) bucket with **Object Lock in compliance mode** | Not even the account root user can delete or overwrite an object before its retention date | Low; use a separate AWS account if you can |
| **Webhook to a partner**: your auditor, legal counsel or parent company | The copy is held by someone else | Low; subscribe to `ledger.root_exported` |
| **RFC 3161 timestamp** (`openssl ts -query`, then send it to a public timestamping authority) | A signed token showing the root existed at that time | Medium |
| **OpenTimestamps** (`ots stamp roots.jsonl`) | Anchored in the Bitcoin blockchain, free | Medium; confirmation takes a few hours |
| Public Git repository | Forks and mirrors keep old history; a force-push shows up | Low, but weaker: the owner can still rewrite it |
| Local file on the app server | Protects against accidents only | None |

!!! warning "Same credentials, no protection"
    If the credentials that can write your database can also delete the anchor, the anchor proves
    nothing. Use a different account, a different owner, or write-once storage.

## How often

Daily is a sensible default. Rows written since the last anchor are protected by the chain alone, so
the export interval is the window in which a truncation could go unnoticed. High-volume or regulated
deployments can export hourly. The job is cheap: it reads two rows.

## In an incident or an audit

Give the auditor three things: the evidence pack (`dpdpkit export --evidence`), the anchor file, and
the output of `dpdpkit ledger check-root`. They can recompute every row hash independently. See
[Consent ledger](../concepts/ledger.md) for the hashing rules.
