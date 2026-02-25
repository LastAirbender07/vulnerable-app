import sqlite3

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
