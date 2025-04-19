import os
import sqlite3

from flask import g


def get_users_db():
    if "db" not in g:
        os.makedirs("data", exist_ok=True)
        database = os.path.join("data/users", "users.db")
        g.db = sqlite3.connect(database)
        g.db.row_factory = sqlite3.Row
    return g.db


# Connect to your SQLite database
def get_likes_db():
    if "db" not in g:
        os.makedirs("data", exist_ok=True)
        database = os.path.join("data/users", "likes.db")
        g.db = sqlite3.connect(database)
        g.db.row_factory = sqlite3.Row
    return g.db
