########################################### app v3.4 #################################################
# integrate html template

import streamlit as st
import pandas as pd
from functools import reduce
from app.config import SAMPLE_RECIPE_PATH, APP_TITLE
from utils.functions import clean, reformat, split_frame, search_recipes
from streamlit_extras.add_vertical_space import add_vertical_space
import streamlit.components.v1 as components
from jinja2 import Template
import ast

# configuration parameters
st.set_page_config(layout="wide", page_title ='frigo vide', initial_sidebar_state='collapsed')
# st.title(APP_TITLE)

# Load Data
dev_df = "C:\\Users\\marie\\OneDrive\\Documents\\cours\\ensae\\3A\\infras_et_systemes_logiciels\\df_development"
df = pd.read_csv(dev_df)
# df = pd.read_csv(SAMPLE_RECIPE_PATH)
# df['clean_dir'] = clean(df['directions'])

# Extract filters values
ingredient_list: set = {x for x in sorted(set(reformat(df['NER']))) if pd.notna(x)}
recipe_durations: set = {x for x in sorted(set(df['CookTime_minutes'])) if pd.notna(x)}
ratings: set = {x for x in sorted(set(df['AggregatedRating'])) if pd.notna(x)}

# define constants
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
if 'total_recipes' not in st.session_state:
    st.session_state.total_recipes = None
if 'search_df' not in st.session_state:
    st.session_state.search_df = None
if 'research_summary' not in st.session_state:
    st.session_state.research_summary = None
if 'filters' not in st.session_state:
    st.session_state.filters = None


filters = {}
research_summary = ''

with st.form("filter_form", clear_on_submit=True):
    st.write("Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    # Ingredients filter
    ingredients = col1.multiselect("Choose one or more ingredient(s)", ingredient_list, default=None) #st.session_state.selected_ingredients if st.session_state.selected_ingredients else 
    st.session_state.selected_ingredients = ingredients  # Update selected ingredients in session state
    if ingredients:
        nb_ingredients = len(ingredients)
        filters['ingredients'] = ingredients
        research_summary += f'ingredients : *{ingredients}*'

    # Recipe duration filter CHANGE TO SLIDER ????
    recipe_time = col2.selectbox("Choose the duration of your recipe", recipe_durations, index=None) #recipe_durations.index(st.session_state.selected_duration) if st.session_state.selected_duration else 
    st.session_state.selected_duration = recipe_time  # Update duration in session state
    if recipe_time: # default to 'Select recipe time'?
        filters['recipe_durations'] = recipe_time
        research_summary += f' - recipe duration <= *{recipe_time}* min.'

    # Ratings filter
    rating = col3.selectbox("Choose a rating", ratings, index=None) #ratings.index(st.session_state.selected_rating) if st.session_state.selected_rating else 
    st.session_state.selected_rating = rating  # Update rating in session state
    if rating:
        filters['ratings'] = rating
        research_summary += f' - rating >= *{rating}*'
    
    other = col4.selectbox("Choose other", ['A', 'B', 'C'], index=None)
    # st.session_state.selected_rating = rating  # Store rating in session state
    if other:
        filters['other'] = other
    # st.write(filters)
    st.session_state.research_summary = research_summary
    st.session_state.filters = filters
    submitted = st.form_submit_button("Apply Filters")

if submitted:
        st.write(filters)
        df_search, total_nr_recipes = search_recipes(df, st.session_state.filters, filter_columns)

        st.session_state.search_df, st.session_state.total_recipes = df_search, total_nr_recipes

        # Split the DataFrame to get the current page data
        # start_idx = (current_page - 1) * batch_size
        # end_idx = start_idx + batch_size
        # page = df_search.iloc[start_idx:end_idx]




def handle_recipe_click(index):
    st.session_state.title = page.iloc[index]['title']
    st.session_state.ingredients = page.iloc[index]['ingredients']
    st.session_state.instructions = page.iloc[index]['directions']
    st.session_state.link = page.iloc[index]['link']
    # st.session_state.correspondance_rate = page.iloc[index]['%']

    # page['%'] = page['NER'].apply(lambda ing: round((nb / len(ast.literal_eval(ing)))*100,1))
    # best = rep['%'].idxmax()
    recipe_title = page.iloc[index]['title']
    c_time = page.iloc[index]['CookTime_minutes']
    prep_time = page.iloc[index]['PrepTime_minutes']
    tot_time = page.iloc[index]['TotalTime_minutes']
    # description = page.iloc[index]['Description']
    keywords = page.iloc[index]['Keywords']
    img_link = page.iloc[index]['Images']
    ing = ast.literal_eval(page.iloc[index]['ingredients'])
    # percent = rep['%'].max()
    directions = page.iloc[index]['clean_dir'] 
    rec_link = page.iloc[index]['link']
    with open("pages/templatev1.2.1.html", "r") as template_file:
        template_content = template_file.read()
        jinja_template = Template(template_content)

    # Render the template with dynamic data
    rendered_html = jinja_template.render(title=recipe_title, prep_time = prep_time, c_time = c_time, tot_time = tot_time,
                                          items=ing, prc = None, dir =directions, keywords = keywords,
                                          link = rec_link, desc= None, img = img_link)

    # Display the HTML in Streamlit app
    components.html(rendered_html, height=800, scrolling=True)

    # with st.spinner() :
    #     st.switch_page("./pages/Recettes.py")

if st.session_state.search_df is not None :
    st.write(f"Research summary : {st.session_state.research_summary} \n")
    st.write(f"There are **{st.session_state.total_recipes}** recipes corresponding :\n")
    add_vertical_space(2)
    recipe_placeholder = st.container()
    bottom_menu = st.columns((4,1,1))
    with bottom_menu[2]:
        batch_size = st.selectbox('Recipes per page', options=[25,50,100])
        total_pages = int(len(st.session_state.search_df)/batch_size) if len(st.session_state.search_df)>batch_size else 1
    with bottom_menu[1]:
        current_page = st.number_input('Page', min_value=1, max_value=total_pages, step=1, key='page_input')
    with bottom_menu[0]:
        st.markdown(f"Page **{current_page}** of **{total_pages}**")

    pages = split_frame(st.session_state.search_df, batch_size+1)
    page = (pages[current_page - 1])
    # st.write(current_page, page)

# faire le lien avec fichier CSS, pas encore actif
# st.markdown(
# """
# <style>
# button {
#     background: none!important;
#     border: none;
#     padding: 0!important;
#     color: black !important;
#     text-decoration: none;
#     cursor: pointer;
#     border: none !important;
# }
# button:hover {
#     text-decoration: none;
#     color: black !important;
# }
# button:focus {
#     outline: none !important;
#     box-shadow: none !important;
#     color: black !important;
# }
# </style>
# """,
# unsafe_allow_html=True,
# )
    for i in range(len(page)):
        if recipe_placeholder.button(page.iloc[i]['title'], key=f"recipe_button_{i}"):
            handle_recipe_click(i)