###################### page d'affichage #################
import streamlit as st
import ast
from streamlit_extras.add_vertical_space import add_vertical_space

# Get all the recipe elements from the session state
recipe_title = st.session_state['title']
ingredients = st.session_state['ingredients']
instructions = st.session_state['instructions']
link = st.session_state['link']
correspondance_rate = st.session_state['correspondance_rate']


st.markdown(
    f"""
    <h1 style="text-align: center; display: inline-block; padding: 10px; border: 2px solid; border-radius: 8px;">
        {recipe_title}
    </h1>
    """,
    unsafe_allow_html=True
)

add_vertical_space(4)
st.write(f"Pourcentage d'ingrédients déjà à disposition : {correspondance_rate} %.")
st.subheader("Ingrédients et leurs proportions:")
for ingr in ast.literal_eval(ingredients) : 
    st.write(f"- {ingr}")
st.subheader("Instructions:")
for line in ast.literal_eval(instructions) :
    st.write(f"- {line}")


st.write(f"> Lien vers la recette: {link}")