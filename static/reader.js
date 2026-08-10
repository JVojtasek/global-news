/* =====================================================================
   Nastavení čtení — kolik toho web pustí a jak natvrdo to dopadne,
   a co si čtenář vybral, že ho zajímá.

   Dokud si čtenář nic nenastaví, tenhle soubor nedělá vůbec nic:
   web vypadá a chová se přesně jako předtím. Nic se nikdy nemaže,
   těžké zprávy se jen složí do klidného shrnutí a jdou rozbalit.

   Výběr zájmů nikdy neopustí prohlížeč. Žádný server o něm neví,
   řazení si dělá prohlížeč sám nad seznamem, který je pro všechny
   stejný. Zdravotní zájmy jsou zájmy, ne diagnóza.

   Všechny texty chodí z window.TDSR nebo z <template> v base.html,
   tady žádné texty nejsou — jinak by nešly přeložit.
   ===================================================================== */
(function () {
  "use strict";

  var T = window.TDSR || {};
  var KEY = "tds-reader";
  var SEEN = "tds-heavy-seen";
  var DEF = { amount: 2, tone: 2, mute: [], brake: true, secs: [], tags: [], own: [] };
  var KEEP = { 1: 12, 2: 30, 3: 0 };   // 0 = bez stropu
  var SHARE = 0.6;                     // strop podílu těžkých karet
  var OWN_MAX = 8;                     // kolik vlastních témat nejvýš
  var OWN_MIN = 3;                     // kratší text by trefil skoro cokoli
  var OWN_PTS = 3;                     // co má vlastní téma za trefu
  var BRAKE_AT = 5;
  var OFF = "reader-off";
  var RAIL = 6;                        // kolik karet do proužku „vybráno“
  var PICKED = 18;                     // kolik článků na stránku „pro tebe“
  var OUTSIDE = 6;                     // kolik článků schválně mimo výběr
  var WAIT = 1200;                     // po jaké chvíli nabídnout průvodce

  var doc = document;
  var root = doc.documentElement;
  var lang = root.getAttribute("lang") || "";
  var base = "";
  var cfg = null;        // null = čtenář si nic nenastavil
  var shown = false;     // "přesto zobrazit" — platí jen pro tohle načtení
  var opener = null;
  var home = false;      // stropy na množství platí jen na titulní straně
  var card = null;       // otevřený uvítací průvodce

  /* ---------------------------------------------------------- úložiště */
  function num(v, lo, hi, dflt) {
    v = parseInt(v, 10);
    return (v >= lo && v <= hi) ? v : dflt;
  }

  function isArr(v) {
    return Object.prototype.toString.call(v) === "[object Array]";
  }

  /* Chybějící seznam je prázdný seznam — starší uložené nastavení
     nesmí kvůli novým polím přestat platit. */
  function strs(v) {
    return isArr(v) ? v.filter(function (x) { return typeof x === "string" && x; }) : [];
  }

  function trim(s) {
    return String(s === null || s === undefined ? "" : s).replace(/^\s+|\s+$/g, "");
  }

  function low(s) {
    return String(s === null || s === undefined ? "" : s).toLowerCase();
  }

  /* Vlastní témata čtenáře: bez mezer po krajích, bez krátkých útržků,
     bez dvakrát téhož (velká a malá písmena jsou totéž) a nejvýš OWN_MAX.
     Platí to na jednom místě, ať téma přišlo z políčka nebo z úložiště. */
  function owns(v) {
    var out = [], seen = [], list = strs(v);
    for (var i = 0; i < list.length && out.length < OWN_MAX; i++) {
      var s = trim(list[i]);
      if (s.length < OWN_MIN) continue;
      if (seen.indexOf(low(s)) >= 0) continue;
      seen.push(low(s));
      out.push(s);
    }
    return out;
  }

  function copy(v) {
    return {
      amount: v.amount, tone: v.tone, brake: v.brake,
      mute: v.mute.slice(0), secs: v.secs.slice(0), tags: v.tags.slice(0),
      own: (v.own || []).slice(0)
    };
  }

  function load() {
    try {
      var raw = window.localStorage.getItem(KEY);
      if (!raw) return null;
      var v = JSON.parse(raw);
      if (!v || typeof v !== "object" || isArr(v)) return null;
      // nesmysl v úložišti se bere jako „čtenář si nic nenastavil“
      if (!("amount" in v) && !("tone" in v) && !("mute" in v) && !("brake" in v)
        && !("secs" in v) && !("tags" in v) && !("own" in v)) return null;
      return {
        amount: num(v.amount, 1, 3, DEF.amount),
        tone: num(v.tone, 1, 3, DEF.tone),
        mute: strs(v.mute),
        brake: v.brake !== false,
        secs: strs(v.secs),
        tags: strs(v.tags),
        own: owns(v.own)
      };
    } catch (e) { return null; }
  }

  function save(v) {
    try { window.localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) { /* soukromý režim */ }
  }

  function forget() {
    try { window.localStorage.removeItem(KEY); } catch (e) { /* nevadí */ }
  }

  function now() { return cfg || DEF; }

  /* ------------------------------------------------------------- karty */
  /* Kopie karet v proužku „vybráno pro tebe“ se do počítání nepletou —
     jsou to jenom odrazy karet, které na stránce už jsou. */
  function list() {
    return [].slice.call(
      doc.querySelectorAll(".hero[data-band]:not(.pick), .card[data-band]:not(.pick)")
    );
  }

  function csv(s) {
    return String(s || "").split(",").map(function (x) {
      return x.replace(/^\s+|\s+$/g, "");
    }).filter(Boolean);
  }

  function topicsOf(el) {
    return csv(el.getAttribute("data-topics"));
  }

  function hit(a, b) {
    if (!a.length || !b.length) return false;
    for (var i = 0; i < a.length; i++) {
      if (b.indexOf(a[i]) >= 0) return true;
    }
    return false;
  }

  function both(a, b) {
    return a.filter(function (x) { return b.indexOf(x) >= 0; });
  }

  function muted(el, mute) {
    return hit(topicsOf(el), mute || []);
  }

  function heavy(el) {
    return (el.getAttribute("data-band") || "") === "heavy";
  }

  /* Titulní strana se pozná podle místa pro řádek o skrytých zprávách —
     zjišťuje se jednou na začátku, než ho případně dolepíme jinam. */
  function isHome() {
    return !!doc.getElementById("reader-hidden-note") || !!doc.querySelector(".hero[data-band]");
  }

  /* Pořadí pro režim „jen přehled“: rozhoduje místo na stránce, a když
     jsou karty na stejném místě svých bloků, jde napřed ta lehčí. */
  function ranked(items) {
    var hosts = [];
    return items.map(function (el, i) {
      var host = el.parentNode;
      var g = hosts.indexOf(host);
      if (g < 0) { g = hosts.length; hosts.push(host); }
      var idx = 0, prev = el.previousElementSibling;
      while (prev) {
        if (prev.hasAttribute && prev.hasAttribute("data-band")) idx++;
        prev = prev.previousElementSibling;
      }
      return {
        el: el, i: i, keep: false,
        pos: g + idx,
        load: parseInt(el.getAttribute("data-load"), 10) || 0
      };
    });
  }

  function hide(el) { el.classList.add(OFF); }

  function calmOn(el) {
    el.classList.add("calm");
    if (!el.querySelector(".reader-mark")) {
      var mark = doc.createElement("span");
      mark.className = "reader-mark";
      if (T.calm) mark.title = T.calm;
      var host = el.querySelector(".body, .hero-text") || el;
      host.insertBefore(mark, host.firstChild);
    }
    [].forEach.call(el.querySelectorAll("a[href]"), function (a) {
      var h = a.getAttribute("href");
      if (h && h.charAt(0) === "/" && h.indexOf("#") < 0) a.setAttribute("href", h + "#brief");
    });
  }

  function calmOff(el) {
    el.classList.remove("calm");
    var mark = el.querySelector(".reader-mark");
    if (mark && mark.parentNode) mark.parentNode.removeChild(mark);
    [].forEach.call(el.querySelectorAll("a[href]"), function (a) {
      var h = a.getAttribute("href");
      if (h && h.slice(-6) === "#brief") a.setAttribute("href", h.slice(0, -6));
    });
  }

  /* ------------------------------------------- řádek „něco je skryté“ */
  function noteBox(need) {
    var box = doc.getElementById("reader-hidden-note");
    if (box || !need) return box;
    var grid = doc.querySelector(".grid");
    if (!grid || !grid.parentNode) return null;
    box = doc.createElement("div");
    box.id = "reader-hidden-note";
    grid.parentNode.insertBefore(box, grid);
    return box;
  }

  function note(n) {
    var box = noteBox(n > 0);
    if (!box) return;
    while (box.firstChild) box.removeChild(box.firstChild);
    box.classList.remove("on");
    if (!n) return;

    var txt = doc.createElement("span");
    txt.className = "reader-hidden-txt";
    txt.textContent = n === 1
      ? (T.hidden1 || "")
      : String(T.hiddenN || "").replace("%d", String(n));

    var btn = doc.createElement("button");
    btn.type = "button";
    btn.className = "reader-showall";
    btn.textContent = T.show || "";
    btn.addEventListener("click", function () { shown = true; apply(); });

    box.appendChild(txt);
    box.appendChild(btn);
    box.classList.add("on");
  }

  /* --------------------------------------------------- výpis na stránce */
  function apply() {
    var items = list();
    if (!items.length) { note(0); return; }

    items.forEach(function (el) { el.classList.remove(OFF); calmOff(el); });

    if (!cfg) { note(0); return; }

    var set = now();
    var alive = items;

    if (!shown) {
      // 1. vypnutá témata — ta jdou pryč bez ohledu na všechno ostatní
      if (set.mute.length) {
        alive = alive.filter(function (el) {
          if (muted(el, set.mute)) { hide(el); return false; }
          return true;
        });
      }

      // 2. kolik toho vůbec ukázat (jen titulní strana)
      var cap = KEEP[set.amount] || 0;
      if (home && cap && alive.length > cap) {
        var rank = ranked(alive);
        rank.slice(0).sort(function (a, b) {
          return (a.pos - b.pos) || (a.load - b.load) || (a.i - b.i);
        }).slice(0, cap).forEach(function (r) { r.keep = true; });
        alive = rank.filter(function (r) {
          if (!r.keep) { hide(r.el); return false; }
          return true;
        }).map(function (r) { return r.el; });
      }

      // 3. vyvážení: těžkých nejvýš 60 %, přebytek se sype odspoda
      if (home && set.tone === 2) {
        var vis = alive.length;
        var hv = alive.filter(heavy).length;
        var dropped = [];
        for (var j = alive.length - 1; j >= 0 && hv > vis * SHARE; j--) {
          if (heavy(alive[j])) {
            hide(alive[j]);
            dropped.push(alive[j]);
            hv--; vis--;
          }
        }
        if (dropped.length) {
          alive = alive.filter(function (el) { return dropped.indexOf(el) < 0; });
        }
      }
    }

    // 4. šetrný režim: těžké zprávy jako klidné shrnutí
    if (set.tone === 1) {
      alive.forEach(function (el) { if (heavy(el)) calmOn(el); });
    }

    note(items.length - alive.length);
  }

  /* ------------------------------------------------------ stránka článku */
  function gate(art) {
    var g = art.querySelector(".reader-gate");
    if (g) return g;
    var first = art.querySelector("[data-layer]");
    if (!first || !first.parentNode) return null;
    g = doc.createElement("div");
    g.className = "reader-gate nofold";
    var p = doc.createElement("p");
    p.className = "reader-note";
    g.appendChild(p);
    first.parentNode.insertBefore(g, first);
    return g;
  }

  function article() {
    var art = doc.querySelector("article.post[data-band]");
    if (!art) return;

    // pokaždé nanovo — po uložení nastavení se to musí umět i vrátit
    art.classList.remove("reader-calmed");
    var old = art.querySelector(".reader-gate");
    if (old) old.classList.remove("on");

    var set = now();
    var brief = !!art.querySelector('[data-layer="BRIEFLY"]');
    var byHash = window.location.hash === "#brief";
    var byMute = !!cfg && muted(art, set.mute);
    var byTone = !!cfg && set.tone === 1 && heavy(art);
    if (!byHash && !byMute && !byTone) return;

    // vypnuté téma musí dát vědět i tam, kde shrnutí není — prázdná
    // stránka není odpověď
    var fold = brief && (byHash || byMute || byTone);
    if (!fold && !byMute) return;
    var g = gate(art);
    if (!g) return;

    var msg = g.querySelector(".reader-note");
    if (msg) msg.textContent = byMute ? (T.hidden1 || T.calm || "") : (T.calm || "");
    if (!fold) {
      g.classList.add("nofold");
    } else {
      g.classList.remove("nofold");
      art.classList.add("reader-calmed");
    }
    g.classList.add("on");

    var more = g.querySelector(".reader-more");
    if (more && !more.tdsWired) {
      more.tdsWired = true;
      more.addEventListener("click", function () {
        art.classList.remove("reader-calmed");
        g.classList.remove("on");
        if (window.location.hash === "#brief" && window.history && window.history.replaceState) {
          try {
            window.history.replaceState(null, "", window.location.pathname + window.location.search);
          } catch (e) { /* nevadí */ }
        }
      });
    }
  }

  /* ----------------------------------------------------------- pauza */
  function brake() {
    if (!cfg || !cfg.brake) return;
    var art = doc.querySelector("article.post[data-band]");
    if (!art || !heavy(art)) return;

    var n = 0;
    try { n = parseInt(window.sessionStorage.getItem(SEEN), 10) || 0; } catch (e) { return; }
    n += 1;
    try { window.sessionStorage.setItem(SEEN, String(n)); } catch (e) { /* nevadí */ }
    if (n < BRAKE_AT) return;

    var bar = doc.createElement("div");
    bar.className = "reader-brake";
    bar.setAttribute("role", "status");

    var p = doc.createElement("p");
    p.textContent = T.brakeMsg || "";

    var alt = doc.createElement("a");
    alt.className = "reader-brake-alt";
    alt.href = base + "/" + lang + "/goodnews/";
    alt.textContent = T.brakeAlt || "";

    var ok = doc.createElement("button");
    ok.type = "button";
    ok.className = "reader-brake-ok";
    ok.textContent = T.brakeOk || "";
    ok.addEventListener("click", function () {
      try { window.sessionStorage.setItem(SEEN, "0"); } catch (e) { /* nevadí */ }
      if (bar.parentNode) bar.parentNode.removeChild(bar);
    });

    bar.appendChild(p);
    bar.appendChild(alt);
    bar.appendChild(ok);
    doc.body.appendChild(bar);
  }

  /* ================================================================
     Řazení podle toho, co si čtenář vybral

     Počítá se v prohlížeči, ze seznamu, který je pro všechny stejný.
     Nikam se nic neposílá a nikdo se nedozví, co koho zajímá.

     Položka je vždycky {tags, topics, sec, band, date} — jedno, jestli
     přišla z karty na stránce, nebo ze seznamu článků.
     ================================================================ */

  /* Kolik dní je článku. Záporné (budoucí datum) se bere jako dnešek. */
  function age(d) {
    var p = String(d || "").split("-");
    if (p.length !== 3) return 9999;
    var was = Date.UTC(+p[0], +p[1] - 1, +p[2]);
    if (isNaN(was)) return 9999;
    var n = new Date();
    var day = Date.UTC(n.getFullYear(), n.getMonth(), n.getDate());
    return Math.round((day - was) / 86400000);
  }

  function fresh(d) {
    var a = age(d);
    if (a <= 0) return 2;      // dnešní
    if (a <= 3) return 1;      // do tří dnů
    return 0;
  }

  /* Vlastní téma je obyčejné slovo, ne značka — hledá se proto přímo
     v titulku a perexu. Žádné chytré hledání v tom není a slibovat ho
     nebudeme; text se v `ob_own_help` říká na rovinu. */
  function ownHits(it, set) {
    var list = set.own || [], txt = it.text || "", n = 0;
    if (!txt) return 0;
    for (var i = 0; i < list.length; i++) {
      if (txt.indexOf(low(list[i])) >= 0) n++;
    }
    return n;
  }

  /* Shoda s výběrem čtenáře. Nula znamená „tohle si nevybral“ —
     podle toho se pozná, co patří schválně mimo jeho okruh. */
  function bond(it, set) {
    return 3 * both(it.tags, set.tags).length
      + OWN_PTS * ownHits(it, set)
      + (it.sec && set.secs.indexOf(it.sec) >= 0 ? 2 : 0);
  }

  /* null = vypnuté téma, takový článek se neukáže vůbec nikde */
  function score(it, set) {
    if (hit(it.topics, set.mute)) return null;
    var s = bond(it, set) + fresh(it.date);
    if (it.band === "heavy" && set.tone === 1) s -= 1;
    return s;
  }

  function chosen(set) {
    return !!(set && (set.secs.length || set.tags.length || (set.own || []).length));
  }

  /* rubrika se pozná z odkazu: /základ/jazyk/rubrika/článek/ */
  function sectionOf(el) {
    var a = el.querySelector("a[href]");
    var h = a ? (a.getAttribute("href") || "") : "";
    h = h.split("#")[0].split("?")[0];
    if (base && h.indexOf(base) === 0) h = h.slice(base.length);
    var parts = h.split("/").filter(Boolean);
    var i = parts.indexOf(lang);
    return (i >= 0 && parts.length > i + 1) ? parts[i + 1] : "";
  }

  /* Titulek a perex karty — jediné, v čem se dá hledat vlastní téma.
     Rubrika nad titulkem se schválně nepočítá, jinak by slovo „zdraví“
     vytáhlo celou rubriku. */
  function textOf(el) {
    var h = el.querySelector("h1, h2, h3");
    var d = el.querySelector(".body > p, p.dek");
    return low((h ? h.textContent : "") + " " + (d ? d.textContent : ""));
  }

  function fromCard(el) {
    return {
      el: el,
      tags: csv(el.getAttribute("data-tags")),
      topics: topicsOf(el),
      sec: sectionOf(el),
      band: el.getAttribute("data-band") || "",
      date: el.getAttribute("data-date") || "",
      text: textOf(el)
    };
  }

  function fromJson(o) {
    return {
      raw: o,
      tags: csv(o.g), topics: csv(o.p), sec: o.s || "",
      band: o.b || "", date: o.dt || "",
      text: low((o.t || "") + " " + (o.d || ""))
    };
  }

  /* ---------------------------------------------------------- panel */
  function panel() { return doc.getElementById("reader-panel"); }

  /* Volby (rubriky, zájmy, posuvníky) jsou v <template> jednou a odsud
     se klonují — do nastavení i do průvodce. Kdyby byly dvakrát v HTML,
     rozešly by se. */
  function mount(host, uid) {
    var tpl = doc.getElementById("tds-choices");
    if (!tpl || !tpl.content || !host) return;
    [].forEach.call(host.querySelectorAll(".ob-slot"), function (slot) {
      if (slot.firstChild) return;
      var src = tpl.content.querySelector('[data-part="' + slot.getAttribute("data-slot") + '"]');
      if (!src) return;
      var part = src.cloneNode(true);
      // popisky musí patřit ke svým posuvníkům, a to i ve druhé kopii
      [].forEach.call(part.querySelectorAll("input[data-key]"), function (inp) {
        var id = uid + "-" + inp.getAttribute("data-key");
        var box = inp.parentNode;
        inp.id = id;
        var lab = box.querySelector("label.reader-lab");
        if (lab) lab.setAttribute("for", id);
        var help = box.querySelector(".reader-help");
        if (help) {
          help.id = id + "-help";
          inp.setAttribute("aria-describedby", help.id);
        }
      });
      slot.appendChild(part);
    });
  }

  function ticks(root, name, vals) {
    [].forEach.call(root.querySelectorAll('input[name="' + name + '"]'), function (c) {
      c.checked = vals.indexOf(c.value) >= 0;
    });
  }

  function picks(root, name) {
    var out = [];
    [].forEach.call(root.querySelectorAll('input[name="' + name + '"]'), function (c) {
      if (c.checked) out.push(c.value);
    });
    return out;
  }

  /* ------------------------------------------------ vlastní témata
     Štítek si nese svůj text v data-own-val, takže se dá přečíst zpátky
     i s velkými písmeny tak, jak ho čtenář napsal. Pravidla (délka,
     duplicity, strop) drží `owns` a `ownAdd` — obě kopie voleb, panel
     i průvodce, se chovají stejně, protože je to jeden kus kódu.
     ================================================================ */
  function ownBox(root) {
    return root ? root.querySelector("[data-own]") : null;
  }

  function ownNow(box) {
    if (!box) return [];
    return [].slice.call(box.querySelectorAll(".ob-own-chip")).map(function (c) {
      return c.getAttribute("data-own-val") || "";
    }).filter(Boolean);
  }

  function ownChip(txt) {
    var chip = doc.createElement("span");
    chip.className = "ob-own-chip";
    chip.setAttribute("data-own-val", txt);
    var name = doc.createElement("span");
    name.className = "ob-own-txt";
    name.textContent = txt;
    var x = doc.createElement("button");
    x.type = "button";
    x.className = "ob-own-x";
    x.textContent = "×";
    // jméno tlačítka nese samo téma — přeložitelný text sem nepatří
    x.setAttribute("aria-label", txt);
    x.title = txt;
    chip.appendChild(name);
    chip.appendChild(x);
    return chip;
  }

  /* Na stropu se políčko zavře, místo aby psaní tiše zahazovalo. */
  function ownCap(box) {
    if (!box) return;
    var full = ownNow(box).length >= OWN_MAX;
    var inp = box.querySelector(".ob-own-in");
    var add = box.querySelector(".ob-own-add");
    if (inp) inp.disabled = full;
    if (add) add.disabled = full;
  }

  function ownFill(root, list) {
    var box = ownBox(root);
    var host = box && box.querySelector(".ob-own-list");
    if (!host) return;
    wipe(host);
    owns(list).forEach(function (s) { host.appendChild(ownChip(s)); });
    ownCap(box);
  }

  function ownAdd(box) {
    var inp = box.querySelector(".ob-own-in");
    var host = box.querySelector(".ob-own-list");
    if (!inp || !host) return;
    var s = trim(inp.value);
    if (s.length < OWN_MIN) return;          // krátký útržek zůstane v políčku
    var have = ownNow(box);
    if (have.length >= OWN_MAX) return;
    if (owns(have.concat([s])).length === have.length) { inp.value = ""; return; }
    host.appendChild(ownChip(s));
    inp.value = "";
    ownCap(box);
    if (!inp.disabled) { try { inp.focus(); } catch (e) { /* nevadí */ } }
  }

  function ownWire(root) {
    var box = ownBox(root);
    if (!box || box.tdsOwn) return;
    box.tdsOwn = true;
    box.addEventListener("click", function (e) {
      var el = e.target;
      while (el && el !== box) {
        if (el.classList && el.classList.contains("ob-own-add")) { ownAdd(box); return; }
        if (el.classList && el.classList.contains("ob-own-x")) {
          var chip = el.parentNode;
          if (chip && chip.parentNode) chip.parentNode.removeChild(chip);
          ownCap(box);
          return;
        }
        el = el.parentNode;
      }
    });
    // Enter v políčku přidá téma; nastavení se tím neuloží a nezavře
    box.addEventListener("keydown", function (e) {
      if (e.key !== "Enter" && e.keyCode !== 13) return;
      var el = e.target;
      if (!el || !el.classList || !el.classList.contains("ob-own-in")) return;
      e.preventDefault();
      ownAdd(box);
    });
  }

  function fill(root, v) {
    if (!root) return;
    [].forEach.call(root.querySelectorAll("input[data-key]"), function (inp) {
      var k = inp.getAttribute("data-key");
      if (k in v) { inp.value = String(v[k]); step(inp); }
    });
    var br = root.querySelector("#reader-brake");
    if (br) br.checked = !!v.brake;
    ticks(root, "mute", v.mute);
    ticks(root, "secs", v.secs);
    ticks(root, "tags", v.tags);
    ownFill(root, v.own || []);
  }

  /* Posbírá jen to, co v téhle části opravdu je — průvodce se neptá
     na všechno, a co se neptal, to nesmí přepsat. */
  function gather(root, from) {
    var v = copy(from || DEF);
    if (!root) return v;
    [].forEach.call(root.querySelectorAll("input[data-key]"), function (inp) {
      var k = inp.getAttribute("data-key");
      if (k in v) v[k] = num(inp.value, 1, 3, DEF[k]);
    });
    var br = root.querySelector("#reader-brake");
    if (br) v.brake = !!br.checked;
    if (root.querySelector('input[name="mute"]')) v.mute = picks(root, "mute");
    if (root.querySelector('input[name="secs"]')) v.secs = picks(root, "secs");
    if (root.querySelector('input[name="tags"]')) v.tags = picks(root, "tags");
    var box = ownBox(root);
    if (box) v.own = owns(ownNow(box));
    return v;
  }

  function step(input) {
    var box = input.parentNode;
    if (box && box.setAttribute) box.setAttribute("data-v", String(input.value));
  }

  function open() {
    var p = panel();
    if (!p) return;
    fill(doc.getElementById("reader-form"), now());
    opener = doc.activeElement;
    p.removeAttribute("hidden");
    var btn = doc.getElementById("reader-open");
    if (btn) btn.setAttribute("aria-expanded", "true");
    var box = p.querySelector(".reader-box");
    if (box) box.focus();
  }

  function close() {
    var p = panel();
    if (!p || p.hasAttribute("hidden")) return;
    p.setAttribute("hidden", "");
    var btn = doc.getElementById("reader-open");
    if (btn) btn.setAttribute("aria-expanded", "false");
    if (opener && opener.focus) opener.focus();
    opener = null;
  }

  function wire() {
    var btn = doc.getElementById("reader-open");
    if (btn) btn.addEventListener("click", open);

    var p = panel();
    if (p) {
      p.addEventListener("click", function (e) {
        var el = e.target;
        while (el && el !== p) {
          if (el.hasAttribute && el.hasAttribute("data-reader-close")) { close(); return; }
          el = el.parentNode;
        }
      });
    }

    doc.addEventListener("keydown", function (e) {
      if (e.key !== "Escape" && e.keyCode !== 27) return;
      var p = panel();
      if (p && !p.hasAttribute("hidden")) { close(); return; }
      if (card) done(null);               // průvodce zavřít znamená přeskočit
    });

    var form = doc.getElementById("reader-form");
    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var v = gather(form, now());
        if (!v) return;
        cfg = v;
        shown = false;
        save(v);
        apply();
        rail();
        article();
        foryou();
        close();
      });
      form.addEventListener("input", function (e) {
        if (e.target && e.target.type === "range") step(e.target);
      });
    }

    var undo = doc.getElementById("reader-reset");
    if (undo) {
      undo.addEventListener("click", function () {
        forget();
        cfg = null;
        shown = false;
        fill(form, DEF);
        apply();
        rail();
        foryou();
      });
    }
  }

  /* ================================================== vybráno pro tebe
     Proužek nad titulní stranou. Nic se nestahuje ze sítě — jenom se
     vezmou karty, které na stránce už jsou, a ty nejbližší výběru se
     zopakují nahoře. Ostatní zůstávají, kde byly.
     ================================================================ */
  function rail() {
    var old = doc.getElementById("tds-rail");
    if (old && old.parentNode) old.parentNode.removeChild(old);
    if (!cfg || !chosen(cfg)) return;      // nic vybráno = nic navíc

    // jen titulní strana — jinde by proužek jen opakoval, co je pod ním
    var grid = doc.querySelector(".mainside .grid");
    if (!grid || !grid.parentNode) return;

    var best = [].slice.call(doc.querySelectorAll(".card[data-band]:not(.pick)"))
      .map(function (el, i) {
        var it = fromCard(el);
        return { it: it, i: i, s: score(it, cfg), m: bond(it, cfg) };
      })
      .filter(function (r) { return r.s !== null && r.m > 0; });
    if (!best.length) return;
    best.sort(function (a, b) { return (b.s - a.s) || (a.i - b.i); });
    best = best.slice(0, RAIL);

    var box = doc.createElement("section");
    box.className = "pickrail";
    box.id = "tds-rail";
    var head = doc.createElement("h2");
    head.className = "rowhead pickhead";
    head.textContent = T.picked || "";
    var row = doc.createElement("div");
    row.className = "grid tight";
    best.forEach(function (r) {
      var c = r.it.el.cloneNode(true);
      c.removeAttribute("id");
      c.classList.remove(OFF);
      calmOff(c);                       // kopie začíná načisto
      c.classList.add("pick");
      c.classList.add("small");
      if (cfg.tone === 1 && heavy(c)) calmOn(c);
      row.appendChild(c);
    });
    box.appendChild(head);
    box.appendChild(row);

    var note = doc.getElementById("reader-hidden-note");
    var anchor = (note && note.parentNode === grid.parentNode) ? note : grid;
    anchor.parentNode.insertBefore(box, anchor);
  }

  /* =================================================== stránka pro tebe
     Seznam všech článků je pro všechny stejný; co z něj vyleze nahoru,
     rozhodne prohlížeč sám. Když se seznam nestáhne, ukáže se prostě
     výzva k nastavení — rozbitá stránka není odpověď.
     ================================================================ */
  function wipe(el) {
    while (el && el.firstChild) el.removeChild(el.firstChild);
  }

  function shell(o, small) {
    var el = doc.createElement("div");
    el.className = "card" + (small ? " small" : "") + (o.i ? "" : " nopic");
    el.setAttribute("data-load", String(o.l || 0));
    el.setAttribute("data-band", o.b || "mid");
    el.setAttribute("data-topics", o.p || "");
    el.setAttribute("data-tags", o.g || "");
    el.setAttribute("data-date", o.dt || "");
    if (o.i) {
      var wrap = doc.createElement("a");
      wrap.href = o.u;
      var img = doc.createElement("img");
      img.src = o.i;
      img.alt = "";
      img.setAttribute("loading", "lazy");
      wrap.appendChild(img);
      el.appendChild(wrap);
    }
    var body = doc.createElement("div");
    body.className = "body";
    if (o.sl) {
      var k = doc.createElement("div");
      k.className = "kicker";
      k.textContent = o.sl;
      body.appendChild(k);
    }
    var h = doc.createElement("h3");
    var a = doc.createElement("a");
    a.href = o.u;
    a.textContent = o.t || "";
    h.appendChild(a);
    body.appendChild(h);
    if (!small && o.d) {
      var p = doc.createElement("p");
      p.textContent = o.d;
      body.appendChild(p);
    }
    el.appendChild(body);
    return el;
  }

  function fyShow(on) {
    var main = doc.getElementById("fy-main");
    var empty = doc.getElementById("fy-empty");
    if (!main || !empty) return;
    if (on) {
      main.removeAttribute("hidden");
      empty.setAttribute("hidden", "");
    } else {
      main.setAttribute("hidden", "");
      empty.removeAttribute("hidden");
    }
  }

  function byDate(a, b) {
    if (a.it.date === b.it.date) return a.i - b.i;
    return a.it.date < b.it.date ? 1 : -1;
  }

  function fyFill(data) {
    var pick = doc.getElementById("fy-picked");
    var side = doc.getElementById("fy-outside");
    if (!pick || !side) return;

    var set = now();
    var all = data.map(function (o, i) {
      var it = fromJson(o);
      return { it: it, i: i, s: score(it, set), m: bond(it, set) };
    }).filter(function (r) { return r.s !== null; });   // vypnutá témata pryč

    var mine = all.filter(function (r) { return r.m > 0; });
    mine.sort(function (a, b) { return (b.s - a.s) || byDate(a, b); });

    // Schválně: co je mimo vybraný okruh. Noviny, které by čtenáři jen
    // přitakávaly, jsou zrcadlo, ne noviny. Tenhle blok se nikdy neruší.
    var out = all.filter(function (r) { return r.m === 0; });
    out.sort(byDate);

    if (!mine.length) { fyShow(false); return; }

    wipe(pick);
    wipe(side);
    mine.slice(0, PICKED).forEach(function (r) { pick.appendChild(shell(r.it.raw, false)); });
    out.slice(0, OUTSIDE).forEach(function (r) { side.appendChild(shell(r.it.raw, true)); });

    var note = doc.getElementById("fy-health");
    if (note) {
      var care = set.tags.filter(function (x) { return x.indexOf("h_") === 0; }).length;
      if (care) note.removeAttribute("hidden"); else note.setAttribute("hidden", "");
    }

    fyShow(true);
    apply();      // i tady platí, kolik toho a jak natvrdo
  }

  function foryou() {
    if (!doc.getElementById("fy-main")) return;
    if (!cfg || !chosen(cfg) || !window.fetch) { fyShow(false); return; }
    window.fetch(base + "/" + lang + "/articles.json", { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok) throw new Error("http " + r.status);
        return r.json();
      })
      .then(function (data) {
        if (!isArr(data)) throw new Error("tvar");
        fyFill(data);
      })
      .catch(function () { fyShow(false); });
  }

  /* ====================================================== průvodce
     První návštěva: klidná nabídka, ne uvítací zeď. Dá se zavřít,
     přeskočit nebo prostě ignorovat a číst dál. Zavření uloží výchozí
     nastavení, takže se podruhé už neozve.
     ================================================================ */
  function swap(el, on) {
    if (!el) return;
    if (on) el.removeAttribute("hidden"); else el.setAttribute("hidden", "");
  }

  function at() {
    return parseInt(card && card.getAttribute("data-at"), 10) || 1;
  }

  function stepTo(n) {
    if (!card) return;
    var steps = [].slice.call(card.querySelectorAll(".ob-step"));
    var last = steps.length;
    if (!last) return;
    n = Math.max(1, Math.min(last, n));
    steps.forEach(function (s) {
      swap(s, parseInt(s.getAttribute("data-step"), 10) === n);
    });
    var cnt = card.querySelector(".ob-count");
    if (cnt) cnt.textContent = String(T.obStep || "").replace("%d", String(n));
    swap(card.querySelector(".ob-back"), n > 1);
    swap(card.querySelector(".ob-next"), n < last);
    swap(card.querySelector(".ob-done"), n === last);
    card.setAttribute("data-at", String(n));
  }

  /* v = null znamená přeskočeno: uloží se výchozí nastavení a stránka
     se čtenáři pod rukama nezmění */
  function done(v) {
    if (!card) return;
    var box = card;
    card = null;
    if (box.parentNode) box.parentNode.removeChild(box);
    cfg = v || copy(DEF);
    save(cfg);
    if (!v) return;
    shown = false;
    apply();
    rail();
    article();
    foryou();
  }

  function hello() {
    var tpl = doc.getElementById("tds-onboard");
    if (card || !tpl || !tpl.content || load()) return;
    var src = tpl.content.querySelector(".ob-card");
    if (!src) return;

    card = src.cloneNode(true);
    mount(card, "ob");
    ownWire(card);
    fill(card, DEF);
    doc.body.appendChild(card);
    stepTo(1);

    card.addEventListener("click", function (e) {
      var el = e.target;
      while (el && el !== card) {
        if (el.hasAttribute && el.hasAttribute("data-ob-skip")) { done(null); return; }
        if (el.classList) {
          if (el.classList.contains("ob-next")) { stepTo(at() + 1); return; }
          if (el.classList.contains("ob-back")) { stepTo(at() - 1); return; }
          if (el.classList.contains("ob-done")) { done(gather(card, DEF)); return; }
        }
        el = el.parentNode;
      }
    });
    card.addEventListener("input", function (e) {
      if (e.target && e.target.type === "range") step(e.target);
    });
    try { card.focus(); } catch (e) { /* nevadí */ }
  }

  /* ------------------------------------------------------------ start */
  function init() {
    base = (doc.body && doc.body.getAttribute("data-base")) || "";
    home = isHome();
    cfg = load();
    mount(doc.getElementById("reader-form"), "reader");
    ownWire(doc.getElementById("reader-form"));
    wire();
    apply();
    rail();
    article();
    brake();
    foryou();
    if (cfg === null) window.setTimeout(hello, WAIT);
  }

  // stránka „pro tebe“ si tímhle otevírá nastavení
  window.tdsOpenReader = function () { open(); };

  if (doc.readyState === "loading") {
    doc.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
