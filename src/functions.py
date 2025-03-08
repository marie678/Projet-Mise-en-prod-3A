"""
module that holds all streamlit helper functions for the final app
"""

import string
from typing import Any, Tuple

import inflect
import pandas as pd
import streamlit as st
from jinja2 import Template
from spellchecker import SpellChecker


def split_frame(input_df: pd.DataFrame, rows: int) -> list[pd.DataFrame]:
    """
    Splits the input DataFrame into chunks of a specified number of rows

    Args:
        input_df (DataFrame): the dataset that will be split
        rows (int): the number of rows per split

    Returns:
        list[DataFrame]: A list of DataFrame chunks
    """
    df = [input_df.iloc[i:i+rows,:] for i in range(0, len(input_df), rows)]
    return df


def handle_recipe_click(page: pd.DataFrame, index: int) -> None:
    """
    Updates Streamlit session state variables with recipe details -for use across pages- from the 
    given DataFrame row and navigates to the recipe page.

    Parameters:
    ----------
    page : pd.DataFrame
        DataFrame containing recipe data, where each row represents a recipe, with information
        such as title, ingredients, cooking time, etc.
    index : int
        The index of the selected recipe row in the DataFrame

    Session State Variables Updated:
    -------------------------------
    - `title`: str - Recipe title
    - `ingredients`: str - Ingredients list
    - `instructions`: str - Preparation instructions
    - `link`: str - Source link for the recipe
    - `rating`: float - Aggregated rating of the recipe
    - `vote`: int - Number of reviews/votes
    - `author`: str - Name of the recipe's author
    - `c_time`: str - Cooking time
    - `prep_time`: str - Preparation time
    - `servings`: int - Number of servings the recipe yields
    - `tot_time`: str - Total time required for the recipe
    - `description`: str - Description of the recipe
    - `keywords`: str - Relevant keywords or tags for the recipe
    - `img_link`: str - URL to the recipe's image
    - `calories`: float - Calorie content per serving
    - `protein`: float - Protein content per serving
    - `fat`: float - Total fat content per serving
    - `sat_fat`: float - Saturated fat content per serving
    - `chol`: float - Cholesterol content per serving
    - `sodium`: float - Sodium content per serving
    - `carbo`: float - Carbohydrate content per serving
    - `fiber`: float - Fiber content per serving
    - `sugar`: float - Sugar content per serving

    Returns:
    --------
    None
    """
    st.session_state.title = page.iloc[index]['title']
    st.session_state.ingredients = page.iloc[index]['ingredients']
    st.session_state.instructions = page.iloc[index]['directions']
    st.session_state.link = "https://" + page.iloc[index]['link']
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
        st.switch_page("./pages/Recipe page.py")

@st.cache_data(show_spinner=True)
def search_recipes(
    original_df: pd.DataFrame, filters:dict[str, Any], dict_columns: dict[str, str]
    ) -> Tuple[pd.DataFrame, int]:
    """
    Filters a DataFrame of recipes based on specific criterias and returns the filtered results.

    Parameters:
    ----------
    original_df : pd.DataFrame
        The original df containing all the recipes + their info
    filters : dict
        Dictionary of filter criterias, where keys are filter types ('ingredients',
        'recipe_durations_cat', ...) and values are the corresponding filter values
    dict_columns : dict
        Mapping of filter keys to the corresponding columns in the original df

    Returns:
    --------
    pd.DataFrame, int
        A tuple containing the filtered df and the total number of matching recipes

    Filtering Logic:
    ----------------
    The function applies filters in sequence based on the `filters` dictionary. Supported filters:
    - `ingredients`: Filters recipes containing all selected ingredients
    - `recipe_durations_cat`: Filters recipes with the specified duration category
    - `recipe_durations_min`: Filters recipes with durations less than or equal to the specified value
    - `recipe_type`: Filters recipes of a specified type (breakfast, dinner, ...)
    - `vegetarian`: Filters recipes flashed as vegetarian
    - `beginner`: Filters recipes flashed as beginner friendly
    - `provenance`: Filters recipes according to specified world region

    """

    filtered_df = original_df.copy()

    if 'ingredients' in filters.keys():
        col, value = dict_columns['ingredients'], filters['ingredients']
        filtered_df = filtered_df[filtered_df[col].apply(lambda x: all(element in x for element in value))]
    if 'recipe_durations_cat' in filters.keys():
        col, value = dict_columns['recipe_durations_cat'], filters['recipe_durations_cat']
        filtered_df = filtered_df[filtered_df[col] == (value)]
    if 'recipe_durations_min' in filters.keys():
        col, value = dict_columns['recipe_durations_min'], filters['recipe_durations_min']
        filtered_df = filtered_df[filtered_df[col] <= (value)]
    if 'recipe_type' in filters.keys():
        col, value = dict_columns['recipe_types'], filters['recipe_type']
        filtered_df = filtered_df[filtered_df[col] == (value)]
    if 'vegetarian' in filters.keys():
        col, value = dict_columns['vegetarian'], filters['vegetarian']
        filtered_df = filtered_df[filtered_df[col] == (value)]
    if 'beginner' in filters.keys():
        col, value = dict_columns['beginner'], filters['beginner']
        filtered_df = filtered_df[filtered_df[col] == (value)]
    if 'provenance' in filters.keys():
        col, value = dict_columns['provenance'], filters['provenance']
        filtered_df = filtered_df[filtered_df[col].apply(lambda x: all(element in x for element in value))]

    total_nr_recipes : int = len(filtered_df)

    return filtered_df, total_nr_recipes

