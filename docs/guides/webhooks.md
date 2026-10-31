# Webhooks

dpdpkit can notify other systems when something happens: a consent is withdrawn, an erasure is due,
a rights request is opened. Each notification is an HTTPS `POST` with a signed JSON body.

With the FastAPI adapter, webhooks go through an **outbox** in your database:

1. When an event is published, dpdpkit stores one row per endpoint that wants it. The request that
   caused the event never waits on the network.
2. The scheduler sends due rows every 30 seconds.
3. A failed send (network error or any non-2xx response) is retried with exponential backoff: 30 s,
   1 min, 2 min, 4 min… capped at 2 hours, for up to 10 attempts (about 4 hours in total).
4. After the last attempt the row becomes a **dead letter**. It stays until someone redelivers it.
   Nothing is dropped silently.

## Configure endpoints

=== "dpdpkit.yaml"

    ```yaml
    webhooks:
      - id: crm
        url: https://crm.example.in/dpdp-hooks
        secret_env: CRM_WEBHOOK_SECRET        # the secret itself stays in the environment
        events: [consent.withdrawn, erasure.due]
      - id: audit-log
        url: https://logs.example.in/ingest
        secret_env: AUDIT_WEBHOOK_SECRET      # no `events`: receives everything
    ```

=== "Python"

    ```python
    from dpdpkit.events import WebhookEndpoint

    dpdp = DPDPKit(
        ...,
        webhooks=[
            WebhookEndpoint(id="crm", url="https://crm.example.in/dpdp-hooks",
                            secret=os.environ["CRM_WEBHOOK_SECRET"], events=["consent.withdrawn"]),
        ],
    )
    ```

Then run the scheduler (`dpdp.start_scheduler()`), which adds the delivery job whenever an endpoint
is configured. Without APScheduler, call `dpdpkit webhooks send --kit main:dpdp` from cron every minute.

The outbox table is created by `dpdpkit migrate` (migration `0002`).

## Events

| Event | When |
| --- | --- |
| `consent.granted`, `consent.denied`, `consent.withdrawn` | A principal records a decision |
| `notice.published` | A new notice version is published |
| `request.opened`, `request.updated`, `request.closed` | A rights request changes state |
| `export.requested` | An access request needs your data collected |
| `erasure.warning_sent` | A pre-erasure warning was delivered |
| `erasure.due` | An erasure is starting: delete or anonymise this principal's data for the purpose |
| `erasure.completed` | Erasure handlers finished |
| `erasure.processor_notified` | A processor must be told to erase (includes the processor id) |
| `erasure.needs_attention` | A warning or erasure failed and needs a person |
| `ledger.root_exported`, `ledger.tampered` | Root-hash export; failed ledger verification |

The body is the event itself:

```json
{
  "id": "ev_4c1d…",
  "type": "consent.withdrawn",
  "tenant_id": "default",
  "occurred_at": "2027-06-01T09:00:00Z",
  "data": {"principal": "u_42", "purpose": "marketing"}
}
```

## Receiving webhooks

Every request carries three headers:

| Header | Value |
| --- | --- |
| `X-DPDPKit-Event` | The event type |
| `X-DPDPKit-Delivery` | The delivery id (stable across retries) |
| `X-DPDPKit-Signature` | `t=<unix seconds>,v1=<hex HMAC-SHA256 of "<t>.<raw body>">` |

Verify the signature over the **raw** body before parsing it, and reject anything older than five
minutes. Respond with any `2xx` quickly; do slow work in the background.

=== "Python"

    ```python
    from dpdpkit.events import verify_signature

    @app.post("/dpdp-hooks")
    async def hook(request: Request):
        body = await request.body()
        if not verify_signature(SECRET, body, request.headers.get("X-DPDPKit-Signature", "")):
            raise HTTPException(401)
        event = json.loads(body)
        ...
        return {"ok": True}
    ```

=== "Node.js"

    ```js
    import crypto from "node:crypto";

    function verify(secret, rawBody, header, toleranceSeconds = 300) {
      const parts = Object.fromEntries(header.split(",").map((p) => p.split("=", 2)));
      const t = Number(parts.t);
      if (!t || !parts.v1 || Math.abs(Date.now() / 1000 - t) > toleranceSeconds) return false;
      const expected = crypto.createHmac("sha256", secret).update(`${t}.`).update(rawBody).digest("hex");
      return parts.v1.length === expected.length &&
        crypto.timingSafeEqual(Buffer.from(parts.v1), Buffer.from(expected));
    }

    // Express: keep the raw body for verification
    app.post("/dpdp-hooks", express.raw({ type: "application/json" }), (req, res) => {
      if (!verify(process.env.DPDP_SECRET, req.body, req.get("X-DPDPKit-Signature") ?? "")) {
        return res.sendStatus(401);
      }
      const event = JSON.parse(req.body);
      res.sendStatus(204);
    });
    ```

!!! note "Deliveries can repeat"
    A delivery is retried whenever dpdpkit does not see a `2xx`, including when your endpoint did the
    work but the response was lost. Use the event `id` as an idempotency key.

## Dead letters

```bash
dpdpkit webhooks list --kit main:dpdp                 # counts and recent deliveries
dpdpkit webhooks dead --kit main:dpdp                 # what gave up, and the last error
dpdpkit webhooks retry --id wh_… --kit main:dpdp      # one delivery, with a fresh attempt budget
dpdpkit webhooks retry --all --kit main:dpdp
```

From Python: `dpdp.webhooks.dead_letters()`, `dpdp.webhooks.redeliver(delivery_id)` and
`dpdp.webhooks.counts()`. The admin dashboard (v0.4) shows the same list.

A delivery to an endpoint that has been removed from the configuration goes straight to dead letters,
so you can see it rather than lose it.

## Tuning

The defaults suit most installs. To change them, adjust the outbox after creating `DPDPKit`:

```python
dpdp.webhooks.max_attempts = 15
dpdp.webhooks.max_delay = dt.timedelta(hours=6)
```

Several processes may run `deliver_due()` at the same time: each delivery is claimed before it is sent,
so it goes out once per attempt.
