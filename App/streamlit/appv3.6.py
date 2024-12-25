########################################### app v3.5 #################################################
# link with recipes 

import streamlit as st
import pandas as pd
from functools import reduce
from app.config import SAMPLE_RECIPE_PATH, APP_TITLE, SAMPLE_RECIPE_PATH3
from utils.functions import clean, reformat, split_frame, search_recipes
from streamlit_extras.add_vertical_space import add_vertical_space
import numpy as np
from collections import Counter
# from jinja2 import Template
# import streamlit.components.v1 as components


# configuration parameters
st.set_page_config(layout="wide", page_title ='frigo vide', initial_sidebar_state='collapsed')
# import of the cleaned and formated dataset of 10k recipes
df = pd.read_parquet(SAMPLE_RECIPE_PATH3)


### FILTERS ###
'''
Six binary filters (True/False):
    Vegetarian (Vegetarian_Friendly)
    Beginner-Friendly (Beginner_Friendly)
    Asian Cuisine (Asian)
    African Cuisine (African)
    North & South American Cuisine (North & South America)
    European & Eastern European Cuisine (Europe and Eastern Europe)
Two categorical filters:
    Recipe Type (Main Course, Dessert, Beverage, or Breakfast) (RecipeType)
    Total Time Range (Under 30 minutes, Between 30 minutes and 1 hour, or Over 1 hour) (TotalTime_cat)
'''

counter_ingredients: Counter = Counter(x for row in df['NER'] for x in row)
ingredient_list: set = {item[0] for item in counter_ingredients.most_common()} # ingredients sorted by frequency
recipe_durations: list = ['< 30min', '< 1h', '> 1h']
recipe_types: set = {x for x in sorted(set(df['RecipeType'])) if pd.notna(x)}


filter_columns: dict = {
    'ingredients': 'NER',
    'recipe_durations': 'TotalTime_cat',
    'recipe_types': 'RecipeType',
    'vegetarian': 'Vegetarian_Friendly',
    'beginner': 'Beginner_Friendly',
    # 'ratings': 'AggregatedRating',
}

####################################### INITIALIZE SESSION STATE ######################################
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
if 'research_summary' not in st.session_state:
    st.session_state.research_summary = None
if 'filters' not in st.session_state:
    st.session_state.filters = None
if 'search_input' not in st.session_state:
    st.session_state.search_input = None
if 'recipe_type' not in st.session_state:
    st.session_state.recipe_type = None
if 'rating' not in st.session_state:
    st.session_state.rating = None
if 'vote' not in st.session_state:
    st.session_state.vote = None
if 'author' not in st.session_state:
    st.session_state.author = None
if 'c_time' not in st.session_state:
    st.session_state.c_time = None
if 'prep_time' not in st.session_state:
    st.session_state.prep_time = None
if 'servings' not in st.session_state:
    st.session_state.servings = None
if 'tot_time' not in st.session_state:
    st.session_state.tot_time = None
if 'description' not in st.session_state:
    st.session_state.description = None
if 'keywords' not in st.session_state:
    st.session_state.keywords = None
if 'img_link' not in st.session_state:
    st.session_state.img_link = None
if 'rec_link' not in st.session_state:
    st.session_state.rec_link = None
if 'calories' not in st.session_state:
    st.session_state.calories = None
if 'protein' not in st.session_state:
    st.session_state.protein = None
if 'fat' not in st.session_state:
    st.session_state.fat = None
if 'sat_fat' not in st.session_state:
    st.session_state.sat_fat = None
if 'chol' not in st.session_state:
    st.session_state.chol = None
if 'sodium' not in st.session_state:
    st.session_state.sodium = None
if 'carbo' not in st.session_state:
    st.session_state.carbo = None
if 'fiber' not in st.session_state:
    st.session_state.fiber = None
if 'sugar' not in st.session_state:
    st.session_state.sugar = None
#####################################################################################################

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
        ingr: str = ', '.join(str(x) for x in ingredients)
        research_summary += f'ingredients : *{ingr}*'

    # Recipe duration filter
    recipe_time = col2.select_slider("Choose the duration of your recipe", options=recipe_durations, value=None) #min_value=int(min(recipe_durations)), max_value=int(max(recipe_durations)), value=20, step=5)
    # recipe_time = col2.selectbox("Choose the duration of your recipe", recipe_durations, index=None) #recipe_durations.index(st.session_state.selected_duration) if st.session_state.selected_duration else 
    st.session_state.selected_duration = recipe_time  # Update duration in session state
    if recipe_time:
        filters['recipe_durations'] = recipe_time
        research_summary += f' - recipe duration : *{recipe_time}*'

    # Recipe Type filter
    recipe_type = col3.selectbox("Choose the type of your recipe", recipe_types, index=None)
    st.session_state.recipe_type = recipe_type
    if recipe_type:
        filters['recipe_type'] = recipe_type
        research_summary += f' - recipe type : *{recipe_type}*'

    # # Ratings filter
    # rating = col3.slider("Choose a rating", min_value=(min(ratings)), max_value=(max(ratings)), value=3.0, step=0.5) #ratings.index(st.session_state.selected_rating) if st.session_state.selected_rating else 
    # st.session_state.selected_rating = rating  # Update rating in session state
    # if rating:
    #     filters['ratings'] = rating
    #     research_summary += f' - rating >= *{rating}*'
    
    other = col4.selectbox("Choose other", ['A', 'B', 'C'], index=None)
    if other:
        filters['other'] = other
    st.session_state.research_summary = research_summary
    st.session_state.filters = filters
    submitted = st.form_submit_button("Apply Filters")

