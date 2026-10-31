/**
 * Profile & 3-Month Trip Settings Page Logic
 */

document.addEventListener("DOMContentLoaded", async () => {
  setupProfileListeners();
  await loadProfileData();
});

function setupProfileListeners() {
  const tripForm = document.getElementById("form-trip-settings");
  if (tripForm) {
    tripForm.addEventListener("submit", handleSaveTripSettings);
  }

  const pinForm = document.getElementById("form-update-pin");
  if (pinForm) {
    pinForm.addEventListener("submit", handleUpdatePin);
  }

  const manualLcForm = document.getElementById("form-manual-lc");
  if (manualLcForm) {
    manualLcForm.addEventListener("submit", handleSaveManualLc);
  }
}

async function loadProfileData() {
  try {
    const cfg = await App.api("/api/config");
    populateTripForm(cfg);

    const lcRes = await App.api("/api/leetcode/profile");
    renderLeetCodeProfile(lcRes);
  } catch (err) {
    console.error("Failed to load profile data:", err);
  }
}

function populateTripForm(cfg) {
  document.getElementById("trip-name-input").value = cfg.trip_name || "";
  document.getElementById("trip-start-input").value = cfg.trip_start_date || "";
  document.getElementById("trip-duration-input").value = cfg.trip_duration_days || 90;
  document.getElementById("trip-target-input").value = cfg.trip_target_problems || 150;
  document.getElementById("trip-manifesto-input").value = cfg.trip_manifesto || "";
  document.getElementById("lc-username-input").value = cfg.leetcode_username || "";
}

