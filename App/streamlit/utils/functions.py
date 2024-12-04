import ast
from functools import reduce
import operator

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