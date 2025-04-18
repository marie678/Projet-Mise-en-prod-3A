"""
Module that creates columns used for streamlit filters.
includes :
    - categorize_duration
    - assign_category
    - is_non_vegetarian
    - find_world_cuisine
    - data_filter
"""

import logging
import re
import time
from typing import List

import pandas as pd

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def categorize_duration(total_minutes: float) -> str:
    """
    Categorizes durations into three categories:
        - '< 30min' if the duration is less than 30 minutes
        - '< 1h' if the duration is between 30 and 60 minutes
        - '> 1h' if the duration is more than 60 minutes

    Args:
        total_minutes (float): duration in minutes

    Returns:
        str: the category string
    """
    return '< 30min' if total_minutes <= 30 else '< 1h' if total_minutes <= 60 else '> 1h'


def assign_category(row: pd.Series) -> str:
    """
    Assigns a recipe category based on the values in the RecipeCategory, Keywords and title columns
    using predefined patterns

    Args:
        row (pd.Series): A row of the DataFrame containing the following columns:
            - RecipeCategory: A string representing the recipe category
            - Keywords: A list of keywords related to the recipe
                    (e.g., ['Dessert', 'Oven', '< 4 Hours', 'Easy'])
            - title: A string representing the title of the recipe

    Returns:
        str: The assigned category for the recipe, between 4 possibilities:
                        'Main Course', 'Breakfast', 'Dessert', 'Beverages'
             If no match is found, returns 'Other'
    """
    patterns = {
        'Main Course': r'lunch|meal|meat|chicken|beef|pork|steak|turkey|duck|fish|salmon|lamb|crab|\
            shrimp|lobster|tuna|vegetable|potato|rice|noodle|pasta|penne|spaghetti|macaroni\
            |linguine|pizza|quiche|lentil|tofu|onion|soup|stew|dressing',
        'Breakfast': r'breakfast',
        'Dessert': r'dessert|cake|cookie|brownie|muffin|biscuit|babka|sweet|candy|sugar|banana',
        'Beverages': r'beverage|cocktail|smoothie|lemonade|coffee',
    }
    # Check the RecipeCategory, Keywords and title for patterns
    for source in ['RecipeCategory', 'Keywords', 'title']:
        value = row[source]
        if value is not None and isinstance(value, (str, list)):
            text = (
                ' '.join([str(v) for v in value if v is not None])
                if isinstance(value, list)
                else value
            )
            for category, pattern in patterns.items():
                if re.search(pattern, text.lower()):
                    return category
    return 'Other'


def is_non_vegetarian(ingredient_list: List[str]) -> bool:
    """
    Checks if any non-vegetarian keyword is present in the list of ingredients

    Args:
        ingredient_list (List[str]): A list of ingredients

    Returns:
        bool: True if any non-vegetarian keyword is found, False otherwise
    """
    non_veg_keywords = {
        'meat', 'chicken', 'beef', 'pork', 'bacon', 'ham', 'steak', 'scallop', 'tilapia', 'anchovy',
        'sausage', 'lamb', 'duck', 'goose', 'lobster', 'shrimp', 'prawn', 'crab', 'halibut', 'cod',
        'squid', 'octopus', 'calamari', 'oyster', 'mussel', 'clam', 'snail', 'seafood', 'anchovies',
        'prosciutto', 'salami', 'pepperoni', 'pancetta', 'chorizo', 'andouille', 'pate', 'haddock',
        'veal', 'venison', 'game', 'poultry', 'turkey', 'bison', 'boar', 'fish', 'tuna', 'salmon',
    }
    for ingredient in ingredient_list:
        if any(keyword in str(ingredient).lower() for keyword in non_veg_keywords):
            return True
    return False


def find_world_cuisine(keywords: List[str]) -> str:
    """
    Identifies and returns the first matching world cuisine keyword from a given list of keywords.

    Args:
        keywords (List[str]): A list of keywords related to the recipe.

    Returns:
        str: The name of the matched cuisine from a predefined list, or 'Unknown' if no match is found.
    """
    world_cuisines = [
        'Asian', 'Indian', 'Chinese', 'Thai', 'Japanese', 'Hawaiian', 'Russian', 'Korean', 'French',
        'Vietnamese', 'Indonesian', 'Malaysian', 'Pakistani', 'Cantonese', 'Nepalese', 'Cambodian',
        'Mongolian', 'Filipino', 'Asia', 'New Zeland', 'Australian', 'Lebanese', 'Turkish', 'Dutch',
        'Palestinian', 'African', 'Egyptian', 'Nigerian', 'Sudanese', 'Ecuadorean', 'Moroccan',
        'Ethiopian', 'Somalian', 'Mexican', 'U.S.', 'Caribbean', 'American', 'Hawaiian', 'Cuban',
        'Venezuelan', 'Peruvian', 'Puerto Rican', 'Colombian', 'Chilean', 'Costa Rican', 'Spanish',
        'Guatemalan', 'Honduran', 'Brazilian', 'European', 'Greek', 'German',  'Portuguese',
        'Scottish', 'Polish', 'Austrian', 'Hungarian', 'Danish', 'Turkish', 'Finnish', 'Belgian',
        'Norwegian', 'Welsh', 'Czech', 'Scandinavian', 'Icelandic'
    ]
    keywords_lower = [str(k.strip('#')).lower() for k in keywords]
    for cuisine in world_cuisines:
        if cuisine.lower() in keywords_lower:
            return cuisine
    return 'Unknown'


def data_filter(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create columns for streamlit filters

    Args:
        df (pd.DataFrame): the merged and processed Dataframe

    Returns:
        pd.DataFrame: DataFrame with new columns
    """
    start_time = time.time()
    df.loc[:, 'TotalTime_cat'] = df['TotalTime_minutes'].apply(categorize_duration)
    df.loc[:, 'RecipeType'] = df.apply(assign_category, axis=1)
    df = df[df['RecipeType'] != 'Other'].reset_index(drop=True)
    df.loc[:, 'Beginner_Friendly'] = df['Keywords'].apply(lambda x: '#Easy' in x)
    df.loc[:, 'Vegetarian_Friendly'] = ~df['ingredients'].apply(is_non_vegetarian)
    df.loc[:, 'World_Cuisine'] = df['Keywords'].apply(find_world_cuisine)
    df = df[df['World_Cuisine'].isin(df['World_Cuisine'].value_counts()[lambda x: x > 10].index)]
    logging.info("Nutrition data set loaded in --- %s seconds ---", (time.time() - start_time))

    return df
