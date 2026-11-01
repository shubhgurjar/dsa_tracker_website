/**
 * Dedicated Topic & Flashcards Page Logic
 */

let currentConceptId = null;
let currentConcept = null;
let allFlashcards = [];
let activeEditCardId = null;

document.addEventListener("DOMContentLoaded", async () => {
  // Parse concept id from URL: /topic?id=...
  const urlParams = new URLSearchParams(window.location.search);
  const idParam = urlParams.get("id");

  // Default to 2 (Strings) if no ID parameter is passed
  if (!idParam) {
    currentConceptId = 2;
  } else {
    currentConceptId = parseInt(idParam) || 2;
  }

  setupEventListeners();
  await loadTopicData();
});

function setupEventListeners() {
  const searchInput = document.getElementById("fc-search");
  const tagFilter = document.getElementById("fc-tag-filter");
  const urgencyFilter = document.getElementById("fc-urgency-filter");

  if (searchInput) searchInput.addEventListener("input", renderFilteredFlashcards);
  if (tagFilter) tagFilter.addEventListener("change", renderFilteredFlashcards);
  if (urgencyFilter) urgencyFilter.addEventListener("change", renderFilteredFlashcards);

  const addForm = document.getElementById("form-add-flashcard");
  if (addForm) addForm.addEventListener("submit", handleSaveFlashcard);
}

async function loadTopicData() {
  try {
    const data = await App.api(`/api/concepts/${currentConceptId}`);
    currentConcept = data;
    allFlashcards = data.flashcards || [];

    renderTopicHeader(data);
    renderFilteredFlashcards();
    renderLinkedProblems(data.linked_problems || []);
  } catch (err) {
    console.error("Failed to load topic:", err);
    App.showToast(`Error loading topic: ${err.message}`, "error");
  }
}

function renderTopicHeader(concept) {
  document.title = `${concept.name} - Flashcards | Minimal DSA Tracker`;

  const titleEl = document.getElementById("topic-title");
  const catEl = document.getElementById("topic-category");
  const descEl = document.getElementById("topic-desc");
  const statusSelect = document.getElementById("topic-status-select");
  const starsEl = document.getElementById("topic-confidence-stars");
  const fcCountBadge = document.getElementById("topic-fc-count");
  const probCountBadge = document.getElementById("topic-prob-count");
  const lastRevBadge = document.getElementById("topic-last-revised");

  if (titleEl) titleEl.innerText = concept.name;
  if (catEl) catEl.innerText = `${concept.type === "data_structure" ? "🧱 Data Structure" : "⚡ Algorithm"} • ${concept.category || "Core"}`;
  if (descEl) descEl.innerText = concept.description || "";
  
  if (statusSelect) {
    statusSelect.value = concept.status || "Not Started";
  }

  if (starsEl) {
    const conf = concept.confidence || 1;
    starsEl.innerHTML = `${'★'.repeat(conf)}${'☆'.repeat(5 - conf)}`;
    starsEl.title = `Confidence: ${conf}/5 (click to change)`;
  }

  if (fcCountBadge) {
    fcCountBadge.innerText = `🗂️ ${allFlashcards.length} Flashcard${allFlashcards.length === 1 ? '' : 's'}`;
  }

  if (probCountBadge) {
    probCountBadge.innerText = `🎯 ${concept.problems_solved || 0} Solved Problem${concept.problems_solved === 1 ? '' : 's'}`;
  }

  if (lastRevBadge) {
    lastRevBadge.innerHTML = App.formatDaysAgoBadge(concept.days_since_revised);
  }
}