def initialize_session_state() -> None:
    """
    Initializes all necessary keys in the Streamlit session state if they are not already present
    Allows for better readability in the app file
    """
    default_values = {
        'title': '',
        'ingredients': '',
        'instructions': '',
        'link': '',
        'total_recipes': None,
        'search_df': None,
        'research_summary': None,
        'filters': None,
        'recipe_type': None,
        'rating': None,
        'vote': None,
        'author': None,
        'c_time': None,
        'prep_time': None,
        'servings': None,
        'tot_time': None,
        'description': None,
        'keywords': None,
        'img_link': None,
        'rec_link': None,
        'calories': None,
        'protein': None,
        'fat': None,
        'sat_fat': None,
        'chol': None,
        'sodium': None,
        'carbo': None,
        'fiber': None,
        'sugar': None,
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def display_html_in_streamlit(html_file_path, css_file_path, height, width):
    """Displays HTML content from a file in a Streamlit app with its styling in seperate css file.

    Args:
        html_file_path (str): The path to the HTML file.
        css_file_path (str) : The path to ths css file.
        height (int) : The height of the html page to render.
        width (int) : The width of the html page to render.
    """
    try:
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            jinja_template = Template(html_content)
        with open(css_file_path, "r", encoding="utf-8") as css_file:
            css = css_file.read()
        rendered_html = jinja_template.render(css = css)
        st.components.v1.html(rendered_html, height = height, width = width, scrolling=True)
    except FileNotFoundError:
        st.error(f"Error: HTML file not found at {html_file_path}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def clean_query(query:str)-> str:
    """Cleans the query passed by the user by removing ponctuation between ingredients 
    and singularizing them.

    Args:
       query (str): The raw search query of the user.

    Returns: string (query wwithout ponctuation and in singular)
    """
    inflect_engine = inflect.engine()
    # Remove punctuation
    rm_ponct = ''.join([char for char in query if char not in string.punctuation])
    # Singularize words
    cleaned_query = [inflect_engine.singular_noun(ingredient) or ingredient for ingredient in rm_ponct.split()]
    return ' '.join(cleaned_query)

def query_error(query: list, ing: list, rec: list):
    """Handles query error by returning an error message when no recipe or ingredient are found, 
    either the word might be missplelled and, when corrected, recognized or the word is unknown.
    If the query is correct, returns a message to inform that recipes were found.

    Args:
       query (list): The search query of the user transformed into a list of words.
       ing (list) : The list of unique ingredients.
       rec (list) : The list of recipes.
    """
    response: list = []
    spell = SpellChecker()

    # Check if all words in the query already match valid ingredients or recipes
    if all(word in ing or any(word in r for r in rec) for word in query):
        return st.markdown("Matching recipes or ingredients found! Fill out desired filters and \
                           press *find a recipe*")

    # else attempt a correction
    for word in query:
        if word not in ing and not any(word in r for r in rec):
            corrected_word = spell.correction(word)
            if corrected_word in ing or any(corrected_word in r for r in rec):
                response.append(corrected_word)

    # Respond to the user
    if not response:
        return st.write('No recipes or ingredients found. Try changing your query.')

    return st.write(f'Did you mean {", ".join(response)} ?')
