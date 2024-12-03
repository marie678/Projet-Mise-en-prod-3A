import streamlit as st
import pandas as pd
 
st.write("""
# My first app
Hello *world!*
""")
 
df = pd.read_csv("c:\\Users\\guibe\\OneDrive\\Documents\\ENSAE\\3A\\S1\\Infra\\projet\\Projet-Infra-3A\\Data\\echant_10k_recipes.csv")
st.line_chart(df, y ='title')