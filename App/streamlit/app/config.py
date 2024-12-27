import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SAMPLE_RECIPE_PATH = os.path.join(BASE_DIR, 'Data\echant_10k_recipes.csv')
SAMPLE_RECIPE_PATH_MAC = os.path.join(BASE_DIR, 'Data/echant_10k_recipes.csv')
SAMPLE_RECIPE_PATH2 = os.path.join(BASE_DIR, 'Data\echant_10k_recipes2.csv')
SAMPLE_RECIPE_PATH3 = os.path.join(BASE_DIR, 'Data/sample_recipes_10k.parquet')
APP_TITLE = """ Welcome to frigo vide 🍊🍐🍄"""