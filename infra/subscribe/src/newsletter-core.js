/* Pure subscription lifecycle. A deployment must provide an atomic store and
   mail adapter; this module never reads browser preferences or sends on its own. */
const SECTIONS = new Set(['world','business','tech','science','culture','travel','motoring','sport','food','goodnews','history','questions','meaning','relationships','parenting','wonder','ai','safety','soul','mysteries']);
const encoder = new TextEncoder();
const hex = bytes => Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
async function digest(value) { return hex(new Uint8Array(await crypto.subtle.digest('SHA-256', encoder.encode(value)))); }
function token() { return hex(crypto.getRandomValues(new Uint8Array(32))); }
function validate(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('invalid');
  const allowed = new Set(['email','lang','sections','consent']);
  if (Object.keys(input).some(k => !allowed.has(k))) throw new Error('invalid');
  const email = typeof input.email === 'string' ? input.email.trim().toLowerCase() : '';
  if (email.length > 254 || !/^[^\s@]+@[^\s@.]+\.[^\s@.]+$/.test(email)) throw new Error('invalid');
  if (!['cs','en'].includes(input.lang) || input.consent !== true || !Array.isArray(input.sections)) throw new Error('invalid');
  const sections = [...new Set(input.sections)];
  if (!sections.length || sections.length > 10 || sections.some(s => typeof s !== 'string' || !SECTIONS.has(s))) throw new Error('invalid');
  return { email, lang: input.lang, sections };
}
/* registerPending must atomically replace only the PENDING request, never
   clear an existing unsubscribe or change a confirmed reader's preferences.
   It must enforce resend rate limits and expiry; the real adapter is pending. */
export async function requestSubscription(input, {store, mail, origin, now = Date.now()}) {
  const data = validate(input);
  if (origin !== 'https://mypaper.news') throw new Error('invalid origin');
  const secret = token();
  const result = await store.registerPending({...data, tokenHash: await digest(secret), expiresAt: now + 86400000, now});
  if (result.reason === 'full') throw new Error('capacity');
  if (result.accepted) {
    try {
      await mail.sendConfirmation({email:data.email, lang:data.lang, token:secret});
    } catch (err) {
      if (store.cancelPending) await store.cancelPending(data.email, await digest(secret));
      throw err;
    }
  }
  return {ok:true};
}
/* consumeConfirmation must verify the hash, expiry, and one-time use in one
   transaction; it alone may activate or reactivate the subscriber. */
export async function confirmSubscription(secret, {store, now = Date.now()}) {
  if (!/^[a-f0-9]{64}$/.test(secret || '')) return false;
  return !!(await store.consumeConfirmation(await digest(secret), now));
}
/* One-click unsubscribing must be an atomic, idempotent store operation. */
export async function unsubscribe(secret, {store}) {
  if (!/^[a-f0-9]{64}$/.test(secret || '')) return false;
  return !!(await store.unsubscribeByHash(await digest(secret)));
}
export { validate, digest };
