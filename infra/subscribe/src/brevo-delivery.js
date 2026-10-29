/* Draft only: Brevo account, domain and unsubscribe behaviour must be
   verified against a real mailbox before connecting to the scheduler. */
const escape = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

export function brevoDelivery({apiKey,senderEmail='briefing@mail.mypaper.news',fetcher=fetch}) {
 if (!apiKey || !/^[^\s@]+@mail\.mypaper\.news$/.test(senderEmail)) throw new Error('invalid configuration');
 return {async send({email,lang,text,unsubscribeUrl}) {
  if (!['cs','en'].includes(lang) || typeof text!=='string' || !text.includes(unsubscribeUrl)) throw new Error('invalid delivery');
  const unsubscribe=new URL(unsubscribeUrl);
  if (unsubscribe.protocol!=='https:' || unsubscribe.pathname!=='/unsubscribe') throw new Error('invalid unsubscribe URL');
  const body={sender:{name:'My Paper',email:senderEmail},to:[{email}],
   subject:lang==='cs'?'Váš ranní briefing My Paper':'Your My Paper morning briefing',
   textContent:text,tags:['mypaper-briefing'],htmlContent:'<html><body><pre style="white-space:pre-wrap;font-family:sans-serif">'+escape(text)+'</pre><p><a href="'+escape(unsubscribeUrl)+'">'+(lang==='cs'?'Odhlásit odběr':'Unsubscribe')+'</a></p></body></html>'};
  const r=await fetcher('https://api.brevo.com/v3/smtp/email',{method:'POST',headers:{'api-key':apiKey,'content-type':'application/json','accept':'application/json'},body:JSON.stringify(body)});
  if(!r.ok) throw new Error('provider request failed');
  const result=await r.json();
  if(!result.messageId) throw new Error('provider response missing message id');
  return {id:result.messageId};
 }};
}
