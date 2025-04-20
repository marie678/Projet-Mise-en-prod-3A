# Changes with the 'Mise en production' course

The following general project and more detailed repository structure graphs illustrate how the project has evolved from its previous version. They highlight changes in architecture, data handling, and code structure. For more details on these improvements, refer to the sections below:

Original project structure             |  Current project structure
:-------------------------:|:-------------------------:
 ![](https://github.com/user-attachments/assets/2c4d1c0c-2302-4329-b107-0ab745f07161) | ![](https://github.com/user-attachments/assets/174222c2-6639-492a-a75b-780b495a7946)

 Original repository architecture             |  Current repository architecture
:-------------------------:|:-------------------------:
 ![](https://github.com/user-attachments/assets/2b1a1195-0d0f-4f5d-82a8-c6ecc084dfcd) | ![](https://github.com/user-attachments/assets/ec2ceadd-666f-4937-adec-b52227ac49a8)




## Repository organisation / architecture
The new repository architecture was simplified:

- Instead of giving access to older versions of the app via a "dev" folder in the repository, we used tags which allow us to retrace our steps and at the same time make the application architecture visible in root.

- There is no longer a separation between data, preprocessing and application folders. This also enables better visibility and faster understanding of the project.

- A unique README now summarizes all the application functionalities and characteristics.


## Data externalisation

Instead of doing the preprocessing locally on our computers, using the datasets downloaded from kaggle and then saving the pre processed dataset in Github, we now do the preprocessing as part of the application code using the original dataframes in an s3 folder.

We also directly use parquet files to load and process the data which saves time and memory. Indeed,

<table>
  <tr>
    <td>Data set</td>
    <td colspan="3"> Minimum loading time - memory</td>
  </tr>
  <tr>
    <td> </td>
    <td>CSV</td>
    <td>Parquet</td>
    <td>Optimized parquet</td>
  </tr>
  <tr>
    <td> Recipes </td>
    <td> 16 s - 687k Ko </td>
    <td> 7 s - 174k Ko</td>
    <td> 6 s - 91963124 bites / 11.5k Ko</td>
  </tr>
  <tr>
    <td> recipes_data </td>
    <td> 65 s - 1 256k Ko </td>
    <td> 40 s - 986k Ko </td>
    <td> 36 s - 89245812 bites / 11k Ko</td>
  </tr>
</table>

The preprocessing code was adapted to reduce the compute time.

## Code

- The quality of the code was improved and tested (imports in order, pep8 coding conventions, typing, ...).

- More functions were created and put in a unique structured folder. Rather than having them in a unique script we created 3 folders and 11 scripts with different functionality for more visibility.

- Load/create the preprocessed dataset when the app is opened for the first time only.

- External parametrization with YAML file: the dataframes related parameters (columns to keep or format, file names) and s3 connexion parameters were externalized.
  
- Additional logging was added throughout the codebase to help track the application's state and performance. In particular, the entire preprocessing is now timed step by step, making it easier to identify bottlenecks and optimize performance when needed.

## User Functionality

A new set of user-related features was added to enhance personalization and interactivity:

- User authentication: Users can now register and log in to the app. Authentication is handled via a Flask backend API, compatible with the Streamlit frontend.

- Recipe liking: Logged-in users can like recipes, which are then saved to their personal user space for later access.

- Database integration:

  - A Users table stores authentication information.

  - A Likes table stores the recipes liked by users.

Both databases are implemented using SQLAlchemy for seamless integration with the backend API.

This new layer of functionality lays the groundwork for future personalization features such as saved preferences, history tracking, and personalized recommendations. While we didn’t have time to implement those additional features yet, the most technically challenging part is now done.



## Application

- Created CI tests to continuously test the code quality and run the unit tests + to continuously deploy a Docker image of the app to Dockerhub
- Deployed manually via kubernetes
- Then created a CD pipeline to deploy automatically via ArgoCD
