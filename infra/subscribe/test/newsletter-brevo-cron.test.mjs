import assert from 'node:assert/strict';
import {runScheduled} from '../src/newsletter-cron.js';
let endpoints=[],updates=[];
const fetcher=async (url,opts={})=>{
 url=String(url);endpoints.push(url);
 if(url.endsWith('/articles.json'))return Response.json([{u:'/cs/world/',t:'News',dt:'2026-10-29',s:'world'}]);
 if(url==='https://unit.neon.tech/sql'){
  const {query}=JSON.parse(opts.body); let rows=[];
  if(query.startsWith('SELECT s.id'))rows=[{id:'00000000-0000-0000-0000-000000000001',email:'test@example.invalid',lang:'cs',sections:['world']}];
  else if(query.startsWith('INSERT INTO briefing.send_budget'))rows=[{used:1}];
  else if(query.startsWith('INSERT INTO briefing.deliveries'))rows=[{subscriber_id:'id'}];
  else if(query.startsWith('UPDATE briefing.deliveries'))updates.push(query);
  else throw Error('unexpected SQL');
  return Response.json({rows});
 }
 if(url==='https://api.brevo.com/v3/smtp/email'){
  const body=JSON.parse(opts.body);assert.match(body.textContent,/unsubscribe/);assert.match(body.htmlContent,/Odhlásit odběr/);
  assert.equal(opts.headers['api-key'],'test');return Response.json({messageId:'test-id'},{status:201});
 }
 throw Error('unexpected request');
};
const env={ENABLE_DELIVERY:'true',MAIL_PROVIDER:'brevo',BREVO_API_KEY:'test',DATABASE_URL:'postgresql://user:password@unit.neon.tech/db',UNSUBSCRIBE_SECRET:'s'.repeat(40),PUBLIC_WORKER_URL:'https://worker.example'};
assert.deepEqual(await runScheduled(env,new Date('2026-10-29T06:15:00Z'),fetcher),{sent:1,skipped:0,unknown:0});
assert.equal(endpoints.filter(x=>x.includes('api.brevo.com')).length,1);
assert.equal(endpoints.filter(x=>x.includes('api.resend.com')).length,0);
assert.match(updates[0],/state='sent'/);
console.log('Simulated Brevo cron: delivery isolated from Resend');
