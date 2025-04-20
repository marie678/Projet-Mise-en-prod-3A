"""
Contains the streamlit code to display the search engine and criterias,
as well as the search results.
"""

import os
from collections import Counter
from pathlib import Path
from typing import Any, List

import pandas as pd
import streamlit as st
import yaml
from loguru import logger
from streamlit_extras.add_vertical_space import add_vertical_space

from src.application.query_helpers import clean_query, query_error
from src.application.recipe_finder_functions import search_recipes, split_frame
from src.application.st_session_functions import (handle_recipe_click,
                                                  initialize_session_state)
from src.preprocessing.filter import data_filter
from src.preprocessing.format import data_preprocessing
from src.preprocessing.load import merge
from src.user_functionalities.auth_ui import show_user_panel

# configuration parameters
st.set_page_config(
    layout="wide",
    page_title='Recipe Finder',
    initial_sidebar_state='collapsed',
    page_icon="🍴"
)

# displays login info in sidebar
show_user_panel()  # always display login info in sidebar

# import of the cleaned and formated dataset of 10k recipes :
PROJECT_ROOT = Path(__file__).resolve().parent.parent # absolute path to the project root
config_path = PROJECT_ROOT / "utils" / "config.yaml"

with open(config_path, "r") as file:
    config = yaml.safe_load(file)
DATA_DIR = config['DATA_DIR']
NUTRITION_FILE_NAME = config['s3']['nutrition_file_name']
MEASUREMENTS_FILE_NAME = config['s3']['measurements_file_name']

data_folder = os.path.join(PROJECT_ROOT, "data/recipe")

# if no data folder or if it is empty : create the dataset and save it in data folder
if not os.path.isfile(os.path.join(data_folder, 'final_df.parquet')):
    with st.spinner("⏳ Initializing the dataset... This may take a few minutes."):
        os.makedirs(data_folder, exist_ok=True)
        data_folder = Path(data_folder)
        recipe_nutrition_path = os.path.join(DATA_DIR, NUTRITION_FILE_NAME).replace("\\", "/")
        recipe_measurements_path = os.path.join(DATA_DIR, MEASUREMENTS_FILE_NAME).replace("\\", "/")

        logger.info("Starting data processing pipeline...")

        merged = merge(recipe_nutrition_path, recipe_measurements_path)
        df_prepro = data_preprocessing(merged)
        df_filtered = data_filter(df_prepro)
        output_path = data_folder / 'final_df.parquet'
        if not os.path.exists(output_path):
            df_filtered.to_parquet(output_path, index=False)

        logger.success(f"Processed dataset saved to {output_path}")
        logger.success("Pipeline execution completed successfully.")
        logger.add("data_cleaning.log", rotation="10 MB", level="INFO", format="{time} - {level} - {message}")
    st.success("✅ Dataset loaded and ready to go!")

# load the dataset
DATASET_PATH = os.path.join(data_folder, 'final_df.parquet')
df: pd.DataFrame = pd.read_parquet(DATASET_PATH)


####################################### FILTERS INITIALIZATION #####################################

counter_ingredients: Counter[str] = Counter(x for row in df['NER'] for x in row)
ingredient_list: set[str] = {item[0] for item in counter_ingredients.most_common()}  # ingredients sorted by frequency
recipe_durations_cat: List[str] = ['< 30min', '< 1h', '> 1h']
recipe_durations_min: set[float] = {x for x in sorted(set(df['TotalTime_minutes'])) if pd.notna(x)}
recipe_types: set[str] = {x for x in sorted(set(df['RecipeType'])) if pd.notna(x)}
provenance: set[str] = {x for x in sorted(set(df['World_Cuisine'])) if pd.notna(x)}

filter_columns: dict[str, str] = {
    'ingredients': 'NER',
    'recipe_durations_min': 'TotalTime_minutes',
    'recipe_types': 'RecipeType',
    'vegetarian': 'Vegetarian_Friendly',
    'beginner': 'Beginner_Friendly',
    'provenance': 'World_Cuisine'
}
filters: dict[str, Any] = {}
research_summary: str = ''

######################## SESSION STATE INITIALIZATION ##########################
initialize_session_state()

############################# WEB PAGE DISPLAY #################################

# Display header
st.markdown(
    """
    <style>
    .header {
        font-family: 'Playfair Display', serif; /* Example serif font */
        font-size: 2em; /* Adjust size as needed */
        text-align: center; /* Center the text */
        margin-top: 20px; /* Add some top margin */
        margin-bottom: 20px;
        color: black;
    }
    </style>
    <div class='header'>FRIDGE & COOK</div>
    """,
    unsafe_allow_html=True,
)

# Text input to search recipes by title
title_search_query: str = st.text_input(
                        "Search a recipe (by title or ingredient(s))", key="title_search_query"
                        )

# clean query
cleaned_query: str = clean_query(title_search_query)

# error handling
rec: list = list(df['title'].apply(lambda x: x.lower()).values)
query_error(cleaned_query.split(), ingredient_list, rec)

