/* Live desk: refreshes public headlines every five minutes.

   The browser downloads one generated JSON snapshot from the repository's
   dedicated live-feed branch. It sends no reader settings, cookies or profile;
   the selected desk only filters the already downloaded list locally. */
(function () {
  "use strict";

  var boxes = [].slice.call(document.querySelectorAll("[data-live-feed]"));
  var brief = document.querySelector("[data-live-briefing]");
  if ((!boxes.length && !brief) || !window.fetch) return;

  function csvText(box, name, fallback) {
    return box.getAttribute(name) || fallback || "";
  }

  function stamp(value) {
    var n = Date.parse(value || "");
    return isFinite(n) ? n : 0;
  }

  function ago(box, value) {
    var ms = stamp(value);
    if (!ms) return "";
    var mins = Math.max(0, Math.floor((Date.now() - ms) / 60000));
    if (mins < 1) return csvText(box, "data-ago-now", "just now");
    var attr = "data-ago-min", n = mins;
    if (mins >= 1440) { attr = "data-ago-day"; n = Math.floor(mins / 1440); }
    else if (mins >= 60) { attr = "data-ago-hour"; n = Math.floor(mins / 60); }
    return csvText(box, attr, "%d").replace("%d", n);
  }

  function exact(box, value) {
    var ms = stamp(value);
    if (!ms) return "";
    var d = new Date(ms), lang = csvText(box, "data-lang", "en");
    try {
      var date = new Intl.DateTimeFormat(lang === "cs" ? "cs-CZ" : "en-GB", {
        timeZone: "Europe/Prague", day: "numeric", month: lang === "cs" ? "numeric" : "short"
      }).format(d);
      var time = new Intl.DateTimeFormat(lang === "cs" ? "cs-CZ" : "en-GB", {
        timeZone: "Europe/Prague", hour: "2-digit", minute: "2-digit", hour12: false
      }).format(d);
      return date + " · " + time;
    } catch (e) { return d.toISOString().slice(5, 16).replace("T", " · "); }
  }

  function node(tag, cls, text) {
    var el = document.createElement(tag);
    if (cls) el.className = cls;
    if (text !== undefined && text !== null) el.textContent = text;
    return el;
  }

  function safeUrl(value) {
    return /^https?:\/\//i.test(String(value || "")) ? String(value) : "";
  }

  function fetchFeed(url) {
    if (!url) return Promise.resolve(null);
    var join = url.indexOf("?") >= 0 ? "&" : "?";
    return window.fetch(url + join + "v=" + Date.now(), {cache: "no-store", credentials: "omit"})
      .then(function (response) {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
      }).then(function (data) {
        if (!data || !Array.isArray(data.items) || !data.items.length || !stamp(data.generated_at)) {
          throw new Error("invalid feed");
        }
        return data;
      }).catch(function () { return null; });
  }

  function newestFeed(primaryUrl) {
    // The live-feed branch is normally freshest. A snapshot built into the
    // deployed site is an independent fallback when GitHub's scheduled jobs
    // are queued. Choose by actual generation time, never by request order.
    return Promise.all([fetchFeed(primaryUrl), fetchFeed("/live-news.json")])
      .then(function (feeds) {
        var valid = feeds.filter(function (feed) { return feed; });
        valid.sort(function (a, b) { return stamp(b.generated_at) - stamp(a.generated_at); });
        if (!valid.length) throw new Error("no valid feed");
        return valid[0];
      });
  }

  function makeItem(box, item) {
    var li = node("li", (parseInt(item.score, 10) || 0) >= 70 ? "hot" : "");
    li.setAttribute("data-section", item.section || "world");

    var when = node("div", "ticker-when");
    var time = node("time", "", exact(box, item.published_at));
    time.setAttribute("datetime", item.published_at || "");
    when.appendChild(time);
    when.appendChild(node("span", "", ago(box, item.published_at)));
    if (Date.now() - stamp(item.published_at) < 3600000) {
      when.appendChild(node("b", "ticker-new", csvText(box, "data-new-label", "New")));
    }
    li.appendChild(when);

    var link = node("a", "", item.headline || "");
    link.href = safeUrl(item.url) || "#";
    link.target = "_blank";
    link.rel = "nofollow noopener";
    li.appendChild(link);

    var source = item.source || "";
    var count = parseInt(item.sources_count, 10) || 1;
    if (count > 1) source += " · " + count + " " + csvText(box, "data-sources-word", "sources");
    li.appendChild(node("em", "", source));
    return li;
  }

  function countryData(item) {
    var data = item && item.countries && typeof item.countries === "object" ? item.countries : {};
    return {
      direct: Array.isArray(data.direct) ? data.direct.filter(function (c) {
        return /^[a-z]{2}$/i.test(String(c || ""));
      }).map(function (c) { return String(c).toLowerCase(); }) : [],
      scope: data.scope === "eu" || data.scope === "global" ? data.scope : "none"
    };
  }

  function makeBriefItem(box, item) {
    var reach = countryData(item);
    var li = node("li", "brief-item");
    li.setAttribute("data-countries", reach.direct.join(","));
    li.setAttribute("data-reach", reach.scope);
    li.setAttribute("data-section", item.section || "world");

    var when = node("div", "brief-time");
    var time = node("time", "", ago(box, item.published_at));
    time.setAttribute("datetime", item.published_at || "");
    when.appendChild(time);
    if (item.section) when.appendChild(node("span", "", item.section));
    li.appendChild(when);

    var copy = node("div", "brief-copy");
    var mark = node("span", "brief-country-mark", csvText(box, "data-country-label", "Your country"));
    mark.hidden = true;
    copy.appendChild(mark);
    var heading = node("h3");
    var link = node("a", "", item.headline || "");
    link.href = safeUrl(item.url) || "#";
    link.target = "_blank";
    link.rel = "nofollow noopener";
    heading.appendChild(link);
    copy.appendChild(heading);
    if (item.summary) copy.appendChild(node("p", "", item.summary));
    var source = item.source || "";
    var count = parseInt(item.sources_count, 10) || 1;
    if (count > 1) source += " · " + count + " " + csvText(box, "data-sources-word", "sources");
    copy.appendChild(node("p", "brief-provenance", source));
    li.appendChild(copy);
    return li;
  }

  function briefShow(box, data) {
    var world = box.querySelector("[data-live-brief-world]");
    var home = box.querySelector("[data-live-brief-home]");
    if (!world || !home) return;
    var valid = data.items.filter(function (item) {
      return item && item.headline && safeUrl(item.url) && stamp(item.published_at);
    }).sort(function (a, b) { return stamp(b.published_at) - stamp(a.published_at); });
    var worldLimit = parseInt(box.getAttribute("data-brief-world-limit"), 10) || 8;
    var localLimit = parseInt(box.getAttribute("data-brief-local-limit"), 10) || 6;
    var select = box.querySelector("#brief-country");
    var selected = select ? String(select.value || "").toLowerCase() : "";
    var option = select && select.selectedIndex >= 0 ? select.options[select.selectedIndex] : null;
    var selectedEu = !!(option && option.getAttribute("data-eu") === "1");
    while (world.firstChild) world.removeChild(world.firstChild);
    while (home.firstChild) home.removeChild(home.firstChild);
    valid.slice(0, worldLimit).forEach(function (item) { world.appendChild(makeBriefItem(box, item)); });
    valid.filter(function (item) {
      var reach = countryData(item);
      if (!selected) return false;
      return reach.direct.indexOf(selected) >= 0 || (selectedEu && reach.scope === "eu");
    })
      .slice(0, localLimit).forEach(function (item) { home.appendChild(makeBriefItem(box, item)); });
    var loading = box.querySelector("[data-live-brief-loading]");
    if (loading) loading.hidden = valid.length > 0;
    if (typeof window.tdsRefreshBriefing === "function") window.tdsRefreshBriefing();
  }

  function loadBrief(box) {
    var url = box.getAttribute("data-live-url");
    if (!url) return;
    newestFeed(url).then(function (data) {
        box.tdsBriefData = data;
        briefShow(box, data);
        health(box, data.generated_at);
      }).catch(function () {
        var loading = box.querySelector("[data-live-brief-loading]");
        if (loading && !box.querySelector("[data-live-brief-world] .brief-item")) {
          loading.hidden = false;
          loading.textContent = csvText(box, "data-empty-label", "No verified headline yet.");
        }
      });
  }

  function health(box, generated) {
    var ms = stamp(generated), el = box.querySelector("[data-live-health]");
    var updated = box.querySelector("[data-live-updated]");
    if (!ms) return;
    var delayed = Date.now() - ms > 15 * 60000;
    if (el) {
      el.textContent = delayed ? csvText(box, "data-stale-label", "Feed delayed") : ago(box, generated);
      el.classList.toggle("stale", delayed);
      el.setAttribute("title", csvText(box, "data-updated-label", "Feed checked") + " " + exact(box, generated));
    }
    if (updated) {
      updated.textContent = csvText(box, "data-updated-label", "Feed checked") + ": " +
        exact(box, generated) + " (" + ago(box, generated) + ").";
      updated.setAttribute("data-generated", generated);
    }
  }

  function show(box) {
    var list = box.querySelector("[data-live-list]");
    if (!list || !box.tdsItems) return;
    var selected = box.tdsFilter || "";
    var max = parseInt(box.getAttribute("data-live-limit"), 10) || 14;
    var items = box.tdsItems.filter(function (item) {
      return !selected || item.section === selected;
    }).slice(0, max);
    if (!items.length && selected) {
      selected = "";
      box.tdsFilter = "";
      items = box.tdsItems.slice(0, max);
    }
    while (list.firstChild) list.removeChild(list.firstChild);
    if (items.length) items.forEach(function (item) { list.appendChild(makeItem(box, item)); });
    else list.appendChild(node("li", "ticker-loading", csvText(box, "data-empty-label", "No verified headline yet.")));
    [].forEach.call(box.querySelectorAll("[data-live-filter]"), function (button) {
      button.setAttribute("aria-pressed", button.getAttribute("data-live-filter") === selected ? "true" : "false");
    });
  }

  function refreshAges(box) {
    [].forEach.call(box.querySelectorAll(".ticker-when time[datetime]"), function (time) {
      var age = time.parentNode && time.parentNode.querySelector("span");
      if (age) age.textContent = ago(box, time.getAttribute("datetime"));
    });
    var updated = box.querySelector("[data-live-updated]");
    if (updated) health(box, updated.getAttribute("data-generated"));
  }

  function load(box) {
    var url = box.getAttribute("data-live-url");
    if (!url) return;
    newestFeed(url).then(function (data) {
        box.tdsItems = data.items.filter(function (item) {
          return item && item.headline && safeUrl(item.url) && stamp(item.published_at);
        }).sort(function (a, b) { return stamp(b.published_at) - stamp(a.published_at); });
        health(box, data.generated_at);
        show(box);
      }).catch(function () {
        var el = box.querySelector("[data-live-health]");
        if (el && !el.textContent) {
          el.textContent = csvText(box, "data-stale-label", "Feed delayed");
          el.classList.add("stale");
        }
      });
  }

  boxes.forEach(function (box) {
    box.tdsFilter = box.getAttribute("data-default-section") || "";
    box.addEventListener("click", function (event) {
      var button = event.target;
      while (button && button !== box && !(button.hasAttribute && button.hasAttribute("data-live-filter"))) {
        button = button.parentNode;
      }
      if (!button || button === box) return;
      box.tdsFilter = button.getAttribute("data-live-filter") || "";
      show(box);
    });
    load(box);
    window.setInterval(function () { load(box); }, 300000);
    window.setInterval(function () { refreshAges(box); }, 60000);
  });

  if (brief) {
    brief.addEventListener("change", function (event) {
      if (event.target && event.target.id === "brief-country" && brief.tdsBriefData) {
        briefShow(brief, brief.tdsBriefData);
      }
    });
    loadBrief(brief);
    window.setInterval(function () { loadBrief(brief); }, 300000);
    window.setInterval(function () {
      [].forEach.call(brief.querySelectorAll(".brief-time time[datetime]"), function (time) {
        time.textContent = ago(brief, time.getAttribute("datetime"));
      });
    }, 60000);
  }
})();
