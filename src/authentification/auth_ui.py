import streamlit as st
import requests

URI = "http://127.0.0.1:5000" 

def login_form():
    st.sidebar.header("🔐 Login / Register")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    login_clicked = st.sidebar.button("Login", key="login_btn")
    register_clicked = st.sidebar.button("Register", key="register_btn")

    if login_clicked:
        if not username or not password:
            st.sidebar.warning("Please enter both username and password.")
        else:
            response = requests.post(f"{URI}/login", data={"username": username, "password": password})
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
            response = requests.post(f"{URI}/register", data={"username": username, "password": password})
            if "successfully" in response.text:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.status_message = "✅ Registered successfully!"
                st.rerun()
            else:
                st.sidebar.error("Username is already taken.")

def show_user_panel():
    st.sidebar.markdown("### 🔐 User Panel")

    if st.session_state.get("logged_in"):
        st.sidebar.write(f"👤 Logged in as: `{st.session_state.username}`")

        if st.sidebar.button("Logout", key="logout_btn"):
            response = requests.post(f"{URI}/logout")
            if "successfully" in response.text:
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.status_message = "✅ Logged out successfully"
                st.rerun()
    else:
        st.sidebar.info("🔒 You are not logged in.")
