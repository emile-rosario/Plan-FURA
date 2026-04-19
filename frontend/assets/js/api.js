/**
 * Funeraria Rancier — API Client & UI Utilities
 * Módulo centralizado de comunicación con el backend.
 */

// Detecta entorno: localhost usa dev backend, cualquier otro usa APP_CONFIG.apiUrl
const _isLocal = ["localhost", "127.0.0.1"].includes(location.hostname);
const API_URL = _isLocal
  ? "http://127.0.0.1:8000"
  : (window.APP_CONFIG?.apiUrl || `${location.protocol}//${location.hostname}`);

// ── Sesión ─────────────────────────────────────────────────────
const Auth = {
  getToken: () => localStorage.getItem("fr_token"),
  getUser: () => {
    try { return JSON.parse(localStorage.getItem("fr_user") || "null"); }
    catch { return null; }
  },
  isLoggedIn: () => !!localStorage.getItem("fr_token"),
  isAdmin: () => {
    const u = Auth.getUser();
    return u && u.rol === "admin";
  },
  save: (token, user) => {
    localStorage.setItem("fr_token", token);
    localStorage.setItem("fr_user", JSON.stringify(user));
  },
  clear: () => {
    localStorage.removeItem("fr_token");
    localStorage.removeItem("fr_user");
  },
  logout: () => {
    Auth.clear();
    window.location.href = "login.html";
  },
  requireAuth: () => {
    if (!Auth.isLoggedIn()) {
      window.location.href = "login.html";
      return false;
    }
    return true;
  },
};

// ── HTTP Client ────────────────────────────────────────────────
async function apiCall(endpoint, options = {}) {
  const token = Auth.getToken();
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  try {
    const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
    const isJson = res.headers.get("content-type")?.includes("application/json");
    const data = isJson ? await res.json() : null;

    if (res.status === 401) { Auth.clear(); }

    return { ok: res.ok, status: res.status, data };
  } catch (err) {
    console.error("API Error:", err);
    return { ok: false, status: 0, data: { detail: "Error de conexión con el servidor." } };
  }
}

// ── Endpoints ──────────────────────────────────────────────────
const API = {
  register: (data) => apiCall("/register", { method: "POST", body: JSON.stringify(data) }),
  login: (data) => apiCall("/login", { method: "POST", body: JSON.stringify(data) }),
  me: () => apiCall("/me"),
  forgotPassword: (email) => apiCall("/forgot-password", { method: "POST", body: JSON.stringify({ email }) }),
  resetPassword: (token, new_password) => apiCall("/reset-password", { method: "POST", body: JSON.stringify({ token, new_password }) }),

  // Los endpoints paginados devuelven { total, items, skip, limit }
  getAtaudes: (disponible) => {
    const q = disponible !== undefined ? `?disponible=${disponible}` : "";
    return apiCall(`/ataudes${q}`);
  },
  getAtaud: (id) => apiCall(`/ataudes/${id}`),
  createAtaud: (d) => apiCall("/ataudes", { method: "POST", body: JSON.stringify(d) }),
  updateAtaud: (id, d) => apiCall(`/ataudes/${id}`, { method: "PUT", body: JSON.stringify(d) }),
  deleteAtaud: (id) => apiCall(`/ataudes/${id}`, { method: "DELETE" }),

  getPlanes: () => apiCall("/planes"),
  getPlan: (id) => apiCall(`/planes/${id}`),

  getMiPlan: () => apiCall("/suscripciones/mi-plan"),
  contratarPlan: (planId) => apiCall("/suscripciones", { method: "POST", body: JSON.stringify({ plan_id: planId }) }),
  cancelarPlan: () => apiCall("/suscripciones/mi-plan", { method: "DELETE" }),

  contacto: (d) => apiCall("/contacto", { method: "POST", body: JSON.stringify(d) }),

  // Auth extra
  post: (endpoint, data) => apiCall(endpoint, { method: "POST", body: JSON.stringify(data) }),
  forgotPassword: (email) => apiCall("/forgot-password", { method: "POST", body: JSON.stringify({ email }) }),
  resetPassword: (token, password) => apiCall("/reset-password", { method: "POST", body: JSON.stringify({ token, password }) }),
};

// ── Formatters ─────────────────────────────────────────────────
const Fmt = {
  precio: (n) => "RD$ " + Number(n).toLocaleString("es-DO", { minimumFractionDigits: 2, maximumFractionDigits: 2 }),
  fecha: (d) => new Date(d).toLocaleDateString("es-DO", { year: "numeric", month: "long", day: "numeric" }),
};

// ── UI Helpers ─────────────────────────────────────────────────
const UI = {
  toast(msg, type = "success", duration = 4000) {
    const t = document.createElement("div");
    const colors = {
      success: "bg-emerald-900/90 text-emerald-100 border-emerald-700",
      error: "bg-red-900/90 text-red-100 border-red-700",
      info: "bg-blue-900/90 text-blue-100 border-blue-700",
    };
    t.className = `fixed top-6 right-6 z-[9999] flex items-center gap-3 px-5 py-4 rounded-xl border backdrop-blur-sm shadow-2xl text-sm font-medium transition-all duration-300 ${colors[type] || colors.info}`;
    const icons = { success: "✓", error: "✕", info: "ℹ" };
    t.innerHTML = `<span class="text-base font-bold">${icons[type] || "ℹ"}</span><span>${msg}</span>`;
    document.body.appendChild(t);
    setTimeout(() => { t.style.opacity = "0"; t.style.transform = "translateX(100%)"; }, duration - 300);
    setTimeout(() => t.remove(), duration);
  },

  loading(btn, isLoading, text = "Procesando...") {
    if (!btn) return;
    btn.disabled = isLoading;
    if (isLoading) {
      btn._originalText = btn.innerHTML;
      btn.innerHTML = `<svg class="animate-spin h-4 w-4 mr-2 inline" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-dasharray="32" stroke-dashoffset="12"/></svg>${text}`;
    } else {
      btn.innerHTML = btn._originalText || btn.innerHTML;
    }
  },

  setFieldError(input, msg) {
    input.classList.add("border-red-500");
    let err = input.parentElement.querySelector(".field-error");
    if (!err) { err = document.createElement("p"); err.className = "field-error text-red-400 text-xs mt-1"; input.parentElement.appendChild(err); }
    err.textContent = msg;
  },

  clearFieldErrors(form) {
    form.querySelectorAll(".field-error").forEach(e => e.remove());
    form.querySelectorAll(".border-red-500").forEach(e => e.classList.remove("border-red-500"));
  },

  updateNavAuth() {
    const user = Auth.getUser();
    const loginLinks = document.querySelectorAll("[data-auth='login']");
    const logoutLinks = document.querySelectorAll("[data-auth='logout']");
    const userNameEl = document.querySelectorAll("[data-auth='username']");
    const adminLinks = document.querySelectorAll("[data-auth='admin']");

    if (Auth.isLoggedIn() && user) {
      loginLinks.forEach(el => el.classList.add("hidden"));
      logoutLinks.forEach(el => el.classList.remove("hidden"));
      userNameEl.forEach(el => { el.textContent = user.nombre?.split(" ")[0] || "Usuario"; });
      if (Auth.isAdmin()) adminLinks.forEach(el => el.classList.remove("hidden"));
    } else {
      loginLinks.forEach(el => el.classList.remove("hidden"));
      logoutLinks.forEach(el => el.classList.add("hidden"));
    }
  },
};

// Actualizar navegación al cargar cualquier página
document.addEventListener("DOMContentLoaded", UI.updateNavAuth);
