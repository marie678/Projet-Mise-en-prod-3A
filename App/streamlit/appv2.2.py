########################################### app v1.1 #################################################
# display the query results in list of cliquable elements that redirect to other page
# pb : absence transfert données vers page 1

import streamlit as st
import pandas as pd
from functools import reduce
import operator
import ast
import re
from app.config import SAMPLE_RECIPE_PATH
 
st.title("""
Welcome to frigo vide app
""")
 
df = pd.read_csv(SAMPLE_RECIPE_PATH)

def clean(col) : 
    col2 = []
    col3 = []
    for i in col : 
        i = ast.literal_eval(i)
        col2.append(i)
    for j in col2 : 
        if len(j) == 1 : 
            col3.append(j[0].split('.'))
        else : 
            col3.append(j)
    return col3

df['clean_dir'] = clean(df['directions'])

# initialize session_state with recipe elements
if 'title' not in st.session_state : 
    st.session_state.titre = ''
if 'ingredients' not in st.session_state :
    st.session_state.ingredients = ''
if 'instructions' not in st.session_state:
    st.session_state.instructions = ''
if 'link' not in st.session_state:
    st.session_state.link = ''
if 'correspondance_rate' not in st.session_state :
    st.session_state.correspondance_rate = ''

# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search recipes by ingredients", value="").lower()

# Filter the dataframe using masks
sentence = text_search.split(' ')
nb = len(sentence)
base = r'^{}'
expr = '(?=.*{})'
rep = df[df['NER'].str.contains(base.format(''.join(expr.format(w) for w in sentence)))][['title','NER']]
#m2 = df["Title"].str.contains(text_search)
#df_search = df[m1 | m2]

if text_search:
    st.write(len(rep), "recettes correspondantes")
    rep['%'] = rep['NER'].apply(lambda ing: round((nb / len(ast.literal_eval(ing)))*100,1))
    rep = rep.sort_values('%', ascending=False).head(15)
    best = rep['%'].idxmax()
    df_search = df.loc[best]
    
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
        if st.button(rep.iloc[i]['title']):
            st.session_state.title = rep.iloc[i]['title']
            st.session_state.ingredients = df_search['ingredients']
            st.session_state.instructions = df_search['directions']
            st.session_state.link = df_search['link']
            st.session_state.correspondance_rate = rep['%'].max()
            st.switch_page("./pages/Recettes.py")


