from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import query, execute

workflow_bp = Blueprint('workflow', __name__)

def require_role(*roles):
    def decorator(fn):
        from functools import wraps
        @wraps(fn)
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            if identity['role'] not in roles:
                return jsonify({'error': 'Forbidden'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@workflow_bp.route('/list', methods=['GET'])
@jwt_required()
def list_workflows():
    search = request.args.get('search', '')
    if search:
        rows = query(
            "SELECT w.*, u.full_name as creator_name FROM workflows w LEFT JOIN users u ON w.created_by = u.id WHERE w.name ILIKE %s ORDER BY w.created_at DESC",
            (f'%{search}%',)
        )
    else:
        rows = query(
            "SELECT w.*, u.full_name as creator_name FROM workflows w LEFT JOIN users u ON w.created_by = u.id ORDER BY w.created_at DESC"
        )
    return jsonify([dict(r) for r in (rows or [])])

@workflow_bp.route('/<int:wid>', methods=['GET'])
@jwt_required()
def get_workflow(wid):
    wf = query("SELECT * FROM workflows WHERE id = %s", (wid,), fetch='one')
    if not wf:
        return jsonify({'error': 'Not found'}), 404
    steps = query("SELECT * FROM steps WHERE workflow_id = %s ORDER BY step_order", (wid,))
    schema = query("SELECT * FROM input_schema WHERE workflow_id = %s ORDER BY field_order", (wid,))
    result = dict(wf)
    result['steps'] = [dict(s) for s in (steps or [])]
    result['schema'] = [dict(s) for s in (schema or [])]
    return jsonify(result)

@workflow_bp.route('/create', methods=['POST'])
@jwt_required()
def create_workflow():
    identity = get_jwt_identity()
    if identity['role'] not in ('admin', 'developer'):
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json()
    name = (data.get('name') or '').strip()
    description = data.get('description', '')
    steps = data.get('steps', [])
    schema = data.get('schema', [])

    if not name:
        return jsonify({'error': 'Name required'}), 400

    existing = query("SELECT id FROM workflows WHERE name = %s", (name,), fetch='one')
    if existing:
        return jsonify({'error': 'Workflow name already exists'}), 409

    wf = execute(
        "INSERT INTO workflows (name, description, created_by) VALUES (%s, %s, %s) RETURNING id",
        (name, description, identity['id'])
    )
    wid = wf['id']

    for i, step in enumerate(steps):
        execute(
            "INSERT INTO steps (workflow_id, name, step_order, role, assignee_email, step_type) VALUES (%s, %s, %s, %s, %s, %s)",
            (wid, step.get('name'), i + 1, step.get('role', 'user'), step.get('assignee_email'), step.get('step_type', 'approval'))
        )

    for i, field in enumerate(schema):
        execute(
            "INSERT INTO input_schema (workflow_id, field_name, field_type, is_required, allowed_values, field_order) VALUES (%s, %s, %s, %s, %s, %s)",
            (wid, field.get('field_name'), field.get('field_type', 'string'), field.get('is_required', True), field.get('allowed_values'), i + 1)
        )

    return jsonify({'id': wid, 'message': 'Workflow created'}), 201

@workflow_bp.route('/<int:wid>', methods=['PUT'])
@jwt_required()
def update_workflow(wid):
    identity = get_jwt_identity()
    if identity['role'] not in ('admin', 'developer'):
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json()
    name = (data.get('name') or '').strip()
    description = data.get('description', '')
    steps = data.get('steps', [])
    schema = data.get('schema', [])

    if not name:
        return jsonify({'error': 'Name required'}), 400

    execute("UPDATE workflows SET name=%s, description=%s, updated_at=NOW() WHERE id=%s", (name, description, wid))
    execute("DELETE FROM steps WHERE workflow_id=%s", (wid,))
    execute("DELETE FROM input_schema WHERE workflow_id=%s", (wid,))

    for i, step in enumerate(steps):
        execute(
            "INSERT INTO steps (workflow_id, name, step_order, role, assignee_email, step_type) VALUES (%s, %s, %s, %s, %s, %s)",
            (wid, step.get('name'), i + 1, step.get('role', 'user'), step.get('assignee_email'), step.get('step_type', 'approval'))
        )
    for i, field in enumerate(schema):
        execute(
            "INSERT INTO input_schema (workflow_id, field_name, field_type, is_required, allowed_values, field_order) VALUES (%s, %s, %s, %s, %s, %s)",
            (wid, field.get('field_name'), field.get('field_type', 'string'), field.get('is_required', True), field.get('allowed_values'), i + 1)
        )

    return jsonify({'message': 'Updated'})

@workflow_bp.route('/<int:wid>', methods=['DELETE'])
@jwt_required()
def delete_workflow(wid):
    identity = get_jwt_identity()
    if identity['role'] not in ('admin', 'developer'):
        return jsonify({'error': 'Forbidden'}), 403
    execute("DELETE FROM workflows WHERE id=%s", (wid,))
    return jsonify({'message': 'Deleted'})
