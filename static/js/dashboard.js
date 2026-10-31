/**
 * Dashboard & Quick Overview Page Logic
 */

document.addEventListener("DOMContentLoaded", async () => {
  await loadDashboard();
});

async function loadDashboard() {
  try {
    const data = await App.api("/api/stats/dashboard");
    renderTripBanner(data.trip);
    renderMetrics(data);
    renderUrgentRevisions(data.revisions.urgent_items);
    renderRecentProblems(data.recent_problems);
    renderLeetCodeCard(data.leetcode_profile, data.leetcode_username);
  } catch (err) {
    console.error("Failed to load dashboard stats:", err);
  }
}

function renderTripBanner(trip) {
  const container = document.getElementById("trip-banner-container");
  if (!container) return;

  const dayBadge = document.getElementById("nav-trip-day");
  if (dayBadge) {
    dayBadge.innerText = `Day ${trip.days_elapsed} of ${trip.duration_days}`;
  }

  container.innerHTML = `
    <div class="trip-banner">
      <div class="trip-banner-top">
        <div>
          <h2 class="trip-title">🚀 ${trip.name}</h2>
          <p class="trip-dates">Started: <strong>${trip.start_date}</strong> &bull; Target Completion: <strong>${trip.target_end_date}</strong></p>
          ${trip.manifesto ? `<p style="font-size:0.83rem; color:var(--text-muted); margin-top:0.4rem; font-style:italic;">"${trip.manifesto}"</p>` : ""}
        </div>
        <div class="trip-countdown-stat">
          <div>
            <div class="countdown-number">${trip.days_elapsed}<span style="font-size:1.1rem; color:var(--text-dim); font-weight:500;">/${trip.duration_days}</span></div>
            <div class="countdown-label">${trip.days_remaining} days remaining</div>
          </div>
        </div>
      </div>
      <div class="progress-track">
        <div class="progress-bar-fill" style="width: ${trip.progress_percent}%"></div>
      </div>
      <div class="progress-meta">
        <span>Sprint Progress: <strong>${trip.progress_percent}%</strong></span>
        <span>Goal: <strong>${trip.target_problems} LeetCode Problems</strong></span>
      </div>
    </div>
  `;
}

function renderMetrics(data) {
  const prob = data.problems;
  const ds = data.data_structures;
  const algo = data.algorithms;
  const rev = data.revisions;

  // Problems stat card
  const probVal = document.getElementById("stat-problems-val");
  const probSub = document.getElementById("stat-problems-sub");
  if (probVal && probSub) {
    probVal.innerText = prob.total;
    probSub.innerHTML = `
      <span class="badge badge-easy">${prob.easy} E</span>
      <span class="badge badge-medium">${prob.medium} M</span>
      <span class="badge badge-hard">${prob.hard} H</span>
      <span style="margin-left:0.3rem;">(${prob.target_percent}% of ${prob.target})</span>
    `;
  }

  // DS stat card
  const dsVal = document.getElementById("stat-ds-val");
  const dsSub = document.getElementById("stat-ds-sub");
  if (dsVal && dsSub) {
    dsVal.innerText = `${ds.mastered}/${ds.total}`;
    dsSub.innerHTML = `<span style="color:#10b981;">${ds.mastered} Mastered</span> &bull; <span style="color:#38bdf8;">${ds.in_progress} In Progress</span>`;
  }

  // Algo stat card
  const algoVal = document.getElementById("stat-algo-val");
  const algoSub = document.getElementById("stat-algo-sub");
  if (algoVal && algoSub) {
    algoVal.innerText = `${algo.mastered}/${algo.total}`;
    algoSub.innerHTML = `<span style="color:#10b981;">${algo.mastered} Mastered</span> &bull; <span style="color:#38bdf8;">${algo.in_progress} In Progress</span>`;
  }

  // Revisions stat card
  const revVal = document.getElementById("stat-rev-val");
  const revSub = document.getElementById("stat-rev-sub");
  if (revVal && revSub) {
    revVal.innerText = rev.overdue_count + rev.due_count;
    revSub.innerHTML = `<span style="color:#ef4444;">${rev.overdue_count} Overdue (>14d)</span> &bull; <span style="color:#f59e0b;">${rev.due_count} Due (8-14d)</span>`;
  }
}

