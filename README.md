# Flowise — Workflow Approval System

A full-stack workflow approval application built with Flask (Python) + PostgreSQL backend and plain HTML/CSS/JS frontend.

Demo video --> [Flowence Video Link ](https://drive.google.com/file/d/1N49w6pWcexuqeXoDzwA48KjE8ENtk7w7/view?usp=sharing)

## Project Structure

```
flowise/
├── backend/          ← Flask + PostgreSQL API
│   ├── app.py
│   ├── config.py
│   ├── schema.sql    ← DB schema + seed data
│   ├── requirements.txt
│   ├── routes/
│   │   ├── auth.py
│   │   ├── workflow.py
│   │   ├── execution.py
│   │   └── admin.py
│   └── utils/
│       └── db.py
│
└── frontend/         ← HTML/CSS/JS (no framework)
    ├── login.html
    ├── dashboard.html
    ├── workflow_ui.html
    ├── executions.html
    ├── execution_detail.html
    ├── execution_progress.html
    ├── audit_logs.html
    ├── admin.html
    ├── notifications.html
    ├── css/style.css
    └── js/utils.js
```

## Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE flowise_db;"
psql -U postgres -d flowise_db -f schema.sql

# Run the server
python app.py
```
Backend runs at: **http://localhost:5000**

### 2. Frontend Setup
```bash
cd frontend
python3 -m http.server 8080
```
Open: **http://localhost:8080/login.html**

## Default Credentials
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@flow.com | admin123 |
| Developer | dev@flow.com | dev123 |
| User | user@flow.com | user123 |

## Role Capabilities

**Admin**
- Full system overview (users, workflows, executions)
- Create/manage users
- Access all developer and user features

**Developer**
- Create, edit, delete workflows
- Define steps, input schemas
- Approve or reject execution requests
- View audit logs

**User**
- Submit workflow execution requests
- Track request status and progress
- Receive notifications on status changes

## Workflow Flow
1. User submits an expense form → execution created
2. Developer sees it in Executions panel → reviews inputs
3. Developer approves → advances to next step
4. On reaching Finance Approval step → user gets notified
5. Final approval → status becomes "Accepted"
6. Any rejection → status becomes "Rejected" with reason

## Tech Stack
- **Backend**: Python 3.10+, Flask 3, Flask-JWT-Extended, psycopg2, bcrypt
- **Database**: PostgreSQL 14+
- **Frontend**: HTML5, CSS3, Vanilla JS (no frameworks), Google Fonts
