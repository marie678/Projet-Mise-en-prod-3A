"""Data cleaning functions and creation of the final dataset."""
import ast
import os
import re
from pathlib import Path
from typing import List

import inflect
import yaml
import numpy as np
import pandas as pd
import s3fs
from loguru import logger


# Global instance of inflect.engine()
inflect_engine = inflect.engine()
# Configure Loguru logging
logger.add("data_cleaning.log", rotation="10 MB", level="INFO", format="{time} - {level} - {message}")


# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
config_path = PROJECT_ROOT / "utils" / "config.yaml"

with open(config_path, "r") as file:
    config = yaml.safe_load(file)
DATA_DIR = config['DATA_DIR']
S3_ENDPOINT_URL = config["s3"]["endpoint_url"]

## Utility functions
def iso_to_minutes(iso_duration: str) -> float:
    """
    Convert ISO 8601 durations to total minutes.

    Args:
        iso_duration (str): duration in ISO 8601 format (example: 'PT1H30M')

    Returns:
        float: duration in minutes
    """
    hours = int(re.search(r'(\d+)H', iso_duration).group(1)) if 'H' in iso_duration else 0
    minutes = int(re.search(r'(\d+)M', iso_duration).group(1)) if 'M' in iso_duration else 0
    return hours * 60 + minutes


def categorize_duration(total_minutes: float) -> str:
    """
    Categorizes durations into three categories:
        - '< 30min' if the duration is less than 30 minutes
        - '< 1h' if the duration is between 30 and 60 minutes
        - '> 1h' if the duration is more than 60 minutes

    Args:
        total_minutes (float): duration in minutes

    Returns:
        str: the category string
    """
    return '< 30min' if total_minutes <= 30 else '< 1h' if total_minutes <= 60 else '> 1h'


def format_duration(duration: str) -> str:
    """
    Function to convert ISO 8601 durations to a more readable format.

    Args:
        duration (str): duration in ISO 8601 format (example: 'PT1H30M')

    Returns:
        str: duration (example output: '1 h 30 min')
    """
    hours = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    result = []
    if hours:
        result.append(f"{int(hours.group(1))} h")
    if minutes:
        result.append(f"{int(minutes.group(1))} min")
    return ' '.join(result)


def assign_category(row: pd.Series) -> str:
    """
    Assign a recipe category based on the values in the RecipeCategory, Keywords and title columns
    using predefined patterns.

    Args:
        row (pd.Series): A row of the DataFrame containing the following columns:
            - RecipeCategory: A string representing the recipe category
            - Keywords: A list of keywords related to the recipe
                        (e.g., ['Dessert', 'Oven', '< 4 Hours', 'Easy'])
            - title: A string representing the title of the recipe

    Returns:
        str: The assigned category for the recipe, between 4 possibilities:
                    'Main Course', 'Breakfast', 'Dessert', 'Beverages'
             If no match is found, returns 'Other'
    """
    patterns = {
        'Main Course': r'lunch|meal|meat|chicken|beef|pork|steak|turkey|duck|fish|salmon|lamb|crab\
            |shrimp|lobster|tuna|vegetable|potato|rice|noodle|pasta|penne|spaghetti|macaroni|\
                linguine|pizza|quiche|lentil|tofu|onion|soup|stew|dressing',
        'Breakfast': r'breakfast',
        'Dessert': r'dessert|cake|cookie|brownie|muffin|biscuit|babka|sweet|candy|sugar|banana',
        'Beverages': r'beverage|cocktail|smoothie|lemonade|coffee',
    }
    # Check the RecipeCategory, Keywords and title for patterns
    for source in ['RecipeCategory', 'Keywords', 'title']:
        value = row[source]
        if value is not None and isinstance(value, (str, list)):
            text = (
                " ".join([str(v) for v in value if v is not None])
                if isinstance(value, list)
                else value
            )
            for category, pattern in patterns.items():
                if re.search(pattern, text.lower()):
                    return category
    return 'Other'


def to_singular(ingredients_list: List[str]) -> List[str]:
    """
    Convert a list of ingredient names from plural to singular.

    Args:
        ingredient_list (List[str]): A list of ingredient names

    Returns:
        List[str]: A list of ingredient names where all plural words are converted to singular.
                   Words that are already singular or unrecognized remain unchanged.
    """
    if isinstance(ingredients_list, list):
        return [
            inflect_engine.singular_noun(ingredient) or ingredient
            for ingredient in ingredients_list
            ]
    return ingredients_list


