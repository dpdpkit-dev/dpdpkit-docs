import{n as e}from"./rolldown-runtime-sJBDdmOt.js";import{n as t,t as n}from"./PreferenceCenter-D9C3ePHr.js";var r,i,a,o,s,c;function l(){return(l=e((()=>{t(),r={title:`Components/PreferenceCenter`,component:n,parameters:{docs:{description:{component:`Current consent per purpose with one-click withdrawal (never more steps than granting) and the principal's consent history, loaded when the history is opened.`}}}},i={},a={parameters:{dpdp:{consents:{account:`granted`,marketing:`withdrawn`,analytics:`denied`}}}},o={parameters:{dpdp:{consents:{account:`granted`,marketing:`granted`},fail:`save`}}},s={parameters:{dpdp:{fail:`load`}}},c=[`NothingDecided`,`MixedChoices`,`WithdrawFailed`,`LoadFailed`],i.parameters={...i.parameters,docs:{...i.parameters?.docs,source:{originalSource:`{}`,...i.parameters?.docs?.source}}},a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      consents: {
        account: "granted",
        marketing: "withdrawn",
        analytics: "denied"
      }
    }
  }
}`,...a.parameters?.docs?.source},description:{story:`Open "History of your choices" to see the ledger entries behind each state.`,...a.parameters?.docs?.description}}},o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      consents: {
        account: "granted",
        marketing: "granted"
      },
      fail: "save"
    }
  }
}`,...o.parameters?.docs?.source},description:{story:`The backend rejects the change: press Withdraw to see the error message.`,...o.parameters?.docs?.description}}},s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      fail: "load"
    }
  }
}`,...s.parameters?.docs?.source}}}})))()}l();export{s as LoadFailed,a as MixedChoices,i as NothingDecided,o as WithdrawFailed,c as __namedExportsOrder,r as default};