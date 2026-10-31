# FastAPI adapter

::: dpdpkit.fastapi.app
    options:
      members: [DPDPKit, require_consent, default_kit, ActivityMiddleware]

::: dpdpkit.fastapi.repository
    options:
      members: [SqlAlchemyRepository, make_engine]

::: dpdpkit.fastapi.webhooks
    options:
      members: [WebhookOutbox, WebhookDelivery, DeliveryRun, endpoints_from_config]

::: dpdpkit.fastapi.http.ConsentRequiredHTTP
