import streamlit as st
import pandas as pd
from functools import reduce
import operator
import ast
from app.config import SAMPLE_RECIPE_PATH

 
st.write("""
# My first app
Hello *world!*
""")

df = pd.read_csv(SAMPLE_RECIPE_PATH)

# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search recipes by ingredients", value="").lower()

# Filter the dataframe using masks
sentence = text_search.split(' ')
nb = len(sentence)
base = r'^{}'
expr = '(?=.*{})'
rep = df[df['NER'].str.contains(base.format(''.join(expr.format(w) for w in sentence)))][['title','NER']]
#m2 = df["Title"].str.contains(text_search)
#df_search = df[m1 | m2]

if text_search:
    rep['%'] = rep['NER'].apply(lambda ing: round((nb / len(ast.literal_eval(ing)))*100,1))
    best = rep['%'].idxmax()
    df_search = df.loc[best]
    st.write(df_search)

else :
    st.write(df)