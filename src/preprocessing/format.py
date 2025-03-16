import numpy as np
import pandas as pd
import re
from typing import List, Union
import inflect
import ast


# Global instance of inflect.engine()
inflect_engine = inflect.engine()

def handle_type(df: pd.DataFrame, numeric_float_var: List[str] = [], numeric_int_var: List[str] = [], string_var: List[str] = []):
    """
    This function handles type conversions for the provided columns of a DataFrame.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame.
    numeric_float_var (List[str]): List of columns to convert to float. Defaults to empty list.
    numeric_int_var (List[str]): List of columns to convert to Int64 (nullable integers). Defaults to empty list.
    string_var (List[str]): List of columns to convert to string. Defaults to empty list.
    
    Returns:
    pd.DataFrame: The DataFrame with type conversions applied.
    """
    # Convert to float for numeric_float_var if provided
    if numeric_float_var:
        df[numeric_float_var] = df[numeric_float_var].astype(float)
    
    # Convert to Int64 (nullable integer) for numeric_int_var if provided
    if numeric_int_var:
        df[numeric_int_var] = df[numeric_int_var].where(pd.notna(df[numeric_int_var]), np.nan).astype('Int64')
    
    return df

## Missing values handling
def handle_na(df : pd.DataFrame,numeric_float_var : List[str] = [], numeric_int_var : List[str] = [], string_var: List[str] = [], list_var: List[str] = []):
    """
    
    """
    df = handle_type(df, numeric_float_var, numeric_int_var, string_var)
    # we remove na values
    len_before = len(df)
    for var in list_var: 
        df = df[df[var].apply(lambda x: x is not None and len(x) > 0)]
    df = df.dropna()
    len_after=len(df)
    print(f'From {len_before} to {len_after}')
    return df


## Text formating
def text_formatting(df : pd.DataFrame, cols : List):
    """
    Some textual variables have improper format such as string of list of string ('['','']')
    or list of unbroken strings (['_ . _ . _'])
    """
    for col in cols:
        # First, ensure that any non-list or non-array type values are converted into a list
        df[col] = df[col].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') and x.endswith(']') else [x] if isinstance(x, str) else x
        )
        
        # Then ensure that if it's a list (or ndarray), we check for None values and replace with NaN if necessary
        df[col] = df[col].apply(
            lambda x: [np.nan if item is None else item for item in x] if isinstance(x, (list, np.ndarray)) else x
        )
        
        # Then clean
        if col=='RecipeInstructions' or col=='directions':
            df[col] = df[col].apply(
                lambda x: [instr.strip() + '.' for instr in ' '.join([str(item) for item in x]).split('.') if instr.strip()] if isinstance(x, list) else np.nan
            )
        
    return df



## Handle outliers

def rm_outliers(df : pd.DataFrame):
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
    df['CookTime'] = df['CookTime'].fillna('PT0M')
    df = df.dropna()

    # Create new time variables
    for col in ['CookTime', 'PrepTime', 'TotalTime']:
        df.loc[:, f'{col}_minutes']= df[col].apply(iso_to_minutes) 
    df = df[df['TotalTime_minutes']>0]

    # Convert durations to a more readable format
    for col in ['CookTime', 'PrepTime', 'TotalTime']:
        df.loc[:,col] = df[col].apply(format_duration)

    # Convert ingredients to singular form
    df.loc[:,'NER'] = df['NER'].apply(to_singular)

    # Add '#' before each keyword not nan
    df = df[df['Keywords'].apply(lambda x: not any(val == 'nan.' for val in x))]
    df.loc[:,'Keywords'] = df['Keywords'].apply(lambda keywords: [f'#{word}' for word in keywords])

    # keep only one image link per recipe
    df.loc[:,'Images'] = df['Images'].apply(lambda x:x[0])

    return df


