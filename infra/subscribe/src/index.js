/* =====================================================================
   My Paper — přihlašovací okénko k odběru
   -----------------------------------------------------------------
   Malý program na Cloudflare, který stojí mezi statickým webem
   a dvěma místy, kam adresa patří:

     1. do Neonu ......... aby seznam patřil nám a nikomu jinému
     2. k rozesílací službě ... aby e-maily doopravdy dorazily

   Proč to dělení: uložit adresu je snadné. Doručit e-mail do schránky
   snadné není — je za tím SPF, DKIM, DMARC, odhlašovací odkaz, odražené
   zprávy a reputace domény. Kdybychom rozesílali sami z čerstvé domény,
   spadneme do spamu a pověst mypaper.news si poškodíme natrvalo.
   Rozesílání proto necháváme službě, která to umí. Data si necháváme.

   Když rozesílací služba není nastavená, adresa se uloží do Neonu
   a program to řekne. Nic se neztratí.

   Nasazení: infra/README.md

   Program schválně nepoužívá jedinou cizí knihovnu. Neon má SQL i přes
   obyčejné HTTP, takže se sem vejde celý na pár řádků — a hlavně: soubor
   se dá vložit rovnou do editoru na webu Cloudflare. Odpadá tím
   instalace, příkazová řádka i nástroj wrangler. Pro člověka, který
   není programátor, je to rozdíl mezi „hotovo za pět minut" a „hotovo
   možná".
   ===================================================================== */

/* Dotaz do Neonu přes HTTP. Přesně tohle dělá i oficiální knihovna
   @neondatabase/serverless — jen kolem toho má ještě tisíce řádků,
   které tady k ničemu nejsou.

   Parametry se posílají zvlášť ($1, $2 …), nikdy se nelepí do textu
   dotazu. Kdyby se lepily, stačilo by, aby někdo do políčka na e-mail
   napsal kus SQL, a mohl by si s databází dělat, co chce. */
async function sql(env, query, params = []) {
  const conn = env.DATABASE_URL;
  if (!conn) throw new Error("DATABASE_URL není nastavené");
  const host = new URL(conn).hostname;
  const res = await fetch(`https://${host}/sql`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Neon-Connection-String": conn,
    },
    body: JSON.stringify({ query, params }),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`Neon ${res.status}: ${detail.slice(0, 200)}`);
  }
  const body = await res.json();
  return body.rows || [];
}

/* Nikam neposíláme čitelnou IP adresu. K doložení souhlasu stačí otisk;
   zpětně z něj nikoho nedohledáš, ale prokážeš, že souhlas vznikl. */
