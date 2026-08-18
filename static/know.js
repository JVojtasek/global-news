/* =====================================================================
   Poznej se — nástroje, které o tobě zjistí něco pravdivého
   -----------------------------------------------------------------
   Všechno běží tady v prohlížeči. Žádná odpověď, žádný výsledek a žádný
   čas nikam neodchází — není kam, web je statický a nemá server, který
   by to přijal. To není slib, to je vlastnost stavby (EDITORIAL-CODE,
   oddíl 5).

   Proto tu taky není žádné IQ. Skutečné testy inteligence se dělají pod
   dohledem, na normovaném vzorku a jsou chráněné. Číslo, které by ti
   vypsala webová stránka, by bylo vymyšlené — a vymyšlené číslo je
   přesně to, čím se tyhle noviny nechtějí zabývat.
   ===================================================================== */
(function () {
  "use strict";
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => [...(r || document).querySelectorAll(s)];
  const T = (window.KNOW_STRINGS || {});
  const t = (k, fallback) => T[k] || fallback || k;

  /* ---------------------------------------------------------------
     1) ROZSAH ČÍSELNÉ ŘADY
     Klasická úloha z klinické psychologie: kolik číslic udržíš
     v hlavě naráz. Měří pracovní paměť — tu tabuli, na kterou si
     mozek píše, co zrovna používá.
     --------------------------------------------------------------- */
  const span = {
    delka: 3, chyby: 0, nejlepsi: 0, radek: [], bezi: false,

    start(el) {
      this.delka = 3; this.chyby = 0; this.nejlepsi = 0; this.bezi = true;
      this.el = el; this.dalsi();
    },

    async dalsi() {
      const box = $(".k-span-stage", this.el);
      const vstup = $(".k-span-input", this.el);
      const info = $(".k-span-info", this.el);
      vstup.hidden = true; vstup.value = "";
      this.radek = Array.from({ length: this.delka },
                              () => Math.floor(Math.random() * 10));
      info.textContent = t("span_watch", "Sleduj.");
      /* Číslice po jedné, ať se nedají přečíst jako celek — jinak by
         to neměřilo paměť, ale rychlost čtení. */
      for (const c of this.radek) {
        box.textContent = c;
        box.classList.add("on");
        await pauza(800);
        box.textContent = "";
        box.classList.remove("on");
        await pauza(250);
      }
      box.textContent = "?";
      info.textContent = t("span_type", "Napiš je v pořadí, bez mezer.");
      vstup.hidden = false; vstup.focus();
    },

    odpoved() {
      if (!this.bezi) return;
      const vstup = $(".k-span-input", this.el);
      const zadano = (vstup.value || "").replace(/\D/g, "");
      const spravne = zadano === this.radek.join("");
      if (spravne) {
        this.nejlepsi = this.delka;
        this.chyby = 0;
        this.delka += 1;
        if (this.delka > 12) return this.konec();
        this.dalsi();
      } else {
        this.chyby += 1;
        /* Dva pokusy na délku. Jedno uklouznutí není hranice paměti. */
        if (this.chyby >= 2) return this.konec();
        $(".k-span-info", this.el).textContent =
          t("span_again", "Ne úplně. Ještě jednou stejná délka.");
        setTimeout(() => this.dalsi(), 900);
      }
    },

    konec() {
      this.bezi = false;
      $(".k-span-stage", this.el).textContent = String(this.nejlepsi);
      $(".k-span-input", this.el).hidden = true;
      $(".k-span-info", this.el).textContent = "";
      const v = $(".k-span-result", this.el);
      v.hidden = false;
      v.innerHTML = `<p><b>${t("span_span", "Tvůj rozsah")}: ${this.nejlepsi}</b></p>` +
        `<p>${t("span_note", "")}</p>`;
      $(".k-span-start", this.el).textContent = t("again", "Zkusit znovu");
      $(".k-span-start", this.el).hidden = false;
    },
  };
  const pauza = ms => new Promise(r => setTimeout(r, ms));

  /* ---------------------------------------------------------------
     2) ZKRESLENÍ
     Tady se nic neměří a nic se nehodnotí. Odpovíš, a pak se dozvíš,
     co v tom pokusu vyšlo lidem před tebou a proč. Smysl není zjistit,
     jak jsi na tom — smysl je vidět tu chybu zevnitř, na sobě.
     --------------------------------------------------------------- */
  function biasInit(root) {
    $$(".k-bias-item", root).forEach(item => {
      $$("button.k-opt", item).forEach(btn => {
        btn.addEventListener("click", () => {
          if (item.dataset.done) return;
          item.dataset.done = "1";
          $$("button.k-opt", item).forEach(b => {
            b.disabled = true;
            if (b === btn) b.classList.add("picked");
          });
          const rozbor = $(".k-bias-reveal", item);
          rozbor.hidden = false;
          rozbor.scrollIntoView({ behavior: "smooth", block: "nearest" });
        });
      });
      const form = $(".k-bias-number", item);
      if (form) {
        form.addEventListener("submit", e => {
          e.preventDefault();
          if (item.dataset.done) return;
          item.dataset.done = "1";
          const cislo = $("input", form).value.trim();
          $("input", form).disabled = true;
          $("button", form).disabled = true;
          const rozbor = $(".k-bias-reveal", item);
          const misto = $(".k-your-answer", rozbor);
          if (misto && cislo) misto.textContent = cislo;
          rozbor.hidden = false;
          rozbor.scrollIntoView({ behavior: "smooth", block: "nearest" });
        });
      }
    });
  }

  /* Kotva se losuje. Kdo dostane vysokou, hádá výš — a v rozboru se
     dozví, že to není náhoda a že mu ji vybral los. */
  function kotva(root) {
    const el = $(".k-anchor", root);
    if (!el) return;
    const vysoka = Math.random() < 0.5;
    const cislo = vysoka ? el.dataset.high : el.dataset.low;
    $$(".k-anchor-value", root).forEach(s => (s.textContent = cislo));
    const zprava = $(".k-anchor-which", root);
    if (zprava) {
      zprava.textContent = vysoka ? t("anchor_high", "") : t("anchor_low", "");
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    const spanEl = $(".k-span");
    if (spanEl) {
      $(".k-span-start", spanEl).addEventListener("click", () => {
        $(".k-span-start", spanEl).hidden = true;
        $(".k-span-result", spanEl).hidden = true;
        span.start(spanEl);
      });
      $(".k-span-form", spanEl).addEventListener("submit", e => {
        e.preventDefault(); span.odpoved();
      });
    }
    const biasEl = $(".k-bias");
    if (biasEl) { kotva(biasEl); biasInit(biasEl); }
  });
})();
