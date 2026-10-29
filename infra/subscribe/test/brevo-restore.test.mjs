import assert from 'node:assert/strict';
import {restoreBrevoSubscription} from '../src/brevo-restore.js';
const email='reader@example.com';
const record={email,senderEmail:'briefing@mail.mypaper.news',reason:{code:'unsubscribedViaEmail'}};
function mock(contacts) {const calls=[];return {calls,fetcher:async (url,options)=>{calls.push({url,options});return options.method==='DELETE'?new Response(null,{status:204}):Response.json({count:contacts.length,contacts});}}}
let m=mock([record]);await restoreBrevoSubscription(email,'key',m.fetcher);assert.equal(m.calls.length,2);assert.equal(m.calls[1].options.method,'DELETE');
m=mock([{...record,reason:{code:'hardBounce'}}]);await assert.rejects(restoreBrevoSubscription(email,'key',m.fetcher));assert.equal(m.calls.length,1);
m=mock([record,{...record,senderEmail:'another@example.com'}]);await assert.rejects(restoreBrevoSubscription(email,'key',m.fetcher));assert.equal(m.calls.length,1);
m=mock([]);await restoreBrevoSubscription(email,'key',m.fetcher);assert.equal(m.calls.length,1);
console.log('Brevo restore: confirmed email only, rejects unrelated, spam and bounce blocks');
