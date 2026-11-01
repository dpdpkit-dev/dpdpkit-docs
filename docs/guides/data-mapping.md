# Data-mapping workbook and scan report

Before configuring purposes you need to know what personal data the system holds, where it is kept, who it is
shared with and why. The data-mapping workbook is an `.xlsx` spreadsheet that records the answers during a
workshop with the tech lead and whoever owns compliance. `dpdpkit` then turns it into a `dpdpkit.yaml` and a
scan report you can hand to the client.

```bash
pip install "dpdpkit[workbook]"                       # adds openpyxl
dpdpkit workbook new --template ecommerce             # pre-filled from an industry template
dpdpkit workbook new --from dpdpkit.yaml              # or from an existing configuration
# ... fill it in at the workshop ...
dpdpkit workbook import data-mapping.xlsx --base dpdpkit.yaml --out dpdpkit.yaml --force
dpdpkit workbook report data-mapping.xlsx --out scan-report.md
```

`dpdpkit workbook new` with neither option writes a blank workbook. Fill it in with Excel or LibreOffice. If you
use Google Sheets, download the result as `.xlsx` before importing it.

!!! warning "Engineering facts, not legal advice"
    The workbook records what the system does. Purposes, legal bases, retention periods and notice wording are
    decisions for the client and their counsel. The Purposes sheet has a "Counsel confirmed" column, and the
    import and the report both list every purpose that is not yet confirmed.

## The sheets

| Sheet | One row per | Imported into `dpdpkit.yaml` |
| --- | --- | --- |
| Engagement | field: client, privacy contact, policy pack, overlays, attendees | `contact`, `policy`, `overlays` |
| Data stores | database, bucket, spreadsheet, SaaS tool, log or backup holding personal data | `data_stores` |
| Scan findings | column or file where the PII scan found personal data (types and counts only) | no; feeds the report |
| Data items | kind of personal data, with its plain-language name and whether it is sensitive | `data_items` |
| Processors | outside party processing data for the client, with contract status | `processors` |
| Purposes | purpose: data items, legal basis, required or optional, processors, retention | `purposes` |
| Gaps | readiness check mapped to a dpdpkit feature, with status, risk, owner and due date | no; feeds the report |

Hover over a column header for help. Lists of IDs (a purpose's data items, processors and data stores) are
comma-separated. Columns marked "Not imported" in their help text are there for the workshop and the report.
You can add your own columns; the import matches columns by header and ignores any it doesn't know.

The Gaps sheet starts with fifteen readiness checks: notice, consent, rights, retention, processors, children,
breach, security and contact. Each one cites its source in the Act or Rules and names the dpdpkit feature that
covers it. Give each check a status (`met`, `partly met`, `gap`, `not applicable`), and add rows for anything else
the workshop finds.

## Running the workshop

1. **Before.** Run `dpdpkit workbook new --template <sector>` and fill in the Engagement sheet. The
   [purpose template](purpose-templates.md) gives you a draft of data items, processors and purposes to correct,
   which is quicker than starting from nothing.
2. **Data stores.** List every place personal data is kept, including exports, analytics tools, logs and backups.
   Mark the stores the scan will cover.
3. **Scan.** Record what the PII scan found in Scan findings: data store, location, detected type, confidence,
   rows sampled and matches. Until `dpdpkit scan` ships (dpdpkit-pii, v0.5), record a manual review of the
   schema in the same columns. Never paste sampled values. The import rejects anything other than a number in
   the count columns.
4. **Map.** Point every finding at a data item, or set its action to `delete`, `minimise` or `false positive`.
   Findings with no data item are "not in the registry" in the report.
5. **Purposes.** For each purpose, record the data items, legal basis, whether the service needs it, and the
   retention trigger and period. Optional purposes should end at `withdrawal`. Use a Section 7 basis such as
   `s7_d` for records a law requires you to keep.
6. **Gaps.** Go through the readiness checks together and agree an owner and a date for each gap.

## Importing into `dpdpkit.yaml`

```bash
dpdpkit workbook import data-mapping.xlsx --base dpdpkit.yaml --out dpdpkit.yaml --force
```

The import checks every row and lists every problem at once, with its sheet and row number:

```text
error: the workbook has 3 problem(s):
  Purposes row 6 (ad_audiences): Processors ads not on the Processors sheet
  Purposes row 9 (loyalty): no retention rule (set a trigger and days, or a Third Schedule class)
  Scan findings row 4: Matches must be a count, not '98765 43210' (never paste sampled values)
```

It runs the same registry check that `kit_from_config()` runs, so a file that imports cleanly also loads.
The workbook doesn't hold the notice text. `--base` keeps the notice and any other keys from your existing
configuration, and the workbook's values replace `contact`, `policy`, `overlays` and the registry lists. The
output is plain YAML, so comments in the base file are not carried over. Review the diff before you commit it.

## The scan report

```bash
dpdpkit workbook report data-mapping.xlsx --out scan-report.md
```

The report is Markdown, so you can edit it before sending, or convert it with Pandoc or your editor. It
contains:

- a summary with counts of stores, findings, unregistered locations, unconfirmed purposes and open gaps
- the data stores in scope, which of them were scanned, and the method and limits of the scan
- findings grouped by data store
- personal data not in the registry, with the decision each location needs
- registered data items the scan did not find
- low-confidence findings, listed separately so they don't crowd the main findings
- the open gaps, highest risk first, each mapped to a dpdpkit feature
- next steps, and a sign-off table for the tech lead, the compliance owner and the implementer

Like the workbook, it holds types, locations and counts only, never the sampled values.

## From Python

```python
from pathlib import Path

from dpdpkit.templates import load_template
from dpdpkit.workbook import new_workbook, read_workbook, scan_report

Path("data-mapping.xlsx").write_bytes(new_workbook(load_template("saas").config()))

book = read_workbook("data-mapping.xlsx")  # raises ConfigError listing every problem
config = book.to_config(base=load_template("saas").config())
print(book.unconfirmed_purposes, [f.location for f in book.findings if f.unregistered])
Path("scan-report.md").write_text(scan_report(book), encoding="utf-8")
```
