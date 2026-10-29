/* Draft scheduled delivery implementation. This module is not scheduled or
   deployed. The caller must provide a trusted database query and mail adapter. */
import {selectEdition,renderText} from './newsletter-edition.js';
import {unsubscribeToken} from './neon-store.js';

export function pragueDay(date) {
 return new Intl.DateTimeFormat('en-CA',{timeZone:'Europe/Prague',year:'numeric',month:'2-digit',day:'2-digit'}).format(date);
}
export async function deliverBatch({query,mail,articleIndex,unsubscribeSecret,workerOrigin,day,limit=20,fragmentLinks=false}) {
 if(!/^\d{4}-\d{2}-\d{2}$/.test(day)) throw new Error('invalid day');
 const url=new URL(workerOrigin);
 if(url.protocol!=='https:' || url.origin!==workerOrigin) throw new Error('invalid worker origin');
 const n=Math.min(20,Math.max(1,Number(limit)||20));
 const subscribers=await query(`SELECT s.id,s.email,s.lang,s.sections FROM briefing.subscribers s
   WHERE s.unsubscribed_at IS NULL AND NOT EXISTS (SELECT 1 FROM briefing.deliveries d
   WHERE d.subscriber_id=s.id AND d.edition_date=$1::date) ORDER BY md5(s.id::text || $1::text),s.id LIMIT $2`,[day,n]);
 const counts={sent:0,skipped:0,unknown:0};
 for(const s of subscribers) {
  const edition=selectEdition(articleIndex[s.lang]||[],s.sections,s.lang,day);
  if(!edition.selected.length && !edition.outside) {
   await query(`INSERT INTO briefing.deliveries(subscriber_id,edition_date,state) SELECT id,$2::date,'skipped' FROM briefing.subscribers WHERE id=$1::uuid AND unsubscribed_at IS NULL ON CONFLICT DO NOTHING`,[s.id,day]);
   counts.skipped++;continue;
  }
  const token=await unsubscribeToken(unsubscribeSecret,s.email);
  const link=workerOrigin+'/unsubscribe'+(fragmentLinks?'#':'?')+'t='+token+'&lang='+s.lang;
  const claimed=await query(`INSERT INTO briefing.deliveries(subscriber_id,edition_date,state)
    SELECT id,$2::date,'claimed' FROM briefing.subscribers WHERE id=$1::uuid AND unsubscribed_at IS NULL
    ON CONFLICT DO NOTHING RETURNING subscriber_id`,[s.id,day]);
  if(!claimed.length){counts.skipped++;continue;}
  try {
   const response=await mail.send({email:s.email,lang:s.lang,text:renderText(edition,s.lang,link),unsubscribeUrl:link,key:'briefing/'+day+'/'+s.id});
   if(!response || !response.id) throw new Error('provider did not return id');
   await query(`UPDATE briefing.deliveries SET state='sent',provider_id=$3 WHERE subscriber_id=$1::uuid AND edition_date=$2::date AND state='claimed'`,[s.id,day,response.id]);
   counts.sent++;
  } catch(e) {
   // An uncertain provider response is never retried blindly: it may have sent.
   try {await query(`UPDATE briefing.deliveries SET state='unknown' WHERE subscriber_id=$1::uuid AND edition_date=$2::date AND state='claimed'`,[s.id,day]);} catch(ignore) {}
   counts.unknown++;
   break; // Stop the batch on uncertain delivery or provider failure.
  }
 }
 return counts;
}
