/**
 * Revision Center (Spaced Repetition & Days Ago Tracker)
 */

let activeUrgency = "all";
let activeType = "all";
let queueItems = [];

document.addEventListener("DOMContentLoaded", async () => {
  setupRevisionListeners();
  await loadRevisionQueue();
  await loadRevisionLogs();
});

function setupRevisionListeners() {
  const typeFilter = document.getElementById("rev-type-filter");
  const searchInput = document.getElementById("rev-search");

  if (typeFilter) {
    typeFilter.addEventListener("change", (e) => {
      activeType = e.target.value;
      loadRevisionQueue();
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      loadRevisionQueue();
    });
  }
}

async function loadRevisionQueue() {
  const search = document.getElementById("rev-search")?.value || "";
  const params = new URLSearchParams();
  if (activeType !== "all") params.append("item_type", activeType);
  if (activeUrgency !== "all") params.append("urgency_filter", activeUrgency);
  if (search) params.append("search", search);

  try {
    const data = await App.api(`/api/revision/queue?${params.toString()}`);
    queueItems = data.items;
    renderUrgencyCards(data.counts);
    renderQueueTable(queueItems);
  } catch (err) {
    console.error("Failed to load revision queue:", err);
  }
}

function setUrgencyFilter(urgency) {
  activeUrgency = urgency;
  document.querySelectorAll(".urgency-summary-card").forEach(c => {
    if (c.dataset.urgency === urgency) {
      c.style.borderColor = "var(--accent-primary)";
    } else {
      c.style.borderColor = "var(--border-color)";
    }
  });
  loadRevisionQueue();
}

function renderUrgencyCards(counts) {
  const elOverdue = document.getElementById("count-overdue");
  const elDue = document.getElementById("count-due");
  const elDueSoon = document.getElementById("count-due-soon");
  const elFresh = document.getElementById("count-fresh");

  if (elOverdue) elOverdue.innerText = counts.overdue || 0;
  if (elDue) elDue.innerText = counts.due || 0;
  if (elDueSoon) elDueSoon.innerText = counts.due_soon || 0;
  if (elFresh) elFresh.innerText = counts.fresh || 0;
}

function renderQueueTable(items) {
  const tbody = document.getElementById("revision-queue-tbody");
  if (!tbody) return;

  if (items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; padding: 3rem; color: var(--text-dim);">
          🎉 No items in this revision tier right now! Great job staying on top of your practice.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = items.map(item => {
    const typeBadge = item.item_type === "problem"
      ? `<span class="badge" style="background:rgba(99,102,241,0.15); color:#818cf8;">Problem</span>`
      : `<span class="badge" style="background:rgba(16,185,129,0.15); color:#10b981;">Concept</span>`;

    return `
      <tr>
        <td style="width: 80px;">${typeBadge}</td>
        <td>
          <div style="font-weight: 600; color: #fff;">${escapeHtml(item.title)}</div>
          <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 2px;">${escapeHtml(item.subtitle)}</div>
        </td>
        <td style="font-size: 0.82rem; color: var(--text-dim);">${item.last_revised_date || "Never"}</td>
        <td class="days-ago-cell">
          ${App.formatDaysAgoBadge(item.days_since_revised)}
        </td>
        <td style="font-size: 0.82rem; color: var(--text-muted); text-align: center;">
          ${item.revision_count || 0}x
        </td>
        <td style="text-align: right;">
          <button class="btn btn-sm btn-revise" onclick="quickReviseItem('${item.item_type}', ${item.id}, '${escapeHtml(item.title)}')">
            ✓ Mark Revised Today
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

async function quickReviseItem(itemType, id, title) {
  try {
    await App.api("/api/revision/mark", {
      method: "POST",
      body: JSON.stringify({ item_type: itemType, item_id: id })
    });
    App.showToast(`'${title}' marked as revised today!`);
    await loadRevisionQueue();
    await loadRevisionLogs();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function loadRevisionLogs() {
  const container = document.getElementById("revision-logs-container");
  if (!container) return;

  try {
    const data = await App.api("/api/revision/logs?limit=15");
    const logs = data.logs;

    if (!logs || logs.length === 0) {
      container.innerHTML = `<div style="color:var(--text-dim); font-size:0.85rem; padding:1rem 0;">No revision logs recorded yet.</div>`;
      return;
    }

    container.innerHTML = logs.map(l => `
      <div style="display:flex; justify-content:space-between; align-items:center; padding:0.6rem 0.8rem; background:var(--bg-input); border-radius:var(--radius-sm); margin-bottom:0.4rem; font-size:0.82rem;">
        <div>
          <span style="color:#fff; font-weight:600;">${escapeHtml(l.item_name)}</span>
          <span class="badge" style="font-size:0.7rem; margin-left:6px; background:rgba(255,255,255,0.06); color:var(--text-muted);">${l.item_type}</span>
          ${l.notes ? `<span style="color:var(--text-dim); margin-left:8px; font-style:italic;">— ${escapeHtml(l.notes)}</span>` : ""}
        </div>
        <div style="color:var(--text-dim); font-family:var(--font-mono); font-size:0.78rem;">${l.revised_date}</div>
      </div>
    `).join("");
  } catch (err) {
    console.error("Failed to load revision logs:", err);
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
