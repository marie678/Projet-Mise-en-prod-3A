########################################### app v2.1 #################################################
# display the query results in list of recipes, each being a button that displays information if cliqued

import streamlit as st
import pandas as pd
from functools import reduce
import operator
import ast
import re
from app.config import SAMPLE_RECIPE_PATH, APP_TITLE
from utils.functions import clean

 
st.title(APP_TITLE)
 
df = pd.read_csv(SAMPLE_RECIPE_PATH)
df['clean_dir'] = clean(df['directions'])

if 'titre' not in st.session_state : 
    st.session_state.titre = ' '

# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search recipes by ingredients", value="").lower()


# Filter the dataframe using masks
sentence = text_search.split(' ')
nb = len(sentence)
base = r'^{}'
expr = '(?=.*{})'
rep = df[df['NER'].str.contains(base.format(''.join(expr.format(w) for w in sentence)))][['title','NER']]


if text_search:
    st.write(len(rep), "recettes correspondantes")
    rep['%'] = rep['NER'].apply(lambda ing: round((nb / len(ast.literal_eval(ing)))*100,1))
    rep = rep.sort_values('%', ascending=False).head(15)
    st.markdown(
    """
    <style>
    button {
        background: none!important;
        border: none;
        padding: 0!important;
        color: black !important;
        text-decoration: none;
        cursor: pointer;
        border: none !important;
    }
    button:hover {
        text-decoration: none;
        color: black !important;
    }
    button:focus {
        outline: none !important;
        box-shadow: none !important;
        color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
    for i in range(len(rep)) :
        st.button(rep.iloc[i]['title'])
        st.write(" - ", rep.iloc[i]['%'], " '%' d'ingrédient déjà à disposition")



