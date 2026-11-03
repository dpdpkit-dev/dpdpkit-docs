# @dpdpkit/react

React components and hooks for the consent notice, preference centre, rights request form and language switcher. Use it if your front end is React; for other front ends see [`@dpdpkit/embed`](dpdpkit-embed.md) or the plain [`@dpdpkit/client`](dpdpkit-client.md).

| | |
| --- | --- |
| Install | `npm install @dpdpkit/react @dpdpkit/client` |
| Version | 0.1.0-alpha.2 |
| Requires | React and React DOM 18+, and `@dpdpkit/client` `>=0.1.0-0 <0.2.0` as a peer dependency |
| Source | [dpdpkit-react](https://github.com/dpdpkit-dev/dpdpkit-react) · [Changelog](https://github.com/dpdpkit-dev/dpdpkit-react/blob/main/CHANGELOG.md) |
| Demo | [Try it on the demo site](https://dpdpkit-demo.onrender.com/packages/fastapi) (fictional data; can take a minute or more to wake) |

The components talk to any dpdpkit backend: [`dpdpkit-fastapi`](dpdpkit-fastapi.md), [`dpdpkit-django`](dpdpkit-django.md)
or the [server image](dpdpkit-server.md). See the [package index](index.md).

!!! warning "Not legal advice"
    @dpdpkit/react shows the notice you publish and records the choices people make. Notice wording, purposes and
    retention periods are decisions for you and your counsel, and using the package does not guarantee compliance
    with the DPDP Act, 2023 or the DPDP Rules, 2025.

## Install

```bash
npm install @dpdpkit/react @dpdpkit/client
```

`@dpdpkit/client` is a peer dependency, so your app and the components share one copy. Import the stylesheet once,
near the root of your app:

```tsx
import "@dpdpkit/react/styles.css";
```

## Quickstart

You need a backend serving the dpdpkit endpoints at `/dpdp`, for example the [FastAPI quickstart](../getting-started/fastapi.md).

1. Wrap your page in `DpdpProvider` and add the components.

    ```tsx title="PrivacyPage.tsx"
    import { ConsentNotice, DpdpProvider, LanguageSwitcher, PreferenceCenter, RightsRequestForm } from "@dpdpkit/react";
    import "@dpdpkit/react/styles.css";

    export function PrivacyPage({ closeBanner }: { closeBanner: () => void }) {
      return (
        <DpdpProvider options={{ baseUrl: "/dpdp" }} locale="hi">
          <LanguageSwitcher />
          <ConsentNotice onSaved={closeBanner} />
          <PreferenceCenter />
          <RightsRequestForm />
        </DpdpProvider>
      );
    }
    ```

2. Open the page signed in, tick a purpose and choose **Save my choices**.
3. Check that it was recorded.

    ```bash
    curl localhost:8000/dpdp/consents/me -H "X-User: u_42"
    ```

    The purpose shows as `granted`. Choose **Withdraw** in the preference centre and it shows as `withdrawn`.

Create the `options` object once (outside the component, or in `useMemo`). A new object on every render creates a
new client each time.

### Your own interface

The hooks give you the same data and actions without the markup. Keep the rules in mind: nothing pre-ticked,
equal-weight choices, and withdrawal as easy as granting.

```tsx
import { useConsent, useNotice, useRequests } from "@dpdpkit/react";

const { notice, loading, error } = useNotice();
const { consents, record, withdraw } = useConsent();
const { requests, open } = useRequests();
```

## Configuration

### Components

| Component | Props | What it does |
| --- | --- | --- |
| `DpdpProvider` | `options` or `client`, `locale`, `labels` | Creates (or takes) the client and holds the language and labels. Every other component and hook must be inside it. |
| `ConsentNotice` | `onSaved(states)`, `className` | The itemised notice: one toggle per purpose, nothing pre-ticked, Accept all, Reject all and Save with equal weight. |
| `PreferenceCenter` | none | Current consent per purpose, one-click withdrawal and the consent history. |
| `RightsRequestForm` | `kinds`, `onSubmitted(request)`, `showRequests`, `className` | Opens a rights request and lists the user's requests with due dates. `kinds` limits the types offered. |
| `LanguageSwitcher` | none | Lists the languages the notice is published in and switches the provider's locale. |
| `AgeGate`, `GuardianFlow` | see the exported types | Building blocks for age checks and guardian verification for child accounts. |

`DpdpProvider` options:

| Prop | Type | Default | What it does |
| --- | --- | --- | --- |
| `options` | client options | none | Passed to `createDpdpClient`: `baseUrl`, `headers`, `credentials`, `fetch`. See [`@dpdpkit/client`](dpdpkit-client.md#configuration). |
| `client` | `DpdpClient` | none | Use a client you made yourself, instead of `options`. One of the two is required. |
| `locale` | string | the policy's default language | Initial notice language (BCP 47, such as `hi`). |
| `labels` | partial `Labels` | `defaultLabels` | Overrides for button and status text. |

Legal text always comes from the notice your backend serves, in the user's language: titles, purposes, data items and
the withdraw, rights and Data Protection Board links. Only interface labels live in the package. The `labels` prop
covers those, for example:

```tsx
<DpdpProvider options={{ baseUrl: "/dpdp" }} labels={{ acceptAll: "Sab theek hai", saveChoices: "Save" }}>
```

### Theming

Override these CSS variables on `.dpdp` or any parent element: `--dpdp-accent`, `--dpdp-text`, `--dpdp-bg`,
`--dpdp-border`, `--dpdp-radius`, `--dpdp-font`. Dark mode follows `prefers-color-scheme`.

```css
.privacy { --dpdp-accent: #0b5fff; --dpdp-radius: 4px; }
```

## API reference

See [React components](../reference/react.md) for every component and state in an interactive Storybook, which runs
against an in-memory backend and shows axe-core results for each story. Props, hook return types and `Labels` are in
the package's exported TypeScript types. The HTTP calls behind them are in the [REST contract](../reference/rest.md).

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Error: dpdpkit hooks and components must be inside <DpdpProvider>` | A component or hook ran outside the provider. | Wrap the tree, or the part that uses them, in `DpdpProvider`. |
| `Error: DpdpProvider needs a client or options` | Neither prop was given. | Pass `options={{ baseUrl: "/dpdp" }}` or `client`. |
| The component shows the error message after loading | A request failed: 401, CORS, or a wrong `baseUrl`. | Open the browser's network tab. Send the session cookie or a token in `options.headers`, and check the prefix. |
| Components look unstyled | The stylesheet was not imported. | `import "@dpdpkit/react/styles.css"` once. |
| Everything refetches on each render | `options` is a new object every render. | Create it outside the component or wrap it in `useMemo`. |
| Peer dependency warning for `@dpdpkit/client` | The installed client is outside `>=0.1.0-0 <0.2.0`. | Install a client in the same minor series. |
| Text is in the wrong language | The notice is not published in that `locale`, so the default applies. | Publish the translation, or check `LanguageSwitcher` for the available languages. |
| A toggle is off for a returning visitor | Components tick a box only for consent the user already gave. | Expected. Check `GET /consents/me` for that user. |

## Upgrading

Upgrade `@dpdpkit/react` and `@dpdpkit/client` together: the peer range allows the same minor series only
(`>=0.1.0-0 <0.2.0`). Upgrade the backend first when a release adds endpoints.

There are no breaking changes to report yet: `0.1.0-alpha.2` is part of the first alpha series. Read the
[changelog](https://github.com/dpdpkit-dev/dpdpkit-react/blob/main/CHANGELOG.md) before each upgrade.

See [Versioning and deprecation](../reference/deprecation.md) for how breaking changes are announced.
