# Structure and dependencies of Streamlit_app

## `.streamlit` Directory

*   Contains a file for customizing the Streamlit application's presentation, with font and background settings.

## `assets` Directory

*   Contains all static resources used in the app to customize the front end, such as `.css` for styling, images, `.html` templates, and `.js` scripts.

  ## `data` Directory
*   Stores the input data files, raw and preprocessed, used in the app.

## `images` Directory

*   Contains images used in the homepage user tutorial.

## `pages` Directory

*   Contains the `.py` files that implement the recipe search page and the final recipe page.

## `src` Directory

*   Stores the core functions of the application, where the app's data processing and different utility functions are defined.

## `tests` Directory

*   Includes the test files (`.py`) for the Streamlit application and the data preprocessing functions.

## `utils` Directory

*   Contains the app's configuration file `condig.py` with app settings and constants.

## root files

*  An `app.py` file to launch the welcome page of the app in Streamlit.
*  A `Dockerfile` which defines how to build and run the app in a container using Docker.
*  A `.dockerignore` with the files to exclude from the Docker image.
*  A `requirements.txt` file to list the dependencies needed to run the project and install a virtuel environment.
*  A `README.md` with the project documentation.
*  A `.gitignore` with the files to exclude from version control.
