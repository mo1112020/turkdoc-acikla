const API = "";
let uploadMode = "file";
let toastTimer = null;

// --- Upload tabs ---
document.querySelectorAll(".tab[data-upload-tab]").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab[data-upload-tab]").forEach((t) => {
      t.classList.remove("active");
      t.setAttribute("aria-selected", "false");
    });
    tab.classList.add("active");
    tab.setAttribute("aria-selected", "true");
    uploadMode = tab.dataset.uploadTab;
    document.getElementById("file-panel").classList.toggle("hidden", uploadMode !== "file");
    document.getElementById("text-panel").classList.toggle("hidden", uploadMode !== "text");
  });
});

// --- File drop ---
const fileInput = document.querySelector('input[name="file"]');
const fileDrop = document.getElementById("file-drop");
const filePreview = document.getElementById("file-preview");
const fileNameEl = document.getElementById("file-name");

function setFile(name) {
  if (name) {
    fileNameEl.textContent = name;
    filePreview.classList.remove("hidden");
    fileDrop.classList.add("hidden");
  } else {
    fileNameEl.textContent = "";
    filePreview.classList.add("hidden");
    fileDrop.classList.remove("hidden");
    fileInput.value = "";
  }
}

fileDrop.addEventListener("dragover", (e) => {
  e.preventDefault();
  fileDrop.classList.add("dragover");
});
fileDrop.addEventListener("dragleave", () => fileDrop.classList.remove("dragover"));
fileDrop.addEventListener("drop", (e) => {
  e.preventDefault();
  fileDrop.classList.remove("dragover");
  if (e.dataTransfer.files.length) {
    fileInput.files = e.dataTransfer.files;
    setFile(e.dataTransfer.files[0].name);
  }
});
fileInput.addEventListener("change", () => {
  setFile(fileInput.files[0]?.name || "");
});
document.getElementById("file-clear").addEventListener("click", () => setFile(""));

// --- Toast ---
function showToast(message) {
  const el = document.getElementById("toast");
  el.textContent = message;
  el.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.add("hidden"), 3200);
}

// --- API helpers ---
async function api(path, options = {}) {
  const headers = { ...options.headers };
  if (!(options.body instanceof FormData)) headers["Content-Type"] = "application/json";

  const res = await fetch(API + path, { ...options, headers });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    const detail = data.detail;
    const msg = Array.isArray(detail) ? detail.map((d) => d.msg).join(", ") : (detail || `Error ${res.status}`);
    throw new Error(msg);
  }
  if (res.status === 204) return null;
  return res.json();
}

function urgencyClass(level) {
  return (level || "medium").toLowerCase();
}

function urgencyLabel(level) {
  return (level || "MEDIUM").toUpperCase();
}

