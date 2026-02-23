import os
import yaml

# VULNERABILITY: YAML load without safe_load (code execution)
def load_config():
    config_file = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return yaml.load(f, Loader=yaml.Loader)
    return {}

# VULNERABILITY: Eval usage (arbitrary code execution)
def calculate(expression):
    result = eval(expression)
    return result

# VULNERABILITY: SQL injection helper
def get_user_by_id(user_id):
    import sqlite3
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()

    return user

# VULNERABILITY: Weak encryption
def encrypt_data(data):
    import base64
    # Base64 is encoding, not encryption!
    return base64.b64encode(data.encode()).decode()

def decrypt_data(encrypted):
    import base64
    return base64.b64decode(encrypted).decode()
