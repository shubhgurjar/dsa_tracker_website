/**
 * LeetCode Problems Vault Page Logic
 */

let allProblems = [];
let activeEditProblemId = null;

document.addEventListener("DOMContentLoaded", async () => {
  setupFilterListeners();
  await loadProblems();
});

function setupFilterListeners() {
  const searchInput = document.getElementById("prob-search");
  const diffFilter = document.getElementById("prob-diff-filter");
  const dsFilter = document.getElementById("prob-ds-filter");
  const algoFilter = document.getElementById("prob-algo-filter");
  const urgencyFilter = document.getElementById("prob-urgency-filter");
  const sortSelect = document.getElementById("prob-sort-by");
  const starredToggle = document.getElementById("prob-starred-toggle");

  [searchInput, diffFilter, dsFilter, algoFilter, urgencyFilter, sortSelect].forEach(el => {
    if (el) {
      el.addEventListener("input", () => loadProblems());
      el.addEventListener("change", () => loadProblems());
    }
  });

  if (starredToggle) {
    starredToggle.addEventListener("click", () => {
      starredToggle.classList.toggle("active");
      loadProblems();
    });
  }
}

async function loadProblems() {
  const search = document.getElementById("prob-search")?.value || "";
  const diff = document.getElementById("prob-diff-filter")?.value || "";
  const ds = document.getElementById("prob-ds-filter")?.value || "";
  const algo = document.getElementById("prob-algo-filter")?.value || "";
  const urgency = document.getElementById("prob-urgency-filter")?.value || "";
  const sortBy = document.getElementById("prob-sort-by")?.value || "solved_date_desc";
  const starred = document.getElementById("prob-starred-toggle")?.classList.contains("active") ? 1 : "";

  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (diff && diff !== "all") params.append("difficulty", diff);
  if (ds && ds !== "all") params.append("data_structure", ds);
  if (algo && algo !== "all") params.append("algorithm", algo);
  if (urgency && urgency !== "all") params.append("urgency", urgency);
  if (starred) params.append("starred", starred);
  if (sortBy) params.append("sort_by", sortBy);

  try {
    const data = await App.api(`/api/problems?${params.toString()}`);
    allProblems = data.problems;
    renderProblemsTable(allProblems);
    updateVaultMetrics(allProblems);
  } catch (err) {
    console.error("Failed to load problems:", err);
  }
}

function updateVaultMetrics(problems) {
  const totalCount = problems.length;
  const easyCount = problems.filter(p => p.difficulty === "Easy").length;
  const medCount = problems.filter(p => p.difficulty === "Medium").length;
  const hardCount = problems.filter(p => p.difficulty === "Hard").length;

  const countBadge = document.getElementById("vault-total-count");
  if (countBadge) {
    countBadge.innerText = `${totalCount} Problems`;
  }
}