function renderLeetCodeProfile(lcRes) {
  const container = document.getElementById("lc-stats-display");
  if (!container) return;

  const data = lcRes.data;
  const username = lcRes.username;

  if (!data) {
    container.innerHTML = `
      <div style="color:var(--text-dim); font-size:0.85rem; padding:1rem; background:var(--bg-input); border-radius:var(--radius-sm);">
        No LeetCode profile data cached yet. Enter your username above and click <strong>"Sync from LeetCode"</strong> or enter stats manually.
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div style="background:var(--bg-input); border-radius:var(--radius-sm); padding:1.25rem;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; flex-wrap:wrap;">
        <div>
          <div style="font-size:1.1rem; font-weight:700; color:#fff;">@${escapeHtml(data.username)}</div>
          <div style="font-size:0.75rem; color:var(--text-dim);">Last synced: ${data.last_synced_at || "Recently"}</div>
        </div>
        <div style="font-size:0.85rem; color:var(--text-muted);">
          Global Ranking: <strong style="color:#fff;">#${data.ranking ? data.ranking.toLocaleString() : "N/A"}</strong>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(100px, 1fr)); gap:0.75rem; text-align:center;">
        <div style="padding:0.75rem; background:var(--bg-card); border-radius:var(--radius-sm);">
          <div style="font-size:1.35rem; font-weight:800; color:#fff;">${data.total_solved}</div>
          <div style="font-size:0.7rem; color:var(--text-dim);">TOTAL SOLVED</div>
        </div>
        <div style="padding:0.75rem; background:var(--bg-card); border-radius:var(--radius-sm);">
          <div style="font-size:1.2rem; font-weight:700; color:var(--easy-color);">${data.easy_solved}</div>
          <div style="font-size:0.7rem; color:var(--text-dim);">EASY</div>
        </div>
        <div style="padding:0.75rem; background:var(--bg-card); border-radius:var(--radius-sm);">
          <div style="font-size:1.2rem; font-weight:700; color:var(--medium-color);">${data.medium_solved}</div>
          <div style="font-size:0.7rem; color:var(--text-dim);">MEDIUM</div>
        </div>
        <div style="padding:0.75rem; background:var(--bg-card); border-radius:var(--radius-sm);">
          <div style="font-size:1.2rem; font-weight:700; color:var(--hard-color);">${data.hard_solved}</div>
          <div style="font-size:0.7rem; color:var(--text-dim);">HARD</div>
        </div>
      </div>
    </div>
  `;
}

async function handleSaveTripSettings(e) {
  e.preventDefault();
  const payload = {
    trip_name: document.getElementById("trip-name-input").value.trim(),
    trip_start_date: document.getElementById("trip-start-input").value,
    trip_duration_days: parseInt(document.getElementById("trip-duration-input").value),
    trip_target_problems: parseInt(document.getElementById("trip-target-input").value),
    trip_manifesto: document.getElementById("trip-manifesto-input").value.trim(),
    leetcode_username: document.getElementById("lc-username-input").value.trim()
  };

  try {
    await App.api("/api/config", {
      method: "PUT",
      body: JSON.stringify(payload)
    });
    App.showToast("Trip settings saved successfully!");
    const badge = document.getElementById("nav-trip-day");
    if (badge) badge.innerText = payload.trip_name;
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function handleSyncLeetCode() {
  const username = document.getElementById("lc-username-input").value.trim();
  if (!username) {
    App.showToast("Please enter a LeetCode username first.", "error");
    return;
  }

  const syncBtn = document.getElementById("btn-sync-lc");
  if (syncBtn) {
    syncBtn.innerText = "Syncing...";
    syncBtn.disabled = true;
  }

  try {
    const res = await App.api(`/api/leetcode/sync?username_override=${encodeURIComponent(username)}`, {
      method: "POST"
    });
    App.showToast(res.message);
    const lcRes = await App.api("/api/leetcode/profile");
    renderLeetCodeProfile(lcRes);
  } catch (err) {
    App.showToast(`Sync warning: ${err.message}. You can enter stats manually below!`, "error");
  } finally {
    if (syncBtn) {
      syncBtn.innerText = "↻ Sync from LeetCode";
      syncBtn.disabled = false;
    }
  }
}

async function handleSaveManualLc(e) {
  e.preventDefault();
  const username = document.getElementById("lc-username-input").value.trim() || "User";
  const payload = {
    username: username,
    total_solved: parseInt(document.getElementById("manual-total").value) || 0,
    easy_solved: parseInt(document.getElementById("manual-easy").value) || 0,
    medium_solved: parseInt(document.getElementById("manual-medium").value) || 0,
    hard_solved: parseInt(document.getElementById("manual-hard").value) || 0,
    ranking: parseInt(document.getElementById("manual-ranking").value) || 0
  };

  try {
    const res = await App.api("/api/leetcode/manual", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    App.showToast("LeetCode stats updated manually!");
    const lcRes = await App.api("/api/leetcode/profile");
    renderLeetCodeProfile(lcRes);
    App.closeModal("modal-manual-lc");
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function handleUpdatePin(e) {
  e.preventDefault();
  const oldPin = document.getElementById("pin-current").value;
  const newPin = document.getElementById("pin-new").value;
  const confirmPin = document.getElementById("pin-confirm").value;

  if (newPin !== confirmPin) {
    App.showToast("New PINs do not match!", "error");
    return;
  }

  try {
    const res = await App.api("/api/auth/update-pin", {
      method: "POST",
      body: JSON.stringify({ old_pin: oldPin, new_pin: newPin })
    });
    if (res.token) App.setToken(res.token);
    App.showToast("PIN updated successfully!");
    document.getElementById("form-update-pin").reset();
  } catch (err) {
    App.showToast(`Failed: ${err.message}`, "error");
  }
}

async function handleExportJson() {
  try {
    const token = App.getToken();
    const resp = await fetch("/api/export", {
      headers: token ? { "Authorization": `Bearer ${token}` } : {}
    });
    if (!resp.ok) throw new Error("Export failed");
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `dsa_tracker_backup_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    App.showToast("Backup JSON downloaded!");
  } catch (err) {
    App.showToast(`Export failed: ${err.message}`, "error");
  }
}

async function handleImportJson(e) {
  const file = e.target.files[0];
  if (!file) return;

  try {
    const text = await file.text();
    const payload = JSON.parse(text);

    if (!confirm("Importing backup will replace current problems, concepts, and logs with the backup contents. Proceed?")) {
      e.target.value = "";
      return;
    }

    const res = await App.api("/api/import", {
      method: "POST",
      body: JSON.stringify(payload)
    });
    App.showToast(res.message);
    setTimeout(() => window.location.reload(), 1200);
  } catch (err) {
    App.showToast(`Import error: ${err.message}`, "error");
  } finally {
    e.target.value = "";
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
