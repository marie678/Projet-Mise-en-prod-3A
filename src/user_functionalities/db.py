"""
Provides functions to connect to SQLite databases for users and likes,
ensuring the database files exist and storing the connection in Flask's `g` context object.
"""
import os
import sqlite3

from flask import g


def get_users_db():
    """
    Gets or creates a SQLite database connection for user data,
    and stores it in Flask's application context (`g`).

    Returns:
        sqlite3.Connection: A SQLite database connection to 'data/users/users.db'.
    """
    if "db" not in g:
        os.makedirs("data/users", exist_ok=True)
        database = os.path.join("data/users", "users.db")
        g.db = sqlite3.connect(database)
        g.db.row_factory = sqlite3.Row
    return g.db


def get_likes_db():
    """
    Gets or creates a SQLite database connection for likes data,
    and stores it in Flask's application context (`g`).

    Returns:
        sqlite3.Connection: A SQLite connection to 'data/users/likes.db'.
    """
    if "db" not in g:
        os.makedirs("data/users", exist_ok=True)
        database = os.path.join("data/users", "likes.db")
        g.db = sqlite3.connect(database)
        g.db.row_factory = sqlite3.Row
    return g.db
