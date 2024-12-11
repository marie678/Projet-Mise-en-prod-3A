import ast
from functools import reduce
import operator
import pandas as pd
import streamlit as st

def clean(col) :
    col2 = []
    col3 = []
    for i in col : 
        i = ast.literal_eval(i)
        col2.append(i)
    for j in col2 : 
        if len(j) == 1 : 
            col3.append(j[0].split('.'))
        else : 
            col3.append(j)
    return col3

def reformat(col):
    col2 = []
    for i in col : 
        i = ast.literal_eval(i)
        col2.append(i)
    return  reduce(operator.concat, col2)

def split_frame(input_df: pd.DataFrame, rows: int) -> pd.DataFrame:
    """
    Splits the input DataFrame into chunks of a specified number of rows.

    Args:
        input_df (DataFrame): the dataset that will be split.
        rows (int): the number of rows per split

    Returns:
        list[DataFrame]: A list of DataFrame chunks.
    """
    df = [input_df.iloc[i:i+rows-1,:] for i in range(0, len(input_df), rows)]
    return df



@st.cache_data(show_spinner=True)
def search_recipes(original_df: pd.DataFrame, filters:list, dict_columns: dict): # -> pd.DataFrame, int:
    """
    dict_columns = corresponding column in a dataset to filter on, for a given filter
    """
    base: str = r'^{}'
    expr: str = '(?=.*{})'
    filtered_df = original_df.copy()
    if 'ingredients' in filters.keys():
        col, value = dict_columns['ingredients'], filters['ingredients']
        filtered_df = filtered_df[filtered_df[col].str.contains(base.format(''.join(expr.format(w) for w in value)))]
    if 'recipe_durations' in filters.keys():
        col, value = dict_columns['recipe_durations'], filters['recipe_durations']
        filtered_df = filtered_df[filtered_df[col] <= (value)]
    if 'ratings' in filters.keys():
        col, value = dict_columns['ratings'], filters['ratings']
        filtered_df = filtered_df[filtered_df[col] >= (value)]
    # # Compute the correspondance rates
    # df_search['%'] = df_search['NER'].apply(lambda ing: round((nb_ingredients / len(ast.literal_eval(ing)))*100,1))
    # df_search = df_search.sort_values('%', ascending=False)
    total_nr_recipes : int = len(filtered_df)
    return filtered_df, total_nr_recipes