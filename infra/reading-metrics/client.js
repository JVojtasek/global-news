/* Privacy-preserving draft: set ENDPOINT only after the collector is deployed. */
(() => {
  'use strict';
  const ENDPOINT = '';
  if (!ENDPOINT || navigator.doNotTrack === '1' || navigator.globalPrivacyControl === true) return;
  const language = document.documentElement.lang;
  if (!['cs','en'].includes(language)) return;
  const safePath = /^\/(cs|en)\/(?:world|business|tech|science|culture|history|sport|travel)\/[a-z0-9-]{1,100}\/$/;
  const reviewedPaths = new Set(['/cs/tech/a-backup-is-only-a-promise/', '/en/science/summer-triangle-corner-deneb/']);
  let allowed = new Set();
  const path = location.pathname;
  const isArticle = !!document.querySelector('article.post');
  let start = document.visibilityState === 'visible' ? performance.now() : null;
  let visibleMs = 0, sent = false;
  function send(kind, path, seconds) {
    if (!allowed.has(path)) return;
    fetch(ENDPOINT, {method:'POST', mode:'cors', credentials:'omit',
      referrerPolicy:'no-referrer', keepalive:true,
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({kind, path, seconds})}).catch(() => {});
  }
  fetch(`/${language}/articles.json`, {credentials:'omit',referrerPolicy:'no-referrer'})
    .then(r => r.ok ? r.json() : [])
    .then(items => {
      if (!Array.isArray(items)) return;
      allowed = new Set(items.filter(a => typeof a.u === 'string' && reviewedPaths.has(a.u) && safePath.test(a.u) &&
        a.s !== 'health' && typeof a.g === 'string' &&
        !a.g.split(',').some(t => t.trim().startsWith('h_'))).map(a => a.u));
    }).catch(() => {});
  document.addEventListener('click', e => {
    const link = e.target.closest && e.target.closest('a[href]');
    if (!link || !e.isTrusted) return;
    let url; try { url = new URL(link.href, location.href); } catch { return; }
    if (url.origin === location.origin && !url.search && !url.hash) send('click',url.pathname,0);
  }, {capture:true});
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') start = performance.now();
    else if (start !== null) { visibleMs += performance.now() - start; start = null; }
  });
  window.addEventListener('pagehide', () => {
    if (sent || !isArticle) return;
    sent = true;
    if (start !== null) visibleMs += performance.now() - start;
    const seconds = Math.min(1800, Math.floor(visibleMs / 15000) * 15);
    if (seconds >= 15) send('reading',path,seconds);
  });
})();
