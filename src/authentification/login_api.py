# Flask app setup
from flask import Flask, request
from flask_login import LoginManager, login_user, UserMixin
from flask import g
import sqlite3
import os
from pathlib import Path
import yaml

# Set up a Flask app and login manager
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
config_path = PROJECT_ROOT / "utils" / "config.yaml"
with open(config_path, "r") as file:
    config = yaml.safe_load(file)
app.secret_key = config['FLASK_SECRET_KEY']

# --- Use a database in the /data folder ---
os.makedirs("data", exist_ok=True)
DATABASE = os.path.join("data", "users.db")

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Create table if it doesn't exist ---
def init_db():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    db.commit()
    db.close()

init_db()


# Define a User class that implements the Flask-Login user mixin
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = str(id) 
        self.username = username
        self.password = password

    def __repr__(self):
        return f"User({self.username!r})"



# Load a user from the database
@login_manager.user_loader
def load_user(user_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    if row:
        return User(*row)

# --- Routes ---
@app.route("/")
def index():
    return "Flask backend running."

@app.route("/login", methods=["POST"])
def login():
    cursor = get_db().cursor()
    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        return "Username and password are required.", 400
    
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    row = cursor.fetchone()
    if row:
        user = User(*row)
        login_user(user)
        return "Logged in successfully."
    else:
        return "Invalid username or password.", 401
    

@app.route("/register", methods=["POST"])
def register():
    cursor = get_db().cursor()
    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        return "Username and password are required.", 400
    
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    if row:
        return "Username is already taken.", 409
    else:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        g.db.commit()
        return "Registered successfully.", 201
    
# Set up a route for logging out users
@app.route("/logout", methods=["POST"])
def logout():
    return "Logged out successfully."


if __name__ == "__main__":
    app.run(debug=True)