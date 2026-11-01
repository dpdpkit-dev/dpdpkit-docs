# Industry purpose templates

`dpdpkit init` writes a two-purpose starter file. For common sectors there are fuller starting points: a
complete `dpdpkit.yaml` with the data items, processors, purposes, retention rules and an itemised notice
(English and Hindi) that a typical business in that sector begins with.

```bash
dpdpkit init --list-templates
dpdpkit init --template edtech
```

| Template | For | What to look at first |
| --- | --- | --- |
| `edtech` | Learning apps, coaching and test prep, school and LMS platforms | Learners under 18: parental consent, no tracking or targeted ads |
| `health` | Clinics, telemedicine, diagnostics, health apps | Health data marked `sensitive`; medical-record retention; `s7_f` emergency purpose |
| `ecommerce` | D2C brands, marketplaces, online stores | Invoices kept under tax law (`s7_d`); the Third Schedule switch for 2 crore+ users |
| `fintech` | Payments, lending, wallets, distribution apps | KYC and transaction records kept under law (`s7_d`); masked Aadhaar only |
| `saas` | B2B software | Covers your own users and leads, not the customer data you process for clients |

!!! warning "A starting point, not legal advice"
    Every purpose, legal basis, retention period and line of notice wording in a template is an assumption
    for you and your counsel to confirm. Comments at the top of each file list the questions to settle.
    The Hindi text should be reviewed by a native speaker before you publish it.

## How the templates are built

Every template follows the same rules, and the test suite in `dpdpkit-core` checks them:

- **Nothing is pre-ticked.** Purposes the service cannot run without are `required: true`; everything else
  is optional consent.
- **Optional consent ends at withdrawal.** Every optional purpose uses `retention: {trigger: withdrawal}`,
  so withdrawing consent schedules erasure. Records the law makes you keep belong to a required purpose
  or to one with a Section 7 legal basis.
- **Legal retention uses a Section 7 basis.** KYC records, transaction records and tax invoices use
  `legal_basis: s7_d`, so an erasure request leaves that data in place (see
  [Retention and erasure](../concepts/retention.md)).
- **Every purpose has a retention rule**, every data item and processor is used by at least one purpose,
  and every purpose has a Hindi title.
- **Sector overlays are named, not enabled.** `education`, `health-abdm` and `rbi-kyc` are planned for
  v0.5; the templates say where to add them once they ship.

## Sector notes

**Ed-tech.** DPDP Act s.9 and Rule 10 need verifiable consent from a parent or guardian for learners under
18, and bar tracking, behavioural monitoring and targeted advertising directed at children. The template
limits `product_improvement` and `marketing` to adult learners and parents. Until the guardian flow ships
(v0.5), verify the parent in your own sign-up flow and record their choices with `kit.consent.grant()`.

**Health.** Medical-record retention comes from medical and state law, not the DPDP Rules, so the periods are
placeholders. Pharmacies and labs you share data with are usually Data Fiduciaries in their own right; the
template names them in purpose descriptions rather than listing them as processors.

**E-commerce.** If you have at least 2 crore registered users in India, Rule 8(1) and the Third Schedule
set a 3-year inactivity erasure. Swap the account purpose's retention for the commented line:

```yaml
retention: {third_schedule_class: ecommerce}
```

The period and its start date then come from the policy pack.

**Fintech.** Mark `kyc` and `transactions` complete with `kit.retention.purpose_completed()` when the
customer leaves; the retention clock for the legally required period starts then. Whether credit-bureau
reporting rests on consent or on a legal obligation is flagged for counsel.

**SaaS.** For the data your customers put into the product you are usually their Data Processor, governed by
your contract with them. The template covers what you hold as a Data Fiduciary: user accounts, billing,
support, product analytics and marketing.

## From Python

Onboarding tools can read the same templates:

```python
from dpdpkit import InMemoryRepository, kit_from_config
from dpdpkit.templates import list_templates, load_template

for template in list_templates():
    print(template.id, template.title, template.summary)

config = load_template("health").config()  # a dict, ready to edit
kit = kit_from_config(config, InMemoryRepository(), signing_key="change-me")
```
