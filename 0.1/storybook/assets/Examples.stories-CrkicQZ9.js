import{n as e}from"./rolldown-runtime-sJBDdmOt.js";import{r as t,t as n}from"./ConsentNotice-BDjMisyk.js";import{n as r,t as i}from"./PreferenceCenter-BNhIndHA.js";import{n as a,t as o}from"./RightsRequestForm-BWJqmCXp.js";import{n as s,t as c}from"./LanguageSwitcher-Dm0DkJl5.js";import{i as l}from"./iframe-DotmTG46.js";function u(){return(0,d.jsxs)(`div`,{style:{display:`grid`,gap:`2rem`,maxWidth:`44rem`},children:[(0,d.jsx)(c,{}),(0,d.jsx)(n,{}),(0,d.jsx)(i,{}),(0,d.jsx)(o,{})]})}var d,f,p,m,h,g,_;function v(){return(v=e((()=>{t(),s(),r(),a(),d=l(),f={title:`Examples/Privacy page`,component:u,parameters:{docs:{description:{component:"All the components on one page, sharing one `DpdpProvider`."}}}},p={parameters:{dpdp:{requests:[{kind:`access`,status:`completed`}]}}},m={"--dpdp-accent":`#7a1f5c`,"--dpdp-focus":`#a3307c`,"--dpdp-radius":`2px`,"--dpdp-font":`Georgia, serif`},h={render:()=>(0,d.jsx)(`div`,{style:m,children:(0,d.jsx)(u,{})})},g={parameters:{dpdp:{labels:{acceptAll:`Allow everything`,rejectAll:`Decline all`,saveChoices:`Confirm`,preferencesTitle:`Privacy settings`}}}},_=[`AllComponents`,`Themed`,`CustomLabels`],p.parameters={...p.parameters,docs:{...p.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      requests: [{
        kind: "access",
        status: "completed"
      }]
    }
  }
}`,...p.parameters?.docs?.source},description:{story:`Saving in the notice updates the preference centre, and the other way round.`,...p.parameters?.docs?.description}}},h.parameters={...h.parameters,docs:{...h.parameters?.docs,source:{originalSource:`{
  render: () => <div style={brand}>
      <PrivacyPage />
    </div>
}`,...h.parameters?.docs?.source},description:{story:"The theme is CSS variables on `.dpdp` or any parent: `--dpdp-accent`, `--dpdp-radius`, `--dpdp-font`…",...h.parameters?.docs?.description}}},g.parameters={...g.parameters,docs:{...g.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      labels: {
        acceptAll: "Allow everything",
        rejectAll: "Decline all",
        saveChoices: "Confirm",
        preferencesTitle: "Privacy settings"
      }
    }
  }
}`,...g.parameters?.docs?.source},description:{story:`Interface labels (button text and similar) can be overridden; legal text always comes from the notice.`,...g.parameters?.docs?.description}}}})))()}v();export{p as AllComponents,g as CustomLabels,h as Themed,_ as __namedExportsOrder,f as default};