# Retention and erasure

1. Activity (login, contact) restarts each purpose's inactivity clock.
2. `retention.erasure_pre_notice_hours` before erasure (48 in the base pack), dpdpkit sends a warning
   through your notifier.
3. Erasure runs only after the warning is recorded as **delivered**, and only once the full warning
   period has passed since delivery.
4. Any activity after the warning cancels the erasure.
5. Failed delivery, missing contact details, a failing erasure handler or a legal hold all move the
   schedule to `needs_attention`. A person decides what happens next.
6. Ledger and audit rows are never erased. They are kept for at least `retention.min_log_retention_days`.
