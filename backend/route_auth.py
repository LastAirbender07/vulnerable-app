from flask import Blueprint, request, jsonify
import sqlite3
import jwt
import hashlib
import pickle
import base64

auth_bp = Blueprint('auth', __name__)

# To be imported from app or hardcoded here to keep it simple and vulnerable
SECRET_KEY = "super_secret_key_12345"

# VULNERABILITY 6: SQL Injection - no parameterized queries
@auth_bp.route('/api/login', methods=['POST'])
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

# VULNERABILITY 15: Insecure Deserialization
@auth_bp.route('/api/session/save', methods=['POST'])
def save_session():
    data = request.json
    session_data = data.get('session')

    # Pickle deserialization vulnerability
    serialized = pickle.dumps(session_data)
    encoded = base64.b64encode(serialized).decode()

    return jsonify({'session_token': encoded})

@auth_bp.route('/api/session/load', methods=['POST'])
def load_session():
    data = request.json
    session_token = data.get('session_token')

    # Insecure deserialization - arbitrary code execution
    decoded = base64.b64decode(session_token)
    session_data = pickle.loads(decoded)

    return jsonify({'session': session_data})

# VULNERABILITY 17: Weak password hashing
@auth_bp.route('/api/register', methods=['POST'])
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