function urgencyIcon(level) {
  const map = { LOW: "🟢", MEDIUM: "🟡", HIGH: "🔴" };
  return map[urgencyLabel(level)] || "🟡";
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function sourceLabel(type) {
  const map = { upload: "File upload", text: "Pasted text", image: "Image", pdf: "PDF" };
  return map[(type || "").toLowerCase()] || type || "Document";
}

const PANEL_ICONS = {
  explanation: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`,
  reason: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  deadlines: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
  steps: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>`,
  contacts: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>`,
  text: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`,
};

function panelHtml(icon, color, title, body, collapsible = false) {
  const toggle = collapsible
    ? `<button class="panel-toggle" type="button" aria-expanded="false">
         <div class="panel-head"><span class="panel-icon ${color}">${icon}</span><h3>${title}</h3></div>
         <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
       </button>`
    : `<div class="panel-head"><span class="panel-icon ${color}">${icon}</span><h3>${title}</h3></div>`;

  return `<div class="panel${collapsible ? " collapsible" : ""}">
    ${toggle}
    <div class="panel-body">${body}</div>
  </div>`;
}

// --- Documents ---
async function loadDocuments() {
  const list = document.getElementById("doc-list");
  list.innerHTML = '<div class="skeleton-list"><div class="skeleton"></div><div class="skeleton"></div></div>';

  try {
    const docs = await api("/api/documents");
    if (!docs.length) {
      list.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon" aria-hidden="true">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <p class="empty-title">No documents yet</p>
          <p class="empty-desc">Upload a government letter to get a plain-language explanation.</p>
        </div>`;
      return;
    }

    list.innerHTML = docs.map((d) => `
      <div class="doc-item" data-id="${d.id}" tabindex="0" role="button" aria-label="View ${esc(d.title)}">
        <div>
          <strong>${esc(d.title)}</strong>
          <div class="meta">${formatDate(d.created_at)} · ${esc(sourceLabel(d.source_type))}</div>
        </div>
        <span class="urgency ${urgencyClass(d.urgency)}">${urgencyIcon(d.urgency)} ${urgencyLabel(d.urgency)}</span>
      </div>
    `).join("");

    list.querySelectorAll(".doc-item").forEach((el) => {
      const open = () => showDetail(parseInt(el.dataset.id));
      el.addEventListener("click", open);
      el.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          open();
        }
      });
    });
  } catch (err) {
    list.innerHTML = `<p class="hint" style="color:var(--red)">Could not load documents: ${esc(err.message)}</p>`;
  }
}

async function showDetail(id) {
  const detailEl = document.getElementById("detail");
  const content = document.getElementById("detail-content");

  document.getElementById("main-grid").classList.add("hidden");
  detailEl.classList.remove("hidden");
  content.innerHTML = '<div class="alert alert-loading"><span class="inline-spinner"></span> Loading explanation…</div>';
  window.scrollTo({ top: 0, behavior: "smooth" });

  try {
    const doc = await api(`/api/documents/${id}`);
    renderDetail(doc);
  } catch (err) {
    content.innerHTML = `<div class="alert alert-error">${esc(err.message)}</div>`;
  }
}

function renderDetail(doc) {
  const uClass = urgencyClass(doc.urgency);
  const steps = (doc.next_steps || []).map((s, i) => `<li data-step="${i + 1}">${esc(s)}</li>`).join("");
  const langLabel = (doc.language || "english").charAt(0).toUpperCase() + (doc.language || "english").slice(1);

  document.getElementById("detail-content").innerHTML = `
    <div class="detail-header">
      <h2>${esc(doc.title)}</h2>
      <div class="detail-meta">
        <span class="detail-meta-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          ${esc(doc.sent_by || "Unknown sender")}
        </span>
        <span class="detail-meta-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
          ${esc(langLabel)}
        </span>
        <span class="detail-meta-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          ${formatDate(doc.created_at)}
        </span>
      </div>
    </div>

    <div class="urgency-banner ${uClass}">
      <span class="urgency-banner-icon">${urgencyIcon(doc.urgency)}</span>
      <div class="urgency-banner-text">
        <strong>${urgencyLabel(doc.urgency)} urgency</strong>
        <p>${esc(doc.reason || "No specific reason provided.")}</p>
      </div>
    </div>

    <div class="detail-panels">
      ${panelHtml(PANEL_ICONS.explanation, "blue", `Explanation (${langLabel})`, `<p>${esc(doc.explanation || "No explanation available.")}</p>`)}
      ${panelHtml(PANEL_ICONS.deadlines, "magenta", "Deadlines", `<p>${esc(doc.deadlines || "No deadline detected.")}</p>`)}
      ${panelHtml(PANEL_ICONS.steps, "green", "What you should do", `<ul>${steps || '<li data-step="!">No specific steps identified.</li>'}</ul>`)}
      ${doc.contacts ? panelHtml(PANEL_ICONS.contacts, "amber", "Important contacts", `<p>${esc(doc.contacts)}</p>`) : ""}
      ${panelHtml(PANEL_ICONS.text, "gray", "Original Turkish text", `<div class="extracted-text">${esc(doc.extracted_text || "")}</div>`, true)}
    </div>

    <div class="detail-actions" data-doc-id="${doc.id}">
      <button type="button" class="btn ghost" data-action="reexplain" data-lang="english">Re-explain in English</button>
      <button type="button" class="btn ghost" data-action="reexplain" data-lang="arabic">Re-explain in Arabic</button>
      <button type="button" class="btn danger" data-action="delete">Delete document</button>
    </div>
  `;

  document.querySelectorAll(".panel.collapsible .panel-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const panel = btn.closest(".panel");
      const open = panel.classList.toggle("open");
      btn.setAttribute("aria-expanded", open);
    });
  });
}

document.getElementById("back-btn").addEventListener("click", () => {
  document.getElementById("detail").classList.add("hidden");
  document.getElementById("main-grid").classList.remove("hidden");
});

document.getElementById("detail-content").addEventListener("click", async (e) => {
  const btn = e.target.closest("[data-action]");
  if (!btn) return;

  const actions = btn.closest(".detail-actions");
  if (!actions) return;
  const id = parseInt(actions.dataset.docId, 10);
  const action = btn.dataset.action;

  if (action === "reexplain") {
    const lang = btn.dataset.lang;
    const content = document.getElementById("detail-content");
    content.innerHTML = `<div class="alert alert-loading"><span class="inline-spinner"></span> Re-analyzing in ${esc(lang)}…</div>`;
    try {
      const doc = await api(`/api/documents/${id}/explain?language=${lang}`, { method: "POST" });
      renderDetail(doc);
      showToast(`Explanation updated in ${lang}.`);
    } catch (err) {
      content.innerHTML = `<div class="alert alert-error">${esc(err.message)}</div>`;
    }
    return;
  }

  if (action === "delete") {
    if (!confirm("Delete this document? This cannot be undone.")) return;
    try {
      await api(`/api/documents/${id}`, { method: "DELETE" });
      document.getElementById("detail").classList.add("hidden");
      document.getElementById("main-grid").classList.remove("hidden");
      await loadDocuments();
      showToast("Document deleted.");
    } catch (err) {
      showToast(err.message);
    }
  }
});

// --- Upload ---
document.getElementById("upload-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const errEl = document.getElementById("upload-error");
  const loadEl = document.getElementById("upload-loading");
  const btn = document.getElementById("submit-btn");

  errEl.classList.add("hidden");
  loadEl.classList.remove("hidden");
  btn.disabled = true;
  btn.classList.add("loading");
  btn.querySelector(".btn-spinner").classList.remove("hidden");

  const fd = new FormData(e.target);
  try {
    let doc;
    if (uploadMode === "text") {
      const text = (fd.get("text") || "").trim();
      if (!text) throw new Error("Please paste some Turkish text.");
      doc = await api("/api/documents/text", {
        method: "POST",
        body: JSON.stringify({
          text,
          title: fd.get("title"),
          language: fd.get("language"),
        }),
      });
    } else {
      if (!fileInput.files.length) throw new Error("Please select a file to upload.");
      const formData = new FormData();
      formData.append("file", fileInput.files[0]);
      formData.append("title", fd.get("title"));
      formData.append("language", fd.get("language"));
      doc = await api("/api/documents/upload", { method: "POST", body: formData, headers: {} });
    }
    e.target.reset();
    setFile("");
    await loadDocuments();
    showDetail(doc.id);
    showToast("Document analyzed successfully.");
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove("hidden");
  } finally {
    loadEl.classList.add("hidden");
    btn.disabled = false;
    btn.classList.remove("loading");
    btn.querySelector(".btn-spinner").classList.add("hidden");
  }
});

function esc(str) {
  const d = document.createElement("div");
  d.textContent = str ?? "";
  return d.innerHTML;
}

loadDocuments();
