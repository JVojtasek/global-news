/* Zkoušky přihlašovacího okénka.
   Spustí se takhle, nic se neinstaluje:
       node infra/subscribe/test/subscribe.test.mjs
   Databáze ani rozesílací služba se nevolají — `fetch` je podstrčený,
   takže se zkouší chování programu, ne cizí server. */
import worker from "../src/index.js";

const calls = [];
globalThis.fetch = async (url, opts) => {
  calls.push({ url: String(url), body: JSON.parse(opts.body || "{}") });
  if (String(url).includes("/sql")) {
    return { ok: true, json: async () => ({ rows: [{ unsub_token: "tok-123" }] }) };
  }
  return { ok: true, json: async () => ({ data: { id: "sub_9" } }) };
};

const env = {
  DATABASE_URL: "postgresql://u:p@ep-x-pooler.c-2.eu-central-1.aws.neon.tech/neondb",
  ALLOWED_ORIGINS: "https://mypaper.news",
  SITE_URL: "https://mypaper.news",
  PROVIDER: "beehiiv", PROVIDER_KEY: "k", BEEHIIV_PUBLICATION_ID: "pub_1",
  IP_SALT: "sul",
};

function post(fields, accept = "application/json") {
  return new Request("https://w.dev/", {
    method: "POST",
    headers: { "Content-Type": "application/json", Origin: "https://mypaper.news",
               Accept: accept, "CF-Connecting-IP": "203.0.113.9" },
    body: JSON.stringify(fields),
  });
}

let ok = 0, bad = 0;
const t = async (name, fn) => {
  try { await fn(); console.log("  OK   " + name); ok++; }
  catch (e) { console.log("  CHYBA " + name + " — " + e.message); bad++; }
};
const eq = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b))
  throw new Error(`${m}: ${JSON.stringify(a)} != ${JSON.stringify(b)}`); };

console.log("\nPŘIHLÁŠENÍ K ODBĚRU\n");

await t("platná adresa se uloží a rytmus se předá", async () => {
  calls.length = 0;
  const r = await worker.fetch(post({ email: "Ctenar@Example.com", lang: "cs", cadence: "daily", source: "/cs/" }), env);
  const body = await r.json();
  eq(body.ok, true, "ok");
  const ins = calls.find(c => c.body.query?.includes("insert into"));
  eq(ins.body.params[0], "ctenar@example.com", "adresa se zmenší na malá písmena");
  eq(ins.body.params[2], "daily", "rytmus");
  if (!ins.body.query.includes("$1")) throw new Error("parametry se lepí do textu dotazu!");
});

await t("nesmyslný rytmus spadne na týdenní", async () => {
  calls.length = 0;
  await worker.fetch(post({ email: "a@b.cz", cadence: "kazdou-hodinu" }), env);
  eq(calls.find(c => c.body.query?.includes("insert into")).body.params[2], "weekly", "rytmus");
});

await t("chybějící rytmus je týdenní", async () => {
  calls.length = 0;
  await worker.fetch(post({ email: "a@b.cz" }), env);
  eq(calls.find(c => c.body.query?.includes("insert into")).body.params[2], "weekly", "rytmus");
});

await t("nesmyslná adresa se odmítne", async () => {
  const r = await worker.fetch(post({ email: "tohle-neni-adresa" }), env);
  eq(r.status, 400, "stav");
});

await t("past na roboty tiše zabere", async () => {
  calls.length = 0;
  const r = await worker.fetch(post({ email: "a@b.cz", website: "spam.example" }), env);
  eq((await r.json()).ok, true, "tváří se, že prošlo");
  if (calls.length) throw new Error("robot se dostal do databáze");
});

await t("IP se ukládá jen jako otisk", async () => {
  calls.length = 0;
  await worker.fetch(post({ email: "a@b.cz" }), env);
  const ip = calls.find(c => c.body.query?.includes("insert into")).body.params[4];
  if (ip.includes("203.0.113.9")) throw new Error("čitelná IP v databázi!");
  eq(ip.length, 64, "délka otisku SHA-256");
});

await t("Čech skončí na české děkovné stránce", async () => {
  const r = await worker.fetch(post({ email: "a@b.cz", lang: "cs" }, "text/html"), env);
  eq(r.status, 303, "přesměrování");
  eq(r.headers.get("Location"), "https://mypaper.news/cs/thanks/", "cíl");
});

await t("odhlášení funguje", async () => {
  calls.length = 0;
  const r = await worker.fetch(new Request("https://w.dev/unsubscribe?t=23db547e-4ae8-4ff9-aa8f-4fefd43b458f"), env);
  eq(r.status, 200, "stav");
  if (!calls.some(c => c.body.query?.includes("unsubscribed_at = now()"))) throw new Error("neodhlásilo");
});

await t("odhlášení bez klíče neprojde", async () => {
  const r = await worker.fetch(new Request("https://w.dev/unsubscribe"), env);
  eq(r.status, 400, "stav");
});

