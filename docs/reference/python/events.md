# Events and notifications

::: dpdpkit.events
    options:
      members: [Event, EventBus, WebhookEndpoint, WebhookDispatcher, sign_payload, verify_signature]

::: dpdpkit.notify
    options:
      members: [Notifier, NullNotifier, MemoryNotifier, ConsoleNotifier, SmtpNotifier, render]

::: dpdpkit.ses
    options:
      members: [SesNotifier, poll_ses_events, apply_ses_event, ses_event_outcome]
