const $ = (id) => document.getElementById(id);

const STORAGE_KEY = "pf_categories";
const SOURCE_KEY = "pf_source";
const FILTERS_KEY = "pf_filters";

let allCategories = [];
let selectedIds = [];
let currentIds = [];
let currentSource = localStorage.getItem(SOURCE_KEY) || "youtube";

const DEFAULT_FILTERS = {
  period: "", views: "", comments: "", duration: "", channel: "",
  sort: "random", preset: "",
};
let filterState = { ...DEFAULT_FILTERS };
try {
  filterState = { ...DEFAULT_FILTERS, ...JSON.parse(localStorage.getItem(FILTERS_KEY) || "{}") };
} catch (e) { /* повреждённый state — остаёмся на дефолтах */ }

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
  let val, unit;
  if (n >= 1e6) { val = n / 1e6; unit = "млн"; }
  else if (n >= 1e3) { val = n / 1e3; unit = "тыс."; }
  else return `${n} просмотров`;
  const str = val >= 10 ? Math.round(val).toString() : val.toFixed(1).replace(".", ",").replace(",0", "");
  return `${str} ${unit} просмотров`;
}

function formatTimeAgo(iso) {
  if (!iso) return "";
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 0 || Number.isNaN(diff)) return "";
  const units = [
    [31536000, ["год", "года", "лет"]],
    [2592000,  ["месяц", "месяца", "месяцев"]],
    [604800,   ["неделю", "недели", "недель"]],
    [86400,    ["день", "дня", "дней"]],
    [3600,     ["час", "часа", "часов"]],
    [60,       ["минуту", "минуты", "минут"]],
  ];
  for (const [secs, forms] of units) {
    const n = Math.floor(diff / secs);
    if (n >= 1) return `${n} ${plural(n, forms)} назад`;
  }
  return "только что";
}

function plural(n, [one, few, many]) {
  const mod10 = n % 10, mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return one;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return few;
  return many;
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
  $("f-period").value = filterState.period;
  $("f-views").value = filterState.views;
  $("f-comments").value = filterState.comments;
  $("f-duration").value = filterState.duration;
  $("f-channel").value = filterState.channel;
  $("f-sort").value = filterState.sort;

  const isRu = currentSource === "ru";
  document.querySelectorAll(".yt-only").forEach((el) => el.classList.toggle("hidden", isRu));
  YT_ONLY_SORTS.forEach((sortKey) => {
    const opt = document.querySelector(`#f-sort option[value="${sortKey}"]`);
    if (opt) opt.hidden = isRu;
  });

  document.querySelectorAll(".preset-chip").forEach((c) => {
    c.classList.toggle("active", !!filterState.preset && c.dataset.preset === filterState.preset);
  });
  $("filters-reset").classList.toggle("hidden", isFiltersDefault());
}

function onFilterChange(key, value) {
  filterState[key] = value;
  filterState.preset = "";
  sanitizeFiltersForSource();
  saveFilters();
  syncFiltersUI();
  loadGrid(currentIds);
}

function applyPreset(name) {
  if (filterState.preset === name) {
    filterState = { ...DEFAULT_FILTERS }; // повторный клик по пресету — сброс
  } else {
    filterState = { ...DEFAULT_FILTERS, ...PRESETS[name], preset: name };
  }
  sanitizeFiltersForSource();
  saveFilters();
  syncFiltersUI();
  loadGrid(currentIds);
}

function resetFilters() {
  filterState = { ...DEFAULT_FILTERS };
  saveFilters();
  syncFiltersUI();
  loadGrid(currentIds);
}

/* ---------- Onboarding ---------- */

function renderOnboarding() {
  const grid = $("category-grid");
  grid.innerHTML = "";
  allCategories.forEach(({ id, emoji, label, hint }) => {
    const card = document.createElement("div");
    card.className = "category-card" + (selectedIds.includes(id) ? " selected" : "");
    card.dataset.id = id;
    card.innerHTML = `
      <span class="cat-emoji">${emoji}</span>
      <span class="cat-label">${escHtml(label)}</span>
      <span class="cat-hint">${escHtml(hint)}</span>`;
    card.addEventListener("click", () => {
      const idx = selectedIds.indexOf(id);
      if (idx === -1) selectedIds.push(id);
      else selectedIds.splice(idx, 1);
      card.classList.toggle("selected");
      $("onboarding-continue").disabled = selectedIds.length === 0;
    });
    grid.appendChild(card);
  });
  $("onboarding-continue").disabled = selectedIds.length === 0;
}