async function hashIp(ip, salt) {
  if (!ip) return null;
  const data = new TextEncoder().encode(`${salt || ""}:${ip}`);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

/* Úmyslně mírné. Přísná regulární pravidla na e-maily odmítají platné
   adresy a nezachytí ani o jednu chybu navíc — na to je potvrzovací
   e-mail od rozesílací služby. */
function looksLikeEmail(value) {
  return typeof value === "string"
    && value.length >= 6 && value.length <= 254
    && /^[^\s@]+@[^\s@.]+\.[^\s@]{2,}$/.test(value);
}

function cors(origin, allowed) {
  const ok = allowed.includes(origin) ? origin : allowed[0];
  return {
    "Access-Control-Allow-Origin": ok,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

async function readFields(request) {
  const type = request.headers.get("content-type") || "";
  if (type.includes("application/json")) return await request.json();
  const form = await request.formData();
  return Object.fromEntries(form.entries());
}

/* Předání rozesílací službě. Podporuje beehiiv i MailerLite — obojí má
   free tarif. Když v nastavení nic není, tichý přeskok. */
async function forwardToProvider(env, email, lang, cadence) {
  const provider = (env.PROVIDER || "").toLowerCase();
  try {
    if (provider === "beehiiv" && env.PROVIDER_KEY && env.BEEHIIV_PUBLICATION_ID) {
      const r = await fetch(
        `https://api.beehiiv.com/v2/publications/${env.BEEHIIV_PUBLICATION_ID}/subscriptions`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${env.PROVIDER_KEY}` },
          body: JSON.stringify({ email, reactivate_existing: true, send_welcome_email: true,
                                 utm_source: "mypaper",
                                 custom_fields: [{ name: "lang", value: lang },
                                                 { name: "cadence", value: cadence }] }),
        });
      const body = await r.json().catch(() => ({}));
      return { ok: r.ok, id: body?.data?.id || null };
    }
    if (provider === "mailerlite" && env.PROVIDER_KEY) {
      const r = await fetch("https://connect.mailerlite.com/api/subscribers", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${env.PROVIDER_KEY}` },
        body: JSON.stringify({ email, fields: { lang, cadence } }),
      });
      const body = await r.json().catch(() => ({}));
      return { ok: r.ok, id: body?.data?.id || null };
    }
  } catch (err) {
    /* Výpadek služby nesmí shodit přihlášení. Adresa je v Neonu,
       doplní se ručně nebo příštím během. */
    return { ok: false, id: null, error: String(err) };
  }
  return { ok: false, id: null, error: "provider not configured" };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const allowed = (env.ALLOWED_ORIGINS || "https://mypaper.news").split(",").map((s) => s.trim());
    const head = cors(origin, allowed);
    const url = new URL(request.url);

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: head });

    /* --- odhlášení ------------------------------------------------ */
    if (url.pathname === "/unsubscribe") {
      const token = url.searchParams.get("t");
      if (!token) return new Response("Chybí klíč.", { status: 400, headers: head });
      try {
        await sql(env,
          `update mypaper.subscribers
              set unsubscribed_at = now(), updated_at = now()
            where unsub_token = $1::uuid and unsubscribed_at is null`,
          [token]);
      } catch {
        return new Response("Klíč nesedí.", { status: 400, headers: head });
      }
      return new Response(
        "<!doctype html><meta charset=utf-8><title>Odhlášeno</title>" +
        "<body style='font:16px/1.6 Georgia,serif;max-width:34rem;margin:4rem auto;padding:0 1rem'>" +
        "<h1>Odhlášeno</h1><p>Už ti nic neposíláme. Adresu jsme si nechali jen označenou jako " +
        "odhlášenou, abychom ti omylem nezačali psát znovu.</p>" +
        "<p><a href='https://mypaper.news/'>Zpátky na My Paper</a></p>",
        { status: 200, headers: { ...head, "Content-Type": "text/html; charset=utf-8" } });
    }

    if (request.method !== "POST") return new Response("Method not allowed", { status: 405, headers: head });

    let fields;
    try { fields = await readFields(request); }
    catch { return new Response("Bad request", { status: 400, headers: head }); }

    /* Past na roboty: pole `website` je ve formuláři schované. Člověk ho
       nevidí, robot ho vyplní. Tváříme se, že se povedlo. */
    if (fields.website) return json({ ok: true }, head, request, env);

    const email = String(fields.email || "").trim().toLowerCase();
    if (!looksLikeEmail(email)) return json({ ok: false, error: "email" }, head, request, env, 400);

    const lang = ["cs", "en"].includes(String(fields.lang || "")) ? fields.lang : "en";
    /* Jak často chce psát. Když si nevybere nebo přijde nesmysl, platí
       týdenní — je to menší slib a odhlásí se z něj míň lidí než
       z denního, který si nikdo nevyžádal. */
    const cadence = ["daily", "weekly"].includes(String(fields.cadence || "")) ? fields.cadence : "weekly";
    const source = String(fields.source || "").slice(0, 200) || null;
    const consentText = String(fields.consent_text || "").slice(0, 500) || null;
    const ipHash = await hashIp(request.headers.get("CF-Connecting-IP"), env.IP_SALT);

    let unsubToken = null;
    try {
      const rows = await sql(env,
        `insert into mypaper.subscribers
              (email, lang, cadence, source, consent_ip, consent_text)
         values ($1, $2, $3, $4, $5, $6)
         on conflict (email_lower) do update
            set unsubscribed_at = null,
                lang            = excluded.lang,
                -- Rytmus se přepíše: kdo se přihlásí podruhé, právě teď
                -- řekl, co chce. Zdroj se naopak nechává ten první —
                -- zajímá nás stránka, která ho získala.
                cadence         = excluded.cadence,
                source          = coalesce(mypaper.subscribers.source, excluded.source),
                updated_at      = now()
         returning unsub_token`,
        [email, lang, cadence, source, ipHash, consentText]);
      unsubToken = rows?.[0]?.unsub_token || null;
    } catch (err) {
      return json({ ok: false, error: "db" }, head, request, env, 500);
    }

    const fwd = await forwardToProvider(env, email, lang, cadence);
    if (fwd.ok) {
      try {
        await sql(env,
          `update mypaper.subscribers
              set provider = $1, provider_id = $2, updated_at = now()
            where email_lower = $3`,
          [(env.PROVIDER || "").toLowerCase(), fwd.id, email]);
      } catch { /* uloženo je, zbytek je kosmetika */ }
    }

    return json({ ok: true, delivered: fwd.ok, unsub: unsubToken }, head, request, env, 200, lang);
  },
};

/* Prohlížeč s JavaScriptem chce odpověď v JSON a zůstane na stránce.
   Bez JavaScriptu se formulář odešle normálně — tomu odpovíme
   přesměrováním na děkovnou stránku, ať člověk nekouká do prázdna. */
function json(payload, head, request, env, status = 200, lang = "en") {
  const accept = request.headers.get("Accept") || "";
  const wantsHtml = accept.includes("text/html");
  if (wantsHtml) {
    const base = (env.SITE_URL || "https://mypaper.news").replace(/\/$/, "");
    /* Čech se nesmí po přihlášení ocitnout na anglické stránce. */
    const l = ["cs", "en"].includes(lang) ? lang : "en";
    const to = payload.ok ? `${base}/${l}/thanks/` : `${base}/${l}/#newsletter`;
    return new Response(null, { status: 303, headers: { ...head, Location: to } });
  }
  return new Response(JSON.stringify(payload), {
    status, headers: { ...head, "Content-Type": "application/json" } });
}
