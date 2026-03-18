from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.db import query, execute

execution_bp = Blueprint('execution', __name__)

@execution_bp.route('/execute', methods=['POST'])
@jwt_required()
def execute_workflow():
    identity = get_jwt_identity()
    data = request.get_json()
    workflow_id = data.get('workflow_id')
    inputs = data.get('inputs', {})
    title = data.get('title', 'Untitled Request')

    if not workflow_id:
        return jsonify({'error': 'workflow_id required'}), 400

    wf = query("SELECT * FROM workflows WHERE id=%s AND is_active=TRUE", (workflow_id,), fetch='one')
    if not wf:
        return jsonify({'error': 'Workflow not found'}), 404

    schema = query("SELECT * FROM input_schema WHERE workflow_id=%s ORDER BY field_order", (workflow_id,))
    for field in (schema or []):
        fname = field['field_name']
        ftype = field['field_type']
        required = field['is_required']
        val = inputs.get(fname)

        if required and (val is None or str(val).strip() == ''):
            return jsonify({'error': f'Field "{fname}" is required'}), 400

        if val is not None and str(val).strip():
            if ftype == 'number':
                try:
                    float(str(val))
                except ValueError:
                    return jsonify({'error': f'Field "{fname}" must be a number'}), 400
            if ftype == 'boolean' and str(val).lower() not in ('true', 'false', '1', '0'):
                return jsonify({'error': f'Field "{fname}" must be boolean'}), 400
            if ftype == 'dropdown' and field['allowed_values']:
                allowed = [v.strip() for v in field['allowed_values'].split(',')]
                if val not in allowed:
                    return jsonify({'error': f'Field "{fname}" must be one of: {", ".join(allowed)}'}), 400

    ex = execute(
        "INSERT INTO executions (workflow_id, user_id, status, current_step, title) VALUES (%s, %s, 'active', 1, %s) RETURNING id",
        (workflow_id, identity['id'], title)
    )
    eid = ex['id']

    for k, v in inputs.items():
        execute(
            "INSERT INTO execution_inputs (execution_id, field_name, value) VALUES (%s, %s, %s)",
            (eid, k, str(v))
        )

    execute(
        "INSERT INTO logs (execution_id, user_id, action, note, step_name) VALUES (%s, %s, 'submitted', 'Workflow execution started', 'Start')",
        (eid, identity['id'])
    )

    return jsonify({'execution_id': eid, 'message': 'Workflow started'}), 201

@execution_bp.route('/list', methods=['GET'])
@jwt_required()
def list_executions():
    identity = get_jwt_identity()
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')

    base_sql = """
        SELECT e.*, w.name as workflow_name, u.full_name as submitter_name, u.email as submitter_email
        FROM executions e
        LEFT JOIN workflows w ON e.workflow_id = w.id
        LEFT JOIN users u ON e.user_id = u.id
        WHERE 1=1
    """
    params = []

    if identity['role'] == 'user':
        base_sql += " AND e.user_id = %s"
        params.append(identity['id'])

    if status_filter:
        base_sql += " AND e.status = %s"
        params.append(status_filter)

    if search:
        base_sql += " AND (e.title ILIKE %s OR w.name ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])

    base_sql += " ORDER BY e.created_at DESC"
    rows = query(base_sql, tuple(params))
    return jsonify([dict(r) for r in (rows or [])])

@execution_bp.route('/status/<int:eid>', methods=['GET'])
@jwt_required()
def execution_status(eid):
    identity = get_jwt_identity()
    ex = query("""
        SELECT e.*, w.name as workflow_name, u.full_name as submitter_name
        FROM executions e
        LEFT JOIN workflows w ON e.workflow_id = w.id
        LEFT JOIN users u ON e.user_id = u.id
        WHERE e.id = %s
    """, (eid,), fetch='one')

    if not ex:
        return jsonify({'error': 'Not found'}), 404

    if identity['role'] == 'user' and ex['user_id'] != identity['id']:
        return jsonify({'error': 'Forbidden'}), 403

    steps = query("SELECT * FROM steps WHERE workflow_id=%s ORDER BY step_order", (ex['workflow_id'],))
    inputs = query("SELECT * FROM execution_inputs WHERE execution_id=%s", (eid,))
    logs = query("""
        SELECT l.*, u.full_name FROM logs l
        LEFT JOIN users u ON l.user_id = u.id
        WHERE l.execution_id=%s ORDER BY l.created_at DESC
    """, (eid,))

    result = dict(ex)
    result['steps'] = [dict(s) for s in (steps or [])]
    result['inputs'] = {r['field_name']: r['value'] for r in (inputs or [])}
    result['logs'] = [dict(l) for l in (logs or [])]
    return jsonify(result)