if submitted:
        # st.write(filters)
        df_search, total_nr_recipes = search_recipes(df, st.session_state.filters, filter_columns)
        df_search = df_search.sort_values(by=['AggregatedRating'], ascending=False)
        st.session_state.search_df, st.session_state.total_recipes = df_search, total_nr_recipes


def handle_recipe_click(index):
    st.session_state.title = page.iloc[index]['title']
    st.session_state.ingredients = page.iloc[index]['ingredients']
    st.session_state.instructions = page.iloc[index]['directions']
    st.session_state.link = page.iloc[index]['link']
    # st.session_state.correspondance_rate = page.iloc[index]['%']
    st.session_state.rating = page.iloc[index]['AggregatedRating']
    st.session_state.vote = page.iloc[index]['ReviewCount']
    st.session_state.author = page.iloc[index]['AuthorName']
    st.session_state.c_time = page.iloc[index]['CookTime']
    st.session_state.prep_time = page.iloc[index]['PrepTime']
    st.session_state.servings = page.iloc[index]['RecipeServings']
    st.session_state.tot_time = page.iloc[index]['TotalTime']
    st.session_state.description = page.iloc[index]['Description']
    st.session_state.keywords = page.iloc[index]['Keywords']
    st.session_state.img_link = page.iloc[index]['Images']
    # st.session_state.rec_link = page.iloc[index]['Images']
    st.session_state.calories = page.iloc[index]['Calories']
    st.session_state.protein = page.iloc[index]['ProteinContent']
    st.session_state.fat = page.iloc[index]['FatContent']
    st.session_state.sat_fat = page.iloc[index]['SaturatedFatContent']
    st.session_state.chol = page.iloc[index]['CholesterolContent']
    st.session_state.sodium = page.iloc[index]['SodiumContent']
    st.session_state.carbo = page.iloc[index]['CarbohydrateContent']
    st.session_state.fiber = page.iloc[index]['FiberContent']
    st.session_state.sugar = page.iloc[index]['SugarContent']
    with st.spinner() :
        st.switch_page("./pages/Recettes.py")

        # with open("pages/templatev1.3.html", "r") as template_file:
        #     template_content = template_file.read()
        #     jinja_template = Template(template_content)
                
        # # Render the template with dynamic data
        # rendered_html = jinja_template.render(title=st.session_state.title, author = author, servings = servings,
        #                                     rating = rating, vote =vote,
        #                                     prep_time = prep_time, c_time = c_time, tot_time = tot_time,
        #                                     items=st.session_state.ingredients, dir =directions, keywords = keywords,
        #                                     link = rec_link, desc= description, img = img_link,
        #                                     calories = calories, protein = protein, fat = fat,
        #                                     sat_fat=sat_fat, sugar=sugar, chol = chol, sodium=sodium,
        #                                     carbo = carbo, fiber = fiber)

        # # Display the HTML in Streamlit app
        # components.html(rendered_html, height=1000, width = 900, scrolling=True)
        # if st.button("For more details on recipe") : 
        #     st.write(" details ")
        
# if text_search:
    # rep['%'] = rep['NER'].apply(lambda ing: round((nb / len(list(ing)))*100,1))
    # best = rep['%'].idxmax()    
    # percent = rep['%'].max()
################


# Filter the search_df by title search query if a query is entered
if st.session_state.search_df is not None:
    research_summary = f"**Research summary :** {st.session_state.research_summary} \n"
    number_recipes = f"There are **{st.session_state.total_recipes}** recipes corresponding :\n"

    filtered_by_title_df = st.session_state.search_df[
    st.session_state.search_df['title'].str.contains(title_search_query, case=False, na=False) |
    st.session_state.search_df['NER'].str.contains(title_search_query, case=False, na=False)
    ] if title_search_query else st.session_state.search_df

    if title_search_query:
        research_summary += f', Title search : **{title_search_query}**'
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