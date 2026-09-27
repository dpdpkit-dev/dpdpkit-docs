# Rule to code

Generated from `dpdpkit-policies`. Each row shows a pack key, its value, the legal source and the dpdpkit module that reads it.

| Pack key | Value in `dpdp-rules-2025.v1` | Legal source | What it controls | Code |
| --- | --- | --- | --- | --- |
| `commencement.consent_manager` | `2026-11-13` | DPDP Rules 2025, Rule 4 read with Rule 1(3) | Consent Manager provisions start one year after publication. | `dpdpkit.policy` |
| `commencement.fiduciary_duties` | `2027-05-13` | DPDP Rules 2025, Rule 1(3); G.S.R. 843(E) | Most Data Fiduciary duties and principal rights start eighteen months after publication. | `dpdpkit.policy` |
| `notice.required_links` | `["withdraw", "rights", "board_complaint"]` | DPDP Act s.5, s.6(4); DPDP Rules 2025, Rule 3(c) | A notice must link to withdrawing consent, exercising rights and complaining to the Board. | `dpdpkit.notices` |
| `notice.languages` | `["en", "hi"]` | DPDP Act s.5(3) | Principals may read the notice in English or any Eighth Schedule language. | `dpdpkit.notices` |
| `consent.withdrawal_parity` | `True` | DPDP Act s.6(4); DPDP Rules 2025, Rule 3(c)(i) | Withdrawing consent must be as easy as giving it. | `dpdpkit.consent` |
| `retention.erasure_pre_notice_hours` | `48` | DPDP Rules 2025, Rule 8(2) | Tell the principal at least 48 hours before erasure; any login or contact cancels it. | `dpdpkit.retention` |
| `retention.min_log_retention_days` | `365` | DPDP Rules 2025, Rule 6(1)(e) and Rule 8(3) | Keep personal data, traffic data and processing logs for at least one year. | `dpdpkit.retention`, `dpdpkit.ledger` |
| `retention.third_schedule` | `{"ecommerce": {"min_users": 20000000, "inactivity_years": 3}, "online_gaming": {"min_users": 5000000, "inactivity_years": 3}, "social_media": {"min_users": 20000000, "inactivity_years": 3}}` | DPDP Rules 2025, Rule 8(1), Third Schedule | Large e-commerce, online gaming and social media fiduciaries erase after three years without the principal's approach. | `dpdpkit.retention` |
| `rights.grievance_max_days` | `90` | DPDP Act s.13; DPDP Rules 2025, Rule 14(3) | Publish a grievance response period of no more than 90 days. | `dpdpkit.rights` |
| `rights.request_max_days` | `90` | DPDP Rules 2025, Rule 14; PIB explainer, 14 Nov 2025 | Rights requests are treated as having the same 90-day ceiling. | `dpdpkit.rights` |
| `rights.request_default_target_days` | `30` | dpdpkit default (configurable), below the ceiling | Target response time for rights requests, shown to the principal. | `dpdpkit.rights` |
| `children.age_of_majority` | `18` | DPDP Act s.2(f), s.9; DPDP Rules 2025, Rule 10 | A child is anyone under 18; processing needs verifiable parental consent. | `dpdpkit.guardians` |
| `breach.board_detailed_report_hours` | `72` | DPDP Rules 2025, Rule 7(2)(b) | Send the Board a detailed breach report within 72 hours of becoming aware. | `dpdpkit.incidents` |
