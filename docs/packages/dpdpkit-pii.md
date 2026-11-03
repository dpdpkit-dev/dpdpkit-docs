# dpdpkit-pii

Finds personal data in your databases and files and compares it with the data you have registered, reporting names and counts only. Use it to check that your [data map](../guides/data-mapping.md) covers what is actually stored, as a library, as a `dpdpkit scan` command, or as a container image.

| | |
| --- | --- |
| Install | `pip install --pre dpdpkit-pii` |
| Version | 0.1.0a2 |
| Requires | Python 3.10+, `dpdpkit-core` (same minor series), Presidio, SQLAlchemy 2 |
| Source | [dpdpkit-pii](https://github.com/dpdpkit-dev/dpdpkit-pii) · [Changelog](https://github.com/dpdpkit-dev/dpdpkit-pii/blob/main/CHANGELOG.md) |
| Demo | [Try it on the demo site](https://dpdpkit-demo.onrender.com/packages/pii) (fictional data; can take a minute or more to wake) |

See the [package index](index.md) for the other packages.

!!! warning "Not legal advice"
    A scan is a pattern match on a sample of your data. It can miss personal data and can flag values that are not
    personal data. What counts as personal data, and what you must do about a gap, are decisions for you and your
    counsel, and using the package does not guarantee compliance with the DPDP Act, 2023 or the DPDP Rules, 2025.

## Install

```bash
pip install --pre dpdpkit-pii
pip install --pre "dpdpkit-pii[excel,s3]"
```

| Extra | Adds |
| --- | --- |
| `excel` | Reads `.xlsx` files (openpyxl). |
| `s3` | Reads `s3://` prefixes (boto3). |

The package depends on SQLAlchemy only. To scan PostgreSQL or MySQL, also install a driver such as
`psycopg[binary]` or `pymysql`. Installing it adds `dpdpkit scan` to the `dpdpkit` command from `dpdpkit-core`.

### Container image

```bash
docker run --read-only --tmpfs /tmp ghcr.io/dpdpkit-dev/scanner postgresql://readonly@host/db --sample 500
docker run --read-only -v "$PWD/exports:/data:ro" ghcr.io/dpdpkit-dev/scanner /data --format json
```

The image runs `dpdpkit scan` as the non-root user `10001:10001`, with Excel and S3 support and the PostgreSQL
and MySQL drivers. It needs no writable path other than `/tmp`. Mount a folder read-only to scan files, and mount a
writable folder if you use `--out`.

## Quickstart

1. Create a database user that can only `SELECT`. The scanner refuses a connection that can write.
2. List the names you have registered, one per line (`#` starts a comment, `*` is a wildcard):

    ```text title="registry.txt"
    customers.pan
    customers.phone
    orders.*
    ```

3. Run the scan:

    ```bash
    dpdpkit scan postgresql://readonly@host/db --sample 500 --registry registry.txt --out report.html
    ```

4. Open `report.html`. Unregistered findings, the gaps, are listed first. The command prints
   `wrote report.html (N findings)` on stderr when it has finished.

The same scan from Python:

```python
from dpdpkit.pii import build_report, scan_database

scan = scan_database("postgresql://readonly@host/db", sample=500)
report = build_report(scan, registry=["customers.pan", "customers.phone", "orders.*"])
print(report.to_markdown())  # or report.to_json(), report.to_html(), report.render("md")
```

Scan files, a folder or an S3 prefix with `scan_files`:

```python
from dpdpkit.pii import scan_files

scan = scan_files("s3://my-bucket/exports/", sample=500, exclude=["*.log"])
for f in scan.confident:
    print(f.qualified_name, f.entities, f.confidence)  # e.g. s3://my-bucket/exports/kyc.csv:pan {'IN_PAN': 212} 0.95
```

The scanner reads data but never returns, logs or writes the values it samples. Reports hold names, entity types and
counts only.

To use the recognizers on their own with Presidio:

```python
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from dpdpkit.pii import india_recognizers

registry = RecognizerRegistry()
for recognizer in india_recognizers():
    registry.add_recognizer(recognizer)
results = AnalyzerEngine(registry=registry).analyze(text="PAN ABCPE1234F", language="en")
```

Recognizers cover Aadhaar (with the Verhoeff check), PAN, GSTIN, IFSC, UPI ID, mobile, voter ID, passport, vehicle
registration (including BH series) and ABHA. `classify_column("aadhaar_no")` guesses a category from a column name in
English or Hinglish, with a confidence.

## Configuration

### Command line

`dpdpkit scan TARGET [options]`. `TARGET` is a database URL (anything with `://` other than `s3://`), a file, a
folder or an `s3://bucket/prefix`. `python -m dpdpkit.pii` runs the same command without `dpdpkit-core`'s CLI.

| Option | Default | Meaning |
| --- | --- | --- |
| `--sample N` | 500 | Values read per column or field. Must be at least 1. |
| `--format` | from `--out` suffix, else `markdown` | `json`, `markdown` or `html`. |
| `--out FILE` | print to stdout | Write the report here. `.json`, `.md` and `.html` select the format. |
| `--overwrite` | off | Replace `--out` if it exists. Without it the command refuses. |
| `--registry FILE` | none | Registered names: a JSON array of strings, or one name per line. |
| `--registered NAME` | none | A registered name. Repeat for several. |
| `--include PATTERN` | all | Tables (database) or globs (files) to scan. Repeatable. |
| `--exclude PATTERN` | none | Tables (database) or globs (files) to skip. Repeatable. |
| `--schema NAME` | the connection's default | Database: schema to scan. |
| `--force` | off | Database: scan even if the connection can write, or cannot be shown to be read-only. |
| `--max-bytes N` | 20 MiB | Files: read at most this many bytes per file. Larger CSV and text files are read up to this size; larger JSON and Excel files are skipped. |
| `--text-lines N` | 10000 | Files: non-empty lines read per text file. |
| `--fail-on-gaps` | off | Exit 2 if personal data is found that the registry does not cover. |

Registered names are `table.column`, `schema.table.column` or `file:field`, with `*` wildcards.

### Exit codes

| Code | Meaning |
| --- | --- |
| 0 | The scan finished. |
| 1 | A usage or scan error, shown as `error: ...` on stderr. |
| 2 | `--fail-on-gaps` was set and the scan found unregistered personal data. |

### Read-only checks

For PostgreSQL the scanner checks the connection's privileges, and for MySQL and MariaDB it checks `SHOW GRANTS`. It
then sets the session to read-only. For other databases it cannot verify the connection, so it refuses unless you
pass `--force` (`force=True`). Use a dedicated read-only user rather than `--force`.

### Reading the confidence

Each finding has a confidence from 0 to 1. A column name alone gives a hint, and matching sampled values raise it.
`scan.confident` lists the likely findings and the rest are listed separately as low confidence. Treat both as leads
to check, not conclusions.

## API reference

See the [PII scanner API reference](../reference/python/pii.md), generated from the docstrings.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `error: scan failed: ReadOnlyError: The postgresql connection can write. Connect as a user with SELECT only, or pass force=True.` | The database user can modify data. | Create a user with `SELECT` only. Use `--force` only when you cannot. |
| `The sqlite connection could not be verified as read-only. ...` | The scanner can only verify PostgreSQL, MySQL and MariaDB. | Open the file read-only, or pass `--force`. |
| `error: scan failed: OperationalError` (or another class name) | The database or S3 call failed. The message is hidden because driver messages can contain connection strings or values. | Check the URL, the driver and the network. Run the same URL in `psql` or `mysql`. |
| `error: <path> already exists; pass --overwrite to replace it` | `--out` points at an existing file. | Add `--overwrite` or choose another name. |
| `error: registry file ... is not valid JSON` | The file starts with `[` but is not a JSON array of strings. | Fix the JSON, or use one name per line. |
| `error: --sample must be at least 1` | `--sample 0` or negative. | Use 1 or more. |
| Excel or S3 files are not read | The `excel` or `s3` extra is missing. | `pip install --pre "dpdpkit-pii[excel,s3]"`. |
| Exit code 2 in CI | `--fail-on-gaps` found data that is not registered. | Register the column or field, or remove the data. |
| A column with personal data is not reported | It was not in the sample, the value format is not recognized, or the table was excluded. | Raise `--sample`, check `--include` and `--exclude`, and review by hand. |

## Upgrading

`dpdpkit-pii` needs `dpdpkit-core` in the same minor series (`>=0.1.0a2,<0.2`), so upgrade them together:

```bash
pip install --pre --upgrade dpdpkit-core dpdpkit-pii
```

For the image, pull a newer tag of `ghcr.io/dpdpkit-dev/scanner`.

There are no breaking changes to report yet: `0.1.0a2` is the first working release. Read the
[changelog](https://github.com/dpdpkit-dev/dpdpkit-pii/blob/main/CHANGELOG.md) before each upgrade; recognizers
and column heuristics can change what a scan reports from one release to the next.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
