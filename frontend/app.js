const $ = (id) => document.getElementById(id);

const STORAGE_KEY = "pf_categories";

let allCategories = [];   // из GET /categories
let selectedIds = [];     // выбранные пользователем

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
  $("surprise-btn").classList.remove("hidden");
  showState("empty-state");
}

/* ---------- Chips ---------- */

function renderChips() {
  const row = $("chips-row");
  row.innerHTML = "";
  selectedIds.forEach((id) => {
    const cat = allCategories.find((c) => c.id === id);
    if (!cat) return;
    const chip = document.createElement("button");
    chip.className = "chip";
    chip.dataset.category = id;
    chip.textContent = `${cat.emoji} ${cat.label}`;
    chip.addEventListener("click", () => loadFeed(id));
    row.appendChild(chip);
  });
  const settings = document.createElement("button");
  settings.className = "chip";
  settings.title = "Изменить категории";
  settings.textContent = "⚙";
  settings.addEventListener("click", () => {
    renderOnboarding();
    $("topic-banner").classList.add("hidden");
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
  for (let i = 0; i < 8; i++) {
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

function renderVideoCard(item) {
  const card = document.createElement("div");
  card.className = "video-card";

  const duration = item.duration ? `<span class="duration-badge">${formatDuration(item.duration)}</span>` : "";
  const thumb = item.thumbnail ? `<img src="${escHtml(item.thumbnail)}" alt="" loading="lazy" />` : "";
  const meta = [formatViews(item.views), formatTimeAgo(item.published_at)].filter(Boolean).join(" · ");
  const why = item.why_relevant ? `<div class="why-line">${escHtml(item.why_relevant)}</div>` : "";
  const initial = escHtml((item.channel || "?").charAt(0).toUpperCase());

  card.innerHTML = `
    <div class="thumb-wrap">${thumb}${duration}</div>
    <div class="video-meta">
      <div class="channel-avatar">${initial}</div>
      <div>
        <div class="video-title">${escHtml(item.title)}</div>
        <div class="video-sub">${escHtml(item.channel)}${meta ? "<br>" + meta : ""}</div>
        ${why}
      </div>
    </div>`;

  card.addEventListener("click", () => openPlayer(item));
  return card;
}

function renderNewsCard(item) {
  const a = document.createElement("a");
  a.className = "news-card";
  a.href = item.url;
  a.target = "_blank";
  a.rel = "noopener noreferrer";

  const date = item.published_at ? new Date(item.published_at).toLocaleDateString("ru-RU") : "";
  const why = item.why_relevant ? `<div class="why-line">${escHtml(item.why_relevant)}</div>` : "";

  a.innerHTML = `
    <div class="card-title">${escHtml(item.title)}</div>
    <div class="card-sub">${escHtml(item.source)}${date ? " · " + date : ""}</div>
    ${why}`;
  return a;
}

/* ---------- Player modal ---------- */

function openPlayer(item) {
  if (!item.video_id) {
    window.open(item.url, "_blank", "noopener");
    return;
  }
  $("player-iframe").src = `https://www.youtube.com/embed/${encodeURIComponent(item.video_id)}?autoplay=1`;
  $("modal-title").textContent = item.title;
  $("modal-channel").textContent = item.channel;
  const why = $("modal-why");
  if (item.why_relevant) {
    why.textContent = `💬 ${item.why_relevant}`;
    why.classList.remove("hidden");
  } else {
    why.classList.add("hidden");
  }
  $("player-modal").classList.remove("hidden");
  document.body.style.overflow = "hidden";
}

function closePlayer() {
  $("player-iframe").src = "";
  $("player-modal").classList.add("hidden");
  document.body.style.overflow = "";
}

/* ---------- Feed loading ---------- */

function showState(state) {
  ["onboarding", "empty-state", "loading", "feed"].forEach((id) => $(id).classList.add("hidden"));
  $(state).classList.remove("hidden");
}

async function fetchFeed(url, body) {
  renderSkeletons();
  showState("loading");
  $("topic-banner").classList.add("hidden");

  let data;
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    data = await res.json();
  } catch (e) {
    showState("empty-state");
    setActiveChip(null);
    alert(`Не удалось загрузить ленту: ${e.message}`);
    return;
  }

  renderFeed(data, url === "/surprise");
}

function renderFeed(data, isSurprise) {
  const cat = allCategories.find((c) => c.id === data.category_id);
  const emoji = isSurprise ? "🎲" : (cat ? cat.emoji : "🔍");
  $("banner-text").textContent =
    `${emoji} ${data.category_label} → ${data.topic}. ${data.intro}`;
  $("topic-banner").classList.remove("hidden");

  const grid = $("video-grid");
  grid.innerHTML = "";
  (data.youtube || []).forEach((v) => grid.appendChild(renderVideoCard(v)));

  const searches = data.searches || [];
  const chips = $("searches-chips");
  chips.innerHTML = "";
  searches.forEach((q) => {
    const span = document.createElement("span");
    span.className = "search-chip";
    span.textContent = q;
    chips.appendChild(span);
  });
  $("searches-block").classList.toggle("hidden", searches.length === 0);

  const news = data.news || [];
  const row = $("news-row");
  row.innerHTML = "";
  news.forEach((n) => row.appendChild(renderNewsCard(n)));
  $("news-title").textContent = `Новости по теме «${data.topic}»`;
  $("news-shelf").classList.toggle("hidden", news.length === 0);

  showState("feed");
}

function loadFeed(category) {
  setActiveChip(category);
  fetchFeed("/feed", { category, language: "ru" });
}

function loadSurprise() {
  setActiveChip(null);
  fetchFeed("/surprise", { categories: selectedIds, language: "ru" });
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
    $("surprise-btn").classList.remove("hidden");
    showState("empty-state");
  }
}

/* ---------- Events ---------- */

$("onboarding-continue").addEventListener("click", finishOnboarding);
$("surprise-btn").addEventListener("click", loadSurprise);

$("custom-btn").addEventListener("click", () => {
  const val = $("custom-input").value.trim();
  if (val) { setActiveChip(null); fetchFeed("/feed", { category: val, language: "ru" }); }
});

$("custom-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    const val = $("custom-input").value.trim();
    if (val) { setActiveChip(null); fetchFeed("/feed", { category: val, language: "ru" }); }
  }
});

$("modal-close").addEventListener("click", closePlayer);
document.querySelector(".modal-backdrop").addEventListener("click", closePlayer);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !$("player-modal").classList.contains("hidden")) closePlayer();
});

init();
