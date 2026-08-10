/**
 * Client-side course progress tracker.
 *
 * There is no backend for this site, so "completed" state lives only in
 * this browser's localStorage -- it is NOT the same thing as PROGRESS.md
 * (which the AI maintains based on your actual exercise reviews). This is
 * just a personal, casual "did I get through this module" checkbox for
 * visiting the site, per-device/per-browser, cleared if you clear site data.
 */
(function () {
  "use strict";

  var STORAGE_KEY = "questlog-course-progress";

  // Canonical module list -- keep in sync with the 16 module folders.
  var MODULES = [
    { slug: "module-00-developer-environment-and-tooling", title: "00 — Developer Environment & Tooling" },
    { slug: "module-01-python-properly", title: "01 — Python, Properly" },
    { slug: "module-02-internet-and-web-fundamentals", title: "02 — Internet & Web Fundamentals" },
    { slug: "module-03-html-css-javascript", title: "03 — HTML, CSS & JavaScript" },
    { slug: "module-04-react", title: "04 — React" },
    { slug: "module-05-backend-fastapi", title: "05 — Backend with FastAPI" },
    { slug: "module-06-databases", title: "06 — Databases" },
    { slug: "module-07-auth-security", title: "07 — Auth, Security & API Best Practices" },
    { slug: "module-08-testing-and-quality", title: "08 — Testing & Software Quality" },
    { slug: "module-09-linux-networking-servers", title: "09 — Linux, Networking & Servers" },
    { slug: "module-10-docker-and-containers", title: "10 — Docker & Containers" },
    { slug: "module-11-cicd-cloud-production", title: "11 — CI/CD, Cloud & Production Operations" },
    { slug: "module-12-ai-ml-foundations", title: "12 — AI/ML Foundations" },
    { slug: "module-13-building-with-llm-apis", title: "13 — Building with LLM APIs" },
    { slug: "module-14-rag", title: "14 — RAG" },
    { slug: "module-15-agents-and-modern-ai-workflows", title: "15 — Agents & Modern AI Workflows" }
  ];

  function loadState() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch (e) {
      return {};
    }
  }

  function saveState(state) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      /* localStorage unavailable (private mode, etc.) -- fail silently */
    }
  }

  function completedCount(state) {
    var n = 0;
    for (var i = 0; i < MODULES.length; i++) {
      if (state[MODULES[i].slug]) n++;
    }
    return n;
  }

  // Which module (if any) does the CURRENT page belong to, and is it
  // specifically that module's own overview page (not a lesson/exercise
  // page within it)? Matches regardless of the site's base path
  // ("/Course/..." on GitHub Pages, "/..." when served locally).
  function currentModuleInfo() {
    var path = window.location.pathname;
    var m = path.match(/module-(\d{2})-([a-z0-9-]+)\/?/);
    if (!m) return null;
    var slug = "module-" + m[1] + "-" + m[2];
    var module = null;
    for (var i = 0; i < MODULES.length; i++) {
      if (MODULES[i].slug === slug) { module = MODULES[i]; break; }
    }
    if (!module) return null;
    // Is this the module's OWN index page (README), i.e. nothing after the
    // slug except an optional trailing slash / "index.html"?
    var rest = path.slice(path.indexOf(slug) + slug.length);
    var isOverviewPage = rest === "" || rest === "/" || rest === "/index.html";
    return { module: module, isOverviewPage: isOverviewPage };
  }

  function renderBar() {
    var fill = document.getElementById("course-progress-bar__fill");
    var label = document.getElementById("course-progress-bar__label");
    if (!fill || !label) return;

    var state = loadState();
    var done = completedCount(state);
    var total = MODULES.length;
    var pct = total ? Math.round((done / total) * 100) : 0;

    fill.style.width = pct + "%";
    label.textContent = done + " / " + total + " modules complete — " + pct + "%";
  }

  function renderModuleToggle() {
    // Remove any toggle left over from a previous page (instant nav swaps
    // page content but this script's DOM insertions aren't auto-cleaned).
    var existing = document.getElementById("course-progress-toggle");
    if (existing) existing.remove();

    var info = currentModuleInfo();
    if (!info || !info.isOverviewPage) return;

    var content = document.querySelector(".md-content__inner");
    if (!content) return;

    var state = loadState();
    var isDone = !!state[info.module.slug];

    var wrapper = document.createElement("div");
    wrapper.id = "course-progress-toggle";
    wrapper.className = "course-progress-toggle" + (isDone ? " is-complete" : "");

    var button = document.createElement("button");
    button.type = "button";
    button.textContent = isDone
      ? "✓ Module " + info.module.title.split(" ")[0] + " marked complete"
      : "Mark Module " + info.module.title.split(" ")[0] + " as complete";
    button.addEventListener("click", function () {
      var s = loadState();
      s[info.module.slug] = !s[info.module.slug];
      saveState(s);
      renderBar();
      renderModuleToggle();
    });

    wrapper.appendChild(button);
    content.insertBefore(wrapper, content.firstChild);
  }

  function init() {
    renderBar();
    renderModuleToggle();
  }

  // document$ is Material's own RxJS observable that fires on every page
  // load AND every instant-navigation transition (since instant nav swaps
  // content via fetch() rather than a real page load, plain
  // DOMContentLoaded would only ever fire once). This is Material's own
  // documented hook for exactly this situation.
  if (window.document$) {
    window.document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
