########################################### app v1.5 #################################################
# display the query results in a specially designed html page (sotred in "pages" folder) with new data
import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Template
import pandas as pd
from functools import reduce
import operator
import ast
from app.config import SAMPLE_RECIPE_PATH3, APP_TITLE
import numpy as np
import re

import os
 


# import of the cleaned and formated dataset of 10k recipes
df = pd.read_parquet(SAMPLE_RECIPE_PATH3)

st.write(APP_TITLE)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CSS_PATH = os.path.join(BASE_DIR, 'Projet-Infra-3A\App\streamlit\src\style_res.css')

# Upload the CSS file
with open("src\style_test.css") as f:
    css = f.read()


# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search recipes by ingredients", value="").lower()

# Filter the dataframe using masks
sentence = text_search.split(' ')
nb = len(sentence)
rep = df[df['NER'].apply(lambda x : all(element in x for element in sentence))]


if text_search:
    rep['%'] = rep['NER'].apply(lambda ing: round((nb / len(list(ing)))*100,1))
    best = rep['%'].idxmax()
    df_search = df.loc[best]
    recipe_title = df.loc[best]['title']

    
    with open("pages/test.html", "r") as template_file:
        template_content = template_file.read()
        jinja_template = Template(template_content)

    # Render the template with dynamic data
    rendered_html = jinja_template.render(title=recipe_title, css = css)

    

    # Display the HTML in Streamlit app
    components.html(rendered_html, height=1000, width = 900, scrolling=True)

