// Called only after the recipient submits their one-time confirmation token.
// Brevo's DELETE is account-wide: refuse unless every block is the specific
// unsubscribe of this publication's sender; never clear bounce or spam blocks.
export async function restoreBrevoSubscription(email, apiKey, fetcher=fetch) {
 if (!apiKey || typeof email !== 'string') throw new Error('restore unavailable');
 const found=[];
 for (let offset=0; offset<1000; offset+=100) {
  const r=await fetcher(`https://api.brevo.com/v3/smtp/blockedContacts?limit=100&offset=${offset}`,{headers:{'api-key':apiKey,accept:'application/json'}});
  if (!r.ok) throw new Error('blocklist unavailable');
  const page=await r.json();
  if (!Array.isArray(page.contacts) || !Number.isSafeInteger(page.count) || page.count<0) throw new Error('invalid blocklist');
  for (const item of page.contacts) if (String(item.email||'').toLowerCase()===email.toLowerCase()) found.push(item);
  if (offset+page.contacts.length>=page.count) break;
  if (page.contacts.length!==100 || offset+100>=1000) throw new Error('incomplete blocklist');
 }
 if (!found.length) return;
 if (found.some(item=>String(item.senderEmail||'').toLowerCase()!=='briefing@mail.mypaper.news' || item.reason?.code!=='unsubscribedViaEmail')) throw new Error('manual review required');
 const r=await fetcher('https://api.brevo.com/v3/smtp/blockedContacts/'+encodeURIComponent(email),{method:'DELETE',headers:{'api-key':apiKey}});
 if (!(r.status===204 || r.status===404)) throw new Error('restore failed');
}
