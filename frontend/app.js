const $ = (id) => document.getElementById(id);

const API_BASE = window.location.hostname.includes("stumblefeed.me")
  ? "https://api.stumblefeed.me"
  : "";

const STORAGE_KEY = "pf_categories";
const SOURCE_KEY = "pf_source";
const FILTERS_KEY = "pf_filters";

const CATEGORY_ICONS = {
  science:    `<circle cx="12" cy="12" r="1.5"/><ellipse cx="12" cy="12" rx="10" ry="3.5" transform="rotate(0 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="3.5" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="3.5" transform="rotate(120 12 12)"/>`,
  history:    `<path d="M3 21V8a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v13"/><path d="M3 10h18"/><line x1="7" y1="3" x2="7" y2="6"/><line x1="17" y1="3" x2="17" y2="6"/>`,
  art:        `<circle cx="13.5" cy="6.5" r="1.5"/><circle cx="17.5" cy="10.5" r="1.5"/><circle cx="8.5" cy="7.5" r="1.5"/><circle cx="6.5" cy="12.5" r="1.5"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>`,
  tech:       `<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>`,
  software:   `<rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>`,
  nature:     `<path d="M17 8C8 10 5.9 16.17 3.82 22"/><path d="M9.5 9.1C9.5 9.1 8 13 12 14.5c-1 1.5-3.2 2-5 1.5"/><path d="M14.5 7C14.5 7 18 10 16 14c2 0 4-1 5-3"/>`,
  philosophy: `<path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24A2.5 2.5 0 0 1 9.5 2Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24A2.5 2.5 0 0 0 14.5 2Z"/>`,
  food:       `<path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><line x1="7" y1="2" x2="7" y2="11"/><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/>`,
  games:      `<rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4m-2-2v4"/><circle cx="17" cy="11" r="1" fill="currentColor" stroke="none"/><circle cx="15" cy="13" r="1" fill="currentColor" stroke="none"/>`,
  music:      `<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>`,
  health:     `<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>`,
  business:   `<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>`,
  culture:    `<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>`,
  education:  `<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>`,
  literature: `<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>`,
  movies:     `<rect x="2" y="2" width="20" height="20" rx="2.18"/><line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/><line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="7" x2="7" y2="7"/><line x1="2" y1="17" x2="7" y2="17"/><line x1="17" y1="17" x2="22" y2="17"/><line x1="17" y1="7" x2="22" y2="7"/>`,
  sports:     `<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>`,
  home:       `<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>`,
  fun:        `<circle cx="12" cy="12" r="10"/><path d="M8 13s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/>`,
  travel:     `<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>`,
};

const PRESET_META = {
  latest:    { label: "Default",        icon: `<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>` },
  rising:    { label: "Top Rising",    icon: `<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>` },
  leaders:   { label: "Top Bloggers",  icon: `<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>` },
  discussed: { label: "Top Commented", icon: `<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>` },
  viral:     { label: "Viral Videos",  icon: `<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>` },
};

let allCategories = [];
let selectedIds = [];
let currentSource = localStorage.getItem(SOURCE_KEY) || "youtube";

const DEFAULT_FILTERS = {
  period: "", views: "", comments: "", duration: "", channel: "",
  sort: "random", preset: "",
};
let filterState = { ...DEFAULT_FILTERS };
try {
  filterState = { ...DEFAULT_FILTERS, ...JSON.parse(localStorage.getItem(FILTERS_KEY) || "{}") };
} catch (e) { /* corrupted state — use defaults */ }

/* ---------- Formatting ---------- */

function formatDuration(sec) {
  if (!sec) return "";
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = sec % 60;
  const pad = (n) => String(n).padStart(2, "0");
  return h ? `${h}:${pad(m)}:${pad(s)}` : `${m}:${pad(s)}`;
}

function formatViews(n) {
  if (!n) return "";
  if (n >= 1e6) {
    const val = n / 1e6;
    return `${val >= 10 ? Math.round(val) : val.toFixed(1).replace(".0", "")}M views`;
  }
  if (n >= 1e3) {
    const val = n / 1e3;
    return `${val >= 10 ? Math.round(val) : val.toFixed(1).replace(".0", "")}K views`;
  }
  return `${n} views`;
}

function formatTimeAgo(iso) {
  if (!iso) return "";
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 0 || Number.isNaN(diff)) return "";
  const units = [
    [31536000, "year"], [2592000, "month"], [604800, "week"],
    [86400, "day"], [3600, "hour"], [60, "minute"],
  ];
  for (const [secs, unit] of units) {
    const n = Math.floor(diff / secs);
    if (n >= 1) return `${n} ${unit}${n !== 1 ? "s" : ""} ago`;
  }
  return "just now";
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/* ---------- Source toggle ---------- */

