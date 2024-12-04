########################################### app v3.0 #################################################
# filters

import streamlit as st
import pandas as pd
from functools import reduce
import operator
import ast
import re
from app.config import SAMPLE_RECIPE_PATH, APP_TITLE
from utils.functions import clean, reformat

st.title(APP_TITLE)
 
df = pd.read_csv(SAMPLE_RECIPE_PATH)
df['clean_dir'] = clean(df['directions'])

ingredient_list = sorted(set(reformat(df['NER'])))

base = r'^{}'
expr = '(?=.*{})'

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


menu = st.columns(4)
with menu[0]:
    filter = st.radio("Filtrer les recettes:", options=['Oui', 'Non'], horizontal=True)
if filter == 'Oui':
    with menu[1]:
        filter_criteria = st.selectbox("Critère de filtre:", options=['ingrédients 🍅🍊', 'temps, appareil cuisson, difficulté ... si on a'])
    if filter_criteria == 'ingrédients 🍅🍊' :
        with menu[2]:
            ingredients = st.multiselect("Choisir un (ou plusieurs) ingrédient(s)", ingredient_list)
            nb_ingredients = len(ingredients)
    
    if nb_ingredients > 0 :
        # Filter on the chosen ingredients
        df_search = df[df['NER'].str.contains(base.format(''.join(expr.format(w) for w in ingredients)))]
        # Compute the correspondance rates
        df_search['%'] = df_search['NER'].apply(lambda ing: round((nb_ingredients / len(ast.literal_eval(ing)))*100,1))
        total_nr_recipes = len(df_search)

        # Choose number of recipes to display + reduce the dataframe accordingly
        with menu[3]:
            st.write(f"Il y a {total_nr_recipes} recettes correspondant à votre recherche, combien voulez-vous en afficher ?")
            nb_recipe_displayed = st.slider("", 1, len(df_search), 10) # Nombre de recettes à afficher
        df_search = df_search.sort_values('%', ascending=False).head(nb_recipe_displayed)
        

        # faire le lien avec fichier CSS, pas encore actif
        st.markdown(
    """
    <link rel="stylesheet" href="./src/style.css">
    """,
    unsafe_allow_html=True
        )

        for i in range(nb_recipe_displayed) :
            if st.button(df_search.iloc[i]['title']):
                st.session_state.title = df_search.iloc[i]['title']
                st.session_state.ingredients = df_search.iloc[i]['ingredients']
                st.session_state.instructions = df_search.iloc[i]['directions']
                st.session_state.link = df_search.iloc[i]['link']
                st.session_state.correspondance_rate = df_search.iloc[i]['%']
                st.switch_page("./pages/Recettes.py")