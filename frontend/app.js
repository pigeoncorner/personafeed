const PERSONAS = [
  { id: "scientist", emoji: "🔬", label: "Учёный-физик" },
  { id: "teacher",   emoji: "📚", label: "Учитель" },
  { id: "founder",   emoji: "💼", label: "Стартап-фаундер" },
  { id: "doctor",    emoji: "👩‍⚕️", label: "Врач" },
];

const $ = (id) => document.getElementById(id);

let currentPersona = null;

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

/* ---------- Rendering ---------- */

function renderChips() {
  const row = $("chips-row");
  PERSONAS.forEach(({ id, emoji, label }) => {
    const chip = document.createElement("button");
    chip.className = "chip";
    chip.dataset.persona = id;
    chip.textContent = `${emoji} ${label}`;
    chip.addEventListener("click", () => loadFeed(id));
    row.appendChild(chip);
  });
}

function setActiveChip(personaId) {
  document.querySelectorAll(".chip").forEach((c) => {
    c.classList.toggle("active", c.dataset.persona === personaId);
  });
}

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
  ["empty-state", "loading", "feed"].forEach((id) => $(id).classList.add("hidden"));
  $(state).classList.remove("hidden");
}

async function loadFeed(personaId, customText) {
  currentPersona = personaId;
  setActiveChip(personaId);
  renderSkeletons();
  showState("loading");
  $("persona-banner").classList.add("hidden");

  const body = { persona: customText || personaId, language: "ru" };

  let data;
  try {
    const res = await fetch("/feed", {
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

  // Banner + avatar
  $("banner-text").textContent = `Ты смотришь глазами: ${data.persona_name}. ${data.persona_context}`;
  $("persona-banner").classList.remove("hidden");
  const avatar = $("persona-avatar");
  const known = PERSONAS.find((p) => p.id === personaId);
  avatar.textContent = known ? known.emoji : "👤";
  avatar.title = data.persona_name;
  avatar.classList.remove("hidden");

  // Videos
  const grid = $("video-grid");
  grid.innerHTML = "";
  (data.youtube || []).forEach((v) => grid.appendChild(renderVideoCard(v)));

  // Searches
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

  // News shelf
  const news = data.news || [];
  const row = $("news-row");
  row.innerHTML = "";
  news.forEach((n) => row.appendChild(renderNewsCard(n)));
  $("news-title").textContent = `Новости для персоны «${data.persona_name}»`;
  $("news-shelf").classList.toggle("hidden", news.length === 0);

  showState("feed");
}

/* ---------- Events ---------- */

$("custom-btn").addEventListener("click", () => {
  const val = $("custom-input").value.trim();
  if (val) loadFeed(null, val);
});

$("custom-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    const val = $("custom-input").value.trim();
    if (val) loadFeed(null, val);
  }
});

$("modal-close").addEventListener("click", closePlayer);
document.querySelector(".modal-backdrop").addEventListener("click", closePlayer);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !$("player-modal").classList.contains("hidden")) closePlayer();
});

renderChips();
