"""
Defines a `User` class compatible with Flask-Login,
representing a user with an ID, username, and password.
"""
from flask_login import UserMixin


class User(UserMixin):
    """Represents a user with authentication details."""
    def __init__(self, id, username, password):
        self.id = str(id)
        self.username = username
        self.password = password

    def __repr__(self):
        return f"User({self.username!r})"
