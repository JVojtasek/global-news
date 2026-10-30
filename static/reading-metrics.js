/* Only explicitly reviewed, unchanged articles are eligible for measurement. */
(() => {
  'use strict';
  const ENDPOINT = 'https://mypaper-reading-metrics.jarda-vojtasek.workers.dev';
  if (!ENDPOINT || navigator.doNotTrack === '1' || navigator.globalPrivacyControl === true) return;
  const language = document.documentElement.lang;
  if (!['cs','en'].includes(language)) return;
  const safePath = /^\/(cs|en)\/(?:world|business|tech|science|culture|history|sport|travel)\/[a-z0-9-]{1,100}\/$/;
  let allowed = new Set();
  const path = location.pathname;
  const isArticle = !!document.querySelector('article.post');
  let start = document.visibilityState === 'visible' ? performance.now() : null;
  let visibleMs = 0, sent = false;
  function send(kind, path, seconds) {
    if (!allowed.has(path)) return;
    fetch(ENDPOINT, {method:'POST', mode:'cors', credentials:'omit',
      referrerPolicy:'no-referrer', keepalive:true,
      headers:{'Content-Type':'text/plain'},
      body:JSON.stringify({kind, path, seconds})}).catch(() => {});
  }
  fetch('/reading-metrics-allowlist.json', {credentials:'omit',referrerPolicy:'no-referrer',cache:'no-store'})
    .then(r => r.ok ? r.json() : [])
    .then(items => {
      if (!Array.isArray(items)) return;
      allowed = new Set(items.filter(a => typeof a === 'string' && safePath.test(a)));
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
  window.addEventListener('pageshow', e => {
    if (e.persisted) { sent = false; visibleMs = 0; start = document.visibilityState === 'visible' ? performance.now() : null; }
  });
})();