await t("výpadek databáze vrátí chybu, ne prázdno", async () => {
  const puvodni = globalThis.fetch;
  globalThis.fetch = async () => ({ ok: false, status: 500, text: async () => "mimo provoz" });
  const r = await worker.fetch(post({ email: "a@b.cz" }), env);
  globalThis.fetch = puvodni;
  eq(r.status, 500, "stav");
});


console.log("\nADMIN — ČÍSLA O ODBĚRATELÍCH\n");

const adminEnv = { ...env, ADMIN_TOKEN: "a".repeat(40) };
const get = (path, token) => new Request("https://w.dev" + path, {
  headers: Object.assign({ Origin: "https://mypaper.news" },
                         token ? { Authorization: "Bearer " + token } : {}),
});

await t("bez tokenu nevydá nic", async () => {
  const r = await worker.fetch(get("/admin/summary"), adminEnv);
  eq(r.status, 401, "stav");
});

await t("se špatným tokenem nevydá nic", async () => {
  const r = await worker.fetch(get("/admin/summary", "b".repeat(40)), adminEnv);
  eq(r.status, 401, "stav");
});

await t("když ADMIN_TOKEN není nastavený, je zavřeno", async () => {
  const r = await worker.fetch(get("/admin/summary", "cokoli"), env);
  eq(r.status, 401, "stav");
});

await t("krátký token se odmítne, i kdyby seděl", async () => {
  const slabe = { ...env, ADMIN_TOKEN: "kratke" };
  const r = await worker.fetch(get("/admin/summary", "kratke"), slabe);
  eq(r.status, 401, "stav");
});

await t("se správným tokenem vrátí čísla", async () => {
  const puvodni = globalThis.fetch;
  globalThis.fetch = async () => ({ ok: true, json: async () => ({ rows: [
    { celkem: 3, potvrzeni: 2, odhlaseni: 0, rano: 1, sobota: 2, za7dni: 3, za30dni: 3 },
  ] }) });
  const r = await worker.fetch(get("/admin/summary", "a".repeat(40)), adminEnv);
  const b = await r.json();
  globalThis.fetch = puvodni;
  eq(r.status, 200, "stav");
  eq(b.celkem, 3, "celkem");
});

await t("adresy jsou v přehledu zakryté", async () => {
  const puvodni = globalThis.fetch;
  let n = 0;
  globalThis.fetch = async () => ({ ok: true, json: async () => {
    n++;
    if (n === 1) return { rows: [{ celkem: 1 }] };
    if (n === 5) return { rows: [{ email: "jaroslav@seznam.cz", lang: "cs", cadence: "daily" }] };
    return { rows: [] };
  } });
  const b = await (await worker.fetch(get("/admin/summary", "a".repeat(40)), adminEnv)).json();
  globalThis.fetch = puvodni;
  const e = b.recent[0].email;
  if (e.includes("jaroslav")) throw new Error("celá adresa v přehledu: " + e);
  if (!e.endsWith("@seznam.cz")) throw new Error("nepoznáš, čí to je: " + e);
});

await t("tabulka ke stažení ošetří vzorce v Excelu", async () => {
  const puvodni = globalThis.fetch;
  globalThis.fetch = async () => ({ ok: true, json: async () => ({ rows: [
    { email: "=CMD()|a", lang: "cs", cadence: "daily", source: "", consent_at: "", confirmed: "ano" },
  ] }) });
  const r = await worker.fetch(get("/admin/export.csv?segment=daily", "a".repeat(40)), adminEnv);
  const text = await r.text();
  globalThis.fetch = puvodni;
  if (!text.includes("\"'=CMD()|a\"")) throw new Error("vzorec neošetřen: " + text.slice(0, 80));
});

await t("výběr segmentu se posílá jako parametr, ne v textu dotazu", async () => {
  const puvodni = globalThis.fetch;
  let dotaz = null;
  globalThis.fetch = async (u, o) => { dotaz = JSON.parse(o.body); return { ok: true, json: async () => ({ rows: [] }) }; };
  await worker.fetch(get("/admin/export.csv?segment=daily&lang=cs", "a".repeat(40)), adminEnv);
  globalThis.fetch = puvodni;
  eq(dotaz.params, ["daily", "cs"], "parametry");
});

await t("nesmyslný segment se ignoruje, nevloží se do dotazu", async () => {
  const puvodni = globalThis.fetch;
  let dotaz = null;
  globalThis.fetch = async (u, o) => { dotaz = JSON.parse(o.body); return { ok: true, json: async () => ({ rows: [] }) }; };
  await worker.fetch(get("/admin/export.csv?segment=' or 1=1--", "a".repeat(40)), adminEnv);
  globalThis.fetch = puvodni;
  eq(dotaz.params, [], "žádné parametry");
  if (dotaz.query.includes("1=1")) throw new Error("podvržený text se dostal do dotazu!");
});

console.log(`\n${ok} v pořádku, ${bad} chyb\n`);
process.exit(bad ? 1 : 0);
