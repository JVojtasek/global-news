import assert from 'node:assert/strict';
import {reserveSend} from '../src/newsletter-quota.js';
let attempts=0;
const query=async(sql,params)=>{assert.match(sql,/ON CONFLICT \(day,kind\) DO UPDATE/);assert.match(sql,/THEN 40 ELSE 100/);assert.deepEqual(params,['confirmation']);return ++attempts<=40?[{used:attempts}]:[]};
for(let i=0;i<40;i++) assert.equal(await reserveSend(query),true);
assert.equal(await reserveSend(query),false);
await assert.rejects(()=>reserveSend(async()=>{throw Error('database unavailable')}));
console.log('Daily send budget: atomic reservation and failure closed');
