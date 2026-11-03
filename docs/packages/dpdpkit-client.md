# @dpdpkit/client

The typed TypeScript client for the dpdpkit REST API, with an Express middleware that blocks requests that lack consent. Use it from a browser or Node when you build your own front end or guard Node routes; if you use React or plain HTML, [`@dpdpkit/react`](dpdpkit-react.md) and [`@dpdpkit/embed`](dpdpkit-embed.md) already include it.

| | |
| --- | --- |
| Install | `npm install @dpdpkit/client` |
| Version | 0.1.0-alpha.2 |
| Requires | A browser with `fetch`, or Node 18+. TypeScript is optional; types ship with the package. |
| Source | [dpdpkit-client](https://github.com/dpdpkit-dev/dpdpkit-client) · [Changelog](https://github.com/dpdpkit-dev/dpdpkit-client/blob/main/CHANGELOG.md) |
| Demo | [Try it on the demo site](https://demo.dpdpkit.dev/packages/client) (fictional data) |

The types are generated from the OpenAPI file in `dpdpkit-spec`, so the client matches the FastAPI adapter, the
Django app and the server image. See the [package index](index.md) for the other packages in the stack.

!!! warning "Not legal advice"
    @dpdpkit/client calls the API you run and enforces what you configure. Notice wording, purposes and retention
    periods are decisions for you and your counsel, and using the package does not guarantee compliance with the
    DPDP Act, 2023 or the DPDP Rules, 2025.

## Install

```bash
npm install @dpdpkit/client
```

The package ships ES module and CommonJS builds, with two entry points:

| Import | Adds |
| --- | --- |
| `@dpdpkit/client` | `createDpdpClient`, `DpdpClient`, `DpdpError` and the API types. No dependencies. |
| `@dpdpkit/client/express` | `requireConsent`, a middleware for Express and Connect-style servers. Express is not a dependency. |

## Quickstart

You need a running backend with the dpdpkit endpoints, for example the [FastAPI quickstart](../getting-started/fastapi.md)
mounted at `/dpdp`.

1. Create a client and read the notice.

    ```ts
    import { createDpdpClient, DpdpError } from "@dpdpkit/client";

    const dpdp = createDpdpClient({ baseUrl: "/dpdp" }); // same origin, cookies are sent

    const notice = await dpdp.getNotice("hi");
    ```

2. Record a choice, then withdraw it.

    ```ts
    await dpdp.recordConsents([{ purpose: "marketing", granted: true }], { noticeVersion: notice.version });
    await dpdp.withdraw("marketing");
    ```

3. Open a rights request and read the due date.

    ```ts
    const request = await dpdp.openRequest("erasure");
    console.log(request.due_at);
    ```

4. Handle errors by their stable code.

    ```ts
    try {
      await dpdp.withdraw("marketing");
    } catch (err) {
      if (err instanceof DpdpError && err.code === "invalid_transition") {
        // already withdrawn
      }
    }
    ```

### Guard a Node route

With the [server image](dpdpkit-server.md), your Node backend can refuse a request unless the signed-in user has
consented to a purpose.

```ts
import { requireConsent } from "@dpdpkit/client/express";

const consent = (purpose: string) =>
  requireConsent(purpose, {
    baseUrl: "http://dpdpkit:8000/dpdp",
    principal: (req) => req.user?.id,
    serviceHeaders: (principal) => ({
      Authorization: `Bearer ${process.env.DPDPKIT_API_KEY}`,
      "X-DPDP-Principal": principal,
    }),
  });

app.post("/offers/send", consent("marketing"), sendOffer);
```

Without consent the route answers `403` with `consent_required`. With no signed-in user it answers `401`
`unauthenticated`. If dpdpkit cannot be reached the middleware calls `next(err)` and never lets the request
through.

## Configuration

`createDpdpClient(options)` takes these options.

| Option | Type | Default | What it does |
| --- | --- | --- | --- |
| `baseUrl` | string | none, **required** | Where the API is mounted, including the prefix: `/dpdp` or `https://api.example.in/dpdp`. Trailing slashes are removed. |
| `headers` | object or function | none | Extra headers on every request, such as an end-user token or a CSRF token. A function (sync or `async`) is called per request, so tokens can rotate. |
| `credentials` | `RequestCredentials` | `same-origin` | Use `include` to send cookies to another origin. |
| `fetch` | `typeof fetch` | global `fetch` | A custom `fetch`, for tests or a polyfill. |

`requireConsent(purpose, options)` takes the options above except `headers`, plus:

| Option | Type | Default | What it does |
| --- | --- | --- | --- |
| `principal` | `(req) => string \| undefined` | none, **required** | Maps the request to the user reference your backend registered with dpdpkit. May be `async`. |
| `serviceHeaders` | `(principal) => headers` | none, **required** | Headers that authenticate your backend to the server for that user. Keep the API key on the server. |
| `cacheMs` | number | `0` | Remember an answer for this many milliseconds. The default asks every time; a cache delays the effect of a withdrawal. |

### Methods

| Method | Does |
| --- | --- |
| `getNotice(locale?)` | The current notice, in `locale` when it is published. |
| `recordConsents(decisions, { noticeVersion?, locale? })` | Records `[{ purpose, granted }]` and returns the new states. |
| `withdraw(purpose)` | Withdraws one consent. |
| `myConsents()` | The user's consent state per purpose. |
| `receipt()` | The signed consent receipt. |
| `openRequest(kind, details?)` | Opens a rights request. `kind` is `access`, `correction`, `completion`, `updating`, `erasure`, `nomination` or `grievance`. |
| `myRequests()`, `getRequest(id)` | Lists the user's requests, or reads one. |
| `exportMyData()`, `exportMyDataHtml()` | The user's data as JSON or as an HTML page. |
| `recordActivity(principal, at?)` | Tells dpdpkit the user was active, which restarts inactivity clocks. Needs service credentials. |
| `admin.*` | `listRequests`, `getRequest`, `updateRequest`, `retentionPreview`, `verifyLedger`, `auditExport`. These need an admin role; never ship them to a public page. |

Every failure throws `DpdpError` with `status`, `code` (the stable [error code](../reference/rest.md)), `message` and
`details`. If the body is not the standard error shape, `code` is `http_error`.

## API reference

The methods, request and response shapes and error codes are those of the [REST contract](../reference/rest.md).
The TypeScript types (`Notice`, `ConsentState`, `RightsRequest`, `RequestKind` and the rest) are exported from the
package root, and your editor shows them on hover.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `DpdpError` with code `unauthenticated` (401) | The backend could not tell who the user is. | Send the session cookie (`credentials: "include"` across origins) or an end-user token in `headers`. |
| `TypeError: Failed to fetch` in the browser | A CORS block, a wrong `baseUrl`, or the server is down. | Allow your origin on the backend, and check `baseUrl` includes the prefix (`/dpdp`). |
| `DpdpError` with code `http_error` | The response was not dpdpkit's error JSON, often a proxy or a 404 page. | Check that `baseUrl` points at the dpdpkit mount, not at your app's root. |
| `DpdpError` with code `invalid_transition` | The consent is already in the state you asked for. | Treat it as done, or reload the consents first. |
| `requireConsent` always answers `403 consent_required` | The user has no granted consent for that purpose, or the purpose name is misspelled. | Check `myConsents()` for the user and match the purpose id in `dpdpkit.yaml`. |
| `requireConsent` passes errors to `next` with code `dpdpkit_unreachable` | The middleware cannot reach the server. | Check `baseUrl` and the network from your backend. The route stays closed until it can. |
| `fetch is not a function` on Node | Node older than 18 has no global `fetch`. | Upgrade Node, or pass a `fetch` in the options. |
| Admin calls return 403 | The caller has no admin role. | Call `admin.*` only from trusted code with admin credentials. |

## Upgrading

Upgrade `@dpdpkit/client` together with `@dpdpkit/react`, which accepts the same minor series only
(`>=0.1.0-0 <0.2.0`). The client works with any backend that serves the same REST contract version, so upgrade the
backend first when a release adds endpoints.

There are no breaking changes to report yet: `0.1.0-alpha.2` is part of the first alpha series. Read the
[changelog](https://github.com/dpdpkit-dev/dpdpkit-client/blob/main/CHANGELOG.md) before each upgrade.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
