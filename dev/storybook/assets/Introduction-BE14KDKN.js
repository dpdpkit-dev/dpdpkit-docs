import{n as e}from"./rolldown-runtime-sJBDdmOt.js";import{i as t}from"./iframe-Dy3SzJqU.js";import{i as n,r}from"./react-Bg8UoiFE.js";import{a as i,o as a}from"./blocks-BL9xAeo2.js";function o(e){let t={a:`a`,blockquote:`blockquote`,code:`code`,h1:`h1`,h2:`h2`,li:`li`,p:`p`,pre:`pre`,strong:`strong`,ul:`ul`,...n(),...e.components};return(0,c.jsxs)(c.Fragment,{children:[(0,c.jsx)(i,{title:`Introduction`}),`
`,(0,c.jsx)(t.h1,{id:`dpdpkitreact`,children:`@dpdpkit/react`}),`
`,(0,c.jsxs)(t.p,{children:[`React components and hooks for `,(0,c.jsx)(t.a,{href:`https://dpdpkit-dev.github.io/dpdpkit-docs/`,rel:`nofollow`,children:`dpdpkit`}),`: an itemised consent notice,
a preference centre with one-click withdrawal, a rights request form and a language switcher.`]}),`
`,(0,c.jsxs)(t.blockquote,{children:[`
`,(0,c.jsxs)(t.p,{children:[(0,c.jsx)(t.strong,{children:`Disclaimer.`}),` dpdpkit is software that helps you implement obligations under India's Digital Personal
Data Protection Act, 2023 and the DPDP Rules, 2025. It does not provide legal advice and does not
guarantee compliance.`]}),`
`]}),`
`,(0,c.jsx)(t.pre,{children:(0,c.jsx)(t.code,{className:`language-bash`,children:`npm i @dpdpkit/react @dpdpkit/client
`})}),`
`,(0,c.jsx)(t.pre,{children:(0,c.jsx)(t.code,{className:`language-tsx`,children:`import { ConsentNotice, DpdpProvider, LanguageSwitcher, PreferenceCenter, RightsRequestForm } from "@dpdpkit/react";
import "@dpdpkit/react/styles.css";

<DpdpProvider options={{ baseUrl: "/dpdp" }} locale="hi">
  <LanguageSwitcher />
  <ConsentNotice onSaved={() => closeBanner()} />
  <PreferenceCenter />
  <RightsRequestForm />
</DpdpProvider>
`})}),`
`,(0,c.jsx)(t.h2,{id:`about-these-stories`,children:`About these stories`}),`
`,(0,c.jsxs)(t.p,{children:[`The stories run against an in-memory backend in your browser: nothing you click is sent anywhere, and a
reload starts again. In your app the same components talk to a dpdpkit backend (the FastAPI or Django
adapter, `,(0,c.jsx)(t.code,{children:`dpdpkit-server`}),` or dpdpkit Cloud) through `,(0,c.jsx)(t.code,{children:`@dpdpkit/client`}),`. The notice, its purposes and its
translations are example content, not a template to copy.`]}),`
`,(0,c.jsxs)(t.p,{children:[`The `,(0,c.jsx)(t.strong,{children:`Accessibility`}),` panel runs axe-core on each story. The same checks run in CI.`]}),`
`,(0,c.jsx)(t.h2,{id:`design-rules-the-components-follow`,children:`Design rules the components follow`}),`
`,(0,c.jsxs)(t.ul,{children:[`
`,(0,c.jsxs)(t.li,{children:[(0,c.jsx)(t.strong,{children:`Legal text comes from the API.`}),` Titles, purposes, data items and links come from the notice in the
principal's language. Only interface labels (button text) live in the package; override them with `,(0,c.jsx)(t.code,{children:`labels`}),`.`]}),`
`,(0,c.jsxs)(t.li,{children:[(0,c.jsx)(t.strong,{children:`Nothing pre-ticked.`}),` A box is ticked only if the principal previously gave that consent.`]}),`
`,(0,c.jsxs)(t.li,{children:[(0,c.jsx)(t.strong,{children:`Equal choices.`}),` "Accept all", "Reject all" and "Save my choices" share one style.`]}),`
`,(0,c.jsxs)(t.li,{children:[(0,c.jsx)(t.strong,{children:`Withdrawal is one click`}),`, never more steps than granting.`]}),`
`,(0,c.jsxs)(t.li,{children:[(0,c.jsx)(t.strong,{children:`Always linked:`}),` withdraw, your rights, and complaining to the Data Protection Board.`]}),`
`]})]})}function s(e={}){let{wrapper:t}={...n(),...e.components};return t?(0,c.jsx)(t,{...e,children:(0,c.jsx)(o,{...e})}):o(e)}var c;function l(){return(l=e((()=>{c=t(),r(),a()})))()}l();export{s as default};