function updateSourceToggle() {
  $("src-youtube").classList.toggle("active", currentSource === "youtube");
  $("src-ru").classList.toggle("active", currentSource === "ru");
}

function setSource(src) {
  currentSource = src;
  localStorage.setItem(SOURCE_KEY, src);
  updateSourceToggle();
  sanitizeFiltersForSource();
  saveFilters();
  syncFiltersUI();
  loadGrid(selectedIds);
}

/* ---------- Filters ---------- */

const PRESETS = {
  latest:    {},
  rising:    { period: "30", views: "lt10k", channel: "young", sort: "velocity" },
  leaders:   { channel: "top", sort: "views" },
  discussed: { comments: "100", sort: "comments" },
  viral:     { period: "30", sort: "views" },
};

const YT_ONLY_FIELDS = ["comments", "channel"];
const YT_ONLY_SORTS = ["comments", "engagement"];
const YT_ONLY_PRESETS = ["leaders", "discussed", "viral"];

function sanitizeFiltersForSource() {
  if (currentSource !== "ru") return;
  YT_ONLY_FIELDS.forEach((k) => { filterState[k] = ""; });
  if (YT_ONLY_SORTS.includes(filterState.sort)) filterState.sort = "random";
  if (YT_ONLY_PRESETS.includes(filterState.preset)) filterState.preset = "";
}

function isFiltersDefault() {
  return Object.keys(DEFAULT_FILTERS).every((k) => filterState[k] === DEFAULT_FILTERS[k]);
}

function saveFilters() {
  localStorage.setItem(FILTERS_KEY, JSON.stringify(filterState));
}

function buildFilterPayload() {
  const f = {};
  const s = filterState;
  if (s.period) f.period_days = Number(s.period);
  if (s.views === "lt10k") f.views_max = 10000;
  else if (s.views === "mid") { f.views_min = 10000; f.views_max = 100000; }
  else if (s.views === "gt100k") f.views_min = 100000;
  if (s.comments) f.comments_min = Number(s.comments);
  if (s.duration === "noshorts") f.exclude_shorts = true;
  else if (s.duration === "lt4") f.duration_max = 240;
  else if (s.duration === "4to20") { f.duration_min = 240; f.duration_max = 1200; }
  else if (s.duration === "gt20") f.duration_min = 1200;
  if (s.channel === "top") f.subscribers_min = 100000;
  else if (s.channel === "small") f.subscribers_max = 10000;
  else if (s.channel === "young") f.channel_age_max_days = 365;
  if (s.preset === "viral") f.viral_ratio_min = 2;
  return Object.keys(f).length ? f : null;
}

function syncFiltersUI() {
  renderPresetsCompact();
}

function onFilterChange(key, value) {
  filterState[key] = value;
  filterState.preset = "";
  sanitizeFiltersForSource();
  saveFilters();
  syncFiltersUI();
  loadGrid(selectedIds);
}

function applyPreset(name) {
  if (filterState.preset === name) {
    filterState = { ...DEFAULT_FILTERS };
  } else {
    filterState = { ...DEFAULT_FILTERS, ...PRESETS[name], preset: name };
  }
  sanitizeFiltersForSource();
  saveFilters();
  syncFiltersUI();
  loadGrid(selectedIds);
}

function resetFilters() {
  filterState = { ...DEFAULT_FILTERS };
  saveFilters();
  syncFiltersUI();
  loadGrid(selectedIds);
}

/* ---------- Category panel ---------- */

function renderCategoryPanel() {
  const grid = $("category-grid");
  grid.innerHTML = "";
  allCategories.forEach(({ id, emoji, label, hint }) => {
    const card = document.createElement("div");
    card.className = "category-card" + (selectedIds.includes(id) ? " selected" : "");
    card.dataset.id = id;
    const iconPaths = CATEGORY_ICONS[id] || '';
    card.innerHTML = `
      <span class="cat-icon"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${iconPaths}</svg></span>
      <span class="cat-label">${escHtml(label)}</span>
      <span class="cat-hint">${escHtml(hint)}</span>`;
    card.addEventListener("click", () => {
      const idx = selectedIds.indexOf(id);
      if (idx === -1) {
        selectedIds.push(id);
        card.classList.add("selected");
      } else {
        if (selectedIds.length === 1) return;
        selectedIds.splice(idx, 1);
        card.classList.remove("selected");
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(selectedIds));
      renderTopicsCompact();
      loadGrid(selectedIds);
    });
    grid.appendChild(card);
  });
}

