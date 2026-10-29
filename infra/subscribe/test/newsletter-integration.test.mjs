import assert from 'node:assert/strict';
import worker from '../src/newsletter-worker.js';
let pending=null, active=null, confirmLink='';
const oldFetch=globalThis.fetch;
globalThis.fetch=async (url,opts={})=>{
 url=String(url);
 if(url.includes('siteverify'))return Response.json({success:true,hostname:'mypaper.news',action:'newsletter'});
 if(url==='https://api.resend.com/emails'){const body=JSON.parse(opts.body);confirmLink=body.text.split('\n').at(-1);return Response.json({id:'sample'});}
 if(url==='https://unit.neon.tech/sql'){
  const {query,params}=JSON.parse(opts.body);let rows=[];
  if(query.includes('INSERT INTO briefing.pending_confirmations')){pending={email:params[0],lang:params[1],sections:JSON.parse(params[2]),hash:params[3]};rows=[{email:pending.email}]}
  else if(query.includes('INSERT INTO briefing.send_budget')){rows=[{used:1}]}
  else if(query.includes('SELECT email FROM briefing.pending_confirmations')){if(pending?.hash===params[0])rows=[{email:pending.email}]}
  else if(query.includes('briefing.confirm_pending')){if(pending?.hash===params[0]){active={...pending,unsubscribeHash:params[2],unsubscribed:false};pending=null;rows=[{status:'confirmed'}]}}
  else if(query.includes('UPDATE briefing.subscribers SET unsubscribed_at')){if(active?.unsubscribeHash===params[0]){active.unsubscribed=true;rows=[{id:'sample'}]}}
  else throw Error('unexpected query');
  return Response.json({rows});
 }
 throw Error('unexpected host');
};
try {
 const env={MAIL_PROVIDER:'resend',DATABASE_URL:'postgresql://user:password@unit.neon.tech/db',UNSUBSCRIBE_SECRET:'s'.repeat(40),RESEND_API_KEY:'fake',PUBLIC_WORKER_URL:'https://worker.example',TURNSTILE_SECRET:'fake'};
 const json=JSON.stringify({email:'reader@example.invalid',lang:'cs',sections:['world'],consent:true,challenge:'valid'});
 let r=await worker.fetch(new Request('https://worker.example/subscribe',{method:'POST',headers:{origin:'https://mypaper.news','content-type':'application/json'},body:json}),env);
 assert.equal(r.status,200);assert.equal(active,null);assert.ok(confirmLink.startsWith('https://worker.example/confirm?t='));
 const token=new URL(confirmLink).searchParams.get('t');
 r=await worker.fetch(new Request(confirmLink),env);assert.equal(r.status,200);assert.equal(active,null);
 r=await worker.fetch(new Request('https://worker.example/confirm',{method:'POST',body:new URLSearchParams({token})}),env);assert.equal(r.status,200);assert.equal(active.unsubscribed,false);
 const {unsubscribeToken}=await import('../src/neon-store.js');const ut=await unsubscribeToken(env.UNSUBSCRIBE_SECRET,'reader@example.invalid');
 r=await worker.fetch(new Request('https://worker.example/unsubscribe',{method:'POST',body:new URLSearchParams({token:ut})}),env);assert.equal(r.status,200);assert.equal(active.unsubscribed,true);
 console.log('Integration using simulated Neon, Turnstile and Resend: sign-up, confirmation and opt-out passed');
} finally {globalThis.fetch=oldFetch}
