import pandas as pd
from pathlib import Path
from src.data_cleaning import *

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
config_path = PROJECT_ROOT / "utils" / "config.yaml"

with open(config_path, "r") as file:
    config = yaml.safe_load(file)
DATA_DIR = config['DATA_DIR']


### Tests for utility functions ###
def test_iso_to_minutes():
    assert iso_to_minutes('PT1H30M') == 90
    assert iso_to_minutes('PT45M') == 45
    assert iso_to_minutes('PT2H') == 120
    assert iso_to_minutes('PT0M') == 0

def test_categorize_duration():
    assert categorize_duration(20) == '< 30min'
    assert categorize_duration(45) == '< 1h'
    assert categorize_duration(90) == '> 1h'

def test_format_duration():
    assert format_duration('PT1H30M') == '1 h 30 min'
    assert format_duration('PT45M') == '45 min'
    assert format_duration('PT2H') == '2 h'

def test_assign_category():
    row = pd.Series({
        'RecipeCategory': 'Tarts',
        'Keywords': ['Dessert', 'Lemon', 'Oven'],
        'title': 'Lemon Tart'
    })
    assert assign_category(row) == 'Dessert'

    row = pd.Series({
        'RecipeCategory': 'Chicken',
        'Keywords': ['Chicken', 'Meat', 'Indian'],
        'title': 'Biryani'
    })
    assert assign_category(row) == 'Main Course'
    
def test_to_singular():
    assert to_singular(['apples', 'bananas', 'berries']) == ['apple', 'banana', 'berry']

def test_is_non_vegetarian():
    assert is_non_vegetarian(['chicken', 'broccoli', 'potato']) == True
    assert is_non_vegetarian(['carrot', 'onion', 'tomato', 'egg']) == False

def test_find_world_cuisine():
    assert find_world_cuisine(['Vegetable', 'Mexican', '< 30 Mins']) == 'Mexican'
    assert find_world_cuisine(['Asian', 'Spicy', 'Indian']) == 'Asian'
    assert find_world_cuisine(['Bevrages', 'Fruit', 'Healthy']) == 'Unknown'


### Test main function ###
def test_main():
    # Setup test file paths
    test_recipe_nutrition_path = os.path.join(DATA_DIR, 'recipes.parquet').replace("\\", "/")
    # test_recipe_measurements_path = os.path.join(DATA_DIR, 'recipes_data.csv').replace("\\", "/")
    test_recipe_measurements_path = os.path.join(DATA_DIR, 'recipes_data.parquet').replace("\\", "/")
    output_dir = PROJECT_ROOT / 'data'
    if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    output_path = output_dir / 'sample_recipes_10k.parquet'
    df = main(test_recipe_nutrition_path, test_recipe_measurements_path, output_path)

    assert len(df) <= 10000  #Dataframe should have at most 10,000 rows
    assert df['title'].is_unique  #Titles should be unique
    assert (df['TotalTime_minutes'] > 0).all()  #TotalTime_minutes should be strictly positive
    assert set(df['RecipeType']).issubset(['Breakfast', 'Main Course', 'Dessert', 'Beverages'])  #Check for unexpected recipe types
    assert all(isinstance(keywords, list) and all(k.startswith('#') for k in keywords) for keywords in df['Keywords'])  #Keywords should be lists of strings starting with hashtags
    assert pd.api.types.is_integer_dtype(df['RecipeServings'])  #RecipeServings should be integers
    assert pd.api.types.is_integer_dtype(df['ReviewCount'])  #ReviewCount should be integers
    assert df['Images'].apply(lambda x: isinstance(x, str)).all()  #Images column should only contain strings
    assert not df.isnull().any().any() #DataFrame should not have missing values