function closeFlyouts() {
  $("topics-flyout").classList.add("hidden");
  $("presets-flyout").classList.add("hidden");
  $("topics-compact").setAttribute("aria-expanded", "false");
  $("presets-compact").setAttribute("aria-expanded", "false");
  $("topics-chevron-icon").classList.remove("open");
  $("presets-chevron-icon").classList.remove("open");
}

function toggleTopicsFlyout(e) {
  e.stopPropagation();
  const isOpen = !$("topics-flyout").classList.contains("hidden");
  closeFlyouts();
  if (!isOpen) {
    $("topics-flyout").classList.remove("hidden");
    $("topics-compact").setAttribute("aria-expanded", "true");
    $("topics-chevron-icon").classList.add("open");
  }
}

function togglePresetsFlyout(e) {
  e.stopPropagation();
  const isOpen = !$("presets-flyout").classList.contains("hidden");
  closeFlyouts();
  if (!isOpen) {
    renderPresetsFlyout();
    $("presets-flyout").classList.remove("hidden");
    $("presets-compact").setAttribute("aria-expanded", "true");
    $("presets-chevron-icon").classList.add("open");
    positionPresetsFlyout();
  }
}

function positionPresetsFlyout() {
  const btn = $("presets-compact");
  const flyout = $("presets-flyout");
  const rect = btn.getBoundingClientRect();
  flyout.style.top = (rect.bottom + 4) + "px";
  flyout.style.left = rect.left + "px";
}

function renderTopicsCompact() {
  const summary = $("topics-summary");
  if (!summary) return;
  if (allCategories.length === 0) { summary.innerHTML = ""; return; }
  const allSelected = selectedIds.length === allCategories.length;
  if (allSelected || selectedIds.length === 0) {
    summary.innerHTML = `<span class="summary-all">All</span>`;
  } else {
    const icons = selectedIds.slice(0, 4).map((id) => {
      const paths = CATEGORY_ICONS[id] || "";
      return `<svg class="topic-thumb-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths}</svg>`;
    }).join("");
    const overflow = selectedIds.length > 4
      ? `<span class="summary-overflow">+${selectedIds.length - 4}</span>`
      : "";
    summary.innerHTML = icons + overflow;
  }
}

function renderPresetsCompact() {
  const summary = $("presets-summary");
  if (!summary) return;
  const key = filterState.preset || "latest";
  const meta = PRESET_META[key] || PRESET_META.latest;
  summary.innerHTML = `<svg class="preset-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${meta.icon}</svg><span>${escHtml(meta.label)}</span>`;
}

function renderPresetsFlyout() {
  const grid = $("presets-grid");
  if (!grid) return;
  grid.innerHTML = "";
  const isRu = currentSource === "ru";
  const activeKey = filterState.preset || "latest";
  Object.entries(PRESET_META).forEach(([key, { label, icon }]) => {
    const isYtOnly = YT_ONLY_PRESETS.includes(key);
    const btn = document.createElement("button");
    btn.className = "preset-option" +
      (key === activeKey ? " active" : "") +
      (isRu && isYtOnly ? " yt-only-disabled" : "");
    if (isRu && isYtOnly) btn.disabled = true;
    btn.innerHTML = `<svg class="preset-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icon}</svg><span>${escHtml(label)}</span>`;
    btn.addEventListener("click", () => {
      if (key === "latest") {
        resetFilters();
      } else {
        applyPreset(key);
      }
      closeFlyouts();
    });
    grid.appendChild(btn);
  });
}

/* ---------- Rendering ---------- */

function renderSkeletons() {
  const grid = $("skeleton-grid");
  grid.innerHTML = "";
  for (let i = 0; i < 12; i++) {
    const card = document.createElement("div");
    card.className = "video-card skeleton";
    card.innerHTML = `
      <div class="thumb-wrap"></div>
      <div class="video-meta">
        <div class="channel-avatar"></div>
        <div style="flex:1">
          <div class="sk-line"></div>
          <div class="sk-line short"></div>
        </div>
      </div>`;
    grid.appendChild(card);
  }
}

const SOURCE_LABELS = { youtube: "YouTube", vk: "VK", rutube: "RuTube" };

function renderVideoCard(item) {
  const card = document.createElement("div");
  card.className = "video-card";

  const duration = item.duration ? `<span class="duration-badge">${formatDuration(item.duration)}</span>` : "";
  const thumb = item.thumbnail ? `<img src="${escHtml(item.thumbnail)}" alt="" loading="lazy" />` : "";
  const meta = [formatViews(item.views), formatTimeAgo(item.published_at)].filter(Boolean).join(" · ");
  const initial = escHtml((item.channel || "?").charAt(0).toUpperCase());
  const catBadge = item.category_label
    ? `<span class="cat-badge">${escHtml(item.category_label)}</span>`
    : "";
  const srcLabel = SOURCE_LABELS[item.source] || item.source;
  const srcBadge = srcLabel
    ? `<span class="source-badge src-${escHtml(item.source || "")}">${escHtml(srcLabel)}</span>`
    : "";

  card.innerHTML = `
    <div class="thumb-wrap">${thumb}${duration}</div>
    <div class="video-meta">
      <div class="channel-avatar">${initial}</div>
      <div>
        <div class="video-title">${escHtml(item.title)}</div>
        <div class="video-sub">${escHtml(item.channel)}${meta ? "<br>" + meta : ""}</div>
        <div class="card-badges">${catBadge}${srcBadge}</div>
      </div>
    </div>`;

  card.addEventListener("click", () => openPlayer(item));
  return card;
}

