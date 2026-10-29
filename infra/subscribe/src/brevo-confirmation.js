/* Preparatory adapter for a separately verified Brevo account. It is not wired
   into the production worker until the account and sending domain are tested. */
export function brevoConfirmation({apiKey,workerOrigin,senderEmail='confirm@mail.mypaper.news',fetcher=fetch}) {
 const url=new URL(workerOrigin);
 if(url.protocol!=='https:' || url.origin!==workerOrigin || !apiKey) throw new Error('invalid configuration');
 return {async sendConfirmation({email,lang,token}) {
  if(!['cs','en'].includes(lang)||!/^[a-f0-9]{64}$/.test(token)) throw new Error('invalid confirmation');
  const link=workerOrigin+'/confirm#t='+token+'&lang='+lang;
  const subject=lang==='cs'?'Potvrďte odběr My Paper':'Confirm your My Paper subscription';
  const message=lang==='cs'?'Potvrďte svůj odběr kliknutím na odkaz:':'Confirm your subscription using this link:';
  const textContent=message+'\n'+link;
  const escape=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const htmlContent='<html><body><p>'+escape(message)+'</p><p><a href="'+escape(link)+'">'+escape(link)+'</a></p></body></html>';
  const response=await fetcher('https://api.brevo.com/v3/smtp/email',{
   method:'POST',headers:{'api-key':apiKey,'content-type':'application/json','accept':'application/json'},
   body:JSON.stringify({sender:{name:'My Paper',email:senderEmail},to:[{email}],subject,textContent,htmlContent,tags:['mypaper-briefing']})
  });
  if(!response.ok) throw new Error('confirmation delivery failed');
  const result=await response.json();
  if(!result.messageId) throw new Error('confirmation response missing message id');
 }};
}
