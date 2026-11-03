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
| `breach.cert_in_report_hours` | `(overlay only)` | CERT-In Directions No. 20(3)/2022-CERT-In, 28 April 2022, Direction (ii); overlay cert-in-2022 | Report cyber incidents to CERT-In within 6 hours of noticing them. Only present with the overlay. | `dpdpkit.incidents` |
| `retention.log_retention_in_india_days` | `(overlay only)` | CERT-In Directions No. 20(3)/2022-CERT-In, 28 April 2022, Direction (iv); overlay cert-in-2022 | Keep ICT system logs for 180 days within Indian jurisdiction. Only present with the overlay. | `dpdpkit.retention`, `dpdpkit.ledger` |
| `retention.kyc_record_retention_years` | `(overlay only)` | RBI Master Direction - KYC Direction, 2016 (record management); PMLA 2002 s.12; overlay rbi-kyc | Keep KYC and account records for at least 5 years after the business relationship ends. Only present with the overlay. | `dpdpkit.retention` |
| `retention.legal_hold_reasons` | `(overlay only)` | PMLA 2002 s.12; RBI Master Direction - KYC Direction, 2016; overlay rbi-kyc | Reason codes offered when placing a legal hold on KYC-related data. Only present with the overlay. | `dpdpkit.retention` |
| `consent.external_consent_reference_types` | `(overlay only)` | National Digital Health Mission Health Data Management Policy (ABDM); overlay health-abdm | External ABDM consent identifiers a consent record may reference instead of duplicating the consent. Only present with the overlay. | `dpdpkit.ledger` |
| `children.fourth_schedule_exemption_codes` | `(overlay only)` | DPDP Rules 2025, rule 12 and Fourth Schedule; DPDP Act s.9(1), s.9(3); overlay education | Exemption codes a purpose may carry to skip parental-consent gating and the tracking bar, for educational institutions and their transport. Only present with the overlay. | `dpdpkit.guardians` |
| `retention.health_record_retention_years` | `(overlay only)` | IMC (Professional Conduct, Etiquette and Ethics) Regulations 2002, reg. 1.3.1; overlay health-abdm | Keep medical records for at least 3 years from the start of treatment. Only present with the overlay. | `dpdpkit.retention` |