def is_non_vegetarian(ingredient_list: List[str]) -> bool:
    """
    Check if any non-vegetarian keyword is present in the list of ingredients.

    Args:
        ingredient_list (List[str]): A list of ingredients

    Returns:
        bool: True if any non-vegetarian keyword is found, False otherwise
    """
    non_veg_keywords = {
        'meat', 'chicken', 'beef', 'pork', 'fish', 'bacon', 'ham', 'steak', 'scallop',
        'sausage', 'lamb', 'duck', 'goose', 'lobster', 'shrimp', 'prawn', 'crab',
        'squid', 'octopus', 'calamari', 'oyster', 'mussel', 'clam', 'snail', 'seafood',
        'prosciutto', 'salami', 'pepperoni', 'pancetta', 'chorizo', 'andouille', 'pate',
        'veal', 'venison', 'game', 'poultry', 'turkey', 'bison', 'boar',
        'tuna', 'salmon', 'cod', 'haddock', 'halibut', 'tilapia', 'anchovy', 'anchovies',
    }
    for ingredient in ingredient_list:
        if any(keyword in str(ingredient).lower() for keyword in non_veg_keywords):
            return True
    return False


def find_world_cuisine(keywords: List[str]) -> str:
    """
    Identify and return the first matching world cuisine keyword from a given list of keywords.

    Args:
        keywords (List[str]): A list of keywords related to the recipe.

    Returns:
        str: The name of the matched cuisine from a predefined list, or 'Unknown' if no match is found.
    """
    world_cuisines = [
        'Asian', 'Indian', 'Chinese', 'Thai', 'Japanese', 'Hawaiian', 'Russian', 'Korean',
        'Vietnamese', 'Indonesian', 'Malaysian', 'Pakistani', 'Cantonese', 'Nepalese', 'Cambodian',
        'Mongolian', 'Filipino', 'Asia', 'New Zeland', 'Australian', 'Lebanese', 'Turkish',
        'Palestinian', 'African', 'Egyptian', 'Nigerian', 'Sudanese', 'Ecuadorean', 'Moroccan',
        'Ethiopian', 'Somalian', 'Mexican', 'U.S.', 'Caribbean', 'American', 'Hawaiian', 'Cuban',
        'Venezuelan', 'Peruvian', 'Puerto Rican', 'Colombian', 'Chilean', 'Costa Rican',
        'Guatemalan', 'Honduran', 'Brazilian', 'European', 'Greek', 'German', 'Spanish',
        'Portuguese', 'French', 'Scottish', 'Polish', 'Austrian', 'Hungarian', 'Danish', 'Turkish',
        'Finnish', 'Dutch', 'Belgian', 'Norwegian', 'Welsh', 'Czech', 'Scandinavian', 'Icelandic'
    ]
    keywords_lower = [str(k).lower() for k in keywords]
    for cuisine in world_cuisines:
        if cuisine.lower() in keywords_lower:
            return cuisine
    return 'Unknown'


## Dataset loading functions
def load_nutrition_data(data_path: str, fs: s3fs.S3FileSystem) -> pd.DataFrame:
    """
    Load and clean the recipe dataset with nutrition information.
    The dataset should be in the parquet format.

    Args:
        data_path (str): path to the recipe nutrition dataset in parquet format
        fs (s3fs.S3FileSystem): File system object for remote access (S3/MinIO)

    Returns:
        pd.DataFrame: cleaned dataset
    """
    df = pd.read_parquet(data_path, filesystem=fs)
    df = df.drop(columns=['RecipeId', 'AuthorId', 'DatePublished', 'RecipeYield'])
    df = df.drop_duplicates(subset=['Name', 'AuthorName'])
    # Filter out outliers
    df = df[(df['Calories'] > 0) & (df['Calories'] <= 1500) & (df['RecipeServings'] <= 72)]

    # Process array-like columns
    for col in ['Images', 'Keywords', 'RecipeInstructions']:
        df[col] = df[col].apply(
            lambda x: (
                list(x)
                if isinstance(x, (list, np.ndarray))
                and not all(item is None for item in x)
                else np.nan
            )
        )
    # Extract the first link in the 'Images' column
    df['Images'] = df['Images'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else np.nan
        )
    # Clean recipe instructions
    df['RecipeInstructions'] = df['RecipeInstructions'].apply(
        lambda x: (
            [instr.strip() + '.' for instr in ' '.join(x).split('.') if instr.strip()]
            if isinstance(x, list)
            else np.nan
        )
    )

    df['CookTime'] = df['CookTime'].fillna('PT0M')
    df = df.dropna().reset_index(drop=True)
    df[['ReviewCount', 'RecipeServings']] = df[['ReviewCount', 'RecipeServings']].astype(int)
    return df


