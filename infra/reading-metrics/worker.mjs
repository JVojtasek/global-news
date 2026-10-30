// An intentionally narrow collector. It never reads cookies, IP addresses,
// referrers, browser storage, form values or reader preferences.
const ORIGIN = 'https://mypaper.news';
const safePath = /^\/(cs|en)\/(?:world|business|tech|science|culture|history|sport|travel)\/[a-z0-9-]{1,100}\/$/;
const headers = {'Access-Control-Allow-Origin': ORIGIN, 'Vary':'Origin', 'Cache-Control':'no-store'};

export function validArticle(path, reviewedPaths) {
  return typeof path === 'string' && safePath.test(path) && reviewedPaths.includes(path);
}

export async function handle(request, env, fetcher = fetch) {
  if (env.ENABLE_COLLECTOR !== 'true') return new Response(null,{status:503});
  if (request.headers.get('Origin') !== ORIGIN) return new Response(null,{status:403});
  if (request.method === 'OPTIONS') return new Response(null,{status:204,headers:{...headers,'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'content-type'}});
  if (request.method !== 'POST') return new Response(null,{status:405,headers});
  if (!env.RATE_LIMITER || !(await env.RATE_LIMITER.limit({key:'collector'})).success)
    return new Response(null,{status:429,headers});
  if (Number(request.headers.get('content-length') || 0) > 256) return new Response(null,{status:400,headers});
  const reader = request.body?.getReader();
  if (!reader) return new Response(null,{status:400,headers});
  let raw = '', size = 0; const decoder = new TextDecoder();
  for (;;) {
    const {done,value} = await reader.read(); if (done) break;
    size += value.byteLength;
    if (size > 256) { await reader.cancel(); return new Response(null,{status:400,headers}); }
    raw += decoder.decode(value,{stream:true});
  }
  raw += decoder.decode();
  let data;
  try { data = JSON.parse(raw); } catch { return new Response(null,{status:400,headers}); }
  if (!data || Object.keys(data).sort().join(',') !== 'kind,path,seconds' ||
      !safePath.test(data.path || '') || !['click','reading'].includes(data.kind) ||
      !Number.isInteger(data.seconds) || data.seconds < 0 || data.seconds > 1800 ||
      data.seconds % 15 !== 0 || (data.kind === 'click' && data.seconds !== 0))
    return new Response(null,{status:400,headers});
  const res = await fetcher(`${ORIGIN}/reading-metrics-allowlist.json`, {cache:'no-store'});
  if (!res.ok) return new Response(null,{status:503,headers});
  const reviewed = await res.json();
  if (!Array.isArray(reviewed) || !validArticle(data.path,reviewed))
    return new Response(null,{status:400,headers});
  const day = new Date().toISOString().slice(0,10);
  await env.DB.prepare(`INSERT INTO daily_metrics (day,path,clicks,reading_samples,reading_seconds)
    SELECT ?1,?2,?3,?4,?5 WHERE
    COALESCE((SELECT SUM(clicks + reading_samples) FROM daily_metrics WHERE day=?1),0) < 5000
    ON CONFLICT(day,path) DO UPDATE SET
    clicks=clicks+excluded.clicks, reading_samples=reading_samples+excluded.reading_samples,
    reading_seconds=reading_seconds+excluded.reading_seconds`)
    .bind(day,data.path,data.kind === 'click' ? 1 : 0,data.kind === 'reading' ? 1 : 0,data.seconds).run();
  return new Response(null,{status:204,headers});
}
export default {
  async fetch(request, env) {
    try { return await handle(request, env); }
    catch { return new Response(null, {status:500}); }
  },
  async scheduled(event, env) {
    await env.DB.prepare("DELETE FROM daily_metrics WHERE day < date('now','-90 days')").run();
  }
};
