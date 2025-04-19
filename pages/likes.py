import streamlit as st
import pandas as pd
import requests
import os
from pathlib import Path
import yaml
from loguru import logger

from streamlit_extras.add_vertical_space import add_vertical_space
from src.application.recipe_finder_functions import split_frame
from src.user_functionalities.auth_ui import show_user_panel
from src.user_functionalities.like import get_liked_recipes
from src.preprocessing.filter import data_filter
from src.preprocessing.format import data_preprocessing
from src.preprocessing.load import merge
from src.application.st_session_functions import handle_recipe_click


URI = 'http://127.0.0.1:5000'  # URL for your Flask app

# configuration parameters
st.set_page_config(layout="wide", page_title='Liked recipes', initial_sidebar_state='collapsed', page_icon="❤")

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

st.markdown(
    """
    <style>
    .h1 {
    margin-bottom: 0.5rem;
    font-size: 1.5em;
    }
    </style>
    <div class='h1'>Recipes you liked ❤ </div>
    """,
    unsafe_allow_html=True,
)


show_user_panel()  # <-- always displays login info in sidebar

# import of the cleaned and formated dataset of 10k recipes :

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
config_path = PROJECT_ROOT / "utils" / "config.yaml"
with open(config_path, "r") as file:
    config = yaml.safe_load(file)
DATA_DIR = config['DATA_DIR']
NUTRITION_FILE_NAME = config['s3']['nutrition_file_name']
MEASUREMENTS_FILE_NAME = config['s3']['measurements_file_name']

data_folder = os.path.join(PROJECT_ROOT, "data/recipe")

# if no data folder or if it is empty : create the dataset and save it in data folder
if not os.path.exists(data_folder) or not os.listdir(data_folder):
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


# Home and recipe finder button
_, col1, col2, _ = st.columns([2, 1, 1, 2])
if col1.button("🔎 Recipe Finder"):
    st.switch_page("pages/recipe_finder_page.py")
if col2.button("🏠 Home Page"):
    st.switch_page("app.py")

# load the dataset
DATASET_PATH = os.path.join(data_folder, 'final_df.parquet')
df: pd.DataFrame = pd.read_parquet(DATASET_PATH)


# Get the list of liked recipes for the current user from the Flask backend
liked_recipes = st.session_state.get("liked_recipes", [])

if not liked_recipes:
    st.info("You have no liked recipes or data was not loaded.")
else: 
    df = df[df['recipe_id'].isin(liked_recipes)]
    st.session_state.total_recipes = len(df)

    # Display the results
    if st.session_state.total_recipes != 0:
        NUMBER_RECIPES = f"There are **{st.session_state.total_recipes} recipes** you liked :"
        st.write(NUMBER_RECIPES)
        add_vertical_space(2)

    recipe_placeholder = st.container()
    bottom_menu = st.columns((4, 1, 1))
    with bottom_menu[2]:
        batch_size = st.selectbox('Recipes per page', options=[5,10])
        total_pages = int(len(df)/batch_size) if len(df) > batch_size else 1
    with bottom_menu[1]:
        current_page = st.number_input('Page', min_value=1, max_value=total_pages, step=1, key='page_input')
    with bottom_menu[0]:
        st.markdown(f"Page **{current_page}** of **{total_pages}**")

    # Paginate the filtered DataFrame
    pages = split_frame(df, batch_size)
    page = pages[current_page - 1] if len(pages) > 0 else pd.DataFrame()


    # Display filtered recipes with pagination + html formatting
    for i in range(len(page)):
        recipe = page.iloc[i]
        recipe_id = recipe['recipe_id']  
    
        # Display recipe info with formatting
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
    
        # "Go to Recipe" button to redirect to the recipe page
        if recipe_placeholder.button(
            "Go to Recipe",
            key=f"recipe_button_{i}",
            help=f"View details for {recipe['title']}"
        ):
            handle_recipe_click(page, i)