function finishOnboarding() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(selectedIds));
  renderChips();
  $("chips-row").classList.remove("hidden");
  $("filters-row").classList.remove("hidden");
  $("surprise-btn").classList.remove("hidden");
  $("source-toggle").classList.remove("hidden");
  updateSourceToggle();
  syncFiltersUI();
  loadGrid(selectedIds);
}

/* ---------- Chips ---------- */

function renderChips() {
  const row = $("chips-row");
  row.innerHTML = "";

  const allChip = document.createElement("button");
  allChip.className = "chip";
  allChip.dataset.category = "__all__";
  allChip.textContent = "Все";
  allChip.addEventListener("click", () => loadGrid(selectedIds));
  row.appendChild(allChip);

  selectedIds.forEach((id) => {
    const cat = allCategories.find((c) => c.id === id);
    if (!cat) return;
    const chip = document.createElement("button");
    chip.className = "chip";
    chip.dataset.category = id;
    chip.textContent = `${cat.emoji} ${cat.label}`;
    chip.addEventListener("click", () => loadGrid([id]));
    row.appendChild(chip);
  });

  const settings = document.createElement("button");
  settings.className = "chip";
  settings.title = "Изменить категории";
  settings.textContent = "⚙";
  settings.addEventListener("click", () => {
    renderOnboarding();
    showState("onboarding");
  });
  row.appendChild(settings);
}

function setActiveChip(categoryId) {
  document.querySelectorAll(".chip").forEach((c) => {
    c.classList.toggle("active", !!categoryId && c.dataset.category === categoryId);
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
    // RuTube / VK embed
    iframeSrc = item.embed_url;
  } else if (item.video_id) {
    // YouTube embed
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
  ["onboarding", "loading", "feed"].forEach((id) => $(id).classList.add("hidden"));
  $(state).classList.remove("hidden");
}

async function loadGrid(categoryIds) {
  const chipKey = categoryIds.length === 1 ? categoryIds[0] : "__all__";
  setActiveChip(chipKey);
  renderSkeletons();
  showState("loading");

  let data;
  try {
    const res = await fetch("/grid", {
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
    $("video-grid").innerHTML = `<p class="error-msg">Не удалось загрузить ленту: ${escHtml(e.message)}</p>`;
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
    const res = await fetch("/categories");
    allCategories = await res.json();
  } catch (e) {
    alert("Не удалось загрузить категории. Проверьте, что сервер запущен.");
    return;
  }

  const stored = localStorage.getItem(STORAGE_KEY);
  selectedIds = stored ? JSON.parse(stored) : [];
  selectedIds = selectedIds.filter((id) => allCategories.some((c) => c.id === id));

  if (selectedIds.length === 0) {
    renderOnboarding();
    showState("onboarding");
  } else {
    renderChips();
    $("chips-row").classList.remove("hidden");
    $("filters-row").classList.remove("hidden");
    $("surprise-btn").classList.remove("hidden");
    $("source-toggle").classList.remove("hidden");
    updateSourceToggle();
    syncFiltersUI();
    loadGrid(selectedIds);
  }
}

/* ---------- Events ---------- */

$("onboarding-continue").addEventListener("click", finishOnboarding);
$("surprise-btn").addEventListener("click", () => loadGrid(selectedIds));
$("src-youtube").addEventListener("click", () => setSource("youtube"));
$("src-ru").addEventListener("click", () => setSource("ru"));

$("modal-close").addEventListener("click", closePlayer);
document.querySelector(".modal-backdrop").addEventListener("click", closePlayer);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !$("player-modal").classList.contains("hidden")) closePlayer();
});

$("filters-toggle").addEventListener("click", () => $("filters-panel").classList.toggle("hidden"));
["period", "views", "comments", "duration", "channel"].forEach((key) => {
  $(`f-${key}`).addEventListener("change", (e) => onFilterChange(key, e.target.value));
});
$("f-sort").addEventListener("change", (e) => onFilterChange("sort", e.target.value));
document.querySelectorAll(".preset-chip").forEach((c) => {
  c.addEventListener("click", () => applyPreset(c.dataset.preset));
});
$("filters-reset").addEventListener("click", resetFilters);

init();
