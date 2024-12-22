import numpy as np
import pandas as pd
import re
import ast


def load_nutrition_data(data_path: str) -> pd.DataFrame: 
    """
    Load and clean the recipe dataset with nutrition information. The dataset should be in the parquet format.

    Args:
        data_path (str): path to the recipe nutrition dataset in parquet format

    Returns:
        pd.DataFrame: cleaned dataset
    """
    # Import data
    df = pd.read_parquet(data_path)

    selected_columns = [
        'Name', 'AuthorName', 'CookTime', 'PrepTime', 'TotalTime', 'Description', 'Images',
        'RecipeCategory', 'Keywords', 'RecipeIngredientQuantities', 'RecipeIngredientParts',
        'AggregatedRating', 'ReviewCount', 'Calories', 'FatContent', 'ProteinContent',
        'RecipeServings', 'RecipeInstructions'
    ]
    df = df[selected_columns]

    # Drop duplicate recipes
    df = df.drop_duplicates(subset=['Name','AuthorName'])

    # Filter out outliers
    df = df[ ( df['Calories'] > 0 ) & ( df['Calories'] <= 1500) & ( df['RecipeServings'] <= 72 ) ]

    # Process array-like columns
    for col in ['Images', 'Keywords', 'RecipeInstructions']:
        df[col] = df[col].apply(
            lambda x: list(x) if isinstance(x, (list, np.ndarray)) and not all(item is None for item in x) else np.nan
        )   

    # Extract the first link in the 'Images' column 
    df['Images'] = df['Images'].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else np.nan
    )

    # Clean recipe instructions
    df['RecipeInstructions'] = df['RecipeInstructions'].apply(
        lambda x: [instr.strip() + '.' for instr in ' '.join(x).split('.') if instr.strip()] if isinstance(x, list) else np.nan
    )

    # Fill missing values in the 'CookTime' column 
    df['CookTime'] = df['CookTime'].fillna('PT0M')

    # Drop missing values
    df = df.dropna().reset_index(drop=True)

    return df


def load_measurements_data(data_path: str) -> pd.DataFrame: 
    """
    Load and clean the recipe measurements dataset

    Args:
        data_path (str): path to the recipe dataset in csv format

    Returns:
        pd.DataFrame: cleaned dataset
    """
    # Import data
    df = pd.read_csv(data_path)
    df = df[['title', 'ingredients', 'directions', 'link', 'NER']]

    # Drop duplicates recipes
    df = df.drop_duplicates(subset=['title', 'directions'])

    # Parse stringified list columns into Python lists
    for col in ['ingredients', 'directions', 'NER']:
        df[col] = df[col].apply(
            lambda x: ast.literal_eval(x) if isinstance(x, str) else np.nan
        )   

    # Drop missing values
    df = df.dropna().reset_index(drop=True)

    return df


