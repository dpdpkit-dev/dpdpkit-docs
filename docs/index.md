# dpdpkit

Open-source building blocks for India's Digital Personal Data Protection Act, 2023 and DPDP Rules, 2025.
dpdpkit provides a consent ledger, versioned notices, rights requests, retention with pre-erasure
warnings, and audit evidence. It runs inside your own app, against your own database.

| You use | Install |
| --- | --- |
| FastAPI | `pip install "dpdpkit[fastapi]"` |
| Django (v0.4) | `pip install "dpdpkit[django]"` |
| Node, PHP, Java, Go, .NET (v0.5) | `docker run ghcr.io/dpdpkit-dev/server` |
| React front end | `npm i @dpdpkit/react @dpdpkit/client` |

Most Data Fiduciary obligations become enforceable on **13 May 2027**.

## Principles

- **Primitives, not promises.** dpdpkit gives you tools. It never claims to make you compliant.
- **Rules as data.** Every legal number lives in a versioned [policy pack](concepts/policy-packs.md).
- **Fail safe.** If a warning is not delivered or a job fails, dpdpkit holds and alerts. It never deletes or files anything on its own.
- **Your data stays with you.** Open-source installs never call home.
