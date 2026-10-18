(function () {
  "use strict";
  var root = document.documentElement;

  /* Theme: system by default, explicit choice remembered per browser. */
  function readTheme() { try { return localStorage.getItem("theme"); } catch (e) { return null; } }
  function applyTheme(t) {
    if (t === "dark" || t === "light") { root.setAttribute("data-theme", t); }
    else if (t === "system") { root.removeAttribute("data-theme"); }
    var btn = document.getElementById("theme-toggle");
    if (btn) {
      var dark = root.getAttribute("data-theme") === "dark" ||
        (!root.getAttribute("data-theme") && window.matchMedia("(prefers-color-scheme: dark)").matches);
      btn.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
      btn.querySelector(".sun").hidden = !dark;
      btn.querySelector(".moon").hidden = dark;
    }
  }
  applyTheme(readTheme());
  var toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme") === "dark" ||
        (!root.getAttribute("data-theme") && window.matchMedia("(prefers-color-scheme: dark)").matches);
      var next = dark ? "light" : "dark";
      try { localStorage.setItem("theme", next); } catch (e) {}
      applyTheme(next);
    });
  }

  /* Mobile navigation */
  var menuBtn = document.getElementById("menu-btn");
  var navLinks = document.getElementById("nav-links");
  if (menuBtn && navLinks) {
    menuBtn.addEventListener("click", function () {
      var open = navLinks.classList.toggle("open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* Current page highlight */
  var here = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav-links a").forEach(function (a) {
    var target = a.getAttribute("href").split("/").pop() || "index.html";
    if (target === here) a.setAttribute("aria-current", "page");
  });

  /* Live GitHub stars on project cards (silent if the API is unreachable). */
  var starEls = document.querySelectorAll("[data-repo]");
  if (starEls.length && window.fetch) {
    fetch("https://api.github.com/users/Dimitrios-Kafetzis/repos?per_page=100", { headers: { Accept: "application/vnd.github+json" } })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
      .then(function (repos) {
        var byName = {};
        repos.forEach(function (r) { byName[r.name.toLowerCase()] = r.stargazers_count; });
        starEls.forEach(function (el) {
          var n = byName[el.getAttribute("data-repo").toLowerCase()];
          if (typeof n === "number") {
            el.querySelector(".n").textContent = n;
            el.hidden = false;
          }
        });
      })
      .catch(function () {});
  }

  /* Project filters */
  var filterBar = document.getElementById("filters");
  if (filterBar) {
    var cards = document.querySelectorAll("#project-grid .card");
    function setFilter(key) {
      filterBar.querySelectorAll("button").forEach(function (b) {
        b.setAttribute("aria-pressed", b.getAttribute("data-filter") === key ? "true" : "false");
      });
      cards.forEach(function (c) {
        c.hidden = !(key === "all" || c.getAttribute("data-cat") === key);
      });
    }
    filterBar.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-filter]");
      if (b) setFilter(b.getAttribute("data-filter"));
    });
    var initial = (location.hash || "").replace("#", "");
    if (initial && filterBar.querySelector('[data-filter="' + initial + '"]')) setFilter(initial);
    else setFilter("all");
  }

  /* Copy email */
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = btn.getAttribute("data-copy");
      var done = function () {
        if (btn.hasAttribute("data-copy-label")) { btn.classList.add("done"); btn.setAttribute("title", "Link copied"); setTimeout(function () { btn.classList.remove("done"); btn.setAttribute("title", "Copy link"); }, 1600); }
        else { btn.textContent = "Copied"; setTimeout(function () { btn.textContent = "Copy"; }, 1600); }
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { selectCode(btn); });
      } else { selectCode(btn); }
    });
  });
  function selectCode(btn) {
    var code = btn.parentElement.querySelector("code");
    if (!code) { try { window.prompt("Copy this link", btn.getAttribute("data-copy")); } catch (e) {} return; }
    var range = document.createRange(); range.selectNodeContents(code);
    var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
  }

  /* Footer year */
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();
})();
