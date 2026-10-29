import assert from 'node:assert/strict';
import {runScheduled} from '../src/newsletter-cron.js';
let calls=0;const fetcher=async()=>{calls++;throw Error('should not run')};
assert.deepEqual(await runScheduled({},new Date('2026-10-29T06:00:00Z'),fetcher),{disabled:true});
await assert.rejects(()=>runScheduled({ENABLE_DELIVERY:'true'},new Date('2026-10-29T06:00:00Z'),fetcher));
const env={ENABLE_DELIVERY:'true',MAIL_PROVIDER:'resend',DATABASE_URL:'postgresql://a:b@host.neon.tech/db',RESEND_API_KEY:'x',UNSUBSCRIBE_SECRET:'x'.repeat(40),PUBLIC_WORKER_URL:'https://worker.test'};
assert.deepEqual(await runScheduled(env,new Date('2026-10-29T10:00:00Z'),fetcher),{outsideWindow:true});assert.equal(calls,0);
console.log('Cron: fails closed and respects Prague delivery window');
