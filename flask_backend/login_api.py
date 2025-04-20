# Flask app setup
import os
import sqlite3

from flask import Blueprint, g, request
from flask_login import login_user, logout_user
from src.user_functionalities.db import get_users_db
from src.user_functionalities.user_model import User

login_routes = Blueprint("login_routes", __name__)


# --- Use a database in the /data folder ---
os.makedirs("data/users", exist_ok=True)
DATABASE = os.path.join("data/users", "users.db")


@login_routes.teardown_request
def close_db(exception=None):
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


# --- Routes ---
@login_routes.route("/")
def index():
    return "Flask backend running."


@login_routes.route("/login", methods=["POST"])
def login():
    cursor = get_users_db().cursor()
    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        return "Username and password are required.", 400

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )
    row = cursor.fetchone()
    if row:
        user = User(*row)
        login_user(user)
        return "Logged in successfully."
    return "Invalid username or password.", 401


@login_routes.route("/register", methods=["POST"])
def register():
    cursor = get_users_db().cursor()
    username = request.form["username"]
    password = request.form["password"]

    if not username or not password:
        return "Username and password are required.", 400

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )
    row = cursor.fetchone()
    if row:
        return "Username is already taken.", 409
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
    )
    g.db.commit()
    return "Registered successfully.", 201


# Set up a route for logging out users
@login_routes.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return "Logged out successfully."
