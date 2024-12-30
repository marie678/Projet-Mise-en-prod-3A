########################################### app v1.0 #################################################
# first steps with streamlit : display the query results in a df form
import streamlit as st
import pandas as pd
from functools import reduce
import operator
import ast
from app.config import SAMPLE_RECIPE_PATH, APP_TITLE

 
st.write(APP_TITLE)
df = pd.read_csv(SAMPLE_RECIPE_PATH)

# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search recipes by ingredients", value="").lower()

# Filter the dataframe using masks
sentence = text_search.split(' ')
nb = len(sentence)
base = r'^{}'
expr = '(?=.*{})'
rep = df[df['NER'].str.contains(base.format(''.join(expr.format(w) for w in sentence)))][['title','NER']]

if text_search:
    rep['%'] = rep['NER'].apply(lambda ing: round((nb / len(ast.literal_eval(ing)))*100,1))
    best = rep['%'].idxmax()
    df_search = df.loc[best]
    st.write(df_search)

else :
    st.write(df)