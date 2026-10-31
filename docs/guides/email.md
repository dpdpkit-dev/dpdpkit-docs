# Email delivery

dpdpkit sends one kind of message that has legal weight: the **pre-erasure warning** (Rule 8). An
erasure only runs after its warning is recorded as *delivered*, and only once the full warning period
has passed since that moment. So the notifier you choose decides what "delivered" means.

| Notifier | "Delivered" means | Use it for |
| --- | --- | --- |
| `NullNotifier` (default) | Never: every send fails | Keeps erasure switched off until you choose a transport |
| `ConsoleNotifier` | Printed to the console | Local development only |
| `SmtpNotifier` | Accepted by your SMTP relay | Any provider with SMTP |
| `SesNotifier` | Accepted by Amazon SES | SES without event tracking |
| `SesNotifier(track_delivery=True)` | SES reports the recipient's mail server accepted it | The strongest evidence available |

## SMTP

```python
from dpdpkit import SmtpNotifier

notifier = SmtpNotifier("smtp.example.in", 587, sender="privacy@example.in",
                        username=os.environ["SMTP_USER"], password=os.environ["SMTP_PASSWORD"])
```

## Amazon SES

```bash
pip install --pre "dpdpkit[ses]"
```

```python
from dpdpkit.ses import SesNotifier

notifier = SesNotifier("privacy@example.in", region="ap-south-1")
```

Credentials come from the usual AWS chain (environment, instance role, `~/.aws`). The sender address or
its domain must be verified in SES, and the account must be out of the SES sandbox to email anyone.

### Tracked delivery

With `track_delivery=True`, a message SES accepts is recorded as **queued**. The pre-erasure warning
does not count, and no erasure clock starts, until SES reports a `Delivery` event. A `Bounce`, `Reject`
or `Rendering Failure` moves the erasure to `needs_attention` for a person to resolve.

One-time AWS setup:

1. Create an SES **configuration set** (for example `dpdp`) with an **event destination** that publishes
   *Delivery, Bounce, Reject* and *Rendering failure* events to an **SNS topic**.
2. Create an **SQS queue** and subscribe it to that topic.
3. Give the app's IAM role `ses:SendEmail` and, on the queue, `sqs:ReceiveMessage` and `sqs:DeleteMessage`.

Then:

```python
from dpdpkit.ses import SesNotifier, poll_ses_events

notifier = SesNotifier("privacy@example.in", region="ap-south-1",
                       configuration_set="dpdp", track_delivery=True)

# every minute, next to the retention job (scheduler, cron or a worker):
poll_ses_events(kit, "https://sqs.ap-south-1.amazonaws.com/123456789012/dpdp-ses")
```

Each message carries a `dpdpkit_receipt` tag, so events are matched to dpdpkit's delivery receipts.
Events for mail dpdpkit did not send are ignored. A queue message is deleted only after its event has
been recorded.

!!! warning "Why a queue and not an HTTPS endpoint"
    A forged "delivered" event would start an erasure clock early. Reading events from SQS with your
    own AWS credentials means only SES can produce them. If you must receive SNS over HTTPS instead,
    verify every SNS message signature before calling `apply_ses_event`.

## SMS and WhatsApp

The built-in notifiers send email only; SMS and WhatsApp messages get a failed receipt. Implement the
`Notifier` protocol (one method, `send(message) -> DeliveryReceipt`) to use another provider. Return
`DeliveryStatus.QUEUED` when the provider confirms later, and report the outcome with
`kit.retention.confirm_warning_delivery(receipt_id, delivered)`.
