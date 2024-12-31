# What to do with the ingredients left in my fridge?

## Project overview 

This project is part of the "Infrastructure and software systems" course. The goal of this project is to develop a Streamlit application that helps users find recipes based on the ingredients they have in their fridge. By entering available ingredients and specifying preferences like preparation time, or recipe type, users can receive several recipe suggestions. 

## Features

Our application is composed of 3 pages:

- **Homepage**: A homepage with an image tutorial and a usage example to guide our users.
- **Search Page**:
  A search page with a search bar where you can search(\*) in two ways:
    *   **Search by title:** (e.g., pizza, burger, quiche, smoothie, cake).
    *   **Search by ingredients:** (e.g., egg, beef, strawberry). You can add multiple ingredients.
 
  (\*) Note that you can search without any format restrictions (such as plural / singular, lower/upper case, poncutation between words).

   Several filters are available to customize recipes according to your preferences:
    *   **Quick and easy recipes:** No time to cook ? Activate the "Beginner friendly" recipes option and select recipes ready in less than an hour!
    *   **World Cuisine:** Do you feel like traveling? Choose the country you want to escape to with the "Choose a provenance" filter.
    *   **Vegetarian options:** Are you vegetarian? We've thought of you! Find plenty of varied and balanced recipes by activating the "Vegetarian recipes" option.

  If you're unsure about the spelling of an ingredient, worry not as we've integrated a spell checker ! Even if you type "letuce," a suggestion appears below the search bar showing "Did you mean lettuce?". Finally, if you don't have a specific recipe or ingredients in mind and are actually here to get ideas, you can just look for ideas with the filters.

  Once you've clicked on the "Find Recipe" button, a list of results ordered by descending ratings appears with :
    *  The main characteristics of recipes corresponding to your search (title, rating, cook time, etc).
    *  The possibility to go the next page to see more results if there are a lot and also adjust the number of recipes per page.
    *  The possibility to navigate between the recipe page and your current search page in case you want to get a better grasp on a recipe but are still indesicive.
- **Recipe Page**: Finally this printable recipe page provides all the information you need to prepare your best meal: preparation time, cooking time, ingredients, directions, ratings, nutrition facts, and a link to the original recipe page.


## Data sources

This project uses two datasets sourced from Kaggle. We combined them to create a 10,000 clean and operational recipe data set for our application. Detailed information about the cleaning and preprocessing steps can be found in the [Preprocessing](https://github.com/nguibe/Projet-Infra-3A/tree/main/final_app/Preprocessing) folder.

## Installation 


## Usage 

### With python 
The web app is built with streamlit. You can run it with the following steps :
1. Cloning this repo
``
git clone https://github.com/nguibe/Projet-Infra-3A.git
``
2. Installing the necessary dependencies from the requirements.lock.txt file
``
pip install -r requirements.lock.txt
``
3. Navigating to the  `final_app/Streamlit_app ` folder
``
cd final_app/Streamlit_app
``
4. Running the main page of the app 
``
streamlit run Welcome_page.py
``
You can then navigate through the different pages within the app.

### With Docker
You can also run our app using the provided **Docker image** (*marie678/streamlit-final-app*) with the following steps :
*Prerequisites*
Ensure that Docker is downloaded and installed on your system, and that you have an active internet connection to pull the image.

1. Pull the Docker Image
``
docker pull marie678/streamlit-final-app:latest
``
2. Run the Docker Container
``
docker run -p 8501:8501 marie678/streamlit-app:latest
``
3. Access the Application
Once the container is running, open your web browser and go to
``
http://localhost:8501
``



## Contributors