def merge_datasets(df_nutrition: pd.DataFrame, df_measurements: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the two recipe datasets

    Args:
        df_nutrition (pd.DataFrame): recipe dataset with nutrition information
        df_measurements (pd.DataFrame): recipe measurements dataset

    Returns:
        pd.DataFrame: merged dataset
    """
    df_merged = pd.merge(df_nutrition, df_measurements, left_on='Name', right_on='title', how='left')

    # Keep the identical recipes in the two datasets based on the instructions
    filtered_df = df_merged[
        df_merged['RecipeInstructions'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None) ==
        df_merged['directions'].apply(lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None)
    ].reset_index(drop=True)

    # Drop unnecessary columns
    df = filtered_df.drop(columns=['Name', 'RecipeIngredientQuantities', 'RecipeIngredientParts', 'RecipeInstructions'])

    return df


def categorize_time(duration: str) -> str:
    """
    Categorizes a string of duration in ISO 8601 format into three categories:
        - '< 30min' if the duration is less than 30 minutes
        - '< 1h' if the duration is between 30 and 60 minutes
        - '> 1h' if the duration is more than 60 minutes

    Args:
        duration (str): duration in ISO 8601 format (example: 'PT1H30M')

    Returns:
        str: the category string
    """
    if pd.isna(duration):
        return np.nan
    hours = re.search(r'(\d+)H', duration)
    minutes = re.search(r'(\d+)M', duration)
    total_minutes = (int(hours.group(1)) * 60 if hours else 0) + (int(minutes.group(1)) if minutes else 0)
    return '< 30min' if total_minutes <= 30 else '< 1h' if total_minutes <= 60 else '> 1h'
    

def duration_to_readable_format(duration: str) -> str:
    """
    Function to convert ISO 8601 durations to a more readable format
    
    Args:
        duration (str): duration in ISO 8601 format (example: 'PT1H30M')
    
    Returns: 
        str: duration (example output: '1 h 30 min')
    """
    if pd.isna(duration): 
        return np.nan
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
    Assigns a recipe category based on the values in the Keywords, title and RecipeCategory columns using predefined patterns

    Args:
        row (pd.Series): A row of the DataFrame containing the following columns:
            - Keywords: A list of keywords related to the recipe (e.g., ['Dessert', 'Oven', '< 4 Hours', 'Easy'])
            - title: A string representing the title of the recipe
            - RecipeCategory: A string representing the recipe category 

    Returns:
        str: The assigned category for the recipe, between 4 possibilities: 'Main Course', 'Breakfast', 'Dessert', 'Beverages'
             If no match is found, returns 'Other'
    """
    patterns = {
        'Main Course': r'lunch|meal|meat|chicken|beef|pork|steak|turkey|duck|fish|salmon|lamb|crab|shrimp|lobster|tuna|vegetable|potato|rice|noodle|pasta|penne|spaghetti|macaroni|linguine|pizza|quiche|bean|lentil|onion|soup|stew|dressing',
        'Breakfast': r'breakfast',
        'Dessert': r'dessert|cake|cookie|brownie|muffin|biscuit|babka|sweet|candy|sugar|banana',
        'Beverages': r'beverage|cocktail|smoothie|lemonade|coffee',
    }
    # Check the Keywords, title, and RecipeCategory for patterns
    for source in ['Keywords', 'title', 'RecipeCategory']:
        value = row[source]
        if value is not None and isinstance(value, (str, list)):
            text = ' '.join([str(v) for v in value if v is not None]) if isinstance(value, list) else value
            for category, pattern in patterns.items():
                if re.search(pattern, text.lower()):
                    return category
    return 'Other'


def is_non_vegetarian(ingredient_list: list) -> bool:
    """
    Checks if any non-vegetarian keyword is present in the list of ingredients

    Args:
        ingredient_list (list): A list of ingredients

    Returns:
        bool: True if any non-vegetarian keyword is found, False otherwise
    """
    # Define the list of non-vegetarian keywords
    non_veg_keywords = {
        'meat', 'chicken', 'beef', 'pork', 'fish', 'bacon', 'ham', 'steak', 'scallop'
        'sausage', 'lamb', 'duck', 'goose', 'lobster', 'shrimp', 'prawn', 'crab',
        'squid', 'octopus', 'calamari', 'oyster', 'mussel', 'clam', 'snail', 'seafood'
        'prosciutto', 'salami', 'pepperoni', 'pancetta', 'chorizo', 'andouille', 'pate', 
        'veal', 'venison', 'game', 'poultry', 'turkey', 'bison', 'boar', 
        'fish', 'tuna', 'salmon', 'cod', 'haddock', 'halibut', 'tilapia', 'anchovy', 'anchovies'
    }
    for ingredient in ingredient_list:
        if any(keyword in str(ingredient).lower() for keyword in non_veg_keywords):
            return True
    return False
    

def create_cuisine_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds 4 binary columns to the input DataFrame: 'Asian', 'African', 'North & South America' and 'Europe and Eastern Europe' based on whether the keywords related to the respective cuisine are found.

    Args:
        df (pd.Dataframe): The input DataFrame. It must contain a column named 'Keywords', which includes lists of strings.

    Returns: 
        pd.Dataframe: The input DataFrame with four additional columns.
    """

    asian_keywords = ['Asian', 'Indian', 'Chinese', 'Southwest Asia (middle East)', 'Thai', 'Japanese', 'Hawaiian', 'Russian', 'Korean', 'Vietnamese', 'Indonesian', 'Malaysian', 'Pakistani', 'Cantonese', 'Nepalese', 'Cambodian', 'Mongolian']
    african_keywords = ['African', 'South African', 'Egyptian', 'Nigerian', 'Sudanese', 'Ecuadorean', 'Moroccan', 'Ethiopian', 'Somalian']
    american_keywords = ['Mexican', 'Southwestern U.S.', 'Caribbean', 'South American', 'Hawaiian', 'Cuban', 'Venezuelan', 'Peruvian', 'Puerto Rican', 'Native American', 'Colombian', 'Chilean', 'Costa Rican', 'Guatemalan', 'Honduran']
    european_keywords = ['Greek', 'Scandinavian', 'German', 'Spanish', 'Russian', 'Hungarian', 'Lebanese', 'Danish', 'Turkish', 'Finnish', 'Dutch', 'Belgian', 'Norwegian', 'Welsh', 'Czech', 'Icelandic']

    def check_keywords(keywords, text):
        text_lower = " ".join(str(item).lower() for item in text) if isinstance(text, list) else str(text).lower() 
        return any(f' {keyword.lower()} ' in f' {text_lower} ' or text_lower.startswith(f'{keyword.lower()} ') or text_lower.endswith(f' {keyword.lower()}') for keyword in keywords)

    df['Asian'] = df['Keywords'].apply(lambda x: check_keywords(asian_keywords, x))
    df['African'] = df['Keywords'].apply(lambda x: check_keywords(african_keywords, x))
    df['North & South America'] = df['Keywords'].apply(lambda x: check_keywords(american_keywords, x))
    df['Europe and Eastern Europe'] = df['Keywords'].apply(lambda x: check_keywords(european_keywords, x))

    return df


def data_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the merged dataset

    Args:
        df (pd.DataFrame): the merged Dataframe 

    Returns:
        pd.DataFrame: cleaned and processed DataFrame
    """
    # Categorize 'TotalTime'
    df['TotalTime_cat'] = df['TotalTime'].apply(categorize_time)

    # Convert readable duration format
    for col in ['CookTime', 'PrepTime', 'TotalTime']:
        df[col] = df[col].apply(duration_to_readable_format)

    # Assign recipe types
    df['RecipeType'] = df.apply(assign_category, axis=1)
    df = df[df['RecipeType'] != 'Other'].reset_index(drop=True)

    # Create boolean variable 'Beginner_Friendly'
    df['Beginner_Friendly'] = df['Keywords'].apply(lambda x: 'Easy' in x)

    # Create boolean variable 'Vegetarian_Friendly'
    df['Vegetarian_Friendly'] = ~df['NER'].apply(lambda x: is_non_vegetarian(x)) 

    # Create world cuisine columns 
    df = create_cuisine_columns(df)

    # Add '#' before each keyword
    df['Keywords'] = df['Keywords'].apply(lambda keywords: [f'#{word}' for word in keywords])

    # Drop recipes with the same title
    df = df.drop_duplicates(subset=['title']).reset_index(drop=True)

    return df


def main(nutrition_path: str, measurements_path: str) -> pd.DataFrame:
    """
    Load and merge the two recipe datasets into a single DataFrame and perform final cleaning
    
    Args:
        nutrition_path (str): path to the recipe nutrition dataset in parquet format
        measurements_path (str): path to the recipe measurements dataset in csv format

    Returns:
        pd.DataFrame: final dataset
    """
    df_nutrition = load_nutrition_data(nutrition_path)
    df_measurements = load_measurements_data(measurements_path)
    df = merge_datasets(df_nutrition, df_measurements)
    return data_preprocessing(df)



if __name__ == "__main__":

    nutrition_path = ''
    measurements_path = ''
    #final_df = main(nutrition_path, measurements_path)
    
    #final_df.to_csv('final_recipes_dataset.csv', index=False)