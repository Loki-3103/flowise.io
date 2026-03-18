-- Flowise Workflow Approval System Schema

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'developer', 'user')),
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflows (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS steps (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES workflows(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    step_order INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL,
    assignee_email VARCHAR(255),
    step_type VARCHAR(50) DEFAULT 'approval' CHECK (step_type IN ('approval', 'notification', 'task')),
    UNIQUE(workflow_id, step_order)
);

CREATE TABLE IF NOT EXISTS input_schema (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES workflows(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(50) NOT NULL CHECK (field_type IN ('string', 'number', 'boolean', 'dropdown')),
    is_required BOOLEAN DEFAULT TRUE,
    allowed_values TEXT,
    field_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS rules (
    id SERIAL PRIMARY KEY,
    step_id INTEGER REFERENCES steps(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    operator VARCHAR(50) NOT NULL,
    value TEXT NOT NULL,
    priority INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS executions (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES workflows(id),
    user_id INTEGER REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'accepted', 'rejected')),
    current_step INTEGER DEFAULT 1,
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS execution_inputs (
    id SERIAL PRIMARY KEY,
    execution_id INTEGER REFERENCES executions(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    value TEXT
);

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    execution_id INTEGER REFERENCES executions(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    note TEXT,
    step_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    execution_id INTEGER REFERENCES executions(id),
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Default users (bcrypt hash of passwords)
-- admin123 -> $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW
-- dev123   -> $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW
-- user123  -> $2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW

INSERT INTO users (email, password, role, full_name) VALUES
('admin@flow.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS2T6eC', 'admin', 'Admin CEO'),
('dev@flow.com',   '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS2T6eC', 'developer', 'Lead Developer'),
('user@flow.com',  '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS2T6eC', 'user', 'Regular User')
ON CONFLICT (email) DO NOTHING;

-- Default Expense Approval workflow
INSERT INTO workflows (name, description, created_by) VALUES
('Expense Approval', 'Standard expense submission and approval flow', 1)
ON CONFLICT (name) DO NOTHING;

-- Steps for default workflow
INSERT INTO steps (workflow_id, name, step_order, role, step_type) VALUES
(1, 'Expense Submission', 1, 'user', 'task'),
(1, 'Manager Approval', 2, 'developer', 'approval'),
(1, 'Finance Approval', 3, 'developer', 'approval'),
(1, 'Task Completion', 4, 'user', 'notification')
ON CONFLICT DO NOTHING;

-- Input schema for default workflow
INSERT INTO input_schema (workflow_id, field_name, field_type, is_required, allowed_values, field_order) VALUES
(1, 'title', 'string', TRUE, NULL, 1),
(1, 'amount', 'number', TRUE, NULL, 2),
(1, 'description', 'string', TRUE, NULL, 3),
(1, 'category', 'dropdown', TRUE, 'Travel,Office Supplies,Software,Hardware,Other', 4)
ON CONFLICT DO NOTHING;
