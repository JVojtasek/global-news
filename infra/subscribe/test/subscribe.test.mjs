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

console.log(`\n${ok} v pořádku, ${bad} chyb\n`);
process.exit(bad ? 1 : 0);
