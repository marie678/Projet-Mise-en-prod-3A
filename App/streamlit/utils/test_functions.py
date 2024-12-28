''' Test functions.py'''

import pytest
from functions import *
import pandas as pd

def test_split_frame():
    df = pd.DataFrame({'A': range(10)})
    result = split_frame(df, 3)
    assert len(result) == 4
    assert all(isinstance(chunk, pd.DataFrame) for chunk in result)  # All are DataFrames
    assert len(result[0]) == 3
    assert len(result[-1]) == 1

def test_search_recipes():
    df = pd.DataFrame({
#         'ingredients': [['tomato', 'cheese'], ['tomato'], ['cheese', 'pepper']],
#         'recipe_durations_cat': ['short', 'medium', 'long'],
#         'recipe_types': ['dinner', 'lunch', 'snack'],
#         'vegetarian': [True, False, True],
#     })

#     filters = {
#         'ingredients': ['tomato'],
#         'recipe_durations_cat': 'short',
#         'recipe_type': 'dinner',
#     }

#     dict_columns = {
#         'ingredients': 'ingredients',
#         'recipe_durations_cat': 'recipe_durations_cat',
#         'recipe_types': 'recipe_types',
#     }

#     result, total = search_recipes(df, filters, dict_columns)
#     assert len(result) == 1
#     assert total == 1
#     assert result.iloc[0]['recipe_types'] == 'dinner'


# from unittest.mock import patch, MagicMock
# import pandas as pd
# from your_module import handle_recipe_click

# def test_handle_recipe_click():
#     # Create mock data
#     mock_df = pd.DataFrame({
#         'title': ['Recipe1'],
#         'ingredients': ['Ingredient1, Ingredient2'],
#         'directions': ['Step1, Step2'],
#         'link': ['http://example.com'],
#         'AggregatedRating': [4.5],
#         'ReviewCount': [10],
#         'AuthorName': ['Author1'],
#         'CookTime': ['30 mins'],
#         'PrepTime': ['15 mins'],
#         'RecipeServings': [4],
#         'TotalTime': ['45 mins'],
#         'Description': ['A delicious recipe'],
#         'Keywords': ['Dinner'],
#         'Images': ['http://image.com'],
#         'Calories': [250],
#         'ProteinContent': [10],
#         'FatContent': [5],
#         'SaturatedFatContent': [2],
#         'CholesterolContent': [30],
#         'SodiumContent': [200],
#         'CarbohydrateContent': [50],
#         'FiberContent': [5],
#         'SugarContent': [10]
#     })

#     with patch("streamlit.session_state", MagicMock()) as mock_session_state, \
#          patch("streamlit.switch_page") as mock_switch_page:
#         handle_recipe_click(mock_df, 0)
#         assert mock_session_state.title == 'Recipe1'
#         assert mock_session_state.ingredients == 'Ingredient1, Ingredient2'
#         mock_switch_page.assert_called_once_with("./pages/Recettes.py")


# from your_module import initialize_session_state
# from unittest.mock import patch, MagicMock

# def test_initialize_session_state():
#     with patch("streamlit.session_state", MagicMock()) as mock_session_state:
#         initialize_session_state()
#         for key in ['title', 'ingredients', 'instructions', 'link']:
#             assert key in mock_session_state
