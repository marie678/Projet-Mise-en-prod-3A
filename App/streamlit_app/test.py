import streamlit as st
import os

# Read the HTML file
html_path = os.path.join('pages', 'test.html')
with open(html_path, 'r') as file:
    html_content = file.read()

# Inject custom CSS (optional, if you want to include custom styles directly)
st.markdown(
    """
    <style>
    @import url('/static/style_res.css');
    </style>
    """,
    unsafe_allow_html=True
)

# Display the HTML content in Streamlit
st.markdown(html_content, unsafe_allow_html=True)