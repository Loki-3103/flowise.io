# Flowise Backend - Flask + PostgreSQL

## Setup

### 1. Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure PostgreSQL
Create a database:
```sql
CREATE DATABASE flowise_db;
```

### 3. Run schema
```bash
psql -U postgres -d flowise_db -f schema.sql
```

### 4. Set environment variables (optional, defaults provided)
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=flowise_db
export DB_USER=postgres
export DB_PASSWORD=postgres
export SECRET_KEY=your-secret-key
export JWT_SECRET_KEY=your-jwt-secret
```

### 5. Run the app
```bash
python app.py
```

Server runs at: http://localhost:5000

## Default Credentials
| Role      | Email           | Password |
|-----------|----------------|----------|
| Admin     | admin@flow.com  | admin123 |
| Developer | dev@flow.com    | dev123   |
| User      | user@flow.com   | user123  |

## API Endpoints

### Auth
- POST /api/auth/login
- POST /api/auth/logout
- GET  /api/auth/me

### Workflows
- GET  /api/workflow/list
- GET  /api/workflow/:id
- POST /api/workflow/create
- PUT  /api/workflow/:id
- DELETE /api/workflow/:id

### Executions
- POST /api/execution/execute
- GET  /api/execution/list
- GET  /api/execution/status/:id
- POST /api/execution/approve
- POST /api/execution/reject
- POST /api/execution/cancel/:id
- GET  /api/execution/logs/:id

### Admin
- GET  /api/admin/overview
- GET  /api/admin/users
- POST /api/admin/users

### Notifications
- GET  /api/notifications/
- GET  /api/notifications/unread-count
- POST /api/notifications/mark-read
