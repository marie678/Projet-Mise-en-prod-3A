import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import ast


def import_recipe_with_nutrition_dataset(data_path: str) -> pd.DataFrame : 
    """
    Function to import and clean the recipe dataset with nutrition information 

    Args:
        - data_path (str) : path of the recipe nutrition dataset in the parquet format

    Returns:
        - df (pd.DataFrame) : cleaned dataset
    """
    # Import data
    df = pd.read_parquet(data_path)

    # Extract relevant columns
    selected_columns = ['Name', 
                        'AuthorName', 
                        'CookTime', 
                        'PrepTime', 
                        'TotalTime', 
                        'Description', 
                        'Images', 
                        'RecipeCategory', 
                        'Keywords', 
                        'RecipeIngredientQuantities', 
                        'RecipeIngredientParts', 
                        'AggregatedRating', 
                        'ReviewCount',
                        'Calories', 
                        'FatContent', 
                        'ProteinContent', 
                        'RecipeServings', 
                        'RecipeInstructions']
    df = df[selected_columns]

    # Drop duplicate recipes
    df = df.drop_duplicates(subset=['title', 'directions'])

    # Filter out outliers
    df = df[ ( df['Calories'] > 0 ) & ( df['Calories'] <= 1500) & ( df['RecipeServings'] <= 72 ) ]

    # Convert columns of arrays into lists
    array_cols = ['Images', 'Keywords', 'RecipeInstructions']
    for col in array_cols:
        df[col] = df[col].apply(
            lambda x: list(x) if isinstance(x, (list, np.ndarray)) and not all(item is None for item in x) else np.nan
        )   

    # Keep the first link only in the column 'Images'
    df['Images'] = df['Images'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else np.nan
    )

    # Make sure the instructions are split correctly
    df['RecipeInstructions'] = df['RecipeInstructions'].apply(
        lambda x: [instr.strip() + '.' for instr in ' '.join(x).split('.') if instr.strip()] if isinstance(x, list) else np.nan
    )

    # Fill NaN values in the column 'CookTime'
    df['CookTime'] = df['CookTime'].fillna('PT0M')

    # Drop NaN values
    df = df.dropna().reset_index(drop=True)

    return df



def import_recipe_with_measurements_dataset(data_path: str) -> pd.DataFrame : 
    """
    Function to import and clean the recipe dataset with measurements

    Args:
        - data_path (str) : path of the recipe dataset in the csv format

    Returns:
        - df (pd.DataFrame) : cleaned dataset
    """
    # Import data
    df = pd.read_csv(data_path)

    # Extract relevant columns
    selected_columns = ['title', 'ingredients', 'directions', 'link', 'NER']
    df = df[selected_columns]

    # Convert strings to lists
    str_list_cols = ['ingredients', 'directions', 'NER']
    for col in str_list_cols:
        df[col] = df[col].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else np.nan
        )   

    # Drop NaN values
    df = df.dropna().reset_index(drop=True)

    return df



def merge_recipe_datasets(df_nutrition: pd.DataFrame, df_measurements: pd.DataFrame) -> pd.DataFrame:
    """
    Function to merge the two recipe datasets

    Args:
        - df_nutrition (pd.DataFrame) : recipe dataset with nutrition information
        - df_measurements (pd.DataFrame) : recipe dataset with measurements

    Returns:
        - df (pd.DataFrame) : merged dataset
    """
    # Merge the two datasets
    df_merged = pd.merge(df_nutrition, df_measurements, left_on='Name', right_on='title', how='left')

    # Keep the identical recipes in the two datasets based on the instructions
    filtered_df = df_merged[
        df_merged['RecipeInstructions'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None) ==
        df_merged['directions'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
    ].reset_index(drop=True)

    # Drop duplicate columns
    columns_to_drop = ['Name', 'RecipeIngredientQuantities', 'RecipeIngredientParts', 'RecipeInstructions']
    df = filtered_df.drop(columns=columns_to_drop)

    return df