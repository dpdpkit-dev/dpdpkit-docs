# Notice review

dpdpkit publishes and records the notice you configure. Whether its wording meets DPDP Act s.5 and Rule 3 is a
call for a lawyer. `dpdpkit notice` prepares that review and ties the lawyer's sign-off to the exact wording
that goes live.

```bash
dpdpkit notice check                              # automated checks; exit 1 if one fails
dpdpkit notice review --out notice-review.md      # review pack for counsel
dpdpkit notice review --template health --out health-review.md   # the same for a purpose template
```

Both commands read `./dpdpkit.yaml` unless you pass another file. Neither one needs a database: they build the
notice in memory, exactly as `sync_notice()` would publish it.

!!! warning "Not legal advice"
    The automated checks test the structure of the notice, not whether it is lawful. A pack that passes every
    check still needs counsel's approval, and the client or their counsel decides on the wording.

## The review pack

`dpdpkit notice review` writes one Markdown file (convert it with Pandoc or paste it into a document if counsel
prefers Word or PDF). It contains:

| Section | What it holds |
| --- | --- |
| Summary | Purposes, locales, and how many checks passed, failed or need fixing before go-live |
| What the reviewer is asked to do | Read every locale, answer the questions, sign off |
| Sign-off | The content hash of each locale and a table for the decision, reviewer, firm, date and signature |
| Automated checks | Each check's result, the requirement and where it comes from |
| Questions for counsel | Points software cannot decide, with the purposes each one concerns |
| Notes from the configuration | The comment block at the top of your `dpdpkit.yaml` or template |
| The notice as principals will see it | Every locale in full: title, body, each purpose with required or optional, legal basis, personal data and processors, the links and contact details |

Fix any failed check before sending the pack. Once counsel has approved the wording, changing it would need a
fresh review anyway.

### Automated checks

| Check | Source | Fails when |
| --- | --- | --- |
| `links` | DPDP Act s.5(1), s.6(4); Rule 3(c) | A locale lacks a link the policy pack requires (withdraw, rights, Board complaint) |
| `itemised_data` | Rule 3(b)(i) | A purpose lists no personal data items |
| `itemised_purposes` | DPDP Act s.5(1)(i); Rule 3(b)(ii) | A consent purpose is missing from the notice or has no description |
| `languages` | DPDP Act s.5(3) | *Warning:* the policy pack ships a language the notice does not provide |
| `translation` | DPDP Act s.5(3); Rule 3(a) | A translated locale shows default-language text: a title, body, purpose description or data item name that was never translated |
| `contact` | DPDP Act s.8(9); Rule 9 | The contact has no name or email |
| `placeholders` | dpdpkit | *Warning:* example names, addresses or links from a starter file or template are still there |

Warnings do not fail `dpdpkit notice check`; add `--strict` to fail on them too, for example in CI before a
release. `dpdpkit notice review --strict` exits 1 when a check fails, after writing the pack.

### Questions for counsel

The pack asks counsel about the points that need judgement:

- **Standalone and plain language** (Rule 3(a)): is the notice shown on its own, apart from terms of service?
- **Informed consent** (s.6(1), Rule 3(b)): does each description give a fair account of what it enables?
- **Necessity** (s.6(1)): is each purpose marked required really necessary for the service?
- **Legal basis** (s.4, s.7): is the legitimate use right for each purpose that does not rely on consent?
- **Withdrawal** (s.6(4)-(6), Rule 3(c)(i)): does the notice say how to withdraw, and what withdrawal means?
- **Children** (s.9, Rule 10): if children may use the service, is the notice addressed to the parent?
- **Existing principals** (s.5(2)): is there a plan to send the notice to people who consented before?
- **Translation fidelity** (s.5(3)): does each translation say the same as the English?

## Sign-off and the ledger

Each locale's hash in the sign-off table is the notice's `content_hash`, the same value dpdpkit stores with the
published notice and records in the `notice.published` audit entry:

```json
{"action": "notice.published", "subject_id": "3", "data": {"locales": {"en": "372f…", "hi": "c2e6…"}}}
```

To show which approved wording went live, keep the signed pack and match its hashes with that entry. The entry
is in `audit_entries.csv` in the evidence pack (`dpdpkit export --evidence`). Any edit to the wording, links or
contact details changes the hash, so a pack signed for one version cannot be passed off as approval of
another.

## Translations

Each locale under `notice.translations` can override the notice title and body, each purpose's `title` and
`description`, and each data item's name:

```yaml
notice:
  title: How we use your personal data
  links: {withdraw: ..., rights: ..., board_complaint: ...}
  translations:
    hi:
      title: हम आपके व्यक्तिगत डेटा का उपयोग कैसे करते हैं
      data_items:
        email: ईमेल पता
      purposes:
        marketing:
          title: आपको ऑफ़र भेजना
          description: उत्पादों और छूट के बारे में कभी-कभार ईमेल।
```

Anything left out falls back to the default-language text, which the `translation` check reports. Have a native
speaker check every translation before the review.

## The purpose templates

The notice wording in each [industry purpose template](purpose-templates.md) goes through a lawyer review
before it is marked as reviewed. `dpdpkit init --list-templates` shows where each one stands:

| Status | Meaning |
| --- | --- |
| awaiting lawyer review | Not reviewed yet. Treat the wording as a draft. |
| reviewed (reviewer, firm, date) | Approved, and the wording is unchanged since the review |
| changed since its review | Approved once, but the wording has changed since, so the approval no longer covers it |

The reviews are recorded in `dpdpkit/templates/reviews.yaml` in `dpdpkit-core`, with the approved hashes. The
test suite fails if a template's notice changes without updating that file. A template review covers the
template's wording only. Once you change the company name, the links or any purpose, the hashes change and the
notice needs your own counsel's approval: run `dpdpkit notice review` on your edited `dpdpkit.yaml`.

### Recording a template review (maintainers)

1. `dpdpkit notice review --template ID --out ID-review.md` for each template, and send the packs to the
   reviewing lawyer with the template files.
2. Apply the changes they ask for to the template, regenerate the pack, and get sign-off on the final hashes.
3. Record the review in `reviews.yaml`: `status: reviewed`, reviewer, firm, date, the scope (for example
   "English wording; Hindi checked by a native speaker") and the hashes from the signed pack.
4. Keep the signed packs with the engagement records, not in the repository.

## From Python

```python
from dpdpkit.review import notice_checks, notice_translations_for, review_pack
from dpdpkit.templates import load_template

template = load_template("edtech")
kit, translations = notice_translations_for(template.config())
for check in notice_checks(kit, translations):
    print(check.status, check.id, check.detail)

print(template.notice_review().describe())   # "notice wording awaiting lawyer review"
markdown = review_pack(template.config(), source="edtech template", notes=template.notes())
```
