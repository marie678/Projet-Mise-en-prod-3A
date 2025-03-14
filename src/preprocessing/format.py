import numpy as np
import pandas as pd
import re
from typing import List, Union
import inflect


# Global instance of inflect.engine()
inflect_engine = inflect.engine()

## Type handling

## Missing values handling
def handle_na(df):
    """
    """

    return df



## Handle outliers

def rm_outliers(df):
    """
    Remove outliers of some numeric variables to keep recipes that make sense
    """
    df = df[(df['Calories'] > 0) & (df['Calories'] <= 1500) & (df['RecipeServings'] <= 72)]
    return df

## Formating functions
def iso_to_minutes(iso_duration: str) -> float:
    """
    Convert ISO 8601 durations to total minutes.

    Args:
        iso_duration (str): duration in ISO 8601 format (example: 'PT1H30M')

    Returns:
        float: duration in minutes
    """
    hours = int(re.search(r'(\d+)H', iso_duration).group(1)) if 'H' in iso_duration else 0
    minutes = int(re.search(r'(\d+)M', iso_duration).group(1)) if 'M' in iso_duration else 0
    return hours * 60 + minutes 
    
def format_duration(duration: str) -> str:
    """
    Function to convert ISO 8601 durations to a more readable format
    
    Args:
        duration (str): duration in ISO 8601 format (example: 'PT1H30M')
    
    Returns: 
        str: duration (example output: '1 h 30 min')
    """
    hours = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    result = []
    if hours:
        result.append(f"{int(hours.group(1))} h")
    if minutes:
        result.append(f"{int(minutes.group(1))} min")
    return ' '.join(result)


def to_singular(ingredients_list: List[str]) -> List[str]:
    """
    Convert a list of ingredient names from plural to singular.

    Args:
        ingredient_list (List[str]): A list of ingredient names

    Returns:
        List[str]: A list of ingredient names where all plural words are converted to singular. Words that are already singular or unrecognized remain unchanged.
    """
    if isinstance(ingredients_list, list):
        return [inflect_engine.singular_noun(ingredient) or ingredient for ingredient in ingredients_list]
    return ingredients_list



def data_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the merged dataset

    Args:
        df (pd.DataFrame): the merged Dataframe 

    Returns:
        pd.DataFrame: cleaned and processed DataFrame
    """

    # Create new variables
    for col in ['CookTime', 'PrepTime', 'TotalTime']:
        df[f'{col}_minutes'] = df[col].apply(iso_to_minutes) 
    df = df[df['TotalTime_minutes']>0]

    # Convert durations to a more readable format
    for col in ['CookTime', 'PrepTime', 'TotalTime']:
        df[col] = df[col].apply(format_duration)
    # Convert ingredients to singular form
    df['NER'] = df['NER'].apply(to_singular)
    # Add '#' before each keyword
    df['Keywords'] = df['Keywords'].apply(lambda keywords: [f'#{word}' for word in keywords])

    return df


