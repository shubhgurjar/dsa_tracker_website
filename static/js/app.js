/**
 * Minimal DSA Tracker - Shared Core Client JS
 */

const App = {
  getToken() {
    return localStorage.getItem("dsa_token") || "";
  },

  setToken(token) {
    localStorage.setItem("dsa_token", token);
  },

  clearToken() {
    localStorage.removeItem("dsa_token");
  },

  async api(endpoint, options = {}) {
    const headers = options.headers || {};
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    options.headers = headers;

    try {
      const response = await fetch(endpoint, options);
      if (response.status === 401) {
        if (!window.location.pathname.includes("/login")) {
          window.location.href = "/login";
        }
        throw new Error("Unauthorized");
      }

      const data = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error((data && (data.detail || data.message)) || `Error ${response.status}`);
      }
      return data;
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  },

  formatDaysAgoBadge(days) {
    if (days === 0) {
      return `<span class="badge urgency-fresh" title="Revised today">🌱 Today</span>`;
    } else if (days === 1) {
      return `<span class="badge urgency-fresh" title="Revised yesterday">🌱 Yesterday</span>`;
    } else if (days <= 3) {
      return `<span class="badge urgency-fresh" title="${days} days since last revision">🌱 ${days}d ago</span>`;
    } else if (days <= 7) {
      return `<span class="badge urgency-due_soon" title="${days} days since last revision">⚡ ${days}d ago</span>`;
    } else if (days <= 14) {
      return `<span class="badge urgency-due" title="Due for revision (${days} days ago)">⚠️ ${days}d ago</span>`;
    } else {
      return `<span class="badge urgency-overdue" title="Critically overdue! (${days} days ago)">🚨 ${days}d ago</span>`;
    }
  },

  formatDifficultyBadge(difficulty) {
    const diff = (difficulty || "Medium").toLowerCase();
    return `<span class="badge badge-${diff}">${difficulty}</span>`;
  },

  showToast(message, type = "success") {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    const icon = type === "error" ? "❌" : "✨";
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  },

  openModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.add("open");
  },

  closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) modal.classList.remove("open");
  },

  async initNavbar() {
    try {
      const res = await this.api("/api/auth/status");
      const badge = document.getElementById("nav-trip-day");
      if (badge && res.trip_name) {
        badge.innerText = res.trip_name;
      }
    } catch (e) {
      // If auth required and not authenticated
      if (!window.location.pathname.includes("/login")) {
        window.location.href = "/login";
      }
    }

    // Highlight current page in navbar
    const path = window.location.pathname;
    document.querySelectorAll(".nav-links a").forEach(link => {
      const href = link.getAttribute("href");
      if (href === path || (path === "/" && href === "/dashboard")) {
        link.classList.add("active");
      } else {
        link.classList.remove("active");
      }
    });

    // Setup global Quick Add modal if present
    const addProblemBtn = document.getElementById("btn-nav-add-problem");
    if (addProblemBtn) {
      addProblemBtn.addEventListener("click", () => {
        this.openModal("modal-add-problem");
      });
    }

    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        this.clearToken();
        window.location.href = "/login";
      });
    }
  }
};

// Global click outside to close modals
window.addEventListener("click", (e) => {
  if (e.target.classList.contains("modal-overlay")) {
    e.target.classList.remove("open");
  }
});

document.addEventListener("DOMContentLoaded", () => {
  App.initNavbar();
});
