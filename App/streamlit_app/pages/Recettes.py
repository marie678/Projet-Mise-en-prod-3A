###################### page d'affichage #################
import streamlit as st
import ast
from streamlit_extras.add_vertical_space import add_vertical_space
from jinja2 import Template
import streamlit.components.v1 as components

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
rec_link = st.session_state.rec_link
calories = st.session_state.calories
protein = st.session_state.protein
fat = st.session_state.fat
sat_fat = st.session_state.sat_fat
chol = st.session_state.chol
sodium = st.session_state.sodium
carbo = st.session_state.carbo
fiber = st.session_state.fiber
sugar = st.session_state.sugar

# with open("pages/templatev1.3.html", "r") as template_file:
# with open("pages/templatev1.4.html", "r") as template_file:
with open("pages/templatev1.8.html", "r") as template_file:
    template_content = template_file.read()
    jinja_template = Template(template_content)
        
# Render the template with dynamic data
rendered_html = jinja_template.render(title=recipe_title, author = author, servings = servings,
                                    rating = rating, vote = vote,
                                    prep_time = prep_time, c_time = c_time, tot_time = tot_time,
                                    items=ingredients, dir = directions, keywords = keywords,
                                    link = rec_link, desc = description, img = img_link,
                                    calories = calories, protein = protein, fat = fat,
                                    sat_fat=sat_fat, sugar=sugar, chol = chol, sodium=sodium,
                                    carbo = carbo, fiber = fiber)

# Display the HTML in Streamlit app
components.html(rendered_html, height=1000, width = 900, scrolling=True)