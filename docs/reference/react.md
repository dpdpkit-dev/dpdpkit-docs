# React components

`@dpdpkit/react` gives a React front end the consent notice, preference centre, rights request form and
language switcher, all talking to your dpdpkit backend through `@dpdpkit/client`.

```bash
npm i @dpdpkit/react @dpdpkit/client
```

```tsx
import { ConsentNotice, DpdpProvider, LanguageSwitcher, PreferenceCenter, RightsRequestForm } from "@dpdpkit/react";
import "@dpdpkit/react/styles.css";

<DpdpProvider options={{ baseUrl: "/dpdp" }} locale="hi">
  <LanguageSwitcher />
  <ConsentNotice onSaved={() => closeBanner()} />
  <PreferenceCenter />
  <RightsRequestForm />
</DpdpProvider>
```

| Component | What it does |
| --- | --- |
| `ConsentNotice` | Itemised notice: one toggle per consent purpose, nothing pre-ticked, "Accept all", "Reject all" and "Save my choices" with equal weight, and the required links |
| `PreferenceCenter` | Current consent per purpose, one-click withdrawal, and the principal's consent history |
| `RightsRequestForm` | Opens access, correction, erasure, nomination and grievance requests, and lists the principal's requests with their due dates |
| `LanguageSwitcher` | Offers every language the notice is published in |

Legal text (titles, purposes, data items, links) always comes from the notice your backend serves, in the
principal's language. Only interface labels live in the package; override them with the `labels` prop of
`DpdpProvider`. Theme the components with CSS variables such as `--dpdp-accent` and `--dpdp-radius`.

## Storybook

[Open the Storybook](../storybook/index.html){ target="_blank" } to try every component and state:
first visit, returning visitor, Hindi, loading and error states, theming and custom labels. The stories run
against an in-memory backend in your browser, so nothing you click is sent anywhere. Each story has an
**Accessibility** panel with its axe-core results.

<iframe src="../../storybook/iframe.html?id=examples-privacy-page--all-components&amp;viewMode=story"
        title="Storybook: all @dpdpkit/react components on one privacy page"
        loading="lazy" style="width: 100%; height: 48rem; border: 1px solid var(--md-default-fg-color--lightest); border-radius: 4px;"></iframe>

The Storybook is built from `dpdpkit-react` and published with each version of these docs.
