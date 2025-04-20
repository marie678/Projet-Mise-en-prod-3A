"""
Handles recipe like-related routes in a Flask app, including liking a recipe and retrieving liked
recipes, with SQLite database initialization and teardown support.
"""
import os
import sqlite3

from flask import Blueprint, g, jsonify, request
from src.user_functionalities.db import get_likes_db
from src.user_functionalities.like import get_liked_recipes, like_recipe

like_routes = Blueprint("like_routes", __name__)

# --- Use a database in the /data folder ---
os.makedirs("data/users", exist_ok=True)
DATABASE = os.path.join("data/users", "likes.db")


@like_routes.teardown_request
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# Create the likes table if it doesn't exist
def init_db():
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        user_id INTEGER,
        recipe_id INTEGER,
        PRIMARY KEY (user_id, recipe_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
    );
    """)
    db.commit()
    db.close()


init_db()


# Routes for liking recipes
@like_routes.route("/like_recipe", methods=["POST"])
def like_recipe_route():
    data = request.get_json()  
    recipe_id = data.get("recipe_id")
    user_id = data.get('user_id')
    if not recipe_id:
        return jsonify({"message": "Recipe ID is required"}), 400
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    conn = get_likes_db()
    message, status_code = like_recipe(conn, user_id, recipe_id)
    conn.close()
    return jsonify({"message": message}), status_code


# Route to get liked recipes
@like_routes.route("/liked_recipes", methods=["GET"])
def liked_recipes_route():
    user_id = request.args.get("username")
    if not user_id:
        return jsonify({"message": "Username required"}), 400
    conn = get_likes_db()
    liked_recipes = get_liked_recipes(conn, user_id)
    conn.close()

    return jsonify(liked_recipes), 200