function renderProblemsTable(problems) {
  const tbody = document.getElementById("problems-tbody");
  if (!tbody) return;

  if (problems.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; padding: 3rem; color: var(--text-dim);">
          No problems found matching your filters. Click "+ Log Problem" to add one!
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = problems.map(p => {
    const starIcon = p.starred ? "⭐" : "☆";
    const starClass = p.starred ? "starred" : "";
    const titleHtml = p.problem_url 
      ? `<a href="${escapeHtml(p.problem_url)}" target="_blank" rel="noopener noreferrer" style="color:#fff; font-weight:600; text-decoration:underline; text-decoration-color:rgba(255,255,255,0.2);">${escapeHtml(p.title)} ↗</a>`
      : `<span style="color:#fff; font-weight:600;">${escapeHtml(p.title)}</span>`;

    const tagParts = [];
    if (p.data_structure) tagParts.push(`<span class="badge" style="background:rgba(99,102,241,0.12); color:#818cf8;">${escapeHtml(p.data_structure)}</span>`);
    if (p.algorithm) tagParts.push(`<span class="badge" style="background:rgba(56,189,248,0.12); color:#38bdf8;">${escapeHtml(p.algorithm)}</span>`);
    if (p.pattern) tagParts.push(`<span style="font-size:0.75rem; color:var(--text-dim);">${escapeHtml(p.pattern)}</span>`);

    return `
      <tr>
        <td style="width: 40px; text-align: center;">
          <button class="btn-icon ${starClass}" style="background:none; border:none; cursor:pointer; font-size:1.1rem;" onclick="toggleProblemStar(${p.id})">
            ${starIcon}
          </button>
        </td>
        <td>
          <div style="display:flex; align-items:center; gap:0.4rem;">
            ${p.leetcode_number ? `<span style="font-family:var(--font-mono); font-size:0.8rem; color:var(--text-dim);">#${p.leetcode_number}</span>` : ""}
            ${titleHtml}
          </div>
          <div style="display:flex; gap:0.35rem; margin-top:0.35rem; align-items:center; flex-wrap:wrap;">
            ${tagParts.join(" ")}
          </div>
        </td>
        <td>${App.formatDifficultyBadge(p.difficulty)}</td>
        <td style="font-size:0.82rem; color:var(--text-muted);">${p.solved_date}</td>
        <td class="days-ago-cell">
          ${App.formatDaysAgoBadge(p.days_since_revised)}
          <span style="font-size:0.72rem; color:var(--text-dim); margin-left:4px;">(${p.revision_count || 0}x)</span>
        </td>
        <td style="text-align:right;">
          <div style="display:inline-flex; gap:0.4rem;">
            <button class="btn btn-sm btn-revise" onclick="markProblemRevisedToday(${p.id}, '${escapeHtml(p.title)}')">
              ✓ Revised
            </button>
            <button class="btn btn-sm btn-secondary" onclick="openProblemDetailsModal(${p.id})">
              Details
            </button>
            <button class="btn btn-sm btn-secondary" style="color:#ef4444;" onclick="deleteProblemConfirm(${p.id}, '${escapeHtml(p.title)}')">
              🗑
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

async function toggleProblemStar(problemId) {
  try {
    const res = await App.api(`/api/problems/${problemId}/star`, { method: "POST" });
    await loadProblems();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function markProblemRevisedToday(problemId, title) {
  try {
    await App.api(`/api/problems/${problemId}/revise`, { method: "POST" });
    App.showToast(`'${title}' marked as revised today!`);
    await loadProblems();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function deleteProblemConfirm(problemId, title) {
  if (!confirm(`Are you sure you want to delete problem "${title}"?`)) return;
  try {
    await App.api(`/api/problems/${problemId}`, { method: "DELETE" });
    App.showToast(`Problem "${title}" deleted.`);
    await loadProblems();
  } catch (err) {
    App.showToast(`Failed to delete: ${err.message}`, "error");
  }
}

async function openProblemDetailsModal(problemId) {
  try {
    const p = await App.api(`/api/problems/${problemId}`);
    activeEditProblemId = problemId;

    document.getElementById("detail-prob-title").value = p.title || "";
    document.getElementById("detail-prob-number").value = p.leetcode_number || "";
    document.getElementById("detail-prob-url").value = p.problem_url || "";
    document.getElementById("detail-prob-diff").value = p.difficulty || "Medium";
    document.getElementById("detail-prob-ds").value = p.data_structure || "";
    document.getElementById("detail-prob-algo").value = p.algorithm || "";
    document.getElementById("detail-prob-pattern").value = p.pattern || "";
    document.getElementById("detail-prob-time").value = p.time_complexity || "";
    document.getElementById("detail-prob-space").value = p.space_complexity || "";
    document.getElementById("detail-prob-notes").value = p.approach_notes || "";
    document.getElementById("detail-prob-code").value = p.code_snippet || "";
    document.getElementById("detail-prob-solved-date").value = p.solved_date || "";
    document.getElementById("detail-prob-revised-date").value = p.last_revised_date || "";

    App.openModal("modal-problem-details");
  } catch (err) {
    App.showToast(`Failed to load details: ${err.message}`, "error");
  }
}

async function handleSaveProblemDetails(e) {
  e.preventDefault();
  if (!activeEditProblemId) return;

  const payload = {
    title: document.getElementById("detail-prob-title").value,
    leetcode_number: document.getElementById("detail-prob-number").value ? parseInt(document.getElementById("detail-prob-number").value) : null,
    problem_url: document.getElementById("detail-prob-url").value,
    difficulty: document.getElementById("detail-prob-diff").value,
    data_structure: document.getElementById("detail-prob-ds").value,
    algorithm: document.getElementById("detail-prob-algo").value,
    pattern: document.getElementById("detail-prob-pattern").value,
    time_complexity: document.getElementById("detail-prob-time").value,
    space_complexity: document.getElementById("detail-prob-space").value,
    approach_notes: document.getElementById("detail-prob-notes").value,
    code_snippet: document.getElementById("detail-prob-code").value,
    solved_date: document.getElementById("detail-prob-solved-date").value,
    last_revised_date: document.getElementById("detail-prob-revised-date").value
  };

  try {
    await App.api(`/api/problems/${activeEditProblemId}`, {
      method: "PUT",
      body: JSON.stringify(payload)
    });
    App.showToast("Problem details updated successfully!");
    App.closeModal("modal-problem-details");
    await loadProblems();
  } catch (err) {
    App.showToast(`Failed to update: ${err.message}`, "error");
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
