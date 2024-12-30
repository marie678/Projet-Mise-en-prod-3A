# Recipe data cleaning

The goal of the preprocessing stage is to create a 10,000-recipe dataframe for our *frigo_vide* application. We combined two public Kaggle datasets and created new variables to provide filtering options for users. 

## Data sources 
The datasets used to obtain the final dataset are sourced from Kaggle:

1. [Food.com Recipes and Reviews](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews/data): This dataset provides a wide variety of recipes along with their nutritional information, cooking times, servings, ratings, and more.
2. [Recipe Dataset (2M+ recipes)](https://www.kaggle.com/datasets/wilmerarltstrmberg/recipe-dataset-over-2m/data): This dataset adds information about ingredient quantities and measurements for each recipe. It contains over 2 million recipes, many of which are also included in the first dataset.

Due to size limitations, these files are not included in this repository.

## Data aggregation
The script in `final_app/Preprocessing/data_cleaning.py` merges the two datasets and outputs a cleaned and processed dataframe. The final dataset can be found at `final_app/Data/sample_recipes_10k.parquet`. 

The final dataset includes new categorical and binary filters to enable users to refine their recipe searches within the app:
* `TotalTime_cat` ("< 30min", "< 1h", "> 1h")
* `RecipeType` ("Main Course", "Dessert", "Beverage", or "Breakfast")
* `Beginner_Friendly`(True/False)
* `Vegetarian_Friendly` (True/False)
* `World_Cuisine` ("Indian", "Chinese", "Mexican", "European", etc.)

### Usage

**1. Download the two datasets and add them to the** `final_app/Data/` **folder**
- `recipes.parquet` ([Food.com Recipes and Reviews](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews/data))
- `recipes_data.csv` ([Recipe Dataset (2M+ recipes)](https://www.kaggle.com/datasets/wilmerarltstrmberg/recipe-dataset-over-2m/data))

**2. Install dependencies**

```
pip install -r requirements.txt
```

**3. Run the data cleaning script**

```
python final_app/Preprocessing/data_cleaning.py
```

**Output file:**
The processed dataset will be saved as `final_app/Data/sample_recipes_10k.parquet`.

## Testing

Unit tests for the data cleaning script are provided in `final_app/Preprocessing/test_data_cleaning.py`.

Samples from the original datasets are included for testing:
- `final_app/Data/test_recipes.parquet`
- `final_app/Data/test_recipes_data.csv`

**To run the tests**
```
pytest final_app/Preprocessing/test_data_cleaning.py
```

