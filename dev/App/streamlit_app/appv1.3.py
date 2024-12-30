########################################### app v1.3 #################################################
# display the query results in a specially designed html and css
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
 


# import of the cleaned and formated dataset of 10k recipes
df = pd.read_parquet(SAMPLE_RECIPE_PATH3)

st.write(APP_TITLE)


# Upload the CSS file
with open("src\style_resv2.css") as f:
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
    rating = df.loc[best]['AggregatedRating']
    vote = df.loc[best]['ReviewCount']
    author = df.loc[best]['AuthorName']
    c_time = df.loc[best]['CookTime']
    prep_time = df.loc[best]['PrepTime']
    servings = df.loc[best]['RecipeServings']
    tot_time = df.loc[best]['TotalTime']
    description = df.loc[best]['Description']
    keywords = df.loc[best]['Keywords']
    img_link = df.loc[best]['Images']
    ing = df.loc[best]['ingredients']
    percent = rep['%'].max()
    directions = df.loc[best]['directions']
    rec_link = "https://" + df.loc[best]['link']
    calories = df.loc[best]['Calories']
    protein = df.loc[best]['ProteinContent']
    fat = df.loc[best]['FatContent']
    sat_fat = df.loc[best]['SaturatedFatContent']
    chol = df.loc[best]['CholesterolContent']
    sodium = df.loc[best]['SodiumContent']
    carbo = df.loc[best]['CarbohydrateContent']
    fiber = df.loc[best]['FiberContent']
    sugar = df.loc[best]['SugarContent']
    with open("pages/templatev1.3.1.html", "r") as template_file:
        template_content = template_file.read()
        jinja_template = Template(template_content)

    # Render the template with dynamic data
    rendered_html = jinja_template.render(css = css, title=recipe_title, author = author, servings = servings,
                                          rating = rating, vote =vote,
                                          prep_time = prep_time, c_time = c_time, tot_time = tot_time,
                                          items=ing, prc = percent, dir =directions, keywords = keywords,
                                          link = rec_link, desc= description, img = img_link,
                                          calories = calories, protein = protein, fat = fat,
                                          sat_fat=sat_fat, sugar=sugar, chol = chol, sodium=sodium,
                                          carbo = carbo, fiber = fiber)

    # Display the HTML in Streamlit app
    components.html(rendered_html, height=1000, width = 900, scrolling=True)