/* ---------- Player modal ---------- */

function openPlayer(item) {
  let iframeSrc;
  if (item.embed_url) {
    iframeSrc = item.embed_url;
  } else if (item.video_id) {
    iframeSrc = `https://www.youtube.com/embed/${encodeURIComponent(item.video_id)}?autoplay=1`;
  } else {
    window.open(item.url, "_blank", "noopener");
    return;
  }

  $("player-iframe").src = iframeSrc;
  $("modal-title").textContent = item.title;
  $("modal-channel").textContent = item.channel;
  $("player-modal").classList.remove("hidden");
  document.body.style.overflow = "hidden";
}

function closePlayer() {
  $("player-iframe").src = "";
  $("player-modal").classList.add("hidden");
  document.body.style.overflow = "";
}

/* ---------- Grid loading ---------- */

function showState(state) {
  ["loading", "feed"].forEach((id) => $(id).classList.add("hidden"));
  $(state).classList.remove("hidden");
}

async function loadGrid(categoryIds) {
  renderSkeletons();
  showState("loading");

  let data;
  try {
    const res = await fetch(`${API_BASE}/grid`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ categories: categoryIds, limit: 40, source: currentSource, filters: buildFilterPayload(), sort: filterState.sort }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    data = await res.json();
  } catch (e) {
    showState("feed");
    $("video-grid").innerHTML = `<p class="error-msg">Failed to load feed: ${escHtml(e.message)}</p>`;
    return;
  }

  const grid = $("video-grid");
  grid.innerHTML = "";
  (data.items || []).forEach((v) => grid.appendChild(renderVideoCard(v)));
  showState("feed");
}

/* ---------- Init ---------- */

async function init() {
  try {
    const res = await fetch(`${API_BASE}/categories`);
    allCategories = await res.json();
  } catch (e) {
    alert("Could not load categories. Make sure the server is running.");
    return;
  }

  const stored = localStorage.getItem(STORAGE_KEY);
  selectedIds = stored ? JSON.parse(stored) : [];
  selectedIds = selectedIds.filter((id) => allCategories.some((c) => c.id === id));

  renderCategoryPanel();

  $("slogan-bar").classList.remove("hidden");
  $("toolbar").classList.remove("hidden");
  $("source-toggle").classList.remove("hidden");
  $("new-feed-btn").classList.remove("hidden");
  updateSourceToggle();
  renderTopicsCompact();
  renderPresetsCompact();

  $("topics-select-all").addEventListener("click", () => {
    selectedIds = allCategories.map((c) => c.id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(selectedIds));
    renderCategoryPanel();
    renderTopicsCompact();
    loadGrid(selectedIds);
  });
  $("topics-clear").addEventListener("click", () => {
    if (selectedIds.length <= 1) return;
    selectedIds = [selectedIds[0]];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(selectedIds));
    renderCategoryPanel();
    renderTopicsCompact();
    loadGrid(selectedIds);
  });

  if (selectedIds.length === 0) {
    $("topics-flyout").classList.remove("hidden");
    $("topics-compact").setAttribute("aria-expanded", "true");
    $("topics-chevron-icon").classList.add("open");
  } else {
    loadGrid(selectedIds);
  }
}

/* ---------- Events ---------- */

$("new-feed-btn").addEventListener("click", () => loadGrid(selectedIds));
$("src-youtube").addEventListener("click", () => setSource("youtube"));
$("src-ru").addEventListener("click", () => setSource("ru"));
$("topics-compact").addEventListener("click", toggleTopicsFlyout);
$("presets-compact").addEventListener("click", togglePresetsFlyout);

$("modal-close").addEventListener("click", closePlayer);
document.querySelector(".modal-backdrop").addEventListener("click", closePlayer);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !$("player-modal").classList.contains("hidden")) closePlayer();
});
document.addEventListener("click", (e) => {
  if (!e.target.closest("#toolbar") && !e.target.closest("#topics-flyout") && !e.target.closest("#presets-flyout")) {
    closeFlyouts();
  }
});

init();
