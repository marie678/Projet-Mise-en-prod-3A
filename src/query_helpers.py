"""
module that holds streamlit helper functions for query manipulation in the recipe finder
includes :
    - query cleaning
    - query correction suggestion
"""

import string
import inflect
import streamlit as st
from spellchecker import SpellChecker

def clean_query(query:str)-> str:
    """Cleans the query passed by the user by removing ponctuation between ingredients 
    and singularizing them.

    Args:
       query (str): The raw search query of the user.

    Returns: string (query wwithout ponctuation and in singular)
    """
    inflect_engine = inflect.engine()
    # Remove punctuation
    rm_ponct = ''.join([char for char in query if char not in string.punctuation])
    # Singularize words
    cleaned_query = [inflect_engine.singular_noun(ingredient) or ingredient for ingredient in rm_ponct.split()]
    return ' '.join(cleaned_query)

def query_error(query: list, ing: list, rec: list):
    """Handles query error by returning an error message when no recipe or ingredient are found, 
    either the word might be missplelled and, when corrected, recognized or the word is unknown.
    If the query is correct, returns a message to inform that recipes were found.

    Args:
       query (list): The search query of the user transformed into a list of words.
       ing (list) : The list of unique ingredients.
       rec (list) : The list of recipes.
    """
    response: list = []
    spell = SpellChecker()

    # Check if all words in the query already match valid ingredients or recipes
    if all(word in ing or any(word in r for r in rec) for word in query):
        return st.markdown("Matching recipes or ingredients found! Fill out desired filters and \
                           press *find a recipe*")

    # else attempt a correction
    for word in query:
        if word not in ing and not any(word in r for r in rec):
            corrected_word = spell.correction(word)
            if corrected_word in ing or any(corrected_word in r for r in rec):
                response.append(corrected_word)

    # Respond to the user
    if not response:
        return st.write('No recipes or ingredients found. Try changing your query.')

    return st.write(f'Did you mean {", ".join(response)} ?')
