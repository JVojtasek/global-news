import assert from 'node:assert/strict';
import {runScheduled} from '../src/newsletter-cron.js';
const originalDate = new Date('2026-10-29T06:15:00Z');let api=[],deliveries=[];
const fetcher=async(url,opts={})=>{
 url=String(url); api.push(url);
 if(url.includes('/articles.json'))return Response.json([{u:'/cs/news/',t:'Zpráva',dt:'2026-10-29',s:'world'}]);
 if(url==='https://unit.neon.tech/sql'){
  const {query,params}=JSON.parse(opts.body);let rows=[];
  if(query.startsWith('SELECT s.id'))rows=[{id:'00000000-0000-0000-0000-000000000001',email:'test@example.invalid',lang:'cs',sections:['world']}];
  else if(query.startsWith('INSERT INTO briefing.send_budget'))rows=[{used:1}];
  else if(query.startsWith('INSERT INTO briefing.deliveries'))rows=[{subscriber_id:'id'}];
  else if(query.startsWith('UPDATE briefing.deliveries')){deliveries.push({query,params});}
  else throw Error('unexpected SQL');
  return Response.json({rows});
 }
 if(url==='https://api.resend.com/emails'){assert.ok(opts.headers['Idempotency-Key']);let body=JSON.parse(opts.body);assert.match(body.text,/Zpráva/);assert.match(body.text,/unsubscribe/);assert.match(body.headers['List-Unsubscribe'],/^<https:\/\/worker\.example\/unsubscribe\?t=[a-f0-9]{64}&lang=cs>$/);assert.equal(body.headers['List-Unsubscribe-Post'],'List-Unsubscribe=One-Click');return Response.json({id:'mail-id'});}
 throw Error('unexpected network request');
};
const env={ENABLE_DELIVERY:'true',MAIL_PROVIDER:'resend',DATABASE_URL:'postgresql://user:password@unit.neon.tech/db',RESEND_API_KEY:'fake',UNSUBSCRIBE_SECRET:'s'.repeat(40),PUBLIC_WORKER_URL:'https://worker.example'};
assert.deepEqual(await runScheduled(env,originalDate,fetcher),{sent:1,skipped:0,unknown:0});
assert.equal(api.filter(x=>x==='https://api.resend.com/emails').length,1);
assert.match(deliveries[0].query,/state='sent'/);
console.log('Simulated scheduled delivery: published index, idempotent send, database record passed');
