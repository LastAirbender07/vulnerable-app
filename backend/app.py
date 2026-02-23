from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import os
import pickle
import base64
import subprocess
import hashlib
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded secrets exposed in code
SECRET_KEY = "super_secret_key_12345"
DATABASE_PASSWORD = "admin123"
API_KEY = "sk_live_51HxyzABCDEF123456789"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# VULNERABILITY 2: Insecure CORS configuration
CORS(app, origins="*", supports_credentials=True)

# VULNERABILITY 3: Weak JWT configuration
app.config['SECRET_KEY'] = "weak"

# Initialize database with vulnerable schema
def init_db():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            is_admin INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY,
            title TEXT,
            content TEXT,
            author_id INTEGER,
            created_at TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            post_id INTEGER,
            user_id INTEGER,
            comment TEXT,
            created_at TEXT
        )
    ''')

    # VULNERABILITY 4: Default admin credentials
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        # VULNERABILITY 5: Passwords stored in plain text
        cursor.execute("INSERT INTO users (username, password, email, is_admin) VALUES ('admin', 'admin', 'admin@blog.com', 1)")
        cursor.execute("INSERT INTO users (username, password, email, is_admin) VALUES ('user', 'password', 'user@blog.com', 0)")

    conn.commit()
    conn.close()

init_db()

# VULNERABILITY 6: SQL Injection - no parameterized queries
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    # SQL Injection vulnerability - string concatenation
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()

    if user:
        # VULNERABILITY 7: Weak JWT with no expiration
        token = jwt.encode({'user_id': user[0], 'username': user[1]}, SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token, 'username': user[1], 'is_admin': user[4]})

    return jsonify({'error': 'Invalid credentials'}), 401

# VULNERABILITY 8: Missing authentication check
@app.route('/api/posts', methods=['GET'])
def get_posts():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY created_at DESC")
    posts = cursor.fetchall()
    conn.close()

    return jsonify([{
        'id': p[0],
        'title': p[1],
        'content': p[2],
        'author_id': p[3],
        'created_at': p[4]
    } for p in posts])

# VULNERABILITY 9: SQL Injection via search parameter
@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    search_term = request.args.get('q', '')

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    # SQL Injection in search query
    query = f"SELECT * FROM posts WHERE title LIKE '%{search_term}%' OR content LIKE '%{search_term}%'"
    cursor.execute(query)
    posts = cursor.fetchall()
    conn.close()

    return jsonify([{'id': p[0], 'title': p[1], 'content': p[2]} for p in posts])

# VULNERABILITY 10: Insecure Direct Object Reference (IDOR)
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM posts WHERE id={post_id}")
    post = cursor.fetchone()
    conn.close()

    if post:
        return jsonify({
            'id': post[0],
            'title': post[1],
            'content': post[2],
            'author_id': post[3]
        })
    return jsonify({'error': 'Post not found'}), 404

# VULNERABILITY 11: Missing authorization - any user can delete any post
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM posts WHERE id={post_id}")
    conn.commit()
    conn.close()

    return jsonify({'msg': 'Post deleted'})

# VULNERABILITY 12: No CSRF protection
@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    author_id = data.get('author_id', 1)

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    # SQL Injection here too
    query = f"INSERT INTO posts (title, content, author_id, created_at) VALUES ('{title}', '{content}', {author_id}, '{datetime.now()}')"
    cursor.execute(query)
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': post_id, 'msg': 'Post created'})

# VULNERABILITY 13: Command Injection
@app.route('/api/ping', methods=['POST'])
def ping_host():
    data = request.json
    host = data.get('host', 'localhost')

    # Command injection - unsanitized input passed to shell
    result = subprocess.check_output(f"ping -c 1 {host}", shell=True, stderr=subprocess.STDOUT)

    return jsonify({'output': result.decode()})

# VULNERABILITY 14: Path Traversal
@app.route('/api/files/<path:filename>', methods=['GET'])
def get_file(filename):
    # Path traversal - no sanitization
    base_dir = '/app/uploads'
    file_path = os.path.join(base_dir, filename)

    try:
        return send_file(file_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# VULNERABILITY 15: Insecure Deserialization
@app.route('/api/session/save', methods=['POST'])
def save_session():
    data = request.json
    session_data = data.get('session')

    # Pickle deserialization vulnerability
    serialized = pickle.dumps(session_data)
    encoded = base64.b64encode(serialized).decode()

    return jsonify({'session_token': encoded})

@app.route('/api/session/load', methods=['POST'])
def load_session():
    data = request.json
    session_token = data.get('session_token')

    # Insecure deserialization - arbitrary code execution
    decoded = base64.b64decode(session_token)
    session_data = pickle.loads(decoded)

    return jsonify({'session': session_data})

# VULNERABILITY 16: Information disclosure via debug mode
@app.route('/api/debug/env', methods=['GET'])
def debug_env():
    # Exposes all environment variables including secrets
    return jsonify(dict(os.environ))

# VULNERABILITY 17: Weak password hashing
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # VULNERABILITY: MD5 hashing (weak)
    hashed = hashlib.md5(password.encode()).hexdigest()

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    # SQL Injection in registration
    query = f"INSERT INTO users (username, password, email) VALUES ('{username}', '{hashed}', '{email}')"
    try:
        cursor.execute(query)
        conn.commit()
        conn.close()
        return jsonify({'msg': 'User registered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# VULNERABILITY 18: Mass assignment vulnerability
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    # Mass assignment - user can set is_admin=1
    updates = []
    for key, value in data.items():
        if key in ['username', 'email', 'is_admin']:
            updates.append(f"{key}='{value}'")

    query = f"UPDATE users SET {','.join(updates)} WHERE id={user_id}"
    cursor.execute(query)
    conn.commit()
    conn.close()

    return jsonify({'msg': 'User updated'})

# VULNERABILITY 19: XXE vulnerability (XML parsing)
@app.route('/api/import/xml', methods=['POST'])
def import_xml():
    import xml.etree.ElementTree as ET

    xml_data = request.data.decode()

    # XXE vulnerability - processes external entities
    tree = ET.fromstring(xml_data)

    return jsonify({'msg': 'XML processed', 'root': tree.tag})

# VULNERABILITY 20: Timing attack on authentication
@app.route('/api/admin/verify', methods=['POST'])
def verify_admin():
    data = request.json
    token = data.get('token', '')

    # Timing attack vulnerability - string comparison
    if token == "admin_secret_token_abc123":
        return jsonify({'admin': True})

    return jsonify({'admin': False})

# VULNERABILITY 21: Sensitive data in logs
@app.route('/api/logs', methods=['GET'])
def get_logs():
    # Returns logs with sensitive information
    logs = [
        {'timestamp': '2024-01-15 10:30:00', 'event': 'User login', 'details': 'username=admin, password=admin123, ip=192.168.1.100'},
        {'timestamp': '2024-01-15 10:35:00', 'event': 'API call', 'details': f'API_KEY={API_KEY}'},
        {'timestamp': '2024-01-15 10:40:00', 'event': 'DB query', 'details': f'SELECT * FROM users WHERE password={DATABASE_PASSWORD}'}
    ]
    return jsonify(logs)

# VULNERABILITY 22: Open redirect
@app.route('/api/redirect', methods=['GET'])
def redirect_url():
    url = request.args.get('url', '/')
    # Open redirect - no validation
    from flask import redirect
    return redirect(url)

# VULNERABILITY 23: Race condition in file operations
@app.route('/api/upload', methods=['POST'])
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
@app.route('/api/fetch', methods=['POST'])
def fetch_url():
    import requests
    data = request.json
    url = data.get('url')

    # SSRF - no URL validation, can access internal resources
    response = requests.get(url, timeout=5)

    return jsonify({'content': response.text, 'status': response.status_code})

# VULNERABILITY 25: Insecure random number generation
@app.route('/api/token/generate', methods=['GET'])
def generate_token():
    import random

    # Weak random - predictable tokens
    token = ''.join([str(random.randint(0, 9)) for _ in range(16)])

    return jsonify({'token': token})

if __name__ == '__main__':
    # VULNERABILITY 26: Debug mode enabled in production
    app.run(host='0.0.0.0', port=5000, debug=True)
