"""
Module that loads, partially clean and merges the 2 kaggle data sets used in the most eficient way.
includes :
    - load_nutrition_data
    - load_measurements_data
    - merge
"""

import logging
import time
from pathlib import Path
from typing import List

import pandas as pd
import yaml
from src.preprocessing.format import handle_na, rm_outliers, text_formating

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
config_path = PROJECT_ROOT / "utils" / "config.yaml"

with open(config_path, "r") as file:
    config = yaml.safe_load(file)
DATA_DIR = config['DATA_DIR']

# initialize hyper parameters
keep_col_nutrition = config['nutrition_data']['keep_col']
to_format_nutrition = config['nutrition_data']['to_format']
numeric_float_var_nutrition = config['nutrition_data']['numeric_float_var']
numeric_int_var_nutrition = config['nutrition_data']['numeric_int_var']
list_var_nutrition = config['nutrition_data']['list_var']

keep_col_measurements = config['measurements_data']['keep_col']
to_format_measurements = config['measurements_data']['to_format']
list_var_measurements = config['measurements_data']['list_var']


def load_nutrition_data(nutrition_data_path: str) -> tuple[pd.DataFrame, list]:
    """
    This function loads a nutrition dataset, processes it, and returns the cleaned DataFrame and
        a list of unique recipe names.

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
    logging.info("Nutrition data set loaded in --- %s seconds ---", (end_time - start_time))
    df = df.drop_duplicates(subset=['Name', 'AuthorName'])
    # remove outliers
    df = rm_outliers(df)
    # Process array-like columns
    text_formating(df, to_format_nutrition)
    df = handle_na(df, numeric_float_var_nutrition, numeric_int_var_nutrition, list_var_nutrition)
    logging.info("Nutrition data set cleaned in --- %s seconds ---", (time.time() - end_time))
    recipe_name = df['Name'].drop_duplicates().to_list()
    return df, recipe_name


def load_measurements_data(measurements_data_path: str, recipe_merge: List) -> pd.DataFrame:
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
    logging.info("Measurements data set loaded in --- %s seconds ---", (end_time - start_time))
    df = df[df['title'].isin(recipe_merge)]
    df = df.drop_duplicates(subset=['title', 'directions'])
    text_formating(df, to_format_measurements)
    df = handle_na(df, list_var=list_var_measurements)
    logging.info("Measurements data set cleaned in --- %s seconds ---", (time.time() - end_time))
    return df


def merge(nutrition_data_path: str, measurements_data_path: str) -> pd.DataFrame:
    """
    This function merges two datasets based on recipe names and the first instruction in each dataset.

    Steps involved:
    1. Loads the nutrition data from the given path (`nutrition_data_path`).
    2. Loads the measurements data from the given path (`measurements_data_path`).
    3. Creates a new column 'to_merge' in both datasets, which contains the first element from the
                `RecipeInstructions` and `directions` columns (if available).
    4. Merges the two datasets using the `Name` and `to_merge` columns in the nutrition data and the
                `title` and `to_merge` columns in the measurements data.
    5. Returns the merged DataFrame containing data from both datasets.

    Parameters:
    nutrition_data_path (str): The file path to the nutrition dataset (e.g., a `.parquet` file).
    measurements_data_path (str): The file path to the measurements dataset (e.g., a `.parquet` file).

    Returns:
    pd.DataFrame: The merged DataFrame.
    """
    df_nutrition, recipe_merge = load_nutrition_data(nutrition_data_path)
    df_measurements = load_measurements_data(measurements_data_path, recipe_merge)
    start_time = time.time()
    # create column to merge
    df_nutrition['to_merge'] = df_nutrition['RecipeInstructions'].apply(
                            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
                            )
    df_measurements['to_merge'] = df_measurements['directions'].apply(
                            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
                            )
    # merge on recipe name and first instruction
    df_merged = pd.merge(
                        df_nutrition,
                        df_measurements,
                        left_on=['Name', 'to_merge'],
                        right_on=['title', 'to_merge'],
                        how='inner'
                        )
    # keep only usefull columns and non duplicate rows
    df_merged = df_merged.drop_duplicates(subset=['Name', 'AuthorName'])
    df_merged = df_merged.drop(columns=['to_merge', 'RecipeInstructions', 'Name'])
    logging.info("Data merged in --- %s seconds ---", (time.time() - start_time))
    return df_merged
