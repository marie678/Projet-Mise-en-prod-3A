[![Construction image Docker](https://github.com/marie678/Projet-Mise-en-prod-3A/actions/workflows/ci-docker.yaml/badge.svg)](https://github.com/marie678/Projet-Mise-en-prod-3A/actions/workflows/ci-docker.yaml)
[![CI Tests](https://github.com/marie678/Projet-Mise-en-prod-3A/actions/workflows/ci-tests.yaml/badge.svg)](https://github.com/marie678/Projet-Mise-en-prod-3A/actions/workflows/ci-tests.yaml)

# What to do with the ingredients left in my fridge?

## Project overview 

This project is part of the "Mise en production des projets de Data Science" course. Based on an existing project, the goal is to develop an interactive application that addresses a business problem, and then deploy it on a production infrastructure. We decided to use a previous project we worked on for our "Infrastructures and software systems" class, in which the goal was to develop a Streamlit application that helps users find recipes based on the ingredients they have in their fridge. 

To understand where we began, please refer to the [Projet-Infra-3A repository](https://github.com/nguibe/Projet-Infra-3A). For details on what has been accomplished, including new features and, most importantly, the reorganization of architecture and code for improved productivity, check out the README_new_features.md file.

## Features

Our application is composed of 3 pages:

- **Homepage**

  - A homepage with an image tutorial and a usage example to guide users through the application.
  
- **Search Page**:
  
  - A search page with a search bar, allowing users to search(\*) in two ways:
    *   **Search by title:** (e.g., pizza, burger, quiche, smoothie, cake).
    *   **Search by ingredients:** (e.g., egg, beef, strawberry). You can add multiple ingredients.
 
  (\*) Note that you can search without any format restrictions (such as plural / singular, lower/upper case, poncutation between words).
  If you're unsure about the spelling of an ingredient, don't worry as we've integrated a spell checker !
  Even if you type "letuce," a suggestion appears below the search bar showing "Did you mean lettuce?".

   - Several filters are available to customize recipes according to your preferences:
     * **Quick and easy recipes:** No time to cook ? Activate the "Beginner friendly" recipes option and select recipes ready in less than an hour!
     * **World Cuisine:** Do you feel like traveling? Choose the country you want to escape to with the "Choose a provenance" filter.
     * **Vegetarian option:** Are you vegetarian? We've thought of you! Find plenty of varied and balanced recipes by activating the "Vegetarian recipes" option.

   Finally, if you don't have a specific recipe or ingredient in mind, you can just look for ideas with the filters.

  - Once you've hit the "Find Recipe" button, a list of results ordered by descending ratings appears with :
    *  The main characteristics of recipes corresponding to your search (title, rating, cook time, etc).
    *  The possibility to go the next page to see more results if there are a lot and also adjust the number of recipes per page.
    *  The possibility to navigate between the recipe page and your current search page in case you want to get a better grasp on a recipe but are still indesicive.
      
- **Recipe Page**

  - Finally this printable recipe page provides all the information you need to prepare your best meal: preparation time, cooking time, ingredients, directions, ratings, nutrition facts, and a link to the recipe page on the original website it came from.


## Data 

The goal of the preprocessing stage is to create a 10,000-recipe dataframe for our *frigo_vide* application. We combined two public Kaggle datasets and created new variables to provide filtering options for users. 

**Data sources**

1. [Food.com Recipes and Reviews](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews/data): This dataset provides a wide variety of recipes along with their nutritional information, cooking times, servings, ratings, and more.
2. [Recipe Dataset (2M+ recipes)](https://www.kaggle.com/datasets/wilmerarltstrmberg/recipe-dataset-over-2m/data): This dataset adds information about ingredient quantities and measurements for each recipe. It contains over 2 million recipes, many of which are also included in the first dataset.

These files are stored in SSP Cloud's S3 storage bucket.

**Data aggregation**

The scripts in `src/preprocessing` loads, merges the two datasets and outputs a cleaned and processed dataframe in parquet format. The final dataset can be found at `data/final_df.parquet`. 

The final dataset includes new categorical and binary filters to enable users to refine their recipe searches within the app:
* `TotalTime_cat` ("< 30min", "< 1h", "> 1h")
* `RecipeType` ("Main Course", "Dessert", "Beverage", or "Breakfast")
* `Beginner_Friendly`(True/False)
* `Vegetarian_Friendly` (True/False)
* `World_Cuisine` ("Asian", "Mexican", "European", etc.)

## Repository architecture

<div align="center">
  <img src="https://github.com/user-attachments/assets/174222c2-6639-492a-a75b-780b495a7946" width="700"/>
  <p><em> General project structure </em></p>
</div>

<div align="center">
  <img src="https://github.com/user-attachments/assets/35e499ec-f64c-413c-a745-431b8ec12786" width="800"/>
  <p><em> Functional overwiew of repository architecture </em></p>
</div>


## Installation and Usage

#### As pure application users

Use the application link: https://frigo-vide.lab.sspcloud.fr/ 

#### With python 
The web app is built with streamlit. You can run it with the following steps :

1. Clone this repository
```
git clone https://github.com/marie678/Projet-Mise-en-prod-3A.git
```
2. Install the necessary dependencies from the requirements.lock.txt file
```
pip install -r requirements.lock.txt
```
3. Run the main page of the app 
```
streamlit run app.py
```
You can then navigate through the different pages within the app.

#### With Docker
You can also run our app using the provided **Docker image** (*marie678/mise_en_prod*) with the following steps :

**Prerequisites :**
Ensure that Docker is downloaded and installed on your system, and that you have an active internet connection to pull the image.

1. Pull the Docker Image
```
docker pull marie678/mise_en_prod:v1.0.0
```
This part can take a few minutes to run.

2. Run the Docker Container
```
docker run -p 8501:8501 marie678/mise_en_prod:v1.0.0
```
3. Access the Application \
Once the container is running, open your web browser and go to
``
http://localhost:8501
``

## Contributors

Noémie GUIBE & Marie MEYER

Pauline BIAN and Julia LU also worked on the original project.
