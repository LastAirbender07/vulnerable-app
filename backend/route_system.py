from flask import Blueprint, request, jsonify, send_file, redirect
import os
import subprocess

system_bp = Blueprint('system', __name__)

API_KEY = "sk_live_51HxyzABCDEF123456789"
DATABASE_PASSWORD = "admin123"

# VULNERABILITY 13: Command Injection
@system_bp.route('/api/ping', methods=['POST'])
def ping_host():
    data = request.json
    host = data.get('host', 'localhost')

    # Command injection - unsanitized input passed to shell
    result = subprocess.check_output(f"ping -c 1 {host}", shell=True, stderr=subprocess.STDOUT)

    return jsonify({'output': result.decode()})

# VULNERABILITY 14: Path Traversal
@system_bp.route('/api/files/<path:filename>', methods=['GET'])
def get_file(filename):
    # Path traversal - no sanitization
    base_dir = '/app/uploads'
    file_path = os.path.join(base_dir, filename)

    try:
        return send_file(file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# VULNERABILITY 16: Information disclosure via debug mode
@system_bp.route('/api/debug/env', methods=['GET'])
def debug_env():
    # Exposes all environment variables including secrets
    return jsonify(dict(os.environ))

# VULNERABILITY 21: Sensitive data in logs
@system_bp.route('/api/logs', methods=['GET'])
def get_logs():
    # Returns logs with sensitive information
    logs = [
        {'timestamp': '2024-01-15 10:30:00', 'event': 'User login', 'details': 'username=admin, password=admin123, ip=192.168.1.100'},
        {'timestamp': '2024-01-15 10:35:00', 'event': 'API call', 'details': f'API_KEY={API_KEY}'},
        {'timestamp': '2024-01-15 10:40:00', 'event': 'DB query', 'details': f'SELECT * FROM users WHERE password={DATABASE_PASSWORD}'}
    ]
    return jsonify(logs)

# VULNERABILITY 22: Open redirect
@system_bp.route('/api/redirect', methods=['GET'])
def redirect_url():
    url = request.args.get('url', '/')
    # Open redirect - no validation
    return redirect(url)

# VULNERABILITY 23: Race condition in file operations
@system_bp.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400

    file = request.files['file']
    # No file type validation, no size limit
    filename = file.filename

    # Path traversal via filename
    upload_path = os.path.join('/tmp', filename)
    file.save(upload_path)

    return jsonify({'msg': 'File uploaded', 'path': upload_path})

# VULNERABILITY 24: Server-Side Request Forgery (SSRF)
@system_bp.route('/api/fetch', methods=['POST'])
def fetch_url():
    import requests
    data = request.json
    url = data.get('url')

    # SSRF - no URL validation, can access internal resources
    response = requests.get(url, timeout=5)

    return jsonify({'content': response.text, 'status': response.status_code})

# VULNERABILITY 25: Insecure random number generation
@system_bp.route('/api/token/generate', methods=['GET'])
def generate_token():
    import random

    # Weak random - predictable tokens
    token = ''.join([str(random.randint(0, 9)) for _ in range(16)])

    return jsonify({'token': token})
