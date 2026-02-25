from flask import Flask
from flask_cors import CORS
from db import init_db
from route_auth import auth_bp
from route_posts import posts_bp
from route_users import users_bp
from route_system import system_bp

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

# Initialize database
init_db()

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(users_bp)
app.register_blueprint(system_bp)

if __name__ == '__main__':
    # VULNERABILITY 26: Debug mode enabled in production
    app.run(host='0.0.0.0', port=5000, debug=True)
