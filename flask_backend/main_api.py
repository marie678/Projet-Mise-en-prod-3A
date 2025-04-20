import os
import sys
from pathlib import Path

import yaml
from flask import Flask
from flask_login import LoginManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.user_functionalities.db import get_users_db
from src.user_functionalities.user_model import User

from flask_backend.like_api import like_routes
from flask_backend.login_api import login_routes

# Create Flask app
app = Flask(__name__)

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
config_path = PROJECT_ROOT / "utils" / "config.yaml"
with open(config_path, "r") as file:
    config = yaml.safe_load(file)

app.secret_key = config['FLASK_SECRET_KEY']

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Register Blueprints
app.register_blueprint(login_routes)
app.register_blueprint(like_routes)


# Load a user from the database
@login_manager.user_loader
def load_user(user_id):
    try:
        cursor = get_users_db().cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        if row:
            return User(*row)
    except Exception as e:
        print(f"User load error: {e}")
    return None


# Start server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
