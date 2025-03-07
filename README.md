# What to do with the ingredients left in my fridge?

## Project overview 

This project is part of the "Mise en production des projets de Data Science" course. Based on an existing project, the goal is to develop an interactive application that addresses a business problem, and then deploy it on a production infrastructure. We decided to use a previous project we worked on for our "Infrastructures and software systems" class, in which the goal was to develop a Streamlit application that helps users find recipes based on the ingredients they have in their fridge, and to deploy this streamlit application into production. 

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


## Data sources

This project uses two datasets sourced from Kaggle. We combined them to create a 10,000 clean and operational recipe data set for our application. Detailed information about the cleaning and preprocessing steps can be found in the [Preprocessing](https://github.com/nguibe/Projet-Infra-3A/tree/main/final_app/Preprocessing) folder.

## Installation and Usage

#### With python 
The web app is built with streamlit. You can run it with the following steps :

1. Clone this repository
```
git clone https://github.com/nguibe/Projet-Infra-3A.git
```
2. Install the necessary dependencies from the requirements.lock.txt file
```
pip install -r requirements.lock.txt
```
3. Navigate to the  `final_app/Streamlit_app` folder
```
cd final_app/Streamlit_app
```
4. Run the main page of the app 
```
streamlit run Welcome_page.py
```
You can then navigate through the different pages within the app.

#### With Docker
You can also run our app using the provided **Docker image** (*marie678/streamlit-final-app*) with the following steps :

**Prerequisites :**
Ensure that Docker is downloaded and installed on your system, and that you have an active internet connection to pull the image.

1. Pull the Docker Image
```
docker pull marie678/streamlit-final-app:latest
```
This part can take a few minutes to run.

2. Run the Docker Container
```
docker run -p 8501:8501 marie678/streamlit-final-app:latest
```
3. Access the Application \
Once the container is running, open your web browser and go to
``
http://localhost:8501
``

## Contributors
- Pauline BIAN
- Noémie GUIBE
- Julia LU
- Marie MEYER
