// API base URL - change to your backend URL
const API_BASE = 'http://127.0.0.1:5000/api';

// ── Auth Helpers ──────────────────────────────────────────────────────────────
function getToken() { return localStorage.getItem('fw_token'); }
function getUser() {
  try { return JSON.parse(localStorage.getItem('fw_user') || 'null'); }
  catch { return null; }
}
function setAuth(token, user) {
  localStorage.setItem('fw_token', token);
  localStorage.setItem('fw_user', JSON.stringify(user));
}
function clearAuth() {
  localStorage.removeItem('fw_token');
  localStorage.removeItem('fw_user');
}
function requireAuth(allowedRoles) {
  const user = getUser();
  if (!user || !getToken()) { window.location.href = 'login.html'; return null; }
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    const map = { admin: 'admin.html', developer: 'workflow_ui.html', user: 'dashboard.html' };
    window.location.href = map[user.role] || 'login.html';
    return null;
  }
  return user;
}

// ── API Fetch ─────────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(API_BASE + path, { ...options, headers });
  if (res.status === 401) { clearAuth(); window.location.href = 'login.html'; return null; }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

// ── Date Helpers ──────────────────────────────────────────────────────────────
function fmtDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}
function fmtDateTime(d) {
  if (!d) return '—';
  return new Date(d).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}
function timeAgo(d) {
  if (!d) return '';
  const diff = Date.now() - new Date(d).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

// ── Badge HTML ────────────────────────────────────────────────────────────────
function statusBadge(status) {
  return `<span class="badge badge-${status}">${status}</span>`;
}
function roleBadge(role) {
  return `<span class="badge badge-${role}">${role}</span>`;
}

// ── Sidebar Init ──────────────────────────────────────────────────────────────
function initSidebar(activePage) {
  const user = getUser();
  if (!user) return;

  const adminNav = `
    <div class="nav-section-label">Admin</div>
    <div class="nav-item ${activePage==='admin'?'active':''}" onclick="goto('admin.html')">
      ${icon('layout-grid')} <span>Overview</span>
    </div>
    <div class="nav-item ${activePage==='admin-users'?'active':''}" onclick="goto('admin.html#users')">
      ${icon('users')} <span>Users</span>
    </div>
    <div class="nav-item ${activePage==='admin-logs'?'active':''}" onclick="goto('admin.html#logs')">
      ${icon('file-text')} <span>Audit Logs</span>
    </div>`;

  const devNav = `
    <div class="nav-section-label">Developer</div>
    <div class="nav-item ${activePage==='workflow_ui'?'active':''}" onclick="goto('workflow_ui.html')">
      ${icon('git-branch')} <span>Workflows</span>
    </div>
    <div class="nav-item ${activePage==='executions'?'active':''}" onclick="goto('executions.html')">
      ${icon('activity')} <span>Executions</span>
    </div>
    <div class="nav-item ${activePage==='audit_logs'?'active':''}" onclick="goto('audit_logs.html')">
      ${icon('file-text')} <span>Audit Logs</span>
    </div>`;

  const userNav = `
    <div class="nav-section-label">Main</div>
    <div class="nav-item ${activePage==='dashboard'?'active':''}" onclick="goto('dashboard.html')">
      ${icon('home')} <span>Dashboard</span>
    </div>
    <div class="nav-item ${activePage==='submit'?'active':''}" onclick="goto('dashboard.html#submit')">
      ${icon('plus-circle')} <span>New Request</span>
    </div>
    <div class="nav-item ${activePage==='execution_progress'?'active':''}" onclick="goto('execution_progress.html')">
      ${icon('loader')} <span>My Requests</span>
    </div>
    <div class="nav-item ${activePage==='notifications'?'active':''}" onclick="goto('notifications.html')">
      ${icon('bell')} <span>Notifications</span>
    </div>`;

  const roleNavs = { admin: adminNav + devNav + userNav, developer: devNav + userNav, user: userNav };
  const nav = roleNavs[user.role] || userNav;

  const initials = (user.full_name || user.email).split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);

  document.getElementById('sidebar-nav').innerHTML = nav;
  document.getElementById('sidebar-user-name').textContent = user.full_name || user.email;
  document.getElementById('sidebar-user-role').textContent = user.role;
  document.getElementById('sidebar-avatar').textContent = initials;
}

function goto(page) { window.location.href = page; }

function logout() {
  clearAuth();
  window.location.href = 'login.html';
}

// ── Icons (inline SVG set) ────────────────────────────────────────────────────
const ICONS = {
  'home': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
  'git-branch': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="3" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg>',
  'activity': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
  'file-text': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
  'bell': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>',
  'plus-circle': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>',
  'loader': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="22"/><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"/><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"/><line x1="2" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="22" y2="12"/><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"/><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"/></svg>',
  'layout-grid': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>',
  'users': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
  'check': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
  'x': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>',
  'search': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
  'edit': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>',
  'trash': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>',
  'eye': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>',
  'plus': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
  'log-out': '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
};
function icon(name) { return ICONS[name] || ''; }

// ── Notifications ─────────────────────────────────────────────────────────────
async function loadNotifCount() {
  try {
    const data = await apiFetch('/notifications/unread-count');
    const badge = document.getElementById('notif-badge');
    if (badge) {
      badge.textContent = data.count;
      badge.style.display = data.count > 0 ? 'flex' : 'none';
    }
  } catch {}
}

async function toggleNotifPanel() {
  let panel = document.getElementById('notif-panel');
  if (panel) { panel.remove(); return; }

  const data = await apiFetch('/notifications/');
  const notifs = data || [];

  panel = document.createElement('div');
  panel.id = 'notif-panel';
  panel.className = 'notif-panel';
  panel.innerHTML = `
    <div class="notif-panel-header">
      <span class="notif-panel-title">Notifications</span>
      <button class="btn btn-sm btn-secondary" onclick="markAllRead()">Mark all read</button>
    </div>
    ${notifs.length === 0 ? '<div class="notif-empty">No notifications</div>' :
      notifs.slice(0, 10).map(n => `
        <div class="notif-item ${n.is_read ? '' : 'unread'}" onclick="markRead(${n.id}, this)">
          <div class="notif-msg">${n.message}</div>
          <div class="notif-time">${timeAgo(n.created_at)}</div>
        </div>`).join('')}
  `;
  document.getElementById('notif-wrap').appendChild(panel);
  document.addEventListener('click', closeNotifOutside, true);
}

async function markRead(id, el) {
  await apiFetch('/notifications/mark-read', { method: 'POST', body: JSON.stringify({ id }) });
  el.classList.remove('unread');
  loadNotifCount();
}
async function markAllRead() {
  await apiFetch('/notifications/mark-read', { method: 'POST', body: JSON.stringify({}) });
  document.querySelectorAll('.notif-item.unread').forEach(el => el.classList.remove('unread'));
  loadNotifCount();
  document.getElementById('notif-panel')?.remove();
}
function closeNotifOutside(e) {
  const panel = document.getElementById('notif-panel');
  const btn = document.getElementById('notif-btn');
  if (panel && !panel.contains(e.target) && btn && !btn.contains(e.target)) {
    panel.remove();
    document.removeEventListener('click', closeNotifOutside, true);
  }
}

// ── Alert Helper ──────────────────────────────────────────────────────────────
function showAlert(containerId, message, type = 'error') {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
  setTimeout(() => { if (el) el.innerHTML = ''; }, 4000);
}
