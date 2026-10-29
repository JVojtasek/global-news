/* Draft handler for provider suppression events. Not connected until the
   webhook authentication and delivery ordering are tested with Brevo. */
const SUPPRESS=new Set(['unsubscribed','hard_bounce','invalid_email','spam','blocked']);
export async function processBrevoEvent(event,query) {
 if(!event || typeof event!=='object' || !SUPPRESS.has(event.event)) return {ignored:true};
 // Brevo sends tags as either an array or a JSON-encoded string named tag.
 let tags=event.tags ?? event.tag;
 if(typeof tags==='string') {try {tags=JSON.parse(tags)} catch {tags=[tags]}}
 if(!Array.isArray(tags) || !tags.includes('mypaper-briefing')) return {ignored:true};
 const email=typeof event.email==='string'?event.email.trim().toLowerCase():'';
 const at=Number(event.ts_event);
 if(email.length>254 || !/^[^\s@]+@[^\s@.]+\.[^\s@.]+$/.test(email) || !Number.isSafeInteger(at) || at<1) throw new Error('invalid event');
 // An event predating a newer confirmation must not erase that consent.
 await query(`UPDATE briefing.subscribers SET unsubscribed_at=COALESCE(unsubscribed_at,now()),updated_at=now()
   WHERE email=$1 AND confirmed_at <= to_timestamp($2)`,[email,at]);
 return {suppressed:true};
}
