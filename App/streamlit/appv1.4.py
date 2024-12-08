import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Template
import pandas as pd
from functools import reduce
import operator
import ast
from app.config import SAMPLE_RECIPE_PATH, SAMPLE_RECIPE_PATH2, APP_TITLE
from utils.functions import clean
import numpy as np
 
st.write(APP_TITLE)
df = pd.read_csv(SAMPLE_RECIPE_PATH)
df2 = pd.read_csv(SAMPLE_RECIPE_PATH2)
df= df.merge(df2, left_on='title', right_on='Name')
df['clean_dir'] = clean(df['directions'])

def extract_first_element(x):
    new_x = x.split('"')
    if len(new_x) == 1: 
        return None  
    else:  
        return new_x[1]

df['Images'] = df['Images'].apply(extract_first_element)
df= df.dropna()

# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search recipes by ingredients", value="").lower()

# Filter the dataframe using masks
sentence = text_search.split(' ')
nb = len(sentence)
base = r'^{}'
expr = '(?=.*{})'
rep = df[df['NER'].str.contains(base.format(''.join(expr.format(w) for w in sentence)))][['title','NER']]


if text_search:
    rep['%'] = rep['NER'].apply(lambda ing: round((nb / len(ast.literal_eval(ing)))*100,1))
    best = rep['%'].idxmax()
    df_search = df.loc[best]
    recipe_title = df.loc[best]['title']
    description = df.loc[best]['Description']
    img_link = df.loc[best]['Images']
    ing = ast.literal_eval(df.loc[best]['ingredients'])
    percent = rep['%'].max()
    directions = df.loc[best]['clean_dir'] 
    rec_link = df.loc[best]['link']
    with open("pages/templatev1.3.html", "r") as template_file:
        template_content = template_file.read()
        jinja_template = Template(template_content)

    # Render the template with dynamic data
    rendered_html = jinja_template.render(title=recipe_title, items=ing, prc = percent, dir =directions, 
                                          link = rec_link, desc= description, img = img_link)

    # Display the HTML in Streamlit app
    components.html(rendered_html, height=600, scrolling=True)