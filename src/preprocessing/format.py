"""
Module that processes the data.
includes :
    - handle_type
    - handle_na
    - text_formating
    - rm_outliers
    - iso_to_minutes
    - format_duration
    - to_singular
    - data_preprocessing
"""
import ast
import logging
import re
import time
from typing import List

import inflect
import numpy as np
import pandas as pd

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global instance of inflect.engine()
inflect_engine = inflect.engine()


def handle_type(df: pd.DataFrame, numeric_float_var: List[str] = [], numeric_int_var: List[str] = []) -> pd.DataFrame:
    """
    This function handles type conversions for the provided columns of a DataFrame.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    numeric_float_var (List[str]): List of columns to convert to float. Defaults to empty list.
    numeric_int_var (List[str]): List of columns to convert to Int64 (nullable integers).
            Defaults to empty list.

    Returns:
    pd.DataFrame: The DataFrame with type conversions applied.
    """
    if numeric_float_var:
        df[numeric_float_var] = df[numeric_float_var].astype(float)
    if numeric_int_var:
        df[numeric_int_var] = df[numeric_int_var].where(
                                    pd.notna(df[numeric_int_var]), np.nan
                                    ).astype('Int64')

    return df


def handle_na(df: pd.DataFrame,
              numeric_float_var: List[str] = [],
              numeric_int_var: List[str] = [],
              list_var: List[str] = []
              ) -> pd.DataFrame:
    """
    This function handles missing values in the DataFrame by performing type conversions and
        removing rows with missing data.

    Parameters:
    df (pd.DataFrame): The input DataFrame to handle missing values for.
    numeric_float_var (List[str]): List of columns to convert to float type. Defaults to an empty list.
    numeric_int_var (List[str]): List of columns to convert to Int64 (nullable integers).
                                Defaults to an empty list.
    list_var (List[str]): List of columns that contain lists. Rows with empty or `None` values in
                            these columns will be removed. Defaults to an empty list.

    Returns:
    pd.DataFrame: The DataFrame with missing values handled and type conversions applied.
    """
    df = handle_type(df, numeric_float_var, numeric_int_var)
    len_before = len(df)
    for var in list_var:
        df = df[df[var].apply(lambda x: x is not None and len(x) > 0)]
    df = df.dropna()
    len_after = len(df)
    logging.info("%d NA were removed. The data frame has now %d rows", len_before - len_after, len_after)
    return df


def text_formating(df: pd.DataFrame, cols: List) -> pd.DataFrame:
    """
    This function ensures that textual variables in the specified columns are properly formatted.
    It handles cases where textual data is improperly represented, such as strings that look like lists of strings
    or lists of unbroken strings, and formats them consistently.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing textual columns to format.
    cols (List): A list of column names (strings) in the DataFrame that need text formatting.

    Returns:
    pd.DataFrame: The DataFrame with the specified columns properly formatted.
    """
    for col in cols:
        # First, ensure that any non-list or non-array type values are converted into a list
        df[col] = df[col].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') and x.endswith(']') else [x] if isinstance(x, str) else x
        )

        # Then ensure that if it's a list (or ndarray), we check for None values and replace with NaN if necessary
        df[col] = df[col].apply(
            lambda x: [
                np.nan if item is None
                else item for item in x
                ] if isinstance(x, (list, np.ndarray)) else x
            )

        # Then clean
        if col in ('RecipeInstructions', 'directions'):
            df[col] = df[col].apply(
                lambda x: [instr.strip() + '.' for instr in ' '.join([str(item) for item in x]).split('.') if instr.strip()] if isinstance(x, list) else np.nan
            )

    return df


def rm_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove outliers of some numeric variables to keep recipes that make sense.

    Parameters:
    df (pd.DataFrame): The input DataFrame containing the recipes to be filtered.

    Returns:
    pd.DataFrame: The DataFrame with rows containing outliers removed based on predefined rules.
    """
    df = df[(df['Calories'] > 0) & (df['Calories'] <= 1500) & (df['RecipeServings'] <= 72)]
    return df


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
        List[str]: A list of ingredient names where all plural words are converted to singular.
        Words that are already singular or unrecognized remain unchanged.
    """
    if isinstance(ingredients_list, list):
        return [inflect_engine.singular_noun(ingredient) or ingredient for ingredient in ingredients_list]
    return ingredients_list


def data_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the merged dataset by cleaning, formatting, and transforming various columns.

    Args:
        df (pd.DataFrame): the merged Dataframe

    Returns:
        pd.DataFrame: The cleaned and processed DataFrame.
    """
    start_time = time.time()
    df['CookTime'] = df['CookTime'].fillna('PT0M')
    df = df.dropna()

    # Create new time variables
    for col in ['CookTime', 'PrepTime', 'TotalTime']:
        df.loc[:, f'{col}_minutes'] = df[col].apply(iso_to_minutes)
    df = df[df['TotalTime_minutes'] > 0]

    # Convert durations to a more readable format
    for col in ['CookTime', 'PrepTime', 'TotalTime']:
        df.loc[:, col] = df[col].apply(format_duration)

    # Convert ingredients to singular form
    df.loc[:, 'NER'] = df['NER'].apply(to_singular)

    # Add '#' before each keyword not nan
    df = df[df['Keywords'].apply(lambda x: not any(val == 'nan.' for val in x))]
    df.loc[:, 'Keywords'] = df['Keywords'].apply(lambda keywords: [f'#{word}' for word in keywords])

    # keep only one image link per recipe
    df.loc[:, 'Images'] = df['Images'].apply(lambda x: x[0])

    logging.info("Nutrition data set cleaned in --- %s seconds ---", (time.time() - start_time))
    return df