@execution_bp.route('/approve', methods=['POST'])
@jwt_required()
def approve():
    identity = get_jwt_identity()
    if identity['role'] not in ('admin', 'developer'):
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json()
    eid = data.get('execution_id')
    note = data.get('note', '')

    ex = query("SELECT * FROM executions WHERE id=%s", (eid,), fetch='one')
    if not ex:
        return jsonify({'error': 'Not found'}), 404
    if ex['status'] in ('accepted', 'rejected'):
        return jsonify({'error': 'Already finalized'}), 400

    total_steps = query("SELECT COUNT(*) as cnt FROM steps WHERE workflow_id=%s", (ex['workflow_id'],), fetch='one')
    max_steps = total_steps['cnt']
    current = ex['current_step']

    steps = query("SELECT * FROM steps WHERE workflow_id=%s ORDER BY step_order", (ex['workflow_id'],))
    current_step_obj = next((s for s in steps if s['step_order'] == current), None)
    step_name = current_step_obj['name'] if current_step_obj else f'Step {current}'

    execute(
        "INSERT INTO logs (execution_id, user_id, action, note, step_name) VALUES (%s,%s,'approved',%s,%s)",
        (eid, identity['id'], note, step_name)
    )

    if current >= max_steps:
        execute("UPDATE executions SET status='accepted', updated_at=NOW() WHERE id=%s", (eid,))
        execute(
            "INSERT INTO notifications (user_id, execution_id, message) VALUES (%s,%s,%s)",
            (ex['user_id'], eid, f'Your request "{ex["title"]}" has been fully approved.')
        )
        return jsonify({'message': 'Accepted', 'status': 'accepted'})
    else:
        new_step = current + 1
        execute("UPDATE executions SET current_step=%s, status='active', updated_at=NOW() WHERE id=%s", (new_step, eid))

        next_step = next((s for s in steps if s['step_order'] == new_step), None)
        if next_step and next_step['name'].lower() == 'finance approval':
            execute(
                "INSERT INTO notifications (user_id, execution_id, message) VALUES (%s,%s,%s)",
                (ex['user_id'], eid, f'Your request "{ex["title"]}" has reached Finance Approval.')
            )

        return jsonify({'message': f'Advanced to step {new_step}', 'status': 'active'})

@execution_bp.route('/reject', methods=['POST'])
@jwt_required()
def reject():
    identity = get_jwt_identity()
    if identity['role'] not in ('admin', 'developer'):
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json()
    eid = data.get('execution_id')
    note = data.get('note', '')

    ex = query("SELECT * FROM executions WHERE id=%s", (eid,), fetch='one')
    if not ex:
        return jsonify({'error': 'Not found'}), 404
    if ex['status'] in ('accepted', 'rejected'):
        return jsonify({'error': 'Already finalized'}), 400

    steps = query("SELECT * FROM steps WHERE workflow_id=%s ORDER BY step_order", (ex['workflow_id'],))
    current_step_obj = next((s for s in steps if s['step_order'] == ex['current_step']), None)
    step_name = current_step_obj['name'] if current_step_obj else f'Step {ex["current_step"]}'

    execute("UPDATE executions SET status='rejected', updated_at=NOW() WHERE id=%s", (eid,))
    execute(
        "INSERT INTO logs (execution_id, user_id, action, note, step_name) VALUES (%s,%s,'rejected',%s,%s)",
        (eid, identity['id'], note, step_name)
    )
    execute(
        "INSERT INTO notifications (user_id, execution_id, message) VALUES (%s,%s,%s)",
        (ex['user_id'], eid, f'Your request "{ex["title"]}" was rejected at step: {step_name}.')
    )
    return jsonify({'message': 'Rejected', 'status': 'rejected'})

@execution_bp.route('/logs/<int:eid>', methods=['GET'])
@jwt_required()
def get_logs(eid):
    logs = query("""
        SELECT l.*, u.full_name FROM logs l
        LEFT JOIN users u ON l.user_id = u.id
        WHERE l.execution_id=%s ORDER BY l.created_at ASC
    """, (eid,))
    return jsonify([dict(l) for l in (logs or [])])

@execution_bp.route('/cancel/<int:eid>', methods=['POST'])
@jwt_required()
def cancel_execution(eid):
    identity = get_jwt_identity()
    ex = query("SELECT * FROM executions WHERE id=%s", (eid,), fetch='one')
    if not ex:
        return jsonify({'error': 'Not found'}), 404
    if identity['role'] == 'user' and ex['user_id'] != identity['id']:
        return jsonify({'error': 'Forbidden'}), 403
    if ex['status'] in ('accepted', 'rejected'):
        return jsonify({'error': 'Cannot cancel a finalized execution'}), 400

    execute("UPDATE executions SET status='rejected', updated_at=NOW() WHERE id=%s", (eid,))
    execute(
        "INSERT INTO logs (execution_id, user_id, action, note, step_name) VALUES (%s,%s,'cancelled','Cancelled by user','Cancelled')",
        (eid, identity['id'])
    )
    return jsonify({'message': 'Cancelled'})
