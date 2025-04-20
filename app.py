"""
Welcome page :
This welcome page is the default page of our application.
It consits in an image tutorial and a usage example to guide our users, embeded in a html file
"""

import os
import streamlit as st

from src.application.recipe_finder_functions import display_html_in_streamlit
from src.user_functionalities.auth_ui import login_form, show_user_panel

st.set_page_config(layout="wide", page_title='FRIDGE & COOK',  page_icon="🍴")

####################################### LOGIN FUNCTIONNALITY ###############################

if "status_message" in st.session_state: # Display login and logout messages
    st.success(st.session_state.status_message)
    del st.session_state.status_message  # clear after showing once

# Show login form if user not logged in
if not st.session_state.get("logged_in"):
    login_form()
# if user is already logged in show user info, recipe liked and logout buttons
else:
    show_user_panel()
    st.write("🎉 Welcome back!")

####################################### WELCOME PAGE DISPLAY ###############################

# Load Welcome page.html with the corresponding styling of the page
HTML_FILE_PATH = "assets/html/Welcome_Page.html"
CSS_FILE_PATH = "assets/css/style_welcome.css"

# Check if the file exists before attempting to display it
if os.path.exists(HTML_FILE_PATH):
    _, col, _ = st.columns([3, 2, 3])
    if col.button("🔎 Recipe Finder"):
        st.switch_page("pages/recipe_finder_page.py")
    display_html_in_streamlit(HTML_FILE_PATH, CSS_FILE_PATH, height=2800, width=1080)
else:
    st.error(f"The HTML file '{HTML_FILE_PATH}' does not exist. Please check the path.")
