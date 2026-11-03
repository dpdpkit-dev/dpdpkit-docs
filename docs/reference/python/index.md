# Python API

Generated from the docstrings in [`dpdpkit-core`](https://github.com/dpdpkit-dev/dpdpkit-core),
[`dpdpkit-fastapi`](https://github.com/dpdpkit-dev/dpdpkit-fastapi) and
[`dpdpkit-django`](https://github.com/dpdpkit-dev/dpdpkit-django) on `main`. Everything listed here is
importable from the module shown in each heading.

| Page | What it covers |
| --- | --- |
| [Kit and configuration](kit.md) | `Kit`, `kit_from_config`, `sync_notice`, `Policy`, `Registry` |
| [Consent and notices](consent.md) | `ConsentService`, `NoticeService` |
| [Rights requests](rights.md) | `RightsService`, `IdentityVerifier` |
| [Retention and erasure](retention.md) | `RetentionService`, `ErasureResult` |
| [Ledger](ledger.md) | `Ledger`, `RootSink`, `FileRootSink` |
| [Events and notifications](events.md) | `EventBus`, webhooks, notifiers |
| [Export](export.md) | Principal export and evidence pack |
| [Storage](storage.md) | `Repository` protocol, `InMemoryRepository` |
| [Models and errors](models.md) | Pydantic models, enums and exceptions |
| [FastAPI adapter](fastapi.md) | `DPDPKit`, `require_consent`, `SqlAlchemyRepository` |
| [Django app](django.md) | `requires_consent`, `RequiresConsentMixin`, `PersonalDataRegistry`, `DjangoRepository` |

Names that start with an underscore are private and may change in any release.