function renderUrgentRevisions(items) {
  const tbody = document.getElementById("urgent-revisions-tbody");
  if (!tbody) return;

  if (!items || items.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:var(--text-dim); padding:2rem;">🎉 All items have been revised recently! Keep it up.</td></tr>`;
    return;
  }

  tbody.innerHTML = items.map(item => `
    <tr>
      <td>
        <div style="font-weight:600; color:#fff;">${escapeHtml(item.name)}</div>
        <div style="font-size:0.75rem; color:var(--text-dim);">${item.detail}</div>
      </td>
      <td>
        <span class="badge ${item.item_type === 'problem' ? 'badge-in_progress' : 'badge-mastered'}">
          ${item.item_type === 'problem' ? 'LeetCode' : 'Concept'}
        </span>
      </td>
      <td class="days-ago-cell">
        ${App.formatDaysAgoBadge(item.days_since_revised)}
      </td>
      <td style="text-align:right;">
        <button class="btn btn-sm btn-revise" onclick="markDashboardItemRevised('${item.item_type}', ${item.id}, '${escapeHtml(item.name)}')">
          ✓ Revised Today
        </button>
      </td>
    </tr>
  `).join("");
}

function renderRecentProblems(problems) {
  const tbody = document.getElementById("recent-problems-tbody");
  if (!tbody) return;

  if (!problems || problems.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align:center; color:var(--text-dim); padding:2rem;">No problems logged yet. Click "+ Add Problem" to start!</td></tr>`;
    return;
  }

  tbody.innerHTML = problems.map(p => `
    <tr>
      <td>
        <div style="font-weight:600; color:#fff;">
          ${p.leetcode_number ? `<span style="color:var(--text-dim); margin-right:4px;">#${p.leetcode_number}</span>` : ""}
          ${escapeHtml(p.title)}
        </div>
      </td>
      <td>${App.formatDifficultyBadge(p.difficulty)}</td>
      <td style="font-size:0.8rem; color:var(--text-muted);">${escapeHtml(p.data_structure || p.algorithm || "—")}</td>
      <td style="font-size:0.82rem; color:var(--text-dim);">${p.solved_date}</td>
    </tr>
  `).join("");
}

function renderLeetCodeCard(profile, username) {
  const container = document.getElementById("leetcode-overview-card");
  if (!container) return;

  if (!username) {
    container.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-weight:600; color:#fff;">LeetCode Profile Unlinked</div>
          <div style="font-size:0.82rem; color:var(--text-muted);">Add your LeetCode username in Profile settings to sync solved problems count!</div>
        </div>
        <a href="/profile" class="btn btn-sm btn-secondary">Connect Profile</a>
      </div>
    `;
    return;
  }

  if (profile) {
    container.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div>
          <div style="font-size:0.8rem; color:var(--text-dim); text-transform:uppercase;">LeetCode Profile</div>
          <div style="font-size:1.15rem; font-weight:700; color:#fff;">@${escapeHtml(username)}</div>
          <div style="font-size:0.78rem; color:var(--text-muted);">Global Ranking: <strong>#${profile.ranking ? profile.ranking.toLocaleString() : 'N/A'}</strong></div>
        </div>
        <div style="display:flex; gap:1rem; align-items:center;">
          <div style="text-align:center;">
            <div style="font-size:1.4rem; font-weight:800; color:#fff;">${profile.total_solved}</div>
            <div style="font-size:0.72rem; color:var(--text-dim);">TOTAL SOLVED</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:1.1rem; font-weight:700; color:var(--easy-color);">${profile.easy_solved}</div>
            <div style="font-size:0.72rem; color:var(--text-dim);">EASY</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:1.1rem; font-weight:700; color:var(--medium-color);">${profile.medium_solved}</div>
            <div style="font-size:0.72rem; color:var(--text-dim);">MEDIUM</div>
          </div>
          <div style="text-align:center;">
            <div style="font-size:1.1rem; font-weight:700; color:var(--hard-color);">${profile.hard_solved}</div>
            <div style="font-size:0.72rem; color:var(--text-dim);">HARD</div>
          </div>
          <a href="/profile" class="btn btn-sm btn-secondary" title="Sync Profile">↻</a>
        </div>
      </div>
    `;
  } else {
    container.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
          <div style="font-weight:600; color:#fff;">LeetCode: @${escapeHtml(username)}</div>
          <div style="font-size:0.82rem; color:var(--text-muted);">Syncing pending. Click Sync in profile to load live counts.</div>
        </div>
        <a href="/profile" class="btn btn-sm btn-secondary">Sync Now</a>
      </div>
    `;
  }
}

async function markDashboardItemRevised(itemType, id, name) {
  try {
    await App.api("/api/revision/mark", {
      method: "POST",
      body: JSON.stringify({ item_type: itemType, item_id: id })
    });
    App.showToast(`'${name}' marked as revised today!`);
    await loadDashboard();
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
