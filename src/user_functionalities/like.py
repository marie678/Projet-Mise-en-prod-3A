"""
Provides functions to like a recipe, display a like button in the Streamlit UI,
and retrieve liked recipes for a given user, using both local database access and Flask API requests.
"""
import requests
import streamlit as st

URI = "http://127.0.0.1:5000"  # URL for Flask app


def like_recipe(conn, user_id, recipe_id):
    """
    Allows a user to like a recipe. Checks if the recipe is already liked by the user. 
    If not, inserts a new like into the 'likes' table.

    Args:
        conn (sqlite3.Connection): SQLite database connection.
        user_id (str): The ID of the user liking the recipe.
        recipe_id (int): The ID of the recipe being liked.

    Returns:
        tuple: A dictionary with a message and an HTTP-like status code.
    """
    cursor = conn.cursor()

    # Check if the recipe is already liked by the user
    cursor.execute(
        "SELECT * FROM likes WHERE user_id=? AND recipe_id=?", (user_id, recipe_id)
    )
    if cursor.fetchone():
        return {"message": "Recipe already liked."}, 400

    # Add the liked recipe to the 'likes' table
    cursor.execute(
        "INSERT INTO likes (user_id, recipe_id) VALUES (?, ?)", (user_id, recipe_id)
    )
    conn.commit()
    return {"message": "Recipe liked successfully!"}, 200


def like_recipe_button(recipe_id, col3):
    """
    Displays a like button for the recipe and sends a request to like it if the user is logged in.
    
    Args:
        recipe_id (str): The ID of the recipe to be liked.
        col3 (st.columns): The Streamlit column to display the like button.
    """
    user_id = st.session_state.get("username")

    if col3.button("❤", help="Like recipe"):
        if not user_id:
            st.error("You must be logged in to like recipes.")

        else:
            try:
                response = requests.post(
                    f"{URI}/like_recipe",
                    json={"recipe_id": int(recipe_id), "user_id": str(user_id)},
                )

                if response.status_code == 200:
                    st.success("Recipe liked!")

                else:
                    try:
                        error_message = response.json().get("message", "Unknown error")
                    except ValueError:
                        error_message = response.text
                    st.error(f"Error: {error_message}")
            except Exception as e:
                st.error(f"Request failed: {str(e)}")


def get_liked_recipes(conn, user_id):
    """
    Returns a list of recipe IDs liked by a given user.
    
    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        user_id (str): The ID of the user whose liked recipes are being fetched.

    Returns:
        list: A list of recipe IDs that the user has liked.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT recipe_id
        FROM likes
        WHERE user_id = ?
    """,
        (user_id,),
    )

    rows = cursor.fetchall()
    return [row[0] for row in rows]
