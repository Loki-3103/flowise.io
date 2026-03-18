from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
jwt = JWTManager(app)

from routes.auth import auth_bp
from routes.workflow import workflow_bp
from routes.execution import execution_bp
from routes.admin import admin_bp, notif_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(workflow_bp, url_prefix='/api/workflow')
app.register_blueprint(execution_bp, url_prefix='/api/execution')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(notif_bp, url_prefix='/api/notifications')

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@jwt.unauthorized_loader
def unauthorized(reason):
    return jsonify({'error': 'Unauthorized', 'reason': reason}), 401

@jwt.expired_token_loader
def expired(jwt_header, jwt_data):
    return jsonify({'error': 'Token expired'}), 401

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
