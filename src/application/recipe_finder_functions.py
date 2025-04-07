"""
Module that holds streamlit helper functions for the recipe finder page of the final app
includes :
    - dataframe splitting for multiple pages
    - searching the dataframe according to recipe criterions
    - display of the page with html code
"""

from typing import Any, Tuple

import pandas as pd
import streamlit as st
from jinja2 import Template


def split_frame(input_df: pd.DataFrame, rows: int) -> list[pd.DataFrame]:
    """
    Split the input DataFrame into chunks of a specified number of rows.

    Args:
        input_df (DataFrame): the dataset that will be split
        rows (int): the number of rows per split

    Returns:
        list[DataFrame]: A list of DataFrame chunks
    """
    df = [input_df.iloc[i:i+rows, :] for i in range(0, len(input_df), rows)]
    return df


@st.cache_data(show_spinner=True)
def search_recipes(
    original_df: pd.DataFrame, filters: dict[str, Any], dict_columns: dict[str, str]
        ) -> Tuple[pd.DataFrame, int]:
    """
    Filter a DataFrame of recipes based on specific criterias and returns the filtered results.

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

    total_nr_recipes: int = len(filtered_df)

    return filtered_df, total_nr_recipes


def display_html_in_streamlit(html_file_path, css_file_path, height, width):
    """Display HTML content from a file in a Streamlit app with its styling in seperate css file.

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
        rendered_html = jinja_template.render(css=css)
        st.components.v1.html(rendered_html, height=height, width=width, scrolling=True)
    except FileNotFoundError:
        st.error(f"Error: HTML or CSS file not found at {html_file_path}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
