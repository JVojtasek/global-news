(function () {
  "use strict";
  var doc = document;
  var form = doc.getElementById("daily-quiz");
  var source = doc.getElementById("quiz-data");
  if (!form || !source) return;

  var config;
  try { config = JSON.parse(source.textContent || "{}"); } catch (e) { return; }
  var quiz = config.quiz || {};
  var labels = config.labels || {};
  var questions = quiz.questions || [];
  var progressLabel = doc.getElementById("quiz-progress-label");
  var progressBar = doc.getElementById("quiz-progress-bar");
  var error = doc.getElementById("quiz-form-error");
  var result = doc.getElementById("quiz-personal-result");

  function answered() {
    return questions.filter(function (question) {
      return !!form.querySelector('input[name="' + question.id + '"]:checked');
    }).length;
  }

  function progress() {
    var count = answered();
    if (progressLabel) progressLabel.textContent = count + " / " + questions.length;
    if (progressBar) progressBar.style.width = (questions.length ? count / questions.length * 100 : 0) + "%";
    if (error && count === questions.length) error.hidden = true;
  }

  function selection(question) {
    var chosen = form.querySelector('input[name="' + question.id + '"]:checked');
    if (!chosen) return null;
    return question.options[parseInt(chosen.value, 10)] || null;
  }

  function setInsight(id, heading, text) {
    var box = doc.getElementById(id);
    if (!box) return;
    box.hidden = !heading && !text;
    var h = box.querySelector("h3");
    var p = box.querySelector("p");
    if (h) h.textContent = heading || "";
    if (p) p.textContent = text || "";
  }

  function assessment() {
    var total = 0;
    var dimensionScores = {};
    var dimensionMax = {};
    questions.forEach(function (question) {
      var option = selection(question);
      var score = option ? Number(option.score || 0) : 0;
      total += score;
      dimensionScores[question.dimension] = (dimensionScores[question.dimension] || 0) + score;
      var maximum = Math.max.apply(null, question.options.map(function (row) { return Number(row.score || 0); }));
      dimensionMax[question.dimension] = (dimensionMax[question.dimension] || 0) + maximum;
    });
    var outcome = (quiz.outcomes || []).filter(function (row) { return total >= row.min && total <= row.max; })[0] || {};
    var ranked = (quiz.dimensions || []).map(function (dim) {
      var max = dimensionMax[dim.id] || 1;
      return {dim: dim, ratio: (dimensionScores[dim.id] || 0) / max};
    }).sort(function (a, b) { return b.ratio - a.ratio; });
    return {
      score: labels.score ? labels.score.replace("{score}", total) : String(total),
      title: outcome.title || "", summary: outcome.summary || "",
      strength: ranked.length ? {title: ranked[0].dim.label, text: ranked[0].dim.why} : null,
      next: ranked.length ? {title: ranked[ranked.length - 1].dim.label, text: ranked[ranked.length - 1].dim.action} : null
    };
  }

  function profile() {
    var scores = {};
    (quiz.dimensions || []).forEach(function (dim) { scores[dim.id] = 0; });
    questions.forEach(function (question) {
      var option = selection(question);
      Object.keys((option && option.scores) || {}).forEach(function (key) {
        scores[key] = (scores[key] || 0) + Number(option.scores[key] || 0);
      });
    });
    var ranked = Object.keys(scores).sort(function (a, b) { return scores[b] - scores[a]; });
    var key = ranked[0];
    var outcome = (quiz.outcomes || {})[key] || {};
    var dim = (quiz.dimensions || []).filter(function (row) { return row.id === key; })[0] || {};
    return {
      score: labels.profile || "",
      title: outcome.title || dim.label || "", summary: outcome.summary || "",
      strength: {title: dim.label || outcome.title || "", text: outcome.strength || ""},
      next: {title: labels.next_title || "", text: outcome.action || ""},
      watch: {title: labels.watch_title || "", text: outcome.watch || ""}
    };
  }

  function knowledge() {
    var total = 0;
    questions.forEach(function (question) {
      var option = selection(question);
      if (option && option.correct === true) total += 1;
    });
    var outcome = (quiz.outcomes || []).filter(function (row) { return total >= row.min && total <= row.max; })[0] || {};
    return {
      score: labels.correct ? labels.correct.replace("{score}", total).replace("{total}", questions.length) : total + " / " + questions.length,
      title: outcome.title || "", summary: outcome.summary || ""
    };
  }

  function show(data) {
    var score = doc.getElementById("quiz-score");
    var title = doc.getElementById("quiz-result-title");
    var summary = doc.getElementById("quiz-result-summary");
    if (score) score.textContent = data.score || "";
    if (title) title.textContent = data.title || "";
    if (summary) summary.textContent = data.summary || "";
    setInsight("quiz-strength", data.strength && data.strength.title, data.strength && data.strength.text);
    setInsight("quiz-next", data.next && data.next.title, data.next && data.next.text);
    setInsight("quiz-watch", data.watch && data.watch.title, data.watch && data.watch.text);
    result.hidden = false;
    try { localStorage.setItem("mypaper-quiz-" + quiz.slug, "completed"); } catch (e) {}
    try { result.focus({preventScroll: true}); } catch (e) { result.focus(); }
    result.scrollIntoView({behavior: "smooth", block: "start"});
    if (typeof window.plausible === "function") {
      window.plausible("Quiz completed", {props: {slug: quiz.slug || "", category: quiz.category || ""}});
    }
  }

  form.addEventListener("change", progress);
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (answered() !== questions.length) {
      if (error) error.hidden = false;
      var missing = null;
      questions.some(function (question) {
        if (form.querySelector('input[name="' + question.id + '"]:checked')) return false;
        missing = form.querySelector('[data-question="' + question.id + '"]');
        return true;
      });
      if (missing) missing.scrollIntoView({behavior: "smooth", block: "center"});
      return;
    }
    var data = quiz.mode === "profile" ? profile() : (quiz.mode === "knowledge" ? knowledge() : assessment());
    show(data);
  });

  var reset = doc.getElementById("quiz-reset");
  if (reset) reset.addEventListener("click", function () {
    form.reset();
    result.hidden = true;
    progress();
    form.scrollIntoView({behavior: "smooth", block: "start"});
  });
  progress();
})();
