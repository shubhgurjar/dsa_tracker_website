/**
 * Concepts Page (Data Structures & Algorithms Tracker)
 */

let currentTab = "data_structure"; // 'data_structure' or 'algorithm'
let allConcepts = [];

document.addEventListener("DOMContentLoaded", async () => {
  setupEventListeners();
  await loadConcepts();
});

function setupEventListeners() {
  const tabDs = document.getElementById("tab-ds");
  const tabAlgo = document.getElementById("tab-algo");
  const searchInput = document.getElementById("concept-search");
  const statusFilter = document.getElementById("concept-status-filter");

  if (tabDs && tabAlgo) {
    tabDs.addEventListener("click", () => {
      currentTab = "data_structure";
      tabDs.classList.add("active");
      tabAlgo.classList.remove("active");
      renderFilteredConcepts();
    });

    tabAlgo.addEventListener("click", () => {
      currentTab = "algorithm";
      tabAlgo.classList.add("active");
      tabDs.classList.remove("active");
      renderFilteredConcepts();
    });
  }

  if (searchInput) {
    searchInput.addEventListener("input", () => renderFilteredConcepts());
  }

  if (statusFilter) {
    statusFilter.addEventListener("change", () => renderFilteredConcepts());
  }
}

async function loadConcepts() {
  try {
    const data = await App.api("/api/concepts");
    allConcepts = data.concepts;
    updateSummaryStats(data);
    renderFilteredConcepts();
  } catch (err) {
    console.error("Failed to load concepts:", err);
  }
}

function updateSummaryStats(data) {
  const dsItems = allConcepts.filter(c => c.type === "data_structure");
  const algoItems = allConcepts.filter(c => c.type === "algorithm");

  const tabDs = document.getElementById("tab-ds");
  const tabAlgo = document.getElementById("tab-algo");

  if (tabDs) tabDs.innerText = `🧱 Data Structures (${dsItems.length})`;
  if (tabAlgo) tabAlgo.innerText = `⚡ Algorithms (${algoItems.length})`;

  const masterCount = allConcepts.filter(c => c.status === "Mastered").length;
  const inProgressCount = allConcepts.filter(c => c.status === "In Progress").length;
  const notStartedCount = allConcepts.filter(c => c.status === "Not Started").length;

  const statMastered = document.getElementById("stat-concept-mastered");
  const statInProgress = document.getElementById("stat-concept-in-progress");
  const statNotStarted = document.getElementById("stat-concept-not-started");

  if (statMastered) statMastered.innerText = masterCount;
  if (statInProgress) statInProgress.innerText = inProgressCount;
  if (statNotStarted) statNotStarted.innerText = notStartedCount;
}

