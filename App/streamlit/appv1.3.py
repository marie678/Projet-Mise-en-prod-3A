import streamlit as st
import streamlit.components.v1 as components
from jinja2 import Template
import pandas as pd
from functools import reduce
import operator
import ast
from app.config import SAMPLE_RECIPE_PATH, APP_TITLE
from utils.functions import clean
 
st.write(APP_TITLE)
df = pd.read_csv(SAMPLE_RECIPE_PATH)
df['clean_dir'] = clean(df['directions'])

# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search recipies by ingredients", value="").lower()

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
    ing = ast.literal_eval(df.loc[best]['ingredients'])
    percent = rep['%'].max()
    directions = df.loc[best]['clean_dir'] 
    rec_link = df.loc[best]['link']
    with open("pages/template.html", "r") as template_file:
        template_content = template_file.read()
        jinja_template = Template(template_content)

    # Render the template with dynamic data
    rendered_html = jinja_template.render(title=recipe_title, items=ing, prc = percent, dir =directions, link = rec_link)

    # Display the HTML in Streamlit app
    components.html(rendered_html, height=600, scrolling=True)

