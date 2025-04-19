import streamlit as st
import requests


URI = 'http://127.0.0.1:5000'  # URL for Flask app



# Function to like a recipe
def like_recipe(conn, user_id, recipe_id):
    """
    Allows a user to like a recipe.
    Checks if the recipe is already liked, if not, adds it to the likes table.
    """
    cursor = conn.cursor()

    # Check if the recipe is already liked by the user
    cursor.execute("SELECT * FROM likes WHERE user_id=? AND recipe_id=?", (user_id, recipe_id))
    if cursor.fetchone():
        return {"message": "Recipe already liked."}, 400

    # Add the liked recipe to the 'likes' table
    cursor.execute("INSERT INTO likes (user_id, recipe_id) VALUES (?, ?)", (user_id, recipe_id))
    conn.commit()
    return {"message": "Recipe liked successfully!"}, 200


def like_recipe_button(recipe_id, col1, col2, col3):
    """
    This function displays a like button for the recipe and sends a request to like it.
    """
    user_id = st.session_state.get("username")

    if col3.button("❤", help="Like recipe"):
        if not user_id:
            st.error("You must be logged in to like recipes.")

        else:
            try:
                response = requests.post(f"{URI}/like_recipe", json={"recipe_id": int(recipe_id), "user_id": str(user_id)})

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
    Returns all liked recipes for a given user.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT recipe_id
        FROM likes
        WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()
    # Convert to plain list of recipe IDs
    return [row[0] for row in rows]
