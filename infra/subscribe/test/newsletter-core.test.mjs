import assert from 'node:assert/strict';
import {requestSubscription,confirmSubscription,unsubscribe,validate,digest} from '../src/newsletter-core.js';
let pending, sent;
const store = {async registerPending(v){pending=v;return {accepted:true}},async consumeConfirmation(h,now){if(!pending||pending.tokenHash!==h||now>pending.expiresAt)return false; pending=null;return true},async unsubscribeByHash(h){return h===await digest('a'.repeat(64))}};
const mail = {async sendConfirmation(v){sent=v}};
await requestSubscription({email:'Test@Example.com',lang:'cs',sections:['world'],consent:true},{store,mail,origin:'https://mypaper.news',now:1000});
assert.equal(sent.email,'test@example.com'); assert.notEqual(pending.tokenHash,sent.token); assert.equal(JSON.stringify(pending).includes(sent.token),false);
assert.equal(await confirmSubscription(sent.token,{store,now:2000}),true); assert.equal(await confirmSubscription(sent.token,{store,now:2000}),false);
assert.equal(await unsubscribe('a'.repeat(64),{store}),true);assert.equal(await unsubscribe('wrong',{store}),false);
for(const data of [{email:'x@y.cz',lang:'cs',sections:['health'],consent:true},{email:'x@y.cz',lang:'cs',sections:['world'],consent:false},{email:'x@y.cz',lang:'cs',sections:['world'],consent:true,health:'secret'}]) assert.throws(()=>validate(data));
await assert.rejects(()=>requestSubscription({email:'x@y.cz',lang:'cs',sections:['world'],consent:true},{store,mail,origin:'https://attacker.example'}));
// An existing opt-out remains intact until the recipient confirms the request.
let state = {unsubscribed:true}, next, delivered;
const secondStore = {
  async registerPending(v){next=v;return {accepted:true}},
  async consumeConfirmation(h,now){if(!next || next.tokenHash!==h || now>=next.expiresAt)return false; state.unsubscribed=false; next=null; return true},
};
await requestSubscription({email:'x@y.cz',lang:'cs',sections:['world'],consent:true},{store:secondStore,mail:{async sendConfirmation(v){delivered=v}},origin:'https://mypaper.news',now:0});
assert.equal(state.unsubscribed,true);
assert.equal(await confirmSubscription(delivered.token,{store:secondStore,now:86400000}),false);
assert.equal(state.unsubscribed,true);
console.log('Newsletter lifecycle: validation, confirmation and unsubscribe checks passed');
