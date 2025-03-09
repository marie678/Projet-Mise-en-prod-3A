"""
code for the final results page. Displays the recipe contents with an html file.
"""

import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Template

st.set_page_config(layout="wide", page_title ='Recipe page', initial_sidebar_state='collapsed')
# Display header
st.markdown(
    """
    <style>
    .header {
        font-family: 'Playfair Display', serif; /* Example serif font */
        font-size: 2em; /* Adjust size as needed */
        text-align: center; /* Center the text */
        margin-top: 20px; /* Add some top margin */
        margin-bottom: 20px;
        color: black;
    }
    """,
    unsafe_allow_html=True,
)

if 'title' not in st.session_state :
    st.markdown("Please go to the **Recipe Finder** page and enter filters to find a recipe.")

else :
    # Get all the recipe elements from the session state
    recipe_title = st.session_state['title']
    ingredients = st.session_state['ingredients']
    directions = st.session_state['instructions']
    # link = st.session_state['link']
    # correspondance_rate = st.session_state['correspondance_rate']
    rating = st.session_state.rating
    vote = st.session_state.vote
    author = st.session_state.author
    c_time = st.session_state.c_time
    prep_time = st.session_state.prep_time
    servings = st.session_state.servings
    tot_time = st.session_state.tot_time
    description = st.session_state.description
    keywords = st.session_state.keywords
    img_link = st.session_state.img_link
    rec_link = st.session_state.link
    calories = st.session_state.calories
    protein = st.session_state.protein
    fat = st.session_state.fat
    sat_fat = st.session_state.sat_fat
    chol = st.session_state.chol
    sodium = st.session_state.sodium
    carbo = st.session_state.carbo
    fiber = st.session_state.fiber
    sugar = st.session_state.sugar

    if st.button("🔎 Back to Recipe Finder"):
        st.switch_page("pages/recipe_finder_page.py")

    with open("assets/html/templatev1.4.1.html", "r", encoding='utf-8') as template_file:
        template_content = template_file.read()
        jinja_template = Template(template_content)

    # Upload the CSS file
    with open("assets/css/style_resv3.css") as f:
        css = f.read()

    # Upload the javascript file
    with open("assets/js/scripts.js", encoding="utf-8") as js_file:
        js_content = js_file.read()

    JS_SCRIPT = f"<script>{js_content}</script>"

    # Render the template with dynamic data
    rendered_html = jinja_template.render(css = css, title=recipe_title, author = author,
                                        servings = servings,
                                        rating = rating, vote = vote,
                                        prep_time = prep_time, c_time = c_time, tot_time = tot_time,
                                        items=ingredients, dir = directions, keywords = keywords,
                                        link = rec_link, desc = description, img = img_link,
                                        calories = calories, protein = protein, fat = fat,
                                        sat_fat=sat_fat, sugar=sugar, chol = chol, sodium=sodium,
                                        carbo = carbo, fiber = fiber)

    # Display the HTML in Streamlit app
    components.html(rendered_html + JS_SCRIPT, height=2300, width=1100, scrolling=True)
