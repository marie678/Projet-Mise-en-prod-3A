import ast
from functools import reduce
import operator
import pandas as pd

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