function renderFilteredFlashcards() {
  const container = document.getElementById("flashcards-grid");
  if (!container) return;

  const searchVal = (document.getElementById("fc-search")?.value || "").toLowerCase().trim();
  const tagVal = document.getElementById("fc-tag-filter")?.value || "all";
  const urgencyVal = document.getElementById("fc-urgency-filter")?.value || "all";

  const filtered = allFlashcards.filter(card => {
    if (tagVal !== "all" && card.tag !== tagVal) return false;
    if (urgencyVal !== "all" && card.urgency !== urgencyVal) return false;
    if (searchVal) {
      const matchTitle = (card.title || "").toLowerCase().includes(searchVal);
      const matchContent = (card.content || "").toLowerCase().includes(searchVal);
      if (!matchTitle && !matchContent) return false;
    }
    return true;
  });

  const countBadge = document.getElementById("fc-filtered-count");
  if (countBadge) {
    countBadge.innerText = `${filtered.length} of ${allFlashcards.length} Flashcards`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 3.5rem 1.5rem; background: var(--bg-card); border-radius: var(--radius-md); border: 1px dashed var(--border-color);">
        <div style="font-size: 2rem; margin-bottom: 0.75rem;">🗂️</div>
        <h4 style="color: #fff; font-size: 1.1rem; margin-bottom: 0.35rem;">No Flashcards Found</h4>
        <p style="color: var(--text-muted); font-size: 0.88rem; max-width: 480px; margin: 0 auto 1.25rem;">
          ${allFlashcards.length === 0 
            ? "You haven't created any flashcards for this topic yet. Break down patterns, templates, or cheat sheets with a full page of notes!" 
            : "No flashcards match your current search or filter criteria."}
        </p>
        <button class="btn btn-primary" onclick="openCreateFlashcardModal()">+ Add First Flashcard</button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(card => {
    // Generate preview snippet (first 180 chars)
    const contentText = card.content || "";
    const preview = escapeHtml(contentText.slice(0, 260)) + (contentText.length > 260 ? "..." : "");

    return `
      <div class="card" style="display:flex; flex-direction:column; margin-bottom:0; transition:border-color 0.15s ease;">
        
        <!-- Header -->
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem; gap:0.5rem;">
          <div>
            <span class="badge" style="background:rgba(99,102,241,0.15); color:#818cf8; margin-bottom:0.4rem;">
              🏷️ ${escapeHtml(card.tag || "Pattern")}
            </span>
            <h3 style="font-size:1.15rem; font-weight:700; color:#fff; line-height:1.3; cursor:pointer;" onclick="openFullViewModal(${card.id})">
              ${escapeHtml(card.title)}
            </h3>
          </div>
          <div style="text-align:right;">
            ${App.formatDaysAgoBadge(card.days_since_revised)}
            <div style="font-size:0.72rem; color:var(--text-dim); margin-top:2px;">${card.revision_count || 0}x revised</div>
          </div>
        </div>

        <!-- Content Preview / Body -->
        <div style="background:var(--bg-input); border-radius:var(--radius-sm); padding:0.85rem 1rem; margin-bottom:1rem; flex:1; font-size:0.85rem; line-height:1.55; color:#cbd5e1; white-space:pre-wrap; font-family:var(--font-sans); max-height:220px; overflow-y:auto; border:1px solid rgba(255,255,255,0.04);">
${escapeHtml(card.content)}
        </div>

        <!-- Footer Actions -->
        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-color); padding-top:0.75rem; font-size:0.8rem;">
          <span style="color:var(--text-dim); font-size:0.75rem;">
            Last: <strong>${card.last_revised_date || "Today"}</strong>
          </span>
          <div style="display:flex; gap:0.4rem;">
            <button class="btn btn-sm btn-secondary" onclick="openFullViewModal(${card.id})" title="Full screen reading mode">
              ⤢ Full View
            </button>
            <button class="btn btn-sm btn-secondary" onclick="openEditFlashcardModal(${card.id})" title="Edit card">
              ✏️
            </button>
            <button class="btn btn-sm btn-revise" onclick="markCardRevised(${card.id}, '${escapeHtml(card.title)}')">
              ✓ Revised
            </button>
            <button class="btn btn-sm btn-secondary" style="color:#ef4444;" onclick="deleteFlashcardConfirm(${card.id}, '${escapeHtml(card.title)}')">
              🗑
            </button>
          </div>
        </div>

      </div>
    `;
  }).join("");
}

function renderLinkedProblems(problems) {
  const container = document.getElementById("topic-problems-container");
  if (!container) return;

  if (problems.length === 0) {
    container.innerHTML = `<div style="color:var(--text-dim); font-size:0.85rem; padding:0.5rem 0;">No LeetCode problems logged for this topic yet. Log one using the "+ Log Problem" button above!</div>`;
    return;
  }

  container.innerHTML = problems.map(p => `
    <div style="display:flex; justify-content:space-between; align-items:center; padding:0.6rem 0.8rem; background:var(--bg-input); border-radius:var(--radius-sm); margin-bottom:0.4rem; font-size:0.85rem;">
      <div>
        ${p.leetcode_number ? `<span style="font-family:var(--font-mono); color:var(--text-dim); margin-right:4px;">#${p.leetcode_number}</span>` : ""}
        <span style="color:#fff; font-weight:600;">${escapeHtml(p.title)}</span>
      </div>
      <div style="display:flex; gap:0.5rem; align-items:center;">
        ${App.formatDifficultyBadge(p.difficulty)}
        <span style="font-size:0.78rem; color:var(--text-dim);">${p.solved_date}</span>
      </div>
    </div>
  `).join("");
}

// -------------------------------------------------------------------
// FLASHCARD ACTIONS
// -------------------------------------------------------------------

function openCreateFlashcardModal() {
  activeEditCardId = null;
  document.getElementById("modal-fc-title-header").innerText = `+ New Flashcard (${currentConcept ? currentConcept.name : ''})`;
  document.getElementById("fc-form-title").value = "";
  document.getElementById("fc-form-tag").value = "Pattern";
  document.getElementById("fc-form-content").value = "";
  App.openModal("modal-flashcard-form");
  document.getElementById("fc-form-title").focus();
}

function openEditFlashcardModal(cardId) {
  const card = allFlashcards.find(c => c.id === cardId);
  if (!card) return;

  activeEditCardId = cardId;
  document.getElementById("modal-fc-title-header").innerText = `Edit Flashcard`;
  document.getElementById("fc-form-title").value = card.title || "";
  document.getElementById("fc-form-tag").value = card.tag || "Pattern";
  document.getElementById("fc-form-content").value = card.content || "";
  App.openModal("modal-flashcard-form");
}

async function handleSaveFlashcard(e) {
  e.preventDefault();

  const title = document.getElementById("fc-form-title").value.trim();
  const tag = document.getElementById("fc-form-tag").value.trim();
  const content = document.getElementById("fc-form-content").value.trim();

  if (!title || !content) {
    App.showToast("Please provide both a title and card content.", "error");
    return;
  }

  const payload = { title, tag, content };

  try {
    if (activeEditCardId) {
      await App.api(`/api/flashcards/${activeEditCardId}`, {
        method: "PUT",
        body: JSON.stringify(payload)
      });
      App.showToast("Flashcard updated successfully!");
    } else {
      await App.api(`/api/concepts/${currentConceptId}/flashcards`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
      App.showToast("New flashcard created!");
    }

    App.closeModal("modal-flashcard-form");
    await loadTopicData();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function markCardRevised(cardId, title) {
  try {
    await App.api(`/api/flashcards/${cardId}/revise`, { method: "POST" });
    App.showToast(`Flashcard '${title}' marked as revised today!`);
    await loadTopicData();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function deleteFlashcardConfirm(cardId, title) {
  if (!confirm(`Are you sure you want to delete flashcard "${title}"?`)) return;

  try {
    await App.api(`/api/flashcards/${cardId}`, { method: "DELETE" });
    App.showToast("Flashcard deleted.");
    await loadTopicData();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

// -------------------------------------------------------------------
// FULL VIEW MODAL (Page-worth reading view)
// -------------------------------------------------------------------

let activeFullViewCardId = null;

function openFullViewModal(cardId) {
  const card = allFlashcards.find(c => c.id === cardId);
  if (!card) return;

  activeFullViewCardId = cardId;
  document.getElementById("fullview-tag").innerText = card.tag || "Pattern";
  document.getElementById("fullview-title").innerText = card.title;
  document.getElementById("fullview-urgency").innerHTML = App.formatDaysAgoBadge(card.days_since_revised);
  document.getElementById("fullview-last-rev").innerText = `Last Revised: ${card.last_revised_date || "Today"} (${card.revision_count || 0} times)`;
  document.getElementById("fullview-content").innerText = card.content;

  App.openModal("modal-fullview-flashcard");
}

async function handleFullViewRevise() {
  if (!activeFullViewCardId) return;
  const card = allFlashcards.find(c => c.id === activeFullViewCardId);
  if (!card) return;

  await markCardRevised(card.id, card.title);
  // Update modal urgency badge in real-time
  document.getElementById("fullview-urgency").innerHTML = App.formatDaysAgoBadge(0);
  document.getElementById("fullview-last-rev").innerText = `Last Revised: Today (${(card.revision_count || 0) + 1} times)`;
}

// -------------------------------------------------------------------
// TOPIC LEVEL ACTIONS
// -------------------------------------------------------------------

async function updateCurrentTopicStatus(newStatus) {
  if (!currentConceptId) return;
  try {
    await App.api(`/api/concepts/${currentConceptId}`, {
      method: "PUT",
      body: JSON.stringify({ status: newStatus })
    });
    App.showToast(`Topic status set to ${newStatus}`);
    await loadTopicData();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function promptTopicConfidence() {
  if (!currentConcept) return;
  const val = prompt(`Set confidence for ${currentConcept.name} (1 to 5):`, currentConcept.confidence || 1);
  if (!val) return;
  const num = parseInt(val);
  if (isNaN(num) || num < 1 || num > 5) {
    App.showToast("Enter a number between 1 and 5", "error");
    return;
  }

  try {
    await App.api(`/api/concepts/${currentConceptId}`, {
      method: "PUT",
      body: JSON.stringify({ confidence: num })
    });
    App.showToast(`Confidence updated to ${num}/5`);
    await loadTopicData();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function markOverallTopicRevised() {
  if (!currentConceptId || !currentConcept) return;
  try {
    await App.api(`/api/concepts/${currentConceptId}/revise`, { method: "POST" });
    App.showToast(`Overall topic '${currentConcept.name}' marked revised today!`);
    await loadTopicData();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
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
