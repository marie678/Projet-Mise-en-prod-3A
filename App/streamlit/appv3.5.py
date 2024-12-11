########################################### app v3.2 #################################################
# add search bar

import streamlit as st
import pandas as pd
from functools import reduce
from app.config import SAMPLE_RECIPE_PATH, APP_TITLE
from utils.functions import clean, reformat, split_frame, search_recipes
from streamlit_extras.add_vertical_space import add_vertical_space

# configuration parameters
st.set_page_config(layout="wide", page_title ='frigo vide', initial_sidebar_state='collapsed')
# st.title(APP_TITLE)

# Load Data
dev_df = "C:\\Users\\marie\\OneDrive\\Documents\\cours\\ensae\\3A\\infras_et_systemes_logiciels\\df_development"
df = pd.read_csv(dev_df)
# df = pd.read_csv(SAMPLE_RECIPE_PATH)
# df['clean_dir'] = clean(df['directions'])

# Extract filters values
ingredient_list: set = {x for x in sorted(set(reformat(df['NER']))) if pd.notna(x)}
recipe_durations: set = {x for x in sorted(set(df['CookTime_minutes'])) if pd.notna(x)}
ratings: set = {x for x in sorted(set(df['AggregatedRating'])) if pd.notna(x)}

# define constants
base: str = r'^{}'
expr: str = '(?=.*{})'
filter_columns: dict = {
    'ingredients': 'NER',
    'recipe_durations': 'CookTime_minutes',
    'ratings': 'AggregatedRating',
}

# initialize session_state with recipe elements + widgets
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
if 'selected_ingredients' not in st.session_state:
    st.session_state.selected_ingredients = None
if 'selected_duration' not in st.session_state:
    st.session_state.selected_duration = None
if 'selected_rating' not in st.session_state:
    st.session_state.selected_rating = None
if 'total_recipes' not in st.session_state:
    st.session_state.total_recipes = None
if 'search_df' not in st.session_state:
    st.session_state.search_df = None
if 'search_df2' not in st.session_state:
    st.session_state.search_df2 = None
if 'research_summary' not in st.session_state:
    st.session_state.research_summary = None
if 'filters' not in st.session_state:
    st.session_state.filters = None
if 'search_input' not in st.session_state:
    st.session_state.search_input = None





filters = {}
research_summary = ''

# Text input for searching recipes by title
title_search_query = st.text_input("Search recipes by title", key="title_search_query")

with st.form("filter_form", clear_on_submit=False):
    st.write("Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    # Ingredients filter
    ingredients = col1.multiselect("Choose one or more ingredient(s)", ingredient_list, default=None) #st.session_state.selected_ingredients if st.session_state.selected_ingredients else 
    st.session_state.selected_ingredients = ingredients  # Update selected ingredients in session state
    if ingredients:
        nb_ingredients = len(ingredients)
        filters['ingredients'] = ingredients
        research_summary += f'ingredients : *{ingredients}*'

    # Recipe duration filter CHANGE TO SLIDER ????
    recipe_time = col2.slider("Choose the duration of your recipe", min_value=int(min(recipe_durations)), max_value=int(max(recipe_durations)), value=20, step=5)
    # recipe_time = col2.selectbox("Choose the duration of your recipe", recipe_durations, index=None) #recipe_durations.index(st.session_state.selected_duration) if st.session_state.selected_duration else 
    st.session_state.selected_duration = recipe_time  # Update duration in session state
    if recipe_time: # default to 'Select recipe time'?
        filters['recipe_durations'] = recipe_time
        research_summary += f' - recipe duration <= *{recipe_time}* min.'

    # Ratings filter
    rating = col3.slider("Choose a rating", min_value=(min(ratings)), max_value=(max(ratings)), value=3.0, step=0.5) #ratings.index(st.session_state.selected_rating) if st.session_state.selected_rating else 
    st.session_state.selected_rating = rating  # Update rating in session state
    if rating:
        filters['ratings'] = rating
        research_summary += f' - rating >= *{rating}*'
    
    other = col4.selectbox("Choose other", ['A', 'B', 'C'], index=None)
    # st.session_state.selected_rating = rating  # Store rating in session state
    if other:
        filters['other'] = other
    # st.write(filters)
    st.session_state.research_summary = research_summary
    st.session_state.filters = filters
    submitted = st.form_submit_button("Apply Filters")

# with st.form("search_form", clear_on_submit=True):
#     search_input = st.text_input("Search recipes", value="").lower()
#     st.session_state.search_input = search_input
#     search_submitted = st.form_submit_button("Search")

if submitted:
        # st.write(filters)
        df_search, total_nr_recipes = search_recipes(df, st.session_state.filters, filter_columns)
        st.session_state.search_df, st.session_state.total_recipes = df_search, total_nr_recipes

# if search_submitted:
#      df_search = st.session_state.search_df
#      df = df_search[df_search['title'].astype(str).str.contains(st.session_state.search_input)]
#      st.session_state.search_df = df

def handle_recipe_click(index):
    st.session_state.title = page.iloc[index]['title']
    st.session_state.ingredients = page.iloc[index]['ingredients']
    st.session_state.instructions = page.iloc[index]['directions']
    st.session_state.link = page.iloc[index]['link']
    # st.session_state.correspondance_rate = page.iloc[index]['%']
    with st.spinner() :
        st.switch_page("./pages/Recettes.py")



# # Text input for searching recipes by title
# title_search_query = st.text_input("Search recipes by title", key="title_search_query")
# Filter the search_df by title search query if a query is entered
if st.session_state.search_df is not None:
    research_summary = f"**Research summary :** {st.session_state.research_summary} \n"
    number_recipes = f"There are **{st.session_state.total_recipes}** recipes corresponding :\n"

    filtered_by_title_df = st.session_state.search_df[
        st.session_state.search_df['title'].str.contains(title_search_query, case=False, na=False)
    ] if title_search_query else st.session_state.search_df

    research_summary += f', Title search : {title_search_query}'
    number_recipes = (f"There are **{len(filtered_by_title_df)} recipes** matching your search :")
    st.write(research_summary)
    st.write(number_recipes)
    add_vertical_space(2)
    # Update the total recipes count for title-based filtering
    st.session_state.total_recipes = len(filtered_by_title_df)
    
    
    recipe_placeholder = st.container()
    bottom_menu = st.columns((4,1,1))
    with bottom_menu[2]:
        batch_size = st.selectbox('Recipes per page', options=[25,50,100])
        total_pages = int(len(filtered_by_title_df)/batch_size) if len(filtered_by_title_df)>batch_size else 1
    with bottom_menu[1]:
        current_page = st.number_input('Page', min_value=1, max_value=total_pages, step=1, key='page_input')
    with bottom_menu[0]:
        st.markdown(f"Page **{current_page}** of **{total_pages}**")

    # Paginate the filtered DataFrame
    pages = split_frame(filtered_by_title_df, batch_size+1)
    page = pages[current_page - 1] if len(pages) > 0 else pd.DataFrame()

    # Display filtered recipes with pagination
    for i in range(len(page)):
        if recipe_placeholder.button(page.iloc[i]['title'], key=f"recipe_button_{i}"):
            handle_recipe_click(i)