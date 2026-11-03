import{n as e}from"./rolldown-runtime-sJBDdmOt.js";import{n as t,t as n}from"./RightsRequestForm-BWJqmCXp.js";var r,i,a,o,s,c,l,u;function d(){return(d=e((()=>{t(),{fn:r}=__STORYBOOK_MODULE_TEST__,i={title:`Components/RightsRequestForm`,component:n,args:{onSubmitted:r()},parameters:{docs:{description:{component:`Opens a rights request (access, correction, erasure, nomination, grievance…) and tracks the principal's requests. Choosing a nomination asks for the nominee instead of free text.`}}}},a={},o={parameters:{dpdp:{requests:[{kind:`access`,status:`completed`},{kind:`correction`,status:`in_progress`},{kind:`erasure`,status:`received`}]}}},s={args:{kinds:[`access`,`erasure`,`grievance`]}},c={args:{showRequests:!1},parameters:o.parameters},l={parameters:{dpdp:{fail:`save`}}},u=[`Default`,`WithExistingRequests`,`LimitedKinds`,`WithoutRequestList`,`SubmitFailed`],a.parameters={...a.parameters,docs:{...a.parameters?.docs,source:{originalSource:`{}`,...a.parameters?.docs?.source}}},o.parameters={...o.parameters,docs:{...o.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      requests: [{
        kind: "access",
        status: "completed"
      }, {
        kind: "correction",
        status: "in_progress"
      }, {
        kind: "erasure",
        status: "received"
      }]
    }
  }
}`,...o.parameters?.docs?.source}}},s.parameters={...s.parameters,docs:{...s.parameters?.docs,source:{originalSource:`{
  args: {
    kinds: ["access", "erasure", "grievance"]
  }
}`,...s.parameters?.docs?.source},description:{story:"Offer only some kinds of request with `kinds`.",...s.parameters?.docs?.description}}},c.parameters={...c.parameters,docs:{...c.parameters?.docs,source:{originalSource:`{
  args: {
    showRequests: false
  },
  parameters: WithExistingRequests.parameters
}`,...c.parameters?.docs?.source},description:{story:"`showRequests={false}` hides the table, for example when the requests are listed elsewhere.",...c.parameters?.docs?.description}}},l.parameters={...l.parameters,docs:{...l.parameters?.docs,source:{originalSource:`{
  parameters: {
    dpdp: {
      fail: "save"
    }
  }
}`,...l.parameters?.docs?.source},description:{story:`The backend rejects the request: press Submit to see the error message.`,...l.parameters?.docs?.description}}}})))()}d();export{a as Default,s as LimitedKinds,l as SubmitFailed,o as WithExistingRequests,c as WithoutRequestList,u as __namedExportsOrder,i as default};