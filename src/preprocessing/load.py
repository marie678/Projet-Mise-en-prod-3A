# loading functions
import numpy as np
import pandas as pd
import re
import ast
from typing import List, Tuple
import inflect
from pathlib import Path
import os
import time
from format import rm_outliers, text_formatting, handle_na

# Global instance of inflect.engine()
inflect_engine = inflect.engine()

# hyper para
keep_col_nutrition = ['Name',
 'AuthorName',
 'CookTime',
 'PrepTime',
 'TotalTime',
 'Description',
 'Images',
 'RecipeCategory',
 'Keywords',
 'RecipeIngredientQuantities', #
 'RecipeIngredientParts', #
 'AggregatedRating',
 'ReviewCount',
 'Calories',
 'FatContent',
 'SaturatedFatContent',
 'CholesterolContent',
 'SodiumContent',
 'CarbohydrateContent',
 'FiberContent',
 'SugarContent',
 'ProteinContent',
 'RecipeServings',
 'RecipeInstructions']

keep_col_measurements = ['title','directions','ingredients','link','NER']

#
def load_nutrition_data(nutrition_data_path:str) -> tuple[pd.DataFrame, list]:
    """
    This function loads a nutrition dataset, processes it, and returns the cleaned DataFrame and a list of unique recipe names.

    Steps involved:
    1. Loads the dataset from a specified path (`nutrition_data_path`), keeping only the relevant columns.
    2. Drops duplicate rows based on 'Name' and 'AuthorName'.
    3. Removes outliers from the data using the `rm_outliers` function.
    4. Formats textual columns (such as 'RecipeInstructions' and 'Keywords') to ensure proper structure.
    5. Handles missing values and ensures proper type conversion for numeric and string columns.
    6. Returns the cleaned DataFrame and a list of unique recipe names.

    Parameters:
    nutrition_data_path (str): The path to the nutrition dataset.

    Returns:
    pd.DataFrame: The cleaned and processed DataFrame.
    list: A list of unique recipe names.
    """
    # load first data set
    start_time = time.time()
    df = pd.read_parquet(nutrition_data_path, columns=keep_col_nutrition)
    end_time = time.time()
    print("Nutrition data set loaded in --- %s seconds ---" % (end_time - start_time))
    df = df.drop_duplicates(subset=['Name','AuthorName'])
    # remove outliers
    df = rm_outliers(df)
    # Process array-like columns
    to_format =  ['RecipeInstructions', 'Keywords']
    text_formatting(df, to_format)
    numeric_float_var = ['AggregatedRating', 'Calories','FatContent','SaturatedFatContent','CholesterolContent'
               ,'SodiumContent','CarbohydrateContent','FiberContent','SugarContent','ProteinContent']
    numeric_int_var= ['ReviewCount','RecipeServings']
    string_var= ['Name','AuthorName','CookTime','PrepTime','TotalTime','Description','RecipeCategory']
    list_var = ['Images','Keywords','RecipeInstructions']
    df = handle_na(df, numeric_float_var, numeric_int_var, string_var, list_var)
    print("Cleaned in --- %s seconds ---" % (time.time() - end_time))
    recipe_name = df['Name'].drop_duplicates().to_list()
    return df, recipe_name

def load_measurements_data(measurements_data_path : str,recipe_merge : List) -> pd.DataFrame:
    """
    This function loads a measurements dataset, filters it based on a provided list of recipe titles 
    to reduce cleaning and merging time, removes duplicate rows, processes array-like columns, 
    and handles missing values.

    Steps involved:
    1. Loads the dataset from the given path (`measurements_data_path`), keeping only the relevant columns.
    2. Filters the data to include only rows where the `title` is in the provided `recipe_merge` list.
    3. Removes duplicate rows based on `title` and `directions`.
    4. Formats array-like columns (such as 'ingredients', 'directions', and 'NER') to ensure proper structure.
    5. Handles missing values and ensures proper type conversion for string and list columns.
    6. Returns the cleaned DataFrame.

    Parameters:
    measurements_data_path (str): The path to the measurements dataset (e.g., a `.parquet` file).
    recipe_merge (list): A list of recipe titles to filter the dataset.

    Returns:
    pd.DataFrame: The cleaned and processed DataFrame.
    """
    start_time = time.time()
    df = pd.read_parquet(measurements_data_path, columns=keep_col_measurements)
    end_time = time.time()
    print("Measurements data set loaded in --- %s seconds ---" % (end_time - start_time))
    df= df[df['title'].isin(recipe_merge)]
    df = df.drop_duplicates(subset=['title', 'directions'])
    to_format = ['ingredients', 'directions', 'NER']
    text_formatting(df,to_format)
    string_var= ['title']
    list_var = ['ingredients', 'directions','NER']
    df = handle_na(df, string_var = string_var, list_var = list_var)
    print("Cleaned in --- %s seconds ---" % (time.time() - end_time))
    return df

def merge(nutrition_data_path:str, measurements_data_path:str) -> pd.DataFrame:
    """
    This function merges two datasets based on recipe names and the first instruction in each dataset.

    Steps involved:
    1. Loads the nutrition data from the given path (`nutrition_data_path`).
    2. Loads the measurements data from the given path (`measurements_data_path`).
    3. Creates a new column 'to_merge' in both datasets, which contains the first element from the `RecipeInstructions` and `directions` columns (if available).
    4. Merges the two datasets using the `Name` and `to_merge` columns in the nutrition data and the `title` and `to_merge` columns in the measurements data.
    5. Returns the merged DataFrame containing data from both datasets.

    Parameters:
    nutrition_data_path (str): The file path to the nutrition dataset (e.g., a `.parquet` file).
    measurements_data_path (str): The file path to the measurements dataset (e.g., a `.parquet` file).

    Returns:
    pd.DataFrame: The merged DataFrame.
    """
    df_nutrition, recipe_merge = load_nutrition_data(nutrition_data_path) 
    df_measurements = load_measurements_data(measurements_data_path, recipe_merge)
    # create col to merge
    df_nutrition['to_merge']=df_nutrition['RecipeInstructions'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
    df_measurements['to_merge']=df_measurements['directions'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
    # mege on recipe name and first instruction
    df_merged = pd.merge(df_nutrition, df_measurements, left_on=['Name','to_merge'], right_on=['title','to_merge'], how='inner')
    return df_merged
