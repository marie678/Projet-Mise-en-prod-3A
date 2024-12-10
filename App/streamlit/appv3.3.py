########################################### app v3.2 #################################################
# add more filters

import streamlit as st
import pandas as pd
from functools import reduce
from app.config import SAMPLE_RECIPE_PATH, APP_TITLE
from utils.functions import clean, reformat, split_frame
from streamlit_extras.add_vertical_space import add_vertical_space

# configuration parameters
st.set_page_config(layout="wide", page_title ='frigo vide', initial_sidebar_state='collapsed')
# st.title(APP_TITLE)

dev_df = "C:\\Users\\marie\\OneDrive\\Documents\\cours\\ensae\\3A\\infras_et_systemes_logiciels\\df_development"
df = pd.read_csv(dev_df)
# df = pd.read_csv(SAMPLE_RECIPE_PATH)
# df['clean_dir'] = clean(df['directions'])

ingredient_list: set = {x for x in sorted(set(reformat(df['NER']))) if pd.notna(x)}
recipe_durations: set = {x for x in sorted(set(df['CookTime_minutes'])) if pd.notna(x)}
ratings: set = {x for x in sorted(set(df['AggregatedRating'])) if pd.notna(x)}

base: str = r'^{}'
expr: str = '(?=.*{})'
filter_columns: dict = {
    'ingredients': 'NER',
    'recipe_durations': 'CookTime_minutes',
    'ratings': 'AggregatedRating',
}

# initialize session_state with recipe elements + widgets
if 'title' not in st.session_state : 
    st.session_state.title = ''
if 'ingredients' not in st.session_state :
    st.session_state.ingredients = ''
if 'instructions' not in st.session_state:
    st.session_state.instructions = ''
if 'link' not in st.session_state:
    st.session_state.link = ''
if 'correspondance_rate' not in st.session_state :
    st.session_state.correspondance_rate = ''
if 'selected_ingredients' not in st.session_state:
    st.session_state.selected_ingredients = None
if 'selected_duration' not in st.session_state:
    st.session_state.selected_duration = None
if 'selected_rating' not in st.session_state:
    st.session_state.selected_rating = None


@st.cache_data
def search_recipes(original_df: pd.DataFrame, filters:list, dict_columns: dict): # -> pd.DataFrame, int:
    """
    dict_columns = corresponding column in a dataset to filter on, for a given filter
    """
    filtered_df = original_df.copy()
    if 'ingredients' in filters.keys():
        col = dict_columns['ingredients']
        value = filters['ingredients']
        filtered_df = filtered_df[filtered_df[col].str.contains(base.format(''.join(expr.format(w) for w in value)))]
    if 'recipe_durations' in filters.keys():
        col = dict_columns['recipe_durations']
        value = filters['recipe_durations']
        filtered_df = filtered_df[filtered_df[col] <= (value)]
    if 'ratings' in filters.keys():
        col = dict_columns['ratings']
        value = filters['ratings']
        filtered_df = filtered_df[filtered_df[col] >= (value)]
    # # Compute the correspondance rates
    # df_search['%'] = df_search['NER'].apply(lambda ing: round((nb_ingredients / len(ast.literal_eval(ing)))*100,1))
    # df_search = df_search.sort_values('%', ascending=False)
    total_nr_recipes : int = len(filtered_df)
    return filtered_df, total_nr_recipes


filters = {}
research_summary = ''

with st.form("filter_form", clear_on_submit=True):
    st.write("Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    ingredients = col1.multiselect("Choose one or more ingredient(s)", ingredient_list, default=None) #st.session_state.selected_ingredients if st.session_state.selected_ingredients else 
    st.session_state.selected_ingredients = ingredients  # Update selected ingredients in session state
    if ingredients:
        nb_ingredients = len(ingredients)
        filters['ingredients'] = ingredients
        research_summary += f'- ingredients : *{ingredients}*'

    recipe_time = col2.selectbox("Choose the duration of your recipe", recipe_durations, index=None) #recipe_durations.index(st.session_state.selected_duration) if st.session_state.selected_duration else 
    st.session_state.selected_duration = recipe_time  # Update duration in session state
    if recipe_time: # default to 'Select recipe time'?
        filters['recipe_durations'] = recipe_time
        research_summary += f'- recipe duration <= *{recipe_time}* min.'

    rating = col3.selectbox("Choose a rating", ratings, index=None) #ratings.index(st.session_state.selected_rating) if st.session_state.selected_rating else 
    st.session_state.selected_rating = rating  # Update rating in session state
    if rating:
        filters['ratings'] = rating
        research_summary += f'- rating >= *{rating}*'
    
    other = col4.selectbox("Choose other", ['A', 'B', 'C'], index=None)
    # st.session_state.selected_rating = rating  # Store rating in session state
    if other:
        filters['other'] = other
    # st.write(filters)
    submitted = st.form_submit_button("Apply Filters")

if submitted:
        st.write(filters)
        df_search, total_nr_recipes = search_recipes(df, filters, filter_columns)
        
        st.write(f"Research summary : {research_summary} \n")
        st.write(f"There are **{total_nr_recipes}** recipes corresponding :\n")
        add_vertical_space(2)
        recipe_placeholder = st.container()
        add_vertical_space(2)

        bottom_menu = st.columns((4,1,1))
        with bottom_menu[2]:
            batch_size = st.selectbox('Nombre de recettes par page', options=[25,50,100])
            total_pages = int(len(df_search)/batch_size) if len(df_search)>batch_size else 1
        with bottom_menu[1]:
            current_page = st.number_input('Page', min_value=1, max_value=total_pages, step=1, key='page_input')
        with bottom_menu[0]:
            st.markdown(f"Page **{current_page}** of **{total_pages}**")

        # Split the DataFrame to get the current page data
        # start_idx = (current_page - 1) * batch_size
        # end_idx = start_idx + batch_size
        # page = df_search.iloc[start_idx:end_idx]

        pages = split_frame(df_search, batch_size+1)
        page = (pages[current_page - 1])
        st.write(current_page, page)

        # faire le lien avec fichier CSS, pas encore actif
    #     st.markdown(
    #     """
    #     <style>
    #     button {
    #         background: none!important;
    #         border: none;
    #         padding: 0!important;
    #         color: black !important;
    #         text-decoration: none;
    #         cursor: pointer;
    #         border: none !important;
    #     }
    #     button:hover {
    #         text-decoration: none;
    #         color: black !important;
    #     }
    #     button:focus {
    #         outline: none !important;
    #         box-shadow: none !important;
    #         color: black !important;
    #     }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )
        for i in range(len(page)) :
            if recipe_placeholder.button(page.iloc[i]['title'], key=f"recipe_button_{i}"):
                st.session_state.title = page.iloc[i]['title']
                st.session_state.ingredients = page.iloc[i]['ingredients']
                st.session_state.instructions = page.iloc[i]['directions']
                st.session_state.link = page.iloc[i]['link']
                st.session_state.correspondance_rate = page.iloc[i]['%']
                with st.spinner() :
                    st.switch_page("./pages/Recettes.py")


# reset_button = st.button('Réinitialiser')
# if reset_button :
#     st.rerun()
#     st.session_state.search_triggered = False
#     st.session_state.selected_ingredients = []
#     st.session_state.batch_size = 25
#     st.session_state.current_page = 1

#     ingredients = []  # Reset selected ingredients
#     nb_ingredients = 0
#     page = None  # Clear the current page
#     st.empty()  # Clear all dynamic elements in the app
