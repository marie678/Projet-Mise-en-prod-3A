
import pandas as pd
from functools import reduce
import operator
import ast

base = r'^{}'
expr = '(?=.*{})'
echant = pd.read_csv('echant_10k_recipes.csv')
echant = echant.set_index(echant['Unnamed: 0'].values).drop(columns=['Unnamed: 0'])




def prediction(text):
        sentence = text.split(' ')
        nb = len(sentence)
        rep = echant[echant['NER'].str.contains(base.format(''.join(expr.format(w) for w in sentence)))][['title','NER']]
        rep['%'] = rep['NER'].apply(lambda sentence: round((nb / len(ast.literal_eval(sentence)))*100,1))
        best = rep['%'].idxmax()
        res = echant.loc[best]
        return res
    
print(prediction('olive tomato'))