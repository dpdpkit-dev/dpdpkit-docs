# Consent ledger

Consent events are appended to a SHA-256 hash chain per tenant. Every other state change (requests,
schedules, holds) goes to a second, audit chain.

Each row's hash covers its canonical JSON (every field except `hash`), including `seq` and the previous
row's hash (`prev_hash`). The first row's `prev_hash` is 64 zeros. So:

| Tampering | Detected by |
| --- | --- |
| A row is edited | Its own hash no longer matches (`ledger verify`) |
| An edited row is re-hashed | The next row's `prev_hash` no longer matches (`ledger verify`) |
| A row is deleted | A gap in `seq` (`ledger verify`) |
| The newest rows are cut off, or the chain is rebuilt | Comparison with an exported root hash (`ledger check-root`) |

- `dpdpkit ledger verify` recomputes both chains. It names the first row whose contents or chain link
  do not match (exit code 2).
- `dpdpkit ledger root` prints the current heads; `--out FILE` appends them to an anchor file.
- `dpdpkit ledger check-root --anchors FILE` confirms the chains still match the newest exported root.

Export the root hash periodically to storage you cannot rewrite. See
[Anchoring the root hash](../guides/anchoring.md).
