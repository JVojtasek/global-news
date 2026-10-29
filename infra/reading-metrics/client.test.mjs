import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import vm from 'node:vm';

test('counts only reviewed links, excludes hidden time and sends no private fields', async () => {
  let now=0, posts=[]; const docEvents={}, winEvents={};
  const path='/cs/tech/a-backup-is-only-a-promise/';
  const document={documentElement:{lang:'cs'},visibilityState:'visible',querySelector:()=>({}),
    addEventListener:(n,fn)=>{docEvents[n]=fn}};
  const location=new URL('https://mypaper.news'+path);
  const ctx={document,location,navigator:{},performance:{now:()=>now},URL,
    window:{addEventListener:(n,fn)=>{winEvents[n]=fn}},
    fetch:async(url,options)=>{
      if (String(url).endsWith('articles.json')) return {ok:true,json:async()=>[
        {u:path,s:'tech',g:'security'}, {u:'/cs/science/health-topic/',s:'science',g:''}]};
      posts.push(JSON.parse(options.body)); return {ok:true};
    }};
  const source=(await readFile(new URL('./client.js',import.meta.url),'utf8'))
    .replace("const ENDPOINT = '';", "const ENDPOINT = 'https://metrics.example/';");
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
