const PERSONAS = [
  { id: "scientist", emoji: "🔬", label: "Учёный-физик" },
  { id: "teacher",   emoji: "📚", label: "Учитель" },
  { id: "founder",   emoji: "💼", label: "Стартап-фаундер" },
  { id: "doctor",    emoji: "👩‍⚕️", label: "Врач" },
];

const $ = (id) => document.getElementById(id);

function renderPersonaGrid() {
  const grid = $("persona-grid");
  PERSONAS.forEach(({ id, emoji, label }) => {
    const card = document.createElement("div");
    card.className = "persona-card";
    card.innerHTML = `<span class="emoji">${emoji}</span><span class="label">${label}</span>`;
    card.addEventListener("click", () => loadFeed(id));
    grid.appendChild(card);
  });
}

function showSection(name) {
  ["picker", "loading", "feed"].forEach((s) => $( s).classList.add("hidden"));
  $(name).classList.remove("hidden");
}

function switchTab(name) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
  document.querySelectorAll(".tab-content").forEach((c) => c.classList.add("hidden"));
  document.querySelector(`[data-tab="${name}"]`).classList.add("active");
  $(`tab-${name}`).classList.remove("hidden");
}

function renderVideoCard(item) {
  const a = document.createElement("a");
  a.className = "video-card";
  a.href = item.url;
  a.target = "_blank";
  a.rel = "noopener noreferrer";

  const thumb = item.thumbnail
    ? `<img class="video-thumb" src="${item.thumbnail}" alt="" loading="lazy" />`
    : `<div class="video-thumb"></div>`;

  const why = item.why_relevant
    ? `<div class="why-badge">💬 ${item.why_relevant}</div>`
    : "";

  a.innerHTML = `
    ${thumb}
    <div class="card-body">
      <div class="card-title">${escHtml(item.title)}</div>
      <div class="card-sub">${escHtml(item.channel)}</div>
      ${why}
    </div>`;
  return a;
}

function renderNewsCard(item) {
  const a = document.createElement("a");
  a.className = "news-card";
  a.href = item.url;
  a.target = "_blank";
  a.rel = "noopener noreferrer";

  const date = item.published_at ? new Date(item.published_at).toLocaleDateString("ru-RU") : "";
  const why = item.why_relevant
    ? `<div class="why-badge">💬 ${item.why_relevant}</div>`
    : "";

  a.innerHTML = `
    <div class="card-body">
      <div class="card-title">${escHtml(item.title)}</div>
      <div class="card-sub">${escHtml(item.source)}${date ? " · " + date : ""}</div>
      ${why}
    </div>`;
  return a;
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function loadFeed(personaId, customText) {
  showSection("loading");

  const body = customText
    ? { persona: customText, language: "ru" }
    : { persona: personaId, language: "ru" };

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
    showSection("picker");
    alert(`Не удалось загрузить ленту: ${e.message}`);
    return;
  }

  $("feed-name").textContent = data.persona_name;
  $("feed-context").textContent = data.persona_context;

  const ytCards = $("youtube-cards");
  ytCards.innerHTML = "";
  (data.youtube || []).forEach((v) => ytCards.appendChild(renderVideoCard(v)));

  const newsCards = $("news-cards");
  newsCards.innerHTML = "";
  (data.news || []).forEach((n) => newsCards.appendChild(renderNewsCard(n)));

  const searchesList = $("searches-list");
  searchesList.innerHTML = "";
  (data.searches || []).forEach((q) => {
    const li = document.createElement("li");
    li.textContent = q;
    searchesList.appendChild(li);
  });

  switchTab("youtube");
  showSection("feed");
}

// Event listeners
document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => switchTab(btn.dataset.tab));
});

$("back-btn").addEventListener("click", () => showSection("picker"));

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

renderPersonaGrid();
