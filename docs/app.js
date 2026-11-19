(function () {
  const state = {
    catalog: null,
    view: "topic",
    query: "",
  };

  const library = document.querySelector("#library");
  const topicsNav = document.querySelector("#topics");
  const layout = document.querySelector(".layout");
  const stats = document.querySelector("#stats");
  const topicButton = document.querySelector("#view-topic");
  const dateButton = document.querySelector("#view-date");
  const filterInput = document.querySelector("#filter");

  document.addEventListener("DOMContentLoaded", init);

  async function init() {
    try {
      const response = await fetch("catalog.json");
      if (!response.ok) {
        throw new Error("catalog.json returned " + response.status);
      }
      state.catalog = await response.json();
    } catch (error) {
      library.textContent = "The catalog could not be loaded. Check that docs/catalog.json is present and valid.";
      stats.textContent = "";
      return;
    }

    const summary = state.catalog.summary || "";
    document.querySelector("#lede").textContent = summary;
    if (state.catalog.title) {
      document.title = state.catalog.title;
    }
    const repoLink = document.querySelector("#repo-link");
    if (state.catalog.repository) {
      repoLink.href = state.catalog.repository;
    }

    readUrl();
    topicButton.addEventListener("click", function () {
      setView("topic");
    });
    dateButton.addEventListener("click", function () {
      setView("date");
    });
    filterInput.addEventListener("input", function () {
      state.query = filterInput.value;
      syncUrl();
      render();
    });

    render();
    revealHash();
  }

  function readUrl() {
    const params = new URLSearchParams(location.search);
    if (params.get("view") === "date") {
      state.view = "date";
    }
    state.query = params.get("q") || "";
    filterInput.value = state.query;
    topicButton.setAttribute("aria-pressed", state.view === "topic" ? "true" : "false");
    dateButton.setAttribute("aria-pressed", state.view === "date" ? "true" : "false");
  }

  function syncUrl() {
    const params = new URLSearchParams();
    if (state.view === "date") {
      params.set("view", "date");
    }
    if (state.query.trim()) {
      params.set("q", state.query.trim());
    }
    const query = params.toString();
    history.replaceState(null, "", location.pathname + (query ? "?" + query : "") + location.hash);
  }

  function setView(view) {
    state.view = view;
    topicButton.setAttribute("aria-pressed", view === "topic" ? "true" : "false");
    dateButton.setAttribute("aria-pressed", view === "date" ? "true" : "false");
    syncUrl();
    render();
  }

  function animations() {
    const items = Array.isArray(state.catalog.animations) ? state.catalog.animations : [];
    return items.filter(function (item) {
      return item && typeof item === "object";
    });
  }

  function filteredAnimations() {
    const query = state.query.trim().toLowerCase();
    const items = animations();
    if (!query) {
      return items;
    }
    return items.filter(function (item) {
      return searchable(item).indexOf(query) !== -1;
    });
  }

  function searchable(item) {
    const description = String(item.description || "").replace(/\\([a-zA-Z]+)/g, "$1");
    return [item.title, description, item.topic, item.chapter, item.id, item.status]
      .filter(Boolean)
      .join("\n")
      .toLowerCase();
  }

  function render() {
    const all = animations();
    const shown = filteredAnimations();
    stats.textContent = statsText(shown, all);
    library.textContent = "";
    topicsNav.textContent = "";

    if (!shown.length) {
      topicsNav.hidden = true;
      layout.classList.add("layout-single");
      const empty = el("p", "empty-library", state.query
        ? "Nothing in the library matches that filter."
        : "No animations have been added yet.");
      library.appendChild(empty);
      return;
    }

    if (state.view === "date") {
      topicsNav.hidden = true;
      layout.classList.add("layout-single");
      groupByYear(shown).forEach(function (group) {
        library.appendChild(renderSection(group.label, group.items, true));
      });
      typeset(library);
      return;
    }

    const groups = groupByTopic(shown);
    topicsNav.hidden = false;
    layout.classList.remove("layout-single");
    topicsNav.appendChild(renderTopicNav(groups));
    groups.forEach(function (group) {
      library.appendChild(renderSection(group.label, group.items, false));
    });
    typeset(library);
  }

  function renderTopicNav(groups) {
    const heading = el("h2", null, "Topics");
    const list = document.createElement("ol");
    groups.forEach(function (group) {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = "#" + sectionId(group.label);
      link.appendChild(el("span", null, group.label));
      link.appendChild(el("span", "count", String(group.items.length)));
      item.appendChild(link);
      list.appendChild(item);
    });
    const nav = document.createDocumentFragment();
    nav.appendChild(heading);
    nav.appendChild(list);
    return nav;
  }

  function renderSection(label, items, includeTopic) {
    const section = el("section", "section");
    section.id = sectionId(label);
    const heading = el("h2", "section-heading", label);
    section.appendChild(heading);
    items.forEach(function (item) {
      section.appendChild(renderCard(item, includeTopic));
    });
    return section;
  }

  function renderCard(item, includeTopic) {
    const card = el("article", "card");
    if (item.id) {
      card.id = item.id;
    }

    const meta = el("p", "meta");
    metaParts(item, includeTopic).forEach(function (part) {
      meta.appendChild(el("span", null, part));
    });
    const badge = badgeFor(item);
    if (badge) {
      meta.appendChild(el("span", badge.className, badge.label));
    }
    if (meta.childNodes.length) {
      card.appendChild(meta);
    }

    card.appendChild(el("h3", null, item.title || "Untitled animation"));

    const description = el("div", "description");
    fillDescription(description, item.description || "");
    card.appendChild(description);
    card.appendChild(renderFrame(item));

    const links = renderLinks(item);
    if (links) {
      card.appendChild(links);
    }
    return card;
  }

  function metaParts(item, includeTopic) {
    const parts = [];
    if (includeTopic && item.topic) {
      parts.push(item.topic);
    }
    if (item.chapter) {
      parts.push(item.chapter);
    }
    if (item.date) {
      parts.push(formatDate(item.date));
    }
    return parts;
  }

  function badgeFor(item) {
    if (normalizeVideo(item.video)) {
      return null;
    }
    if (item.status === "upcoming") {
      return { label: "Planned", className: "badge" };
    }
    return { label: "Video not committed", className: "badge badge-missing" };
  }

  function renderFrame(item) {
    const video = normalizeVideo(item.video);
    const frame = el("div", video ? "frame" : "frame frame-empty");
    if (!video) {
      frame.appendChild(emptyMark());
      frame.appendChild(el("p", "empty-title", "No video in the repository yet"));
      frame.appendChild(el(
        "p",
        "empty-detail",
        "The film will play here once an MP4 or WebM is listed in the catalog."
      ));
      return frame;
    }

    const block = el("div", "player-block");

    const player = document.createElement("video");
    player.controls = true;
    player.preload = "metadata";
    player.playsInline = true;
    player.setAttribute("playsinline", "");
    if (video.poster) {
      player.poster = video.poster;
    }
    player.setAttribute("aria-label", item.title || "Animation");
    video.sources.forEach(function (source) {
      const node = document.createElement("source");
      node.src = source.src;
      node.type = source.type;
      player.appendChild(node);
    });
    const fallback = el("p", null, "This browser cannot play the video inline.");
    const inlineLink = document.createElement("a");
    inlineLink.href = primarySource(video.sources).src;
    inlineLink.textContent = "Open the video file";
    fallback.appendChild(document.createTextNode(" "));
    fallback.appendChild(inlineLink);
    player.appendChild(fallback);
    frame.appendChild(player);

    const fileLink = document.createElement("a");
    fileLink.className = "video-link";
    fileLink.href = primarySource(video.sources).src;
    fileLink.textContent = "Open video file";
    block.appendChild(frame);
    block.appendChild(fileLink);
    return block;
  }

  function renderLinks(item) {
    const row = el("div", "links");
    if (item.source) {
      row.appendChild(externalLink(sourceHref(item.source), "Source scene"));
    }
    return row.childNodes.length ? row : null;
  }

  function externalLink(href, text) {
    const link = document.createElement("a");
    link.href = href;
    link.textContent = text;
    if (/^https?:\/\//.test(href)) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    }
    return link;
  }

  function sourceHref(source) {
    if (/^https?:\/\//.test(source)) {
      return source;
    }
    const repository = String(state.catalog.repository || "").replace(/\/$/, "");
    const branch = state.catalog.branch || "main";
    const path = String(source).replace(/^\//, "");
    if (!repository) {
      return path;
    }
    return repository + "/blob/" + branch + "/" + path.split("/").map(encodeURIComponent).join("/");
  }

  function fillDescription(container, text) {
    text.trim().split(/\n\s*\n/).forEach(function (part) {
      const paragraph = document.createElement("p");
      paragraph.textContent = part.trim();
      container.appendChild(paragraph);
    });
  }

  function typeset(root) {
    if (!window.renderMathInElement) {
      return;
    }
    window.renderMathInElement(root, {
      delimiters: [
        { left: "$$", right: "$$", display: true },
        { left: "$", right: "$", display: false },
      ],
      throwOnError: false,
    });
  }

  function groupByTopic(items) {
    const topics = new Map();
    items.forEach(function (item) {
      const label = item.topic || "Untitled";
      if (!topics.has(label)) {
        topics.set(label, []);
      }
      topics.get(label).push(item);
    });
    return Array.from(topics.entries())
      .sort(function (a, b) {
        return a[0].localeCompare(b[0], undefined, { sensitivity: "base" });
      })
      .map(function (entry) {
        return { label: entry[0], items: entry[1] };
      });
  }

  function groupByYear(items) {
    const ordered = items.map(function (item, index) {
      return { item: item, index: index };
    });
    ordered.sort(function (a, b) {
      const left = a.item.date || "";
      const right = b.item.date || "";
      if (left && right && left !== right) {
        return left < right ? 1 : -1;
      }
      if (left && !right) {
        return -1;
      }
      if (!left && right) {
        return 1;
      }
      return a.index - b.index;
    });

    const years = new Map();
    ordered.forEach(function (entry) {
      const label = entry.item.date ? entry.item.date.slice(0, 4) : "Undated";
      if (!years.has(label)) {
        years.set(label, []);
      }
      years.get(label).push(entry.item);
    });
    return Array.from(years.entries()).map(function (entry) {
      return { label: entry[0], items: entry[1] };
    });
  }

  function sectionId(label) {
    const slug = String(label).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    return "section-" + (slug || "untitled");
  }

  function normalizeVideo(video) {
    if (!video) {
      return null;
    }
    if (typeof video === "string") {
      return { sources: [sourceNode(video)], poster: null };
    }
    if (typeof video !== "object") {
      return null;
    }
    const sources = [];
    if (video.webm) {
      sources.push({ src: mediaHref(video.webm), type: "video/webm" });
    }
    if (video.mp4) {
      sources.push({ src: mediaHref(video.mp4), type: "video/mp4" });
    }
    if (!sources.length) {
      return null;
    }
    return {
      sources: sources,
      poster: video.poster ? mediaHref(video.poster) : null,
    };
  }

  function sourceNode(path) {
    return { src: mediaHref(path), type: videoType(path) };
  }

  function primarySource(sources) {
    return sources.find(function (source) {
      return source.type === "video/mp4";
    }) || sources[0];
  }

  function mediaHref(path) {
    const value = String(path);
    if (/^https?:\/\//.test(value)) {
      return value;
    }
    return value.replace(/^\//, "");
  }

  function videoType(path) {
    const clean = String(path).split("?")[0].toLowerCase();
    if (clean.endsWith(".webm")) {
      return "video/webm";
    }
    if (clean.endsWith(".ogv") || clean.endsWith(".ogg")) {
      return "video/ogg";
    }
    return "video/mp4";
  }

  function formatDate(iso) {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || "");
    if (!match) {
      return iso || "";
    }
    const date = new Date(Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])));
    return date.toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
      timeZone: "UTC",
    });
  }

  function statsText(shown, all) {
    const playable = all.filter(function (item) {
      return normalizeVideo(item.video);
    }).length;
    const planned = all.filter(function (item) {
      return item.status === "upcoming" && !normalizeVideo(item.video);
    }).length;
    const noun = all.length === 1 ? "entry" : "entries";
    let text = all.length + " " + noun + " · " + playable + " playable";
    if (planned) {
      text += " · " + planned + " planned";
    }
    if (shown.length !== all.length) {
      text += " · showing " + shown.length;
    }
    return text;
  }

  function emptyMark() {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 64 64");
    svg.setAttribute("aria-hidden", "true");
    svg.classList.add("empty-mark");
    const arc = document.createElementNS("http://www.w3.org/2000/svg", "path");
    arc.setAttribute("d", "M32 32 A16 16 0 1 1 46 22");
    arc.setAttribute("fill", "none");
    arc.setAttribute("stroke", "#f3efe6");
    arc.setAttribute("stroke-width", "1.6");
    arc.setAttribute("stroke-linecap", "round");
    const triangle = document.createElementNS("http://www.w3.org/2000/svg", "path");
    triangle.setAttribute("d", "M16 48 L32 18 L48 48 Z");
    triangle.setAttribute("fill", "none");
    triangle.setAttribute("stroke", "#f3efe6");
    triangle.setAttribute("stroke-width", "1.6");
    const center = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    center.setAttribute("cx", "32");
    center.setAttribute("cy", "34");
    center.setAttribute("r", "2.2");
    center.setAttribute("fill", "#c46a5a");
    svg.appendChild(arc);
    svg.appendChild(triangle);
    svg.appendChild(center);
    return svg;
  }

  function revealHash() {
    if (!location.hash) {
      return;
    }
    const id = decodeURIComponent(location.hash.slice(1));
    const node = document.getElementById(id);
    if (node) {
      node.scrollIntoView();
    }
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) {
      node.className = className;
    }
    if (text != null) {
      node.textContent = text;
    }
    return node;
  }
})();
