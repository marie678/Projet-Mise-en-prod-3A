########################################### Welcome page ##############################################
# This welcome page is the arrival page of our application by default
# It consits in an image tutorial and a usage example to guide our users embeded in a html file

import streamlit as st
from utils.functions import display_html_in_streamlit
import os

# Add a title to the page_title 
st.set_page_config(layout="wide", page_title ='FRIDGE & COOK', initial_sidebar_state='collapsed')

# Load Welcome page.html with the corresponding styling of the page 
html_file_path = "Welcome_Page.html"
css_file_path = "src/style_welcome.css"

# Check if the file exists before attempting to display it
if os.path.exists(html_file_path):
    display_html_in_streamlit(html_file_path, css_file_path, height=2700, width = 1080)
else:
    st.error(f"The HTML file '{html_file_path}' does not exist. Please check the path.")