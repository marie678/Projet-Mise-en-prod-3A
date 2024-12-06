########################################### app v3.2 #################################################
# add search function

import streamlit as st
import pandas as pd
from functools import reduce
import operator
import ast
import re
from app.config import SAMPLE_RECIPE_PATH, APP_TITLE
from utils.functions import clean, reformat, split_frame
from streamlit_extras.add_vertical_space import add_vertical_space

st.set_page_config(layout="wide", page_title ='frigo vide', initial_sidebar_state='collapsed')
st.title(APP_TITLE)

# dev_df = "C:\\Users\\marie\\OneDrive\\Documents\\cours\\ensae\\3A\\infras_et_systemes_logiciels\\df_development"
# df = pd.read_csv(dev_df)

df = pd.read_csv(SAMPLE_RECIPE_PATH)
df['clean_dir'] = clean(df['directions'])

ingredient_list = sorted(set(reformat(df['NER'])))

base = r'^{}'
expr = '(?=.*{})'

# initialize session_state with recipe elements
if 'title' not in st.session_state : 
    st.session_state.title = ''
if 'ingredients' not in st.session_state :
    st.session_state.ingredients = ''
if 'instructions' not in st.session_state:
    st.session_state.instructions = ''
if 'link' not in st.session_state:
    st.session_state.link = ''
if 'correspondance_rate' not in st.session_state :
    st.session_state.correspondance_rate = ''
# if 'search_button' not in st.session_state:
#     st.session_state.search_button = False
if 'selected_ingredients' not in st.session_state:
    st.session_state.selected_ingredients = []
if 'search_triggered' not in st.session_state:
    st.session_state.search_triggered = False


left_col, _ = st.columns((1, 3))
filter_criteria = left_col.selectbox("Critère de filtre:", options=['ingrédients 🍅🍊', 'temps, appareil cuisson, difficulté ... si on a'], )
if filter_criteria == 'ingrédients 🍅🍊' :
        # with menu[2]:
            ingredients = left_col.multiselect("Choisir un (ou plusieurs) ingrédient(s)", ingredient_list, default=st.session_state.selected_ingredients)
            nb_ingredients = len(ingredients)
            st.session_state.selected_ingredients = ingredients  # Store selected ingredients in session state

search_button = st.button("Rechercher")
if search_button :
    st.session_state.search_triggered = True
    # st.balloons()

@st.cache_data
def search_recipes(original_df):
    df_search = original_df[original_df['NER'].str.contains(base.format(''.join(expr.format(w) for w in ingredients)))]
    # Compute the correspondance rates
    df_search['%'] = df_search['NER'].apply(lambda ing: round((nb_ingredients / len(ast.literal_eval(ing)))*100,1))
    df_search = df_search.sort_values('%', ascending=False)
    total_nr_recipes : int = len(df_search)
    return df_search, total_nr_recipes



if st.session_state.search_triggered and nb_ingredients > 0:
        # # Filter on the chosen ingredients
        # df_search = df[df['NER'].str.contains(base.format(''.join(expr.format(w) for w in ingredients)))]
        # # Compute the correspondance rates
        # df_search['%'] = df_search['NER'].apply(lambda ing: round((nb_ingredients / len(ast.literal_eval(ing)))*100,1))
        # df_search = df_search.sort_values('%', ascending=False)
        # total_nr_recipes = len(df_search)
        df_search, total_nr_recipes = search_recipes(df)

        # Choose number of recipes to display + reduce the dataframe accordingly
        # with menu[3]:
        st.write(f"Il y a {total_nr_recipes} recettes correspondant à votre recherche:\n") #, combien voulez-vous en afficher ?")
        add_vertical_space(2)
        recipe_placeholder = st.container()
        add_vertical_space(2)
        bottom_menu = st.columns((4,1,1))
        with bottom_menu[1]:
            batch_size = st.selectbox('Nombre de recettes par page', options=[25,50,100])
        with bottom_menu[2]:
            total_pages = int(len(df_search)/batch_size) if len(df_search)>batch_size else 1
            current_page = st.number_input('Page', min_value=1, max_value=total_pages, step=1)
        with bottom_menu[0]:
            st.markdown(f"Page **{current_page}** de **{total_pages}**")
        pages = split_frame(df_search, batch_size+1)
        page = (pages[current_page - 1])

        # faire le lien avec fichier CSS, pas encore actif
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
        for i in range(len(page)) :
            if recipe_placeholder.button(page.iloc[i]['title']):
                st.session_state.title = page.iloc[i]['title']
                st.session_state.ingredients = page.iloc[i]['ingredients']
                st.session_state.instructions = page.iloc[i]['directions']
                st.session_state.link = page.iloc[i]['link']
                st.session_state.correspondance_rate = page.iloc[i]['%']
                with st.spinner() :
                    st.switch_page("./pages/Recettes.py")


# reset_button = st.button('Réinitialiser')
# if reset_button :
#     st.rerun()
#     st.session_state.search_triggered = False
#     st.session_state.selected_ingredients = []
#     st.session_state.batch_size = 25
#     st.session_state.current_page = 1

#     ingredients = []  # Reset selected ingredients
#     nb_ingredients = 0
#     page = None  # Clear the current page
#     st.empty()  # Clear all dynamic elements in the app