function renderFilteredConcepts() {
  const container = document.getElementById("concepts-grid");
  if (!container) return;

  const searchVal = (document.getElementById("concept-search")?.value || "").toLowerCase().trim();
  const statusVal = document.getElementById("concept-status-filter")?.value || "all";

  const filtered = allConcepts.filter(c => {
    if (c.type !== currentTab) return false;
    if (statusVal !== "all" && c.status !== statusVal) return false;
    if (searchVal) {
      const matchName = c.name.toLowerCase().includes(searchVal);
      const matchCat = (c.category || "").toLowerCase().includes(searchVal);
      const matchDesc = (c.description || "").toLowerCase().includes(searchVal);
      if (!matchName && !matchCat && !matchDesc) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; background: var(--bg-card); border-radius: var(--radius-md); border: 1px dashed var(--border-color);">
        <p style="color: var(--text-dim); font-size: 1rem;">No topics found matching your filters.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(c => `
    <div class="concept-card">
      <div class="concept-top">
        <div>
          <div class="concept-category">${escapeHtml(c.category || "Core")}</div>
          <h4 class="concept-title">${escapeHtml(c.name)}</h4>
        </div>
        <select class="select-control" style="font-size:0.75rem; padding:0.25rem 0.5rem;" onchange="updateConceptStatus(${c.id}, this.value)">
          <option value="Not Started" ${c.status === "Not Started" ? "selected" : ""}>⚪ Not Started</option>
          <option value="In Progress" ${c.status === "In Progress" ? "selected" : ""}>🔵 In Progress</option>
          <option value="Mastered" ${c.status === "Mastered" ? "selected" : ""}>🟢 Mastered</option>
        </select>
      </div>

      <p class="concept-desc">${escapeHtml(c.description || "")}</p>

      ${c.cheat_sheet ? `
        <div style="font-size:0.72rem; color:var(--text-dim); font-weight:600; margin-bottom:0.25rem; text-transform:uppercase;">Cheat Sheet & Patterns:</div>
        <div class="cheat-sheet-box">${escapeHtml(c.cheat_sheet)}</div>
      ` : ""}

      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; font-size:0.8rem;">
        <div>
          <span style="color:var(--text-dim); margin-right:4px;">Confidence:</span>
          <span class="confidence-stars" title="${c.confidence}/5 confidence" onclick="promptConfidence(${c.id}, ${c.confidence})" style="cursor:pointer;">
            ${'★'.repeat(c.confidence || 1)}${'☆'.repeat(5 - (c.confidence || 1))}
          </span>
        </div>
        <span class="badge" style="background:rgba(99, 102, 241, 0.12); color:#818cf8; border:1px solid rgba(99, 102, 241, 0.25);">
          ${c.problems_solved || 0} Problems Solved
        </span>
      </div>

      <div class="concept-footer">
        <div style="display:flex; align-items:center; gap:0.4rem;">
          <span style="font-size:0.75rem; color:var(--text-dim);">Last Revised:</span>
          ${App.formatDaysAgoBadge(c.days_since_revised)}
        </div>
        <div style="display:flex; gap:0.4rem;">
          <button class="btn btn-sm btn-secondary" onclick="openEditConceptModal(${c.id})">✏️ Notes</button>
          <button class="btn btn-sm btn-revise" onclick="markConceptRevised(${c.id}, '${escapeHtml(c.name)}')">✓ Revised</button>
        </div>
      </div>
    </div>
  `).join("");
}

async function updateConceptStatus(conceptId, status) {
  try {
    await App.api(`/api/concepts/${conceptId}`, {
      method: "PUT",
      body: JSON.stringify({ status })
    });
    App.showToast(`Status updated to ${status}`);
    await loadConcepts();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function markConceptRevised(conceptId, name) {
  try {
    await App.api(`/api/concepts/${conceptId}/revise`, { method: "POST" });
    App.showToast(`Concept '${name}' marked revised today!`);
    await loadConcepts();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function promptConfidence(conceptId, currConf) {
  const val = prompt(`Set confidence for this topic (1 to 5):`, currConf);
  if (!val) return;
  const num = parseInt(val);
  if (isNaN(num) || num < 1 || num > 5) {
    App.showToast("Please enter a number between 1 and 5", "error");
    return;
  }
  try {
    await App.api(`/api/concepts/${conceptId}`, {
      method: "PUT",
      body: JSON.stringify({ confidence: num })
    });
    App.showToast(`Confidence set to ${num}/5`);
    await loadConcepts();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

let activeEditConceptId = null;

async function openEditConceptModal(conceptId) {
  try {
    const concept = await App.api(`/api/concepts/${conceptId}`);
    activeEditConceptId = conceptId;
    document.getElementById("edit-concept-title").innerText = `Edit: ${concept.name}`;
    document.getElementById("edit-concept-notes").value = concept.key_notes || "";
    document.getElementById("edit-concept-cheatsheet").value = concept.cheat_sheet || "";
    document.getElementById("edit-concept-confidence").value = concept.confidence || 1;
    document.getElementById("edit-concept-status").value = concept.status || "Not Started";

    // Linked problems list
    const linkedList = document.getElementById("edit-concept-problems-list");
    if (linkedList) {
      if (concept.linked_problems && concept.linked_problems.length > 0) {
        linkedList.innerHTML = concept.linked_problems.map(p => `
          <div style="padding:0.4rem 0.6rem; background:var(--bg-input); border-radius:var(--radius-sm); margin-bottom:0.35rem; display:flex; justify-content:space-between; font-size:0.8rem;">
            <span>#${p.leetcode_number || ''} ${escapeHtml(p.title)}</span>
            <span class="badge badge-${(p.difficulty || 'medium').toLowerCase()}">${p.difficulty}</span>
          </div>
        `).join("");
      } else {
        linkedList.innerHTML = `<div style="color:var(--text-dim); font-size:0.8rem;">No problems logged for this topic yet.</div>`;
      }
    }

    App.openModal("modal-edit-concept");
  } catch (err) {
    App.showToast(`Failed to open concept: ${err.message}`, "error");
  }
}

async function handleSaveConceptEdits(e) {
  e.preventDefault();
  if (!activeEditConceptId) return;

  const payload = {
    key_notes: document.getElementById("edit-concept-notes").value,
    cheat_sheet: document.getElementById("edit-concept-cheatsheet").value,
    confidence: parseInt(document.getElementById("edit-concept-confidence").value),
    status: document.getElementById("edit-concept-status").value
  };

  try {
    await App.api(`/api/concepts/${activeEditConceptId}`, {
      method: "PUT",
      body: JSON.stringify(payload)
    });
    App.showToast("Topic notes updated!");
    App.closeModal("modal-edit-concept");
    await loadConcepts();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function handleCreateCustomTopic(e) {
  e.preventDefault();
  const payload = {
    type: document.getElementById("new-topic-type").value,
    name: document.getElementById("new-topic-name").value,
    category: document.getElementById("new-topic-category").value,
    description: document.getElementById("new-topic-desc").value,
    cheat_sheet: document.getElementById("new-topic-cheatsheet").value,
    status: "Not Started",
    confidence: 1
  };

  try {
    await App.api("/api/concepts", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    App.showToast(`Added new topic: ${payload.name}`);
    App.closeModal("modal-add-topic");
    document.getElementById("form-add-topic").reset();
    await loadConcepts();
  } catch (err) {
    App.showToast(`Failed to add topic: ${err.message}`, "error");
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
