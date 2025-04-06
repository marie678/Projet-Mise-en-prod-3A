import os
from pathlib import Path

import yaml
from loguru import logger
from filter import data_filter
from format import data_preprocessing
from load import merge

logger.add("data_cleaning.log", rotation="10 MB", level="INFO", format="{time} - {level} - {message}")

# Get the absolute path to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
config_path = PROJECT_ROOT / "utils" / "config.yaml"

with open(config_path, "r") as file:
    config = yaml.safe_load(file)
DATA_DIR = config['DATA_DIR']

# path1 = "https://minio.lab.sspcloud.fr/mmeyer/projet-mise-en-prod/data/raw/recipes.parquet"
# path2 = "https://minio.lab.sspcloud.fr/mmeyer/projet-mise-en-prod/data/raw/recipes_data.parquet"

recipe_nutrition_path = os.path.join(DATA_DIR, 'recipes.parquet').replace("\\", "/")
recipe_measurements_path = os.path.join(DATA_DIR, 'recipes_data.parquet').replace("\\", "/")
output_dir = PROJECT_ROOT / 'data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_path = output_dir / 'final_df_1.parquet'

logger.info("Starting data processing pipeline...")

merged = merge(recipe_nutrition_path, recipe_measurements_path)
df_prepro = data_preprocessing(merged)
df_filtered = data_filter(df_prepro)
if output_path:
    df_filtered.to_parquet(output_path, index=False)
    logger.success(f"Processed dataset saved to {output_path}")

logger.success("Pipeline execution completed successfully.")
