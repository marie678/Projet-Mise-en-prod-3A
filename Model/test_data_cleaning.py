import pytest
from data_cleaning import *

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
    assert find_world_cuisine(['Indian', 'Spicy', 'Asian']) == 'Indian'
    assert find_world_cuisine(['Bevrages', 'Fruit', 'Healthy']) == 'Unknown'