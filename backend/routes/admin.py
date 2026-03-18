from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import query, execute

admin_bp = Blueprint('admin', __name__)
notif_bp = Blueprint('notifications', __name__)

@admin_bp.route('/overview', methods=['GET'])
@jwt_required()
def overview():
    identity = get_jwt_identity()
    if identity['role'] != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    total_users = query("SELECT COUNT(*) as cnt FROM users", fetch='one')['cnt']
    total_workflows = query("SELECT COUNT(*) as cnt FROM workflows", fetch='one')['cnt']
    total_executions = query("SELECT COUNT(*) as cnt FROM executions", fetch='one')['cnt']
    by_status = query("SELECT status, COUNT(*) as cnt FROM executions GROUP BY status")
    recent = query("""
        SELECT e.id, e.title, e.status, e.created_at, w.name as workflow_name, u.full_name as submitter
        FROM executions e
        LEFT JOIN workflows w ON e.workflow_id = w.id
        LEFT JOIN users u ON e.user_id = u.id
        ORDER BY e.created_at DESC LIMIT 20
    """)
    users = query("SELECT id, email, role, full_name, created_at FROM users ORDER BY created_at DESC")
    logs = query("""
        SELECT l.*, u.full_name, e.title as execution_title
        FROM logs l
        LEFT JOIN users u ON l.user_id = u.id
        LEFT JOIN executions e ON l.execution_id = e.id
        ORDER BY l.created_at DESC LIMIT 50
    """)

    return jsonify({
        'total_users': total_users,
        'total_workflows': total_workflows,
        'total_executions': total_executions,
        'by_status': [dict(r) for r in (by_status or [])],
        'recent_executions': [dict(r) for r in (recent or [])],
        'users': [dict(r) for r in (users or [])],
        'logs': [dict(r) for r in (logs or [])]
    })

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    identity = get_jwt_identity()
    if identity['role'] != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    users = query("SELECT id, email, role, full_name, created_at FROM users ORDER BY created_at DESC")
    return jsonify([dict(u) for u in (users or [])])

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    identity = get_jwt_identity()
    if identity['role'] != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    import bcrypt as _bcrypt
    data = request.get_json()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    role = data.get('role') or 'user'
    full_name = data.get('full_name') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    if role not in ('admin', 'developer', 'user'):
        return jsonify({'error': 'Invalid role'}), 400

    hashed = _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()
    try:
        user = execute(
            "INSERT INTO users (email, password, role, full_name) VALUES (%s,%s,%s,%s) RETURNING id",
            (email, hashed, role, full_name)
        )
        return jsonify({'id': user['id'], 'message': 'User created'}), 201
    except Exception as e:
        if 'unique' in str(e).lower():
            return jsonify({'error': 'Email already exists'}), 409
        raise

@notif_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    identity = get_jwt_identity()
    rows = query(
        "SELECT * FROM notifications WHERE user_id=%s ORDER BY created_at DESC LIMIT 50",
        (identity['id'],)
    )
    return jsonify([dict(r) for r in (rows or [])])

@notif_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def unread_count():
    identity = get_jwt_identity()
    cnt = query(
        "SELECT COUNT(*) as cnt FROM notifications WHERE user_id=%s AND is_read=FALSE",
        (identity['id'],), fetch='one'
    )
    return jsonify({'count': cnt['cnt']})

@notif_bp.route('/mark-read', methods=['POST'])
@jwt_required()
def mark_read():
    identity = get_jwt_identity()
    data = request.get_json()
    nid = data.get('id')
    if nid:
        execute("UPDATE notifications SET is_read=TRUE WHERE id=%s AND user_id=%s", (nid, identity['id']))
    else:
        execute("UPDATE notifications SET is_read=TRUE WHERE user_id=%s", (identity['id'],))
    return jsonify({'message': 'Marked read'})
