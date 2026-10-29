import assert from 'node:assert/strict';
import {makeHandler} from '../src/newsletter-worker.js';
let pending=null, active=false, messages=[];
const store={
 async registerPending(v){pending=v;return {accepted:true}},
 async cancelPending(email,hash){if(pending?.email===email&&pending?.tokenHash===hash)pending=null},
 async consumeConfirmation(hash,now){if(!pending || pending.tokenHash!==hash || now>=pending.expiresAt)return false;pending=null;active=true;return true},
 async unsubscribeByHash(){const was=active;active=false;return was}
};
const handler=makeHandler({store,mail:{async sendConfirmation(m){messages.push(m)}},verifyChallenge:async x=>x==='pass'});
const post=(path,data)=>new Request('https://worker.test/'+path,{method:'POST',headers:{origin:'https://mypaper.news','content-type':'application/json'},body:JSON.stringify(data)});
const input={email:'reader@example.invalid',lang:'cs',sections:['world','tech'],consent:true,challenge:'pass'};
assert.equal((await handler(post('subscribe',input))).status,200);assert.equal(active,false);assert.equal(messages.length,1);
let token=messages[0].token;let open=await handler(new Request('https://worker.test/confirm?t='+token));assert.equal(open.status,200);assert.equal(active,false);
const confirm=()=>new Request('https://worker.test/confirm',{method:'POST',body:new URLSearchParams({token})});
assert.equal((await handler(confirm())).status,200);assert.equal(active,true);assert.equal((await handler(confirm())).status,400);
const unsubToken='f'.repeat(64);assert.equal((await handler(new Request('https://worker.test/unsubscribe?t='+unsubToken))).status,200);assert.equal(active,true);
assert.equal((await handler(new Request('https://worker.test/unsubscribe',{method:'POST',body:new URLSearchParams({token:unsubToken})}))).status,200);assert.equal(active,false);
assert.equal((await handler(post('subscribe',input))).status,200);assert.equal(active,false);
assert.equal((await handler(post('subscribe',{...input,sections:['health']}))).status,400);
console.log('End-to-end local lifecycle: pending, confirmation, repeat, opt-out and re-registration passed');
