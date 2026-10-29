/* Isolated draft endpoint; never deploy until abuse protection, browser flow,
   real database integration and email delivery have been verified. */
import {requestSubscription, confirmSubscription, unsubscribe} from './newsletter-core.js';
import {neonStore, neonQuery} from './neon-store.js';
import {runScheduled} from './newsletter-cron.js';
import {reserveSend} from './newsletter-quota.js';
import {brevoConfirmation} from './brevo-confirmation.js';
import {processBrevoEvent} from './brevo-events.js';
import {restoreBrevoSubscription} from './brevo-restore.js';

const enc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const headers = {'Cache-Control':'no-store','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff'};
function html(content,status=200) { return new Response('<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>My Paper</title><body><main>'+content+'</main></body></html>',{status,headers:{...headers,'Content-Type':'text/html; charset=utf-8','Content-Security-Policy':"default-src 'none'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"}}); }
async function readLimited(request) {
 const max=4096, header=Number(request.headers.get('content-length'));
 if(Number.isFinite(header) && header>max) throw new Error('too large');
 if(!request.body) return '';
 const reader=request.body.getReader();let size=0,parts=[];
 try {while(true){const {done,value}=await reader.read();if(done)break;size+=value.byteLength;if(size>max){await reader.cancel();throw new Error('too large');}parts.push(value);}}
 finally {reader.releaseLock();}
 const merged=new Uint8Array(size);let at=0;for(const part of parts){merged.set(part,at);at+=part.byteLength;}
 return new TextDecoder('utf-8',{fatal:true,ignoreBOM:false}).decode(merged);
}
function form(action,token,label,lang) {return html('<form method="post" action="/'+action+'"><input type="hidden" name="token" value="'+enc(token)+'"><input type="hidden" name="lang" value="'+enc(lang)+'"><button type="submit">'+label+'</button></form>');}
function fragmentForm(action) {
 const unsubscribe=action==='unsubscribe';
 const script=`(()=>{const p=new URLSearchParams(location.hash.slice(1)),t=p.get('t')||'',en=p.get('lang')==='en';if(!/^[a-f0-9]{64}$/.test(t))return;document.getElementById('token').value=t;document.getElementById('lang').value=en?'en':'cs';document.getElementById('submit').textContent=en?${JSON.stringify(unsubscribe?'Unsubscribe':'Confirm subscription')}:${JSON.stringify(unsubscribe?'Odhlásit odběr':'Potvrdit odběr')};document.getElementById('submit').disabled=false;history.replaceState(null,'',location.pathname);})();`;
 return new Response('<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>My Paper</title><body><main><form method="post" action="/'+action+'"><input id="token" type="hidden" name="token"><input id="lang" type="hidden" name="lang"><button id="submit" type="submit" disabled>Načítání / Loading</button></form><noscript>Pro pokračování povolte JavaScript / Enable JavaScript to continue.</noscript></main><script>'+script+'</script></body></html>',{headers:{...headers,'Content-Type':'text/html; charset=utf-8','Content-Security-Policy':"default-src 'none'; script-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'"}});
}
async function sameSecret(a,b) {
 if(typeof a!=='string'||typeof b!=='string'||b.length<32) return false;
 const e=new TextEncoder();
 const [x,y]=await Promise.all([crypto.subtle.digest('SHA-256',e.encode(a)),crypto.subtle.digest('SHA-256',e.encode(b))]);
 const aa=new Uint8Array(x),bb=new Uint8Array(y);let diff=0;
 for(let i=0;i<aa.length;i++) diff|=aa[i]^bb[i];
 return diff===0;
}
export function makeHandler({store,mail,verifyChallenge,webhookSecret,query}) {
 return async request => {
  const url=new URL(request.url), method=request.method;
  if(url.pathname==='/brevo-events' && method==='POST') {
   const auth=request.headers.get('authorization')||'';
   if(!webhookSecret || webhookSecret.length<32 || !await sameSecret(auth,'Bearer '+webhookSecret) || !query) return new Response('Forbidden',{status:403,headers});
   let event; try {event=JSON.parse(await readLimited(request));} catch {return new Response('Invalid event',{status:400,headers});}
   try {await processBrevoEvent(event,query);return new Response(null,{status:204,headers});}
   catch {return new Response('Event processing failed',{status:503,headers});}
  }
  if (url.pathname==='/subscribe' && method==='POST') {
   const origin=request.headers.get('origin')||'';
   if (origin!=='https://mypaper.news') return new Response('Forbidden',{status:403,headers});
   if ((Number(request.headers.get('content-length'))||0)>4096) return new Response('Too large',{status:413,headers});
   try {
    const body=await readLimited(request);
    const input=JSON.parse(body);
    if (!input || typeof input.challenge !== 'string' || input.challenge.length > 2048 || !verifyChallenge || !(await verifyChallenge(input.challenge))) return new Response(JSON.stringify({ok:false}),{status:403,headers:{...headers,'Access-Control-Allow-Origin':origin,'Vary':'Origin','Content-Type':'application/json'}});
    const {challenge,...subscription}=input;
    await requestSubscription(subscription,{store,mail,origin});
    return new Response(JSON.stringify({ok:true}),{headers:{...headers,'Access-Control-Allow-Origin':origin,'Vary':'Origin','Content-Type':'application/json'}});
   } catch (err) {return new Response(JSON.stringify({ok:false}),{status:(err instanceof SyntaxError || err.message==='invalid')?400:503,headers:{...headers,'Access-Control-Allow-Origin':origin,'Vary':'Origin','Content-Type':'application/json'}});}
  }
  if (url.pathname==='/subscribe' && method==='OPTIONS') {
   if(request.headers.get('origin')!=='https://mypaper.news') return new Response(null,{status:403,headers});
   return new Response(null,{status:204,headers:{...headers,'Access-Control-Allow-Origin':'https://mypaper.news','Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type','Vary':'Origin'}});
  }
  if ((url.pathname==='/confirm'||url.pathname==='/unsubscribe') && method==='GET') {
   const en=url.searchParams.get('lang')==='en', t=url.searchParams.get('t')||'';
   if(!t) return fragmentForm(url.pathname.slice(1));
   if(!/^[a-f0-9]{64}$/.test(t)) return html(en?'The link is invalid.':'Odkaz není platný.',400);
   return form(url.pathname.slice(1),t,url.pathname==='/confirm'?(en?'Confirm subscription':'Potvrdit odběr'):(en?'Unsubscribe':'Odhlásit odběr'),en?'en':'cs');
  }
  if ((url.pathname==='/confirm'||url.pathname==='/unsubscribe') && method==='POST') {
   try {const contentType=request.headers.get('content-type')||'';
    if(url.pathname==='/unsubscribe' && url.searchParams.has('t')) {
     const t=url.searchParams.get('t')||'';
     if(!/^[a-f0-9]{64}$/.test(t)) return new Response('Invalid', {status:400,headers});
     const body=await readLimited(request); let value;
     if(contentType.toLowerCase().startsWith('application/x-www-form-urlencoded')) value=new URLSearchParams(body).get('List-Unsubscribe');
     else if(contentType.toLowerCase().startsWith('multipart/form-data;')) value=(await new Request('https://localhost/',{method:'POST',headers:{'Content-Type':contentType},body}).formData()).get('List-Unsubscribe');
     if(value!=='One-Click') return new Response('Invalid', {status:400,headers});
     const ok=await unsubscribe(t,{store});
     return new Response(ok?'Unsubscribed':'Invalid', {status:ok?200:400,headers});
    }
    if(!contentType.toLowerCase().startsWith('application/x-www-form-urlencoded')) return html('Neplatný požadavek.',400);
    const fields=new URLSearchParams(await readLimited(request)); const t=String(fields.get('token')||''), en=fields.get('lang')==='en';
    const ok=url.pathname==='/confirm'?await confirmSubscription(t,{store}):await unsubscribe(t,{store});
    return html(ok?(url.pathname==='/confirm'?(en?'Your subscription is confirmed.':'Odběr byl potvrzen.'):(en?'You have unsubscribed.':'Odběr byl odhlášen.')):(en?'The link is invalid or has expired.':'Odkaz není platný nebo vypršel.'),ok?200:400);
   } catch {return html('Operaci se nepodařilo provést.',503);}
  }
  return new Response('Not found',{status:404,headers});
 };
}
export default {
 async scheduled(event,env,ctx) { ctx.waitUntil(runScheduled(env,new Date(event.scheduledTime))); },
 async fetch(request,env) {
 const brevo=env.MAIL_PROVIDER==='brevo';
 if (!['brevo','resend'].includes(env.MAIL_PROVIDER)) return new Response('Not configured',{status:503,headers});
 if (!env.DATABASE_URL || !env.UNSUBSCRIBE_SECRET || !(brevo?env.BREVO_API_KEY:env.RESEND_API_KEY) || !env.PUBLIC_WORKER_URL || !env.TURNSTILE_SECRET) return new Response('Not configured',{status:503,headers});
 const endpoint=new URL(env.PUBLIC_WORKER_URL);
 if(endpoint.protocol!=='https:' || endpoint.username || endpoint.password || endpoint.pathname!=='/' || endpoint.search || endpoint.hash) return new Response('Not configured',{status:503,headers});
 const query=neonQuery(env.DATABASE_URL);
 const store=neonStore(query,env.UNSUBSCRIBE_SECRET,brevo?email=>restoreBrevoSubscription(email,env.BREVO_API_KEY):undefined);
 const mail={async sendConfirmation({email,lang,token}) {
   if(!await reserveSend(query)) throw new Error('daily sending budget exhausted');
   if(brevo) return brevoConfirmation({apiKey:env.BREVO_API_KEY,workerOrigin:endpoint.origin}).sendConfirmation({email,lang,token});
   const link=endpoint.origin+'/confirm?t='+token+'&lang='+lang;
   const subject=lang==='cs'?'Potvrďte odběr My Paper':'Confirm your My Paper subscription';
   const message=lang==='cs'?'Potvrďte svůj odběr kliknutím na odkaz:':'Confirm your subscription using this link:';
   const r=await fetch('https://api.resend.com/emails',{method:'POST',headers:{'Authorization':'Bearer '+env.RESEND_API_KEY,'Content-Type':'application/json'},body:JSON.stringify({from:'My Paper <briefing@updates.mypaper.news>',to:[email],subject,text:message+'\n'+link})});
   if(!r.ok) throw new Error('delivery failed');
 }};
 const verifyChallenge=async challenge=>{
   const response=await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({secret:env.TURNSTILE_SECRET,response:challenge})});
   if(!response.ok) return false;
   const result=await response.json();
   return result.success===true && result.hostname==='mypaper.news' && result.action==='newsletter';
 };
 return makeHandler({store,mail,verifyChallenge,webhookSecret:env.BREVO_WEBHOOK_SECRET,query})(request);
}};
