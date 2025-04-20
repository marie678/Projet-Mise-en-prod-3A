"""
Provides a Streamlit sidebar interface for user authentication and session management,
interacting with a backend API.
Includes login, registration, and a user panel with options like viewing liked recipes and logging out.
"""
import requests
import streamlit as st

URI = "http://localhost:5000"


def login_form():
    """
    Handles the login or registration request and updates the session state.
    
    Args:
        endpoint (str): The API endpoint for login or registration.
        username (str): The username of the user.
        password (str): The password of the user.
        action (str): A string describing the action (login or register).
    
    Returns:
        bool: True if action was successful, False otherwise.
    """
    st.sidebar.header("🔐 Login / Register")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    login_clicked = st.sidebar.button("Login", key="login_btn")
    register_clicked = st.sidebar.button("Register", key="register_btn")

    if login_clicked:
        if not username or not password:
            st.sidebar.warning("Please enter both username and password.")
        else:
            response = requests.post(
                f"{URI}/login", data={"username": username, "password": password}
            )
            if "successfully" in response.text:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.status_message = "✅ Logged in successfully!"
                st.rerun()
            else:
                st.sidebar.error("Login failed.")

    elif register_clicked:
        if not username or not password:
            st.sidebar.warning("Please enter both username and password.")
        else:
            response = requests.post(
                f"{URI}/register", data={"username": username, "password": password}
            )
            if "successfully" in response.text:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.status_message = "✅ Registered successfully!"
                st.rerun()
            else:
                st.sidebar.error("Username is already taken.")


def show_user_panel():
    """
    Displays the user panel in the sidebar, allowing logged-in users to:
    - View their liked recipes.
    - Log out of their account.
    
    For non-logged-in users, prompts them to log in or register.
    Provides real-time feedback on actions like logging out and viewing liked recipes.
    """
   
    st.sidebar.markdown("### 🔐 User Panel")

    if st.session_state.get("logged_in"):
        st.sidebar.write(f"👤 Logged in as: `{st.session_state.username}`")

        if st.sidebar.button("❤ Liked recipes"):
            response = requests.get(
                f"{URI}/liked_recipes",
                params={"username": str(st.session_state.username)},
            )

            # Debugging
            if response.status_code == 200:
                try:
                    liked_recipes = response.json()  
                    st.session_state.liked_recipes = liked_recipes
                    if not liked_recipes:
                        st.info("You have no liked recipes.")
                    else:
                        st.switch_page("pages/likes.py")
                except requests.exceptions.JSONDecodeError as e:
                    st.error(f"Failed to decode JSON: {e}. Response: {response.text}")
            else:
                st.error(
                    f"Failed to get liked recipes. Status code: {response.status_code}, Response: {response.text}"
                )

        if st.sidebar.button("Logout", key="logout_btn"):
            response = requests.post(f"{URI}/logout")
            if "successfully" in response.text:
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.status_message = "✅ Logged out successfully"
                st.rerun()
    else:
        st.sidebar.info(
            "🔒 You are not logged in \n\n ↪️ Go to Homepage to login or register!"
        )
