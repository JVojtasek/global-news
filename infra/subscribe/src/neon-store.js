/* Neon PostgreSQL adapter for the My Paper briefing. All calls use bound
   parameters. The adapter is not connected to the old QMA database. */
import {digest} from './newsletter-core.js';
const text = new TextEncoder();
const hex = bytes => Array.from(bytes, b => b.toString(16).padStart(2,'0')).join('');

export async function unsubscribeToken(secret, email) {
  if (typeof secret !== 'string' || secret.length < 32) throw new Error('unsubscribe secret unavailable');
  const key = await crypto.subtle.importKey('raw', text.encode(secret), {name:'HMAC',hash:'SHA-256'}, false, ['sign']);
  return hex(new Uint8Array(await crypto.subtle.sign('HMAC', key, text.encode(email))));
}

export function neonStore(query, unsubscribeSecret, beforeConfirm = async () => {}) {
  return {
    async registerPending({email,lang,sections,tokenHash,now,expiresAt}) {
      const rows = await query(`INSERT INTO briefing.pending_confirmations
        (email,lang,sections,token_hash,requested_at,expires_at)
        SELECT $1,$2,ARRAY(SELECT jsonb_array_elements_text($3::jsonb)),$4,to_timestamp($5 / 1000.0),to_timestamp($6 / 1000.0)
        WHERE (SELECT count(*) FROM briefing.subscribers WHERE unsubscribed_at IS NULL)<100
          OR EXISTS(SELECT 1 FROM briefing.subscribers WHERE email=$1 AND unsubscribed_at IS NULL)
        ON CONFLICT (email) DO UPDATE SET lang=EXCLUDED.lang, sections=EXCLUDED.sections,
          token_hash=EXCLUDED.token_hash, requested_at=EXCLUDED.requested_at, expires_at=EXCLUDED.expires_at
        WHERE briefing.pending_confirmations.requested_at <= EXCLUDED.requested_at - interval '10 minutes'
        RETURNING email`, [email,lang,JSON.stringify(sections),tokenHash,now,expiresAt]);
      if(rows.length===1) return {accepted:true};
      const availability=await query(`SELECT (SELECT count(*) FROM briefing.subscribers WHERE unsubscribed_at IS NULL)<100
        OR EXISTS(SELECT 1 FROM briefing.subscribers WHERE email=$1 AND unsubscribed_at IS NULL) AS available`,[email]);
      return {accepted:false,reason:availability[0]?.available===false?'full':'recent'};
    },
    async cancelPending(email,hash) {
      await query(`DELETE FROM briefing.pending_confirmations WHERE email=$1 AND token_hash=$2`,[email,hash]);
    },
    async consumeConfirmation(tokenHash,now) {
      const lookup = await query(`SELECT email FROM briefing.pending_confirmations
        WHERE token_hash=$1 AND expires_at > to_timestamp($2 / 1000.0)`,[tokenHash,now]);
      if (lookup.length !== 1) return false;
      await beforeConfirm(lookup[0].email);
      const unsubscribeHash = await digest(await unsubscribeToken(unsubscribeSecret,lookup[0].email));
      const rows = await query(`SELECT briefing.confirm_pending($1,$2::bigint,$3) AS status`,[tokenHash,now,unsubscribeHash]);
      return rows.length === 1 && rows[0].status === 'confirmed';
    },
    async unsubscribeByHash(hash) {
      const rows = await query(`UPDATE briefing.subscribers SET unsubscribed_at=COALESCE(unsubscribed_at,now()),updated_at=now()
        WHERE unsubscribe_hash=$1 RETURNING id`,[hash]);
      return rows.length === 1;
    }
  };
}

export function neonQuery(connectionString, fetcher=fetch) {
  const connection = new URL(connectionString);
  if (!['postgres:', 'postgresql:'].includes(connection.protocol) || !connection.hostname.endsWith('.neon.tech')) throw new Error('invalid database connection');
  return async (query,params) => {
    const response=await fetcher(`https://${connection.hostname}/sql`,{method:'POST',
      headers:{'Content-Type':'application/json','Neon-Connection-String':connectionString},
      body:JSON.stringify({query,params})});
    if (!response.ok) throw new Error('Database request failed');
    const data=await response.json();
    if (!Array.isArray(data.rows)) throw new Error('Invalid database response');
    return data.rows;
  };
}