with st.form("filter_form", clear_on_submit=False):
    st.write("Filters")
    col2, col3, col4, col5 = st.columns(4)

    # Recipe duration filter continuous in hours
    recipe_time_hours: float = col2.slider(
        "Choose the duration of your recipe (in hours)",
        min_value=0.0,
        max_value=8.0,
        value=2.00,
        step=0.1
        )
    if recipe_time_hours:
        # Convert the selected value back to minutes for filtering
        recipe_time_minutes: int = int(recipe_time_hours * 60)
        filters['recipe_durations_min'] = recipe_time_minutes
        research_summary += f' - recipe duration <= *{recipe_time_hours}* hours.'

    # Recipe Type filter
    recipe_type = col3.selectbox("Choose the type of your recipe", recipe_types, index=None)
    if recipe_type:
        filters['recipe_type'] = recipe_type
        research_summary += f' - recipe type : *{recipe_type}*'

    # World Cuisine filter
    cuisine = col4.multiselect(
        "Choose a provenance", provenance, default=None, key='cuisine_widget'
        )
    if cuisine:
        filters['provenance'] = cuisine
        prov: str = ', '.join(str(x) for x in cuisine)
        research_summary += f' - provenance : *{cuisine}*'

    # Vegetarian filter
    vege = col5.toggle("Vegetarian recipes ", value=False)
    if vege:
        filters['vegetarian'] = vege
        research_summary += ' - vegetarian recipes only'

    # Beginner friendly filter
    beginner = col5.toggle("Beginner friendly recipes ", value=False)
    if beginner:
        filters['beginner'] = beginner
        research_summary += ' - beginner friendly recipes only'

    st.session_state.research_summary = research_summary
    st.session_state.filters = filters
    submitted = st.form_submit_button("Find a recipe")

# Research recipes in the original dataframe according to the filters
if submitted:
    df_search, total_nr_recipes = search_recipes(df, st.session_state.filters, filter_columns)
    df_search = df_search.sort_values(by=['AggregatedRating'], ascending=False)  # sorted by higher rated
    st.session_state.search_df, st.session_state.total_recipes = df_search, total_nr_recipes
    if len(df_search) == 0:
        st.write("No recipes found. Try adjusting your filters or your research.")

# If no recipes found
if (
    st.session_state.search_df is None
    or st.session_state.search_df.empty
    or len(st.session_state.search_df) == 0
):
    st.write("No recipes found. Try adjusting your filters or your research.")
# Filter the search_df (= the filtered df) by title search query if a query is entered
if st.session_state.search_df is not None:
    research_summary = f"**Research summary :** {st.session_state.research_summary} \n"
    NUMBER_RECIPES = f"There are **{st.session_state.total_recipes}** recipes corresponding :\n"
    if title_search_query:
        research_summary += f', Title search : **{title_search_query}**'
        st.session_state.search_df = st.session_state.search_df[
            st.session_state.search_df['title'].str.contains(
                cleaned_query, case=False, na=False
                )
            | st.session_state.search_df['NER'].apply(
                    lambda x: all(
                        word.lower() in [str(item).lower() for item in x]
                        for word in cleaned_query.split()
                        )
                    )
            ]

    df_search = st.session_state.search_df
    st.session_state.total_recipes = len(df_search)

    # Display the results
    if st.session_state.total_recipes != 0:
        NUMBER_RECIPES = f"There are **{st.session_state.total_recipes} recipes** matching your search :"
        st.write(research_summary)
        st.write(NUMBER_RECIPES)
        add_vertical_space(2)

    recipe_placeholder = st.container()
    bottom_menu = st.columns((4, 1, 1))
    with bottom_menu[2]:
        batch_size = st.selectbox('Recipes per page', options=[10, 25, 50, 100])
        total_pages = int(len(df_search)/batch_size) if len(df_search) > batch_size else 1
    with bottom_menu[1]:
        current_page = st.number_input('Page', min_value=1, max_value=total_pages, step=1, key='page_input')
    with bottom_menu[0]:
        st.markdown(f"Page **{current_page}** of **{total_pages}**")

    # Paginate the filtered DataFrame
    pages = split_frame(df_search, batch_size)
    page = pages[current_page - 1] if len(pages) > 0 else pd.DataFrame()

    # Display filtered recipes with pagination + html formatting
    for i in range(len(page)):
        recipe = page.iloc[i]
        recipe_placeholder.markdown(
            f"""
        <div style="
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            background-color: #f9f9f9;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
            <h3 style="margin: 0; color: #333;">{recipe['title']}</h3>
            <p style="margin: 5px 0; color: #777;">
                <b>Total Time:</b> {recipe['TotalTime']} |
                <b>Rating:</b> {recipe['AggregatedRating']}
            </p>
            <p style="margin: 5px 0; color: #555;">
                {', '.join(str(x) for x in recipe['ingredients'][:10])}...
            </p>
        </div>
        """,
        unsafe_allow_html=True)

        if recipe_placeholder.button(
            "Go to Recipe",
            key=f"recipe_button_{i}",
            help=f"View details for {recipe['title']}"
        ):
            handle_recipe_click(page, i)

if st.button("🏠 Home page"):
    st.switch_page("app.py")
