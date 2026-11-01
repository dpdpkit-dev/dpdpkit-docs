import{n as e}from"./rolldown-runtime-sJBDdmOt.js";import{r as t,t as n}from"./ConsentNotice-CX4ntX-V.js";var r,i,a,o,s,c,l,u,d;function f(){return(f=e((()=>{t(),{fn:r}=__STORYBOOK_MODULE_TEST__,i={title:`Components/ConsentNotice`,component:n,args:{onSaved:r()},parameters:{docs:{description:{component:`The itemised notice: one toggle per consent purpose, nothing pre-ticked, three equal-weight buttons and the required links. Purposes with another legal basis are listed but have no toggle.`}}}},a={},o={parameters:{dpdp:{consents:{account:`granted`,marketing:`withdrawn`,analytics:`denied`}}}},s={parameters:{dpdp:{locale:`hi`}}},c={parameters:{dpdp:{fail:`never`}}},l={parameters:{dpdp:{fail:`load`}}},u={parameters:{dpdp:{fail:`save`}}},d=[`FirstVisit`,`ReturningVisitor`,`Hindi`,`Loading`,`LoadFailed`,`SaveFailed`],a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{}`,...a.parameters?.docs?.source},description:{story:`A principal who has not decided anything yet: every box is empty.`,...a.parameters?.docs?.description}}},o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      consents: {
        account: "granted",
        marketing: "withdrawn",
        analytics: "denied"
      }
    }
  }
}`,...o.parameters?.docs?.source},description:{story:`A box is ticked only where the principal previously gave consent.`,...o.parameters?.docs?.description}}},s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      locale: "hi"
    }
  }
}`,...s.parameters?.docs?.source},description:{story:"Legal text comes from the notice in the principal's language; only button text comes from `labels`.",...s.parameters?.docs?.description}}},c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      fail: "never"
    }
  }
}`,...c.parameters?.docs?.source}}},l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      fail: "load"
    }
  }
}`,...l.parameters?.docs?.source}}},u.parameters={...u.parameters,docs:{...u.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      fail: "save"
    }
  }
}`,...u.parameters?.docs?.source},description:{story:`The backend rejects the save: press any button to see the error message.`,...u.parameters?.docs?.description}}}})))()}f();export{a as FirstVisit,s as Hindi,l as LoadFailed,c as Loading,o as ReturningVisitor,u as SaveFailed,d as __namedExportsOrder,i as default};