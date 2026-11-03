# @dpdpkit/embed

Framework-free web components, `<dpdp-consent>`, `<dpdp-preferences>` and `<dpdp-rights-form>`, that you drop into any page with one script tag. Use it for plain HTML, a CMS, or Vue, Svelte and Angular; for React see [`@dpdpkit/react`](dpdpkit-react.md).

| | |
| --- | --- |
| Install | `npm install @dpdpkit/embed`, or a `<script>` tag from jsDelivr |
| Version | 0.1.0-alpha.2 |
| Requires | A browser with custom elements and shadow DOM. No framework and no other package: [`@dpdpkit/client`](dpdpkit-client.md) is bundled in. |
| Source | [dpdpkit-embed](https://github.com/dpdpkit-dev/dpdpkit-embed) · [Changelog](https://github.com/dpdpkit-dev/dpdpkit-embed/blob/main/CHANGELOG.md) |

The elements work with any dpdpkit backend. Because they run in the visitor's browser, they authenticate with a
short-lived token that your backend mints, best done with the [server image](dpdpkit-server.md). See the
[package index](index.md).

!!! warning "Not legal advice"
    @dpdpkit/embed shows the notice you publish and records the choices people make. Notice wording, purposes and
    retention periods are decisions for you and your counsel, and using the package does not guarantee compliance
    with the DPDP Act, 2023 or the DPDP Rules, 2025.

## Install

From a CDN, one tag registers all three elements:

```html
<script src="https://cdn.jsdelivr.net/npm/@dpdpkit/embed@0.1.0/dist/embed.js" crossorigin="anonymous"></script>
```

Pin the exact version in production, and add a
[Subresource Integrity](https://www.jsdelivr.com/using-sri-with-dynamic-files) hash for it from the jsDelivr page.
`dist/embed.js` is one minified, self-contained file.

From npm, importing the package has no side effects. Register the elements yourself:

```bash
npm install @dpdpkit/embed
```

```ts
import { defineDpdpElements } from "@dpdpkit/embed";

defineDpdpElements();
```

Or `import "@dpdpkit/embed/embed"`, which registers them on import.

## Quickstart

You need a backend with the dpdpkit endpoints, and an endpoint of your own that returns a token for the signed-in
user.

1. Mint a token on your backend. The API key stays on the server and never reaches the browser. With the server image
   this is `POST /v1/tokens`; see the [Node example](dpdpkit-server.md) for a complete `/api/privacy-token` route that
   returns `{ "token": "…", "expires_at": 1767225600 }`.

2. Add the script and the elements to the page.

    ```html
    <script src="https://cdn.jsdelivr.net/npm/@dpdpkit/embed@0.1.0/dist/embed.js" crossorigin="anonymous"></script>

    <dpdp-consent api="/dpdp" token-url="/api/privacy-token" locale="hi"></dpdp-consent>
    <dpdp-preferences api="/dpdp" token-url="/api/privacy-token"></dpdp-preferences>
    <dpdp-rights-form api="/dpdp" token-url="/api/privacy-token"></dpdp-rights-form>
    ```

3. Open the page signed in, choose **Save my choices**, and listen for the result.

    ```html
    <script>
      document.querySelector("dpdp-consent").addEventListener("dpdp-saved", (e) => console.log(e.detail));
    </script>
    ```

    The console prints the recorded consent states.

## Configuration

### Attributes

| Attribute | Elements | What it does |
| --- | --- | --- |
| `api` | all | Base URL of the dpdpkit API, such as `/dpdp`. **Required.** |
| `token` | all | Sent as `Authorization: Bearer <token>`. Read on every request, so it can be rotated. |
| `token-url` | all | Your endpoint that mints a token. Called with `POST` and same-origin cookies. |
| `locale` | all | Notice language (BCP 47). Defaults to the server's choice. |
| `labels` | all | JSON of interface labels to override, for example `{"acceptAll":"Sab theek hai"}`. Also a `labels` property. |
| `kinds` | `dpdp-rights-form` | Space-separated subset of request kinds to offer. |
| `hide-requests` | `dpdp-rights-form` | Do not list the user's existing requests. |

### Handing over the token

Every call carries a token signed by dpdpkit for one person, so the same element can never act for someone else. There
are three ways to give it to the element:

1. `token="…"`: render it into the page. Good for server-rendered pages. It is used until 30 seconds before it expires.
2. `token-url="/api/privacy-token"`: the element `POST`s there and expects `{ "token": "…", "expires_at": 1767225600 }`.
   It refreshes before expiry and, when the API answers 401, fetches a new token and retries once.
3. `el.tokenProvider = async () => ({ token, expires_at })`: the same, from code. It wins over `token-url`.

The browser reads only the expiry, from the unverified payload. The server checks the signature.

### Events

Events bubble and cross the shadow boundary.

| Event | Element | `detail` |
| --- | --- | --- |
| `dpdp-saved` | `dpdp-consent` | The recorded consent states. |
| `dpdp-changed` | `dpdp-preferences` | `{ purpose, granted }` |
| `dpdp-submitted` | `dpdp-rights-form` | The created request. |

### Theming

Styles live in each element's shadow root, so page CSS does not leak in. Set these custom properties on the element or
any ancestor: `--dpdp-font`, `--dpdp-text`, `--dpdp-muted`, `--dpdp-bg`, `--dpdp-surface`, `--dpdp-border`,
`--dpdp-accent`, `--dpdp-accent-text`, `--dpdp-focus`, `--dpdp-radius`, `--dpdp-gap`. Dark mode follows
`prefers-color-scheme`.

```css
dpdp-consent { --dpdp-accent: #0b5fff; --dpdp-radius: 4px; }
```

The elements follow the same rules as the React components: the legal text comes from the API, nothing is pre-ticked,
Accept all, Reject all and Save have equal weight, and the withdraw, rights and Data Protection Board links are always shown.

## API reference

The elements, attributes and events are described above; there is no separate generated reference. The package
exports `defineDpdpElements` and the element classes, with TypeScript types. The HTTP calls behind the elements are in
the [REST contract](../reference/rest.md), and `POST /v1/tokens` is in the [server page](dpdpkit-server.md).

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Elements show nothing and are not styled | The script did not load, so the tags were never registered. | Check the script URL and the network tab. With npm, call `defineDpdpElements()`. |
| The element shows an error and requests answer 401 | No token, an expired token, or `token-url` returned the wrong shape. | Return `{ "token": "…", "expires_at": <unix seconds> }` from the token endpoint, signed in as the user. |
| `token-url` is called but answers 401 or 403 | The token route needs a session, and cookies were not sent. | Serve it from the same origin, and sign the user in before the page renders the elements. |
| Requests are blocked by CORS | `api` is on another origin that does not allow yours. | Use a same-origin path such as `/dpdp` through your proxy, or allow your origin on the backend. |
| `api` seems ignored | The attribute is missing or misspelled. | Set `api="/dpdp"` on every element. |
| The script is blocked in the browser | The SRI hash does not match the version, or the content security policy blocks jsDelivr. | Copy the hash for that exact version, and allow `cdn.jsdelivr.net` in `script-src`. |
| The label override is ignored | `labels` is not valid JSON. | Use double quotes: `labels='{"acceptAll":"Sab theek hai"}'`. |
| Page CSS does not change the look | Styles are inside the shadow root. | Set the `--dpdp-*` custom properties instead. |

## Upgrading

`@dpdpkit/client` is bundled, so there is nothing to keep in step on the front end. Change the pinned version in the
script URL (and its SRI hash) or in `package.json`. Upgrade the backend first when a release adds endpoints.

There are no breaking changes to report yet: `0.1.0-alpha.2` is part of the first alpha series. Read the
[changelog](https://github.com/dpdpkit-dev/dpdpkit-embed/blob/main/CHANGELOG.md) before each upgrade.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
