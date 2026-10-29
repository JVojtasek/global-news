// An intentionally narrow collector. It never reads cookies, IP addresses,
// referrers, browser storage, form values or reader preferences.
const ORIGIN = 'https://mypaper.news';
const safePath = /^\/(cs|en)\/(?:world|business|tech|science|culture|history|sport|travel)\/[a-z0-9-]{1,100}\/$/;
// Fail closed: automatic health tags can be absent or truncated, so only
// explicitly reviewed articles may be measured. Extend after editorial review.
const reviewedPaths = new Set(['/cs/tech/a-backup-is-only-a-promise/', '/en/science/summer-triangle-corner-deneb/']);
const headers = {'Access-Control-Allow-Origin': ORIGIN, 'Vary':'Origin', 'Cache-Control':'no-store'};

export function validArticle(a) {
  return typeof a?.u === 'string' && reviewedPaths.has(a.u) && safePath.test(a.u) && a.s !== 'health' &&
    typeof a.g === 'string' && !a.g.split(',').some(x => x.trim().startsWith('h_'));
}

export async function handle(request, env, fetcher = fetch) {
  if (request.headers.get('Origin') !== ORIGIN) return new Response(null,{status:403});
  if (request.method === 'OPTIONS') return new Response(null,{status:204,headers:{...headers,'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'content-type'}});
  if (request.method !== 'POST') return new Response(null,{status:405,headers});
  const raw = await request.text();
  if (raw.length > 256) return new Response(null,{status:400,headers});
  let data;
  try { data = JSON.parse(raw); } catch { return new Response(null,{status:400,headers}); }
  if (!data || Object.keys(data).sort().join(',') !== 'kind,path,seconds' ||
      !safePath.test(data.path || '') || !['click','reading'].includes(data.kind) ||
      !Number.isInteger(data.seconds) || data.seconds < 0 || data.seconds > 1800 ||
      data.seconds % 15 !== 0 || (data.kind === 'click' && data.seconds !== 0))
    return new Response(null,{status:400,headers});
  const lang = data.path.split('/')[1];
  const res = await fetcher(`${ORIGIN}/${lang}/articles.json`);
  if (!res.ok) return new Response(null,{status:503,headers});
  const articles = await res.json();
  if (!Array.isArray(articles) || !articles.some(a => a.u === data.path && validArticle(a)))
    return new Response(null,{status:400,headers});
  const day = new Date().toISOString().slice(0,10);
  await env.DB.prepare(`INSERT INTO daily_metrics (day,path,clicks,reading_samples,reading_seconds)
    VALUES (?1,?2,?3,?4,?5) ON CONFLICT(day,path) DO UPDATE SET
    clicks=clicks+excluded.clicks, reading_samples=reading_samples+excluded.reading_samples,
    reading_seconds=reading_seconds+excluded.reading_seconds`)
    .bind(day,data.path,data.kind === 'click' ? 1 : 0,data.kind === 'reading' ? 1 : 0,data.seconds).run();
  return new Response(null,{status:204,headers});
}
export default { fetch: handle };
