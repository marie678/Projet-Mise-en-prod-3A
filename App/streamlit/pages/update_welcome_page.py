import streamlit as st
import os
from utils.functions import display_html_in_streamlit


html_file_path = "pages/Welcome Page.html"

# Check if the file exists before attempting to display it
if os.path.exists(html_file_path):
    display_html_in_streamlit(html_file_path)
else:
    st.error(f"The HTML file '{html_file_path}' does not exist. Please check the path.")

# print(html_file_path)