''' Test functions.py'''

import pytest
from streamlit_app.utils.functions import *
import pandas as pd
import time
from streamlit.testing.v1 import AppTest
# from unittest.mock import patch, MagicMock


def test_split_frame():
    df = pd.DataFrame({'A': range(10)})
    result = split_frame(df, 3)
    assert len(result) == 4 # there should be 4 chunks
    assert all(isinstance(chunk, pd.DataFrame) for chunk in result)  # all chunks should be DataFrames
    assert len(result[0]) == 3 # the first chunk should be of length 3
    assert len(result[-1]) == 1 # the last chunk should be of length 1

def test_search_recipes():
    # no need to test for case sensitivity as the filters are already standardized in format
    df = pd.DataFrame({
        'NER': [
            ['onion', 'oregano', 'tomato', 'pepper', 'fresh green bean', 'olive oil', 'salt'], 
            ['italian-style tomato', 'kidney bean', 'corn', 'oregano', 'salt', 'parmesan cheese', 'onion', 'olive oil' 'tomato sauce'],
            ['tomato', 'dressing', 'green onion', 'banana pepper', 'extra virgin olive oil', 'cannellini bean', 'black olive', 'dark red kidney bean', 'red onion', 'salt'],
            ['flour', 'sugar', 'baking powder', 'salt', 'brown sugar', 'egg', 'butter', 'apricot half']
            ],
        'TotalTime_minutes': [156, 60, 34, 90],
        'RecipeType': ['Main Course', 'Main Course', 'Main Course', 'Dessert'],
        'Vegetarian_Friendly': [True, False, False, True],
        'Beginner_Friendly': [True, True, False, True]
    })

    dict_columns: dict[str, str] = {
    'ingredients': 'NER',
    'recipe_durations_min': 'TotalTime_minutes',
    'recipe_types': 'RecipeType',
    'vegetarian': 'Vegetarian_Friendly',
    'beginner': 'Beginner_Friendly',
    }

    filters = {
        'ingredients': ['onion'],
        'recipe_durations_min': 90,
        'recipe_type': 'Main Course',
        'beginner': True
    }
    result, total = search_recipes(df, filters, dict_columns)
    assert len(result) == 1 # only one result fits
    assert total == 1 # total = number of results that fit
    assert result.iloc[0]['RecipeType'] == 'Main Course' # recipe type filter is respected
    assert result.iloc[0]['TotalTime_minutes'] <= 90 # recipe found takes less than 90 minutes

    filters2 = {
        'ingredients': ['onion']
    }
    result2, total2 = search_recipes(df, filters2, dict_columns)
    assert len(result2) == 2 # 2 results fit, 'green onion' doesn't match onion -> checks that partial matches are not included
    assert total2 == 2 # total = number of results that fit

    filters3 = {}
    result3, _ = search_recipes(df, filters3, dict_columns)
    assert len(result3) == len(df) # all recipes are returned

    filters4 = {
        'recipe_durations_min': 90,
    }
    result4, _ = search_recipes(df, filters4, dict_columns)
    assert len(result4) == 3 # 3 recipes with duration <= 90 min, includes the one that is exactly 90

    filters5 = {'recipe_type': 'lunch'}
    result5, _ = search_recipes(df, filters5, dict_columns)
    assert len(result5) == 0  # no matches found, should return an empty DataFrame

    filters6 = {
    'ingredients': ['onion'],
    'recipe_type': 'Dessert'}
    result6, _ = search_recipes(df, filters6, dict_columns)
    assert len(result6) == 0 # checks that not result found with conficting filters

    filters7 = {'ingredients': ['onion', 'tomato']}
    result7, _ = search_recipes(df, filters7, dict_columns)
    assert len(result7) == 1  # only finds recipes with both ingredients

    large_df = pd.concat([df] * 1000, ignore_index=True)
    filters8 = {'ingredients': ['onion']}
    _, total8 = search_recipes(large_df, filters8, dict_columns)
    assert total8 == 2000  # ensure results are consistent on larger df

    # checks caching
    start_time = time.time()
    search_recipes(df, filters, dict_columns)
    first_run_time = time.time() - start_time

    start_time = time.time()
    search_recipes(df, filters, dict_columns)
    second_run_time = time.time() - start_time
    assert second_run_time < first_run_time, "Caching did not improve performance" # second run should be quicker than the first





# def test_search_recipe():
#     """Test that searching a recipe and applying filters works correctly."""
#     # Load the app for testing
#     at = AppTest.from_file("appv3.7.py").run()
    
#     # Simulate the user input for searching a recipe by title
#     title_search_query = "gratin"
#     at.text_input[0].enter(title_search_query).run()  # text_input[0] is the title search box
    
#     # Simulate form submission
#     at.button[0].click().run()  # button[0] is the filter submission button
    
#     # Check if the results contain the expected recipe
#     assert at.write[4].value == f"Research summary : **Research summary** - recipe title search : **{title_search_query}**"
    
#     # Check if any of the recipe results contains "Pasta"
#     recipe_titles = [item.value for item in at.markdown if "title" in item.value.lower()]
#     assert any("Pasta" in title for title in recipe_titles)
    
# def test_filter_recipes():
#     """Test that the filters for recipe duration and type are applied correctly."""
#     at = AppTest.from_file("app.py").run()
    
#     # Simulate the user selecting a filter for recipe duration
#     at.slider[0].set_value(2.0).run()  # Assuming slider[0] is the duration filter
    
#     # Simulate the user selecting a filter for recipe type
#     at.selectbox[0].select("Main").run()  # Assuming selectbox[0] is the recipe type filter
    
#     # Simulate form submission
#     at.button[0].click().run()  # Submit the filter form
    
#     # Check if the research summary contains the filters
#     assert "recipe duration <= *2.0* hours" in at.markdown[0].value
#     assert "recipe type : *Main*" in at.markdown[0].value

    # # Verify that the recipes displayed match the filters
    # filtered_recipes = [item.value for item in at.markdown if "recipe" in item.value.lower()]
    # assert all("Main" in recipe for recipe in filtered_recipes)  # Check that recipes are of type "Main"
    # assert all("Cook Time" in recipe for recipe in filtered_recipes)  # Check for the "Cook Time" label in the recipe card

# def test_handle_recipe_click():
#     """Test that clicking on a recipe handles the click event correctly."""
#     at = AppTest.from_file("appv3.7.py").run()
    
#     # Simulate clicking on a recipe button (assuming button with the recipe title)
#     at.button[1].click().run()  # Assuming button[0] is the recipe click button
    
#     # # Check if the page switches and session state is updated
#     # assert at.session_state["title"] == "Recipe1"  # Assuming the recipe title is "Recipe1"
#     # assert at.session_state["ingredients"] == "ingredient1, ingredient2"
#     assert at.switch_page.called_with("./pages/Recettes.py")  # Check if the page switch was called with the correct page