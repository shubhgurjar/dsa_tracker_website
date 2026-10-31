/**
 * Login / Unlock Page Client Logic
 */

document.addEventListener("DOMContentLoaded", async () => {
  const pinInput = document.getElementById("pin-input");
  if (pinInput) pinInput.focus();

  // If already logged in, check auth status
  try {
    const res = await App.api("/api/auth/status");
    if (res.is_authenticated) {
      window.location.href = "/dashboard";
    }
  } catch (e) {
    // Expected if not authenticated
  }

  const form = document.getElementById("form-login");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const pin = document.getElementById("pin-input").value.trim();
      const errorEl = document.getElementById("login-error");
      errorEl.style.display = "none";

      try {
        const res = await App.api("/api/auth/login", {
          method: "POST",
          body: JSON.stringify({ pin })
        });
        if (res.token) {
          App.setToken(res.token);
        }
        App.showToast("Access granted! Welcome.");
        setTimeout(() => {
          window.location.href = "/dashboard";
        }, 300);
      } catch (err) {
        errorEl.innerText = err.message || "Invalid PIN. Default is 1234.";
        errorEl.style.display = "block";
        document.getElementById("pin-input").value = "";
        document.getElementById("pin-input").focus();
      }
    });
  }
});