def load_measurements_data(data_path: str, fs: s3fs.S3FileSystem) -> pd.DataFrame:
    """
    Load and clean the recipe measurements dataset.

    Args:
        data_path (str): path to the recipe dataset in csv format
        fs (s3fs.S3FileSystem): File system object for remote access (S3/MinIO)

    Returns:
        pd.DataFrame: cleaned dataset
    """
    with fs.open(data_path) as f:
        df = pd.read_csv(f)
    df = df[['title', 'ingredients', 'directions', 'link', 'NER']]
    df = df.drop_duplicates(subset=['title', 'directions'])
    for col in ['ingredients', 'directions', 'NER']:
        df[col] = df[col].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else np.nan
        )
    df = df.dropna().reset_index(drop=True)
    return df


def merge_datasets(df_nutrition: pd.DataFrame, df_measurements: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the nutrition and measurements datasets.

    Args:
        df_nutrition (pd.DataFrame): recipe dataset with nutrition information
        df_measurements (pd.DataFrame): recipe measurements dataset

    Returns:
        pd.DataFrame: merged dataset
    """
    df_merged = pd.merge(df_nutrition, df_measurements, left_on='Name', right_on='title', how='left')

    # Keep the identical recipes in the two datasets based on the instructions
    filtered_df = df_merged[
        df_merged['RecipeInstructions'].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
            )
            == df_merged['directions'].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
                )
        ].reset_index(drop=True)

    df = filtered_df.drop(
        columns=['Name', 'RecipeIngredientQuantities', 'RecipeIngredientParts', 'RecipeInstructions']
        )
    return df


def data_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the merged dataset.

    Args:
        df (pd.DataFrame): the merged Dataframe

    Returns:
        pd.DataFrame: cleaned and processed DataFrame
    """
    # Drop recipes with the same title
    df = df.drop_duplicates(subset=['title'])

    # Create new variables
    for col in ['CookTime', 'PrepTime', 'TotalTime']:
        df[f'{col}_minutes'] = df[col].apply(iso_to_minutes)
    df = df[df['TotalTime_minutes'] > 0]
    df['TotalTime_cat'] = df['TotalTime_minutes'].apply(categorize_duration)
    df['RecipeType'] = df.apply(assign_category, axis=1)
    df = df[df['RecipeType'] != 'Other'].reset_index(drop=True)
    df['Beginner_Friendly'] = df['Keywords'].apply(lambda x: 'Easy' in x)
    df['Vegetarian_Friendly'] = ~df['ingredients'].apply(is_non_vegetarian)
    df['World_Cuisine'] = df['Keywords'].apply(find_world_cuisine)

    # Convert durations to a more readable format
    for col in ['CookTime', 'PrepTime', 'TotalTime']:
        df[col] = df[col].apply(format_duration)
    # Convert ingredients to singular form
    df['NER'] = df['NER'].apply(to_singular)
    # Add '#' before each keyword
    df['Keywords'] = df['Keywords'].apply(lambda keywords: [f'#{word}' for word in keywords])

    return df


def sample_df_10k(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sample 10,000 rows from the given DataFrame while following a predefined distribution of
    `RecipeType` and prioritizing rows where the `World_Cuisine` column has values other than
    'Unknown'.

    Args:
        df (pd.Dataframe): Input DataFrame containing at least the following columns:
            - 'RecipeType' (categorical): Specifies the type of recipe (e.g., 'Dessert', 'Main Course').
            - 'World_Cuisine' (categorical): Specifies the cuisine type or 'Unknown' if not available.

    Returns:
        pd.Dataframe: A DataFrame with 10,000 sampled rows distributed according to `RecipeType`.
    """
    sample_distribution = {
        'Beverages': 1500,
        'Breakfast': 1300,
        'Dessert': 3200,
        'Main Course': 4000
    }
    sampled_dataframes = []

    for recipe_type, sample_size in sample_distribution.items():
        # Filter rows by RecipeType
        df_recipe_type = df[df['RecipeType'] == recipe_type]
        sample_size = min(sample_size, len(df_recipe_type))
        # Prioritize rows where 'Cuisine' is not 'Unknown'
        df_cuisine = df_recipe_type[df_recipe_type['World_Cuisine'] != 'Unknown']
        cuisine_sample_size = min(len(df_cuisine), sample_size)
        sampled_cuisine = df_cuisine.sample(n=cuisine_sample_size, random_state=42)
        # Sample remaining rows if needed
        remaining_sample_size = sample_size - cuisine_sample_size
        df_non_cuisine = df_recipe_type.drop(df_cuisine.index)
        sampled_remaining = df_non_cuisine.sample(
            n=min(len(df_non_cuisine), remaining_sample_size), random_state=42
            )
        # Combine prioritized and remaining samples for this category
        sampled_dataframes.append(pd.concat([sampled_cuisine, sampled_remaining]))

    # Combine all sampled categories and shuffle the final DataFrame
    sampled_df = pd.concat(sampled_dataframes)
    sampled_df = sampled_df.sample(frac=1, random_state=42).reset_index(drop=True)
    return sampled_df


def main(fs: s3fs.S3FileSystem,
         data_path_nutrition: str,
         data_path_measurements: str,
         output_path: Path | None = None) -> None:
    """
    Main function to process and return the final dataset.

    Args:
        fs (s3fs.S3FileSystem): File system object for remote access (S3/MinIO)
        data_path_nutrition (str): Path to the recipe nutrition dataset file (parquet format).
        data_path_measurements (str): Path to the recipe measurements dataset file (csv format).
        output_path (str, optional): Path where to save the processed dataset. If not provided,
                                     the dataset will not be saved.

    Returns:
        pd.DataFrame: The final dataset after merging, preprocessing, and optional sampling.
    """
    try:
# # Check if datasets exist
# if not Path(data_path_nutrition).exists():
#     logger.error(f"Recipe nutrition dataset not found: {data_path_nutrition}")
#     raise FileNotFoundError(f"Recipe nutrition dataset not found: {data_path_nutrition}")
# if not Path(data_path_measurements).exists():
#     logger.error(f"Recipe measurements dataset not found: {data_path_measurements}")
#     raise FileNotFoundError(f"Recipe measurements dataset not found: {data_path_measurements}")

        logger.info("Loading datasets...")
        df_nutrition = load_nutrition_data(data_path_nutrition, fs)
        df_measurements = load_measurements_data(data_path_measurements, fs)
        logger.info("Merging datasets...")
        df = merge_datasets(df_nutrition, df_measurements)
        if df is None or df.empty:
            logger.error("Merged dataset is empty.")
            raise ValueError("Merged dataset is empty.")
        logger.info("Preprocessing data...")
        df = data_preprocessing(df)
        if len(df) > 10000:
            logger.info("Sampling down to 10,000 rows...")
            df = sample_df_10k(df)
        if output_path:
            df.to_parquet(output_path, index=False)
            logger.success(f"Processed dataset saved to {output_path}")

    except Exception as e:
        logger.exception(f"An error occurred while processing the dataset: {e}")
        raise


if __name__ == "__main__":
    try:
        # Initialize the s3fs filesystem with the appropriate endpoint for MinIO
        filesystem = s3fs.S3FileSystem(
            client_kwargs={"endpoint_url": S3_ENDPOINT_URL}
            )

        recipe_nutrition_path = os.path.join(DATA_DIR, 'recipes.parquet').replace("\\", "/")
        recipe_measurements_path = os.path.join(DATA_DIR, 'recipes_data.csv').replace("\\", "/")

        output_path = PROJECT_ROOT / 'Data/sample_recipes_10k.parquet'

        logger.info("Starting data processing pipeline...")
        main(filesystem, recipe_nutrition_path, recipe_measurements_path, output_path)
        logger.success("Pipeline execution completed successfully.")

    except Exception as e:
        logger.error(f"Script execution failed: {e}")
