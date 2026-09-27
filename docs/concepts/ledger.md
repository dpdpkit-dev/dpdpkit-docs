# Consent ledger

Consent events are appended to a SHA-256 hash chain per tenant. Every other state change (requests,
schedules, holds) goes to a second, audit chain.

- `dpdpkit ledger verify` recomputes both chains. It names the first row whose contents or chain link
  do not match (exit code 2).
- `dpdpkit ledger root` prints the current heads. Export them periodically to storage you cannot
  rewrite, so truncating the tail of the chain is detectable too.
