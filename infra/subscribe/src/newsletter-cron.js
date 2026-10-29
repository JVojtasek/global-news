/* Cron wiring is intentionally opt-in. The application is not deployed. */
import {deliverBatch,pragueDay} from './newsletter-delivery.js';
import {neonQuery} from './neon-store.js';
import {reserveSend} from './newsletter-quota.js';
import {brevoDelivery} from './brevo-delivery.js';

export async function runScheduled(env, now = new Date(), fetcher = fetch) {
 if(env.ENABLE_DELIVERY !== 'true') return {disabled:true};
 const brevo=env.MAIL_PROVIDER==='brevo';
 if(!['brevo','resend'].includes(env.MAIL_PROVIDER)) throw new Error('delivery provider not configured');
 if(!env.DATABASE_URL || !(brevo?env.BREVO_API_KEY:env.RESEND_API_KEY) || !env.UNSUBSCRIBE_SECRET || !env.PUBLIC_WORKER_URL) throw new Error('delivery not configured');
 const hour=new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Prague',hour:'2-digit',hourCycle:'h23'}).format(now);
 if(hour!=='07') return {outsideWindow:true};
 const day=pragueDay(now), articleIndex={};
 for(const lang of ['cs','en']) {
  const r=await fetcher('https://mypaper.news/'+lang+'/articles.json');
  if(!r.ok) throw new Error('public article index unavailable');
  const rows=await r.json(); if(!Array.isArray(rows)) throw new Error('invalid public article index');
  articleIndex[lang]=rows;
 }
 const query=neonQuery(env.DATABASE_URL,fetcher);
 const mail={async send({email,lang,text,unsubscribeUrl,key}) {
  if(!await reserveSend(query,'digest')) throw new Error('daily sending budget exhausted');
  if(brevo) return brevoDelivery({apiKey:env.BREVO_API_KEY,fetcher}).send({email,lang,text,unsubscribeUrl});
  const r=await fetcher('https://api.resend.com/emails',{method:'POST',headers:{Authorization:'Bearer '+env.RESEND_API_KEY,'Content-Type':'application/json','Idempotency-Key':key},body:JSON.stringify({from:'My Paper <briefing@updates.mypaper.news>',to:[email],subject:lang==='cs'?'Váš ranní briefing My Paper':'Your My Paper morning briefing',text,headers:{'List-Unsubscribe':'<'+unsubscribeUrl+'>','List-Unsubscribe-Post':'List-Unsubscribe=One-Click'}})});
  if(!r.ok) throw new Error('provider request failed');
  return await r.json();
 }};
 return deliverBatch({query,mail,articleIndex,unsubscribeSecret:env.UNSUBSCRIBE_SECRET,workerOrigin:env.PUBLIC_WORKER_URL,day,limit:10,fragmentLinks:brevo});
}
