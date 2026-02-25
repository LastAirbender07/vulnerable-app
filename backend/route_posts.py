from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime

posts_bp = Blueprint('posts', __name__)

# VULNERABILITY 8: Missing authentication check
@posts_bp.route('/api/posts', methods=['GET'])
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
@posts_bp.route('/api/posts/search', methods=['GET'])
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
@posts_bp.route('/api/posts/<int:post_id>', methods=['GET'])
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
@posts_bp.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM posts WHERE id={post_id}")
    conn.commit()
    conn.close()

    return jsonify({'msg': 'Post deleted'})

# VULNERABILITY 12: No CSRF protection
@posts_bp.route('/api/posts', methods=['POST'])
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

# VULNERABILITY 19: XXE vulnerability (XML parsing)
@posts_bp.route('/api/import/xml', methods=['POST'])
def import_xml():
    import xml.etree.ElementTree as ET

    xml_data = request.data.decode()

    # XXE vulnerability - processes external entities
    tree = ET.fromstring(xml_data)

    return jsonify({'msg': 'XML processed', 'root': tree.tag})
