# sampling

import pandas as pd


def sample_df_10k(df: pd.DataFrame) -> pd.DataFrame:
    """
    Samples 10,000 rows from the given DataFrame while following a predefined distribution of `RecipeType` and prioritizing rows where the `World_Cuisine` column has values other than 'Unknown'.

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
        if len(df_recipe_type) < sample_size:
            sample_size = len(df_recipe_type) 
        # Prioritize rows where 'Cuisine' is not 'Unknown'
        df_cuisine = df_recipe_type[df_recipe_type['World_Cuisine'] != 'Unknown']
        cuisine_sample_size = min(len(df_cuisine), sample_size)
        sampled_cuisine = df_cuisine.sample(n=cuisine_sample_size, random_state=42)
        # Sample remaining rows if needed
        remaining_sample_size = sample_size - cuisine_sample_size
        df_non_cuisine = df_recipe_type.drop(df_cuisine.index)
        sampled_remaining = df_non_cuisine.sample(n=min(len(df_non_cuisine), remaining_sample_size), random_state=42)
        # Combine prioritized and remaining samples for this category
        sampled_dataframes.append(pd.concat([sampled_cuisine, sampled_remaining]))

    # Combine all sampled categories and shuffle the final DataFrame
    sampled_df = pd.concat(sampled_dataframes)
    sampled_df = sampled_df.sample(frac=1, random_state=42).reset_index(drop=True)
    return sampled_df
