import { test } from 'node:test';
import assert from 'node:assert/strict';
import worker, {handle, validArticle} from './worker.mjs';

const article = {u:'/cs/tech/a-backup-is-only-a-promise/',s:'tech',g:'security'};
const health = {u:'/cs/science/sensitive-topic/',s:'science',g:'h_heart'};
const req = payload => new Request('https://metrics.example/',{method:'POST',headers:{origin:'https://mypaper.news'},body:JSON.stringify(payload)});
const fetcher = async () => Response.json([article,health]);
let writes;
const env = {DB:{prepare:() => ({bind:(...args) => ({run:async()=>{writes.push(args)}})})}};

test('accepts a known eligible article and stores only daily totals',async()=>{
  writes=[];
  const r=await handle(req({kind:'reading',path:article.u,seconds:45}),env,fetcher);
  assert.equal(r.status,204); assert.deepEqual(writes[0].slice(1),[article.u,0,1,45]);
});
test('rejects health tags, unknown articles, private fields and invalid durations',async()=>{
  writes=[];
  for (const p of [
    {kind:'click',path:health.u,seconds:0},
    {kind:'click',path:'/cs/tech/not-known/',seconds:0},
    {kind:'click',path:article.u,seconds:0,health:'h_heart'},
    {kind:'reading',path:article.u,seconds:22},
    {kind:'click',path:article.u+'?h_heart=1',seconds:0},
  ]) assert.equal((await handle(req(p),env,fetcher)).status,400);
  assert.equal(writes.length,0); assert.equal(validArticle(health),false);
});
test('rejects requests from other origins',async()=>{
  const r=await handle(new Request('https://metrics.example/',{method:'POST',headers:{origin:'https://other.example'}}),env,fetcher);
  assert.equal(r.status,403);
});
test('Cloudflare execution context is not mistaken for a fetch function',async()=>{
  writes=[]; const previous=globalThis.fetch; globalThis.fetch=fetcher;
  try {
    const r=await worker.fetch(req({kind:'click',path:article.u,seconds:0}),env,{waitUntil(){}});
    assert.equal(r.status,204); assert.equal(writes.length,1);
  } finally { globalThis.fetch=previous; }
});
