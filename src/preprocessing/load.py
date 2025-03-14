# loading functions
import numpy as np
import pandas as pd
import re
import ast
from typing import List, Union
import inflect
from pathlib import Path
import os
import time
from format import rm_outliers

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
def load_nutrition_data(nutrition_data_path):
    # load first data set
    start_time = time.time()
    df = pd.read_parquet(nutrition_data_path, columns=keep_col_nutrition)
    end_time = time.time()
    print("Nutrition data set loaded in --- %s seconds ---" % (end_time - start_time))
    df = df.drop_duplicates(subset=['Name','AuthorName'])
    # remove outliers
    df = rm_outliers(df)
    # Process array-like columns
    for col in ['Images', 'Keywords', 'RecipeInstructions']:
        df[col] = df[col].apply(
            lambda x: list(x) if isinstance(x, (list, np.ndarray)) and not all(item is None for item in x) else np.nan
        )
    # Clean recipe instructions
    df['RecipeInstructions'] = df['RecipeInstructions'].apply(
        lambda x: [instr.strip() + '.' for instr in ' '.join(x).split('.') if instr.strip()] if isinstance(x, list) else np.nan
    )
    df['CookTime'] = df['CookTime'].fillna('PT0M')
    df = df.dropna().reset_index(drop=True)
    print("Cleaned in --- %s seconds ---" % (time.time() - end_time))
    return df

def load_measurements_data(measurements_data_path):
    start_time = time.time()
    df = pd.read_parquet(measurements_data_path, columns=keep_col_measurements)
    end_time = time.time()
    print("Measurements data set loaded in --- %s seconds ---" % (end_time - start_time))
    df = df.drop_duplicates(subset=['title', 'directions'])
    for col in ['ingredients', 'directions', 'NER']:
        df[col] = df[col].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else np.nan
        )  
    df = df.dropna().reset_index(drop=True)
    print("Cleaned in --- %s seconds ---" % (time.time() - end_time))
    return df

def merge(nutrition_data_path, measurements_data_path):
    # create col to merge
    df_nutrition = load_nutrition_data(nutrition_data_path)
    df_measurements = load_measurements_data(measurements_data_path)
    df_nutrition['to_merge']=df_nutrition['RecipeInstructions'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
    df_measurements['to_merge']=df_measurements['directions'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
    # mege on recipe name and first instruction
    df_merged = pd.merge(df_nutrition, df_measurements, left_on=['Name','to_merge'], right_on=['title','to_merge'], how='inner')
    return df_merged
