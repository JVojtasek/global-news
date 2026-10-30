import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

test('published client is the same as the tested source', async () => {
  assert.equal(await readFile(new URL('./client.js',import.meta.url),'utf8'),
               await readFile(new URL('../../static/reading-metrics.js',import.meta.url),'utf8'));
});

test('counts only reviewed links, excludes hidden time and sends no private fields', async () => {
  let now=0, posts=[]; const docEvents={}, winEvents={};
  const path='/cs/tech/a-backup-is-only-a-promise/';
  const document={documentElement:{lang:'cs'},visibilityState:'visible',querySelector:()=>({}),
    addEventListener:(n,fn)=>{docEvents[n]=fn}};
  const location=new URL('https://mypaper.news'+path);
  const ctx={document,location,navigator:{},performance:{now:()=>now},URL,
    window:{addEventListener:(n,fn)=>{winEvents[n]=fn}},
    fetch:async(url,options)=>{
      if (String(url).endsWith('allowlist.json')) return {ok:true,json:async()=>[path]};
      posts.push(JSON.parse(options.body)); return {ok:true};
    }};
  const source=await readFile(new URL('./client.js',import.meta.url),'utf8');
  vm.runInNewContext(source,ctx);
  await new Promise(resolve=>setTimeout(resolve,0));
  docEvents.click({isTrusted:true,target:{closest:()=>({href:'https://mypaper.news'+path})}});
  docEvents.click({isTrusted:true,target:{closest:()=>({href:'https://mypaper.news/cs/science/health-topic/'})}});
  now=30000; document.visibilityState='hidden'; docEvents.visibilitychange();
  now=120000; document.visibilityState='visible'; docEvents.visibilitychange();
  now=135000; winEvents.pagehide();
  assert.equal(posts.length,2);
  assert.deepEqual(posts,[{kind:'click',path,seconds:0},{kind:'reading',path,seconds:45}]);
});
