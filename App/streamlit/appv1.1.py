import streamlit as st
import pandas as pd
from functools import reduce
import operator
import ast

 
st.title("""
Welcome to frigo vide app
""")
 
df = pd.read_csv("c:\\Users\\guibe\\OneDrive\\Documents\\ENSAE\\3A\\S1\\Infra\\projet\\Projet-Infra-3A\\Data\\echant_10k_recipes.csv")
st.write(df)

# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search recipies by ingredients", value="")

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
    st.header(df.loc[best]['title'])
    st.write("Réponse à la requête:", sentence)
    st.write("pourcentage d'ingrédients déjà à disposition", rep['%'].max())
    st.subheader("Ingrédients et leurs proportions:")
    st.write(ast.literal_eval(df.loc[best]['ingredients']))
    st.subheader("Instructions:")
    st.write([i.split('. ') for i in ast.literal_eval(df.loc[best]['directions'])])
    st.write("> Lien vers la recette:", df.loc[best]['link'])


