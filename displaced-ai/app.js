/* Displaced AI — a tiny static site engine.
 * All content comes from content/site.json and the Markdown files it points to.
 * Pages are chosen by the URL hash: #home, #articles, #videos, #links, #about, #read-<slug>
 */
(function () {
  "use strict";

  var main = document.getElementById("main");
  var data = null;
  var cache = {};

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function fmtDate(iso) {
    if (!iso) return "";
    var d = new Date(iso + "T12:00:00");
    if (isNaN(d)) return esc(iso);
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
  }

  function host(url) {
    try { return new URL(url).hostname.replace(/^www\./, ""); } catch (e) { return ""; }
  }

  function md(text) {
    if (window.marked && window.marked.parse) return window.marked.parse(text);
    return "<pre>" + esc(text) + "</pre>";
  }

  function getText(path) {
    if (cache[path]) return Promise.resolve(cache[path]);
    return fetch(path).then(function (r) {
      if (!r.ok) throw new Error(path + " returned " + r.status);
      return r.text();
    }).then(function (t) { cache[path] = t; return t; });
  }

  function sortedArticles() {
    return (data.articles || []).slice().sort(function (a, b) {
      return String(b.date).localeCompare(String(a.date));
    });
  }

  function sortedVideos() {
    return (data.videos || []).slice().sort(function (a, b) {
      return String(b.date || "").localeCompare(String(a.date || ""));
    });
  }

  /* ---------- pieces ---------- */

  function articleItem(a) {
    var tags = (a.tags || []).map(function (t) { return '<span class="tag">' + esc(t) + "</span>"; }).join("");
    return '<li class="article-item"><a href="#read-' + esc(a.slug) + '">' +
      '<div class="meta">' + fmtDate(a.date) + "</div>" +
      "<div><h3>" + esc(a.title) + "</h3>" +
      (a.summary ? "<p>" + esc(a.summary) + "</p>" : "") +
      (tags ? '<div class="tags">' + tags + "</div>" : "") +
      "</div></a></li>";
  }

  function youtubeId(v) {
    var s = v.youtube || "";
    var m = s.match(/(?:youtu\.be\/|v=|embed\/|shorts\/)([\w-]{11})/);
    return m ? m[1] : (/^[\w-]{11}$/.test(s) ? s : "");
  }

  function vimeoId(v) {
    var m = String(v.vimeo || "").match(/(\d{6,})/);
    return m ? m[1] : "";
  }

  function videoSource(v) {
    var id = youtubeId(v);
    if (id) return { kind: "iframe", src: "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0", watch: "https://www.youtube.com/watch?v=" + id, label: "YouTube" };
    id = vimeoId(v);
    if (id) return { kind: "iframe", src: "https://player.vimeo.com/video/" + id + "?autoplay=1", watch: "https://vimeo.com/" + id, label: "Vimeo" };
    if (v.file) return { kind: "file", src: v.file, watch: v.file, label: "Video file" };
    return null;
  }

  function videoCard(v, i) {
    var src = videoSource(v);
    var player;
    if (!src) {
      player = '<div class="player-empty">Add a YouTube link, Vimeo link or video file for this entry in content/site.json</div>';
    } else if (src.kind === "file") {
      player = '<video controls preload="metadata" src="' + esc(src.src) + '"' + (v.poster ? ' poster="' + esc(v.poster) + '"' : "") + "></video>";
    } else {
      player = '<button class="play" type="button" data-video="' + i + '" aria-label="Play ' + esc(v.title) + '">' +
        '<span class="play-dot"></span></button>' +
        '<span class="player-note">' + esc(src.label) + (v.duration ? " · " + esc(v.duration) : "") + "</span>";
    }
    return '<article class="video-card">' +
      '<div class="player" id="player-' + i + '">' + player + "</div>" +
      '<div class="meta">' + (v.date ? "<span>" + fmtDate(v.date) + "</span>" : "") +
      (src && src.kind === "iframe" ? '<a href="' + esc(src.watch) + '" target="_blank" rel="noopener">Watch on ' + esc(src.label) + "</a>" : "") +
      (v.example ? '<span class="badge">Example entry</span>' : "") + "</div>" +
      "<h3>" + esc(v.title) + "</h3>" +
      (v.description ? "<p>" + esc(v.description) + "</p>" : "") +
      "</article>";
  }

  function linkGroups(links) {
    var groups = {};
    var order = [];
    (links || []).forEach(function (l) {
      var g = l.group || "Links";
      if (!groups[g]) { groups[g] = []; order.push(g); }
      groups[g].push(l);
    });
    if (!order.length) return '<p class="empty">No links yet.</p>';
    return '<div class="link-groups">' + order.map(function (g) {
      return '<section class="link-group"><h3>' + esc(g) + "</h3><ul>" + groups[g].map(function (l) {
        return '<li><a href="' + esc(l.url) + '" target="_blank" rel="noopener"><strong>' + esc(l.title) + "</strong>" +
          (l.note ? "<span>" + esc(l.note) + "</span>" : "") +
          '<span class="host">' + esc(host(l.url)) + "</span></a></li>";
      }).join("") + "</ul></section>";
    }).join("") + "</div>";
  }

  function sectionHead(title, moreHash, moreLabel) {
    return '<div class="section-head"><h2>' + esc(title) + "</h2>" +
      (moreHash ? '<a href="#' + moreHash + '">' + esc(moreLabel) + "</a>" : "") + "</div>";
  }

  /* ---------- pages ---------- */

  function pageHome() {
    var s = data.site || {};
    var arts = sortedArticles().slice(0, 4);
    var vids = sortedVideos().slice(0, 2);
    var links = (data.links || []).slice(0, 6);
    return '<section class="hero">' +
      '<p class="eyebrow">' + esc(s.kicker || "A project") + "</p>" +
      "<h1>" + (s.headline || esc(s.title)) + "</h1>" +
      '<p class="lede">' + esc(s.tagline || "") + "</p>" +
      '<div class="hero-actions"><a class="btn btn-primary" href="#articles">Read the articles</a><a class="btn" href="#videos">Watch the videos</a></div>' +
      "</section>" +
      '<section class="section">' + sectionHead("Latest articles", "articles", "All articles →") +
      (arts.length ? '<ul class="article-list">' + arts.map(articleItem).join("") + "</ul>" : '<p class="empty">No articles yet.</p>') + "</section>" +
      '<section class="section">' + sectionHead("Video", "videos", "All video →") +
      (vids.length ? '<div class="video-grid">' + vids.map(function (v) { return videoCard(v, data.videos.indexOf(v)); }).join("") + "</div>" : '<p class="empty">No videos yet.</p>') + "</section>" +
      '<section class="section">' + sectionHead("Further reading", "links", "All links →") + linkGroups(links) + "</section>";
  }

  function pageArticles() {
    var arts = sortedArticles();
    return '<section class="section">' + sectionHead("Articles") +
      (arts.length ? '<ul class="article-list">' + arts.map(articleItem).join("") + "</ul>" : '<p class="empty">No articles yet.</p>') + "</section>";
  }

  function pageVideos() {
    var vids = sortedVideos();
    return '<section class="section">' + sectionHead("Video") +
      (vids.length ? '<div class="video-grid">' + vids.map(function (v) { return videoCard(v, data.videos.indexOf(v)); }).join("") + "</div>" : '<p class="empty">No videos yet.</p>') + "</section>";
  }

  function pageLinks() {
    return '<section class="section">' + sectionHead("Links") + linkGroups(data.links) + "</section>";
  }

  function pageDoc(opts) {
    main.innerHTML = '<article class="reader"><header>' +
      (opts.back ? '<a class="back" href="#articles">← All articles</a>' : "") +
      "<h1>" + esc(opts.title) + "</h1>" +
      (opts.meta ? '<p class="meta">' + opts.meta + "</p>" : "") +
      '</header><div class="prose"><p class="loading">Loading…</p></div></article>';
    var prose = main.querySelector(".prose");
    getText(opts.file).then(function (t) {
      prose.innerHTML = md(t);
      prose.querySelectorAll("a[href^='http']").forEach(function (a) { a.target = "_blank"; a.rel = "noopener"; });
    }).catch(function (e) {
      prose.innerHTML = '<p class="empty">This page could not be loaded (' + esc(e.message) + "). Check that the file path in content/site.json is correct.</p>";
    });
  }

  /* ---------- router ---------- */

  function setNav(name) {
    document.querySelectorAll("[data-nav]").forEach(function (a) {
      if (a.getAttribute("data-nav") === name) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
    });
  }

  function route() {
    var h = (location.hash || "#home").slice(1);
    var siteTitle = (data.site && data.site.title) || "Displaced AI";
    var nav = h, title = siteTitle;

    if (h.indexOf("read-") === 0) {
      var slug = h.slice(5);
      var a = (data.articles || []).filter(function (x) { return x.slug === slug; })[0];
      nav = "articles";
      if (a) {
        title = a.title + " · " + siteTitle;
        pageDoc({ title: a.title, file: a.file, back: true, meta: fmtDate(a.date) + (a.author ? " · " + esc(a.author) : "") });
      } else {
        main.innerHTML = '<p class="empty">That article was not found. <a href="#articles">See all articles</a>.</p>';
      }
    } else if (h === "articles") { main.innerHTML = pageArticles(); title = "Articles · " + siteTitle; }
    else if (h === "videos") { main.innerHTML = pageVideos(); title = "Video · " + siteTitle; }
    else if (h === "links") { main.innerHTML = pageLinks(); title = "Links · " + siteTitle; }
    else if (h === "about") { pageDoc({ title: "About", file: (data.site && data.site.about) || "content/about.md" }); title = "About · " + siteTitle; }
    else { nav = "home"; main.innerHTML = pageHome(); }

    document.title = title;
    setNav(nav);
    if (h !== "home" && location.hash) window.scrollTo(0, 0);
  }

  main.addEventListener("click", function (e) {
    var btn = e.target.closest(".play");
    if (!btn) return;
    var v = data.videos[+btn.getAttribute("data-video")];
    var src = v && videoSource(v);
    if (!src) return;
    var player = document.getElementById("player-" + btn.getAttribute("data-video"));
    player.innerHTML = '<iframe src="' + esc(src.src) + '" title="' + esc(v.title) + '" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>';
  });

  fetch("content/site.json").then(function (r) {
    if (!r.ok) throw new Error("content/site.json returned " + r.status);
    return r.json();
  }).then(function (json) {
    data = json;
    var s = data.site || {};
    var ft = document.getElementById("footer-text");
    if (ft) ft.textContent = s.footer || ("© " + new Date().getFullYear() + " " + (s.title || "Displaced AI"));
    window.addEventListener("hashchange", route);
    route();
  }).catch(function (e) {
    main.innerHTML = '<p class="empty">The site content could not be loaded: ' + esc(e.message) +
      ". If you opened index.html straight from your computer, run a local server instead (see README).</p>";
  });
})();
