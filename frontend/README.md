# Flowise Frontend

## Tech Stack
- Plain HTML, CSS, JavaScript (no frameworks)
- Google Fonts: DM Sans + DM Mono
- Monochromatic design system

## Setup

### Option A: Serve with a simple HTTP server
```bash
cd frontend
python3 -m http.server 8080
# Open http://localhost:8080/login.html
```

Or with Node.js:
```bash
npx serve . -p 8080
```

### Option B: Use Live Server (VS Code extension)
Open `login.html` with Live Server.

## Configuration

The API base URL is set at the top of `js/utils.js`:
```javascript
const API_BASE = 'http://localhost:5000/api';
```
Change this to your backend URL if deployed elsewhere.

## Pages

| File | Role | Description |
|------|------|-------------|
| login.html | All | Login page with role-based redirect |
| dashboard.html | User/All | Submit requests, view own executions |
| execution_progress.html | User | Track request status with progress bars |
| execution_detail.html | All | Full detail view with step progress + logs |
| workflow_ui.html | Developer/Admin | Create, edit, delete workflows |
| executions.html | Developer/Admin | Approve/reject all execution requests |
| audit_logs.html | Developer/Admin | Full audit trail |
| admin.html | Admin | System overview, user management, logs |
| notifications.html | All | Notification inbox |

## Default Credentials
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@flow.com | admin123 |
| Developer | dev@flow.com | dev123 |
| User | user@flow.com | user123 |

## Design System
- Colors: Monochromatic (black/white/gray scale)
- Font: DM Sans (body) + DM Mono (code/values)
- Status badges: Gray=Pending, Blue=Active, Green=Accepted, Red=Rejected
- Layout: Fixed sidebar + scrollable main content
