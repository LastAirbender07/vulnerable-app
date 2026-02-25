from flask import Blueprint, request, jsonify
import sqlite3

users_bp = Blueprint('users', __name__)

# VULNERABILITY 18: Mass assignment vulnerability
@users_bp.route('/api/users/<int:user_id>', methods=['PUT'])
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

# VULNERABILITY 20: Timing attack on authentication
@users_bp.route('/api/admin/verify', methods=['POST'])
def verify_admin():
    data = request.json
    token = data.get('token', '')

    # Timing attack vulnerability - string comparison
    if token == "admin_secret_token_abc123":
        return jsonify({'admin': True})

    return jsonify({'admin': False})
