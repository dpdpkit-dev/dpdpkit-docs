import{n as e}from"./rolldown-runtime-sJBDdmOt.js";import{r as t,t as n}from"./ConsentNotice-BDjMisyk.js";import{n as r,t as i}from"./LanguageSwitcher-Dm0DkJl5.js";import{i as a}from"./iframe-DotmTG46.js";var o,s,c,l,u,d;function f(){return(f=e((()=>{t(),r(),o=a(),s={title:`Components/LanguageSwitcher`,component:i,parameters:{docs:{description:{component:`Offers every language the current notice is published in and switches the provider's locale. It renders nothing when the notice has only one language.`}}}},c={},l={render:e=>(0,o.jsxs)(o.Fragment,{children:[(0,o.jsx)(i,{...e}),(0,o.jsx)(n,{})]})},u={parameters:{dpdp:{locales:[`en`]}}},d=[`Default`,`WithNotice`,`SingleLanguage`],c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{}`,...c.parameters?.docs?.source}}},l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  render: args => <>
      <LanguageSwitcher {...args} />
      <ConsentNotice />
    </>
}`,...l.parameters?.docs?.source},description:{story:`Switching the language reloads the notice in that language.`,...l.parameters?.docs?.description}}},u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      locales: ["en"]
    }
  }
}`,...u.parameters?.docs?.source},description:{story:`Nothing to switch between, so nothing is rendered.`,...u.parameters?.docs?.description}}}})))()}f();export{c as Default,u as SingleLanguage,l as WithNotice,d as __namedExportsOrder,s as default};