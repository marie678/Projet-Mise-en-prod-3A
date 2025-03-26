# Changes with the 'Mise en production' course

![image](https://github.com/user-attachments/assets/2c4d1c0c-2302-4329-b107-0ab745f07161)



## Repository organisation / architecture
no dev / final_app, no separation between data preprocessing and application, unique read me



## Data externalized

Instead of doing the preprocessing locally on our computers using the data sets downloaded from kaggle and then saving the pre processed dataset in Github, we now do the preprocessing as part of the application code using the original data frames in an s3 folder.

We also directly use parquet files to do load and process the data wich saves time and memory.

Preprocessing code 

## Code

- tested quality of code (imports in order, pep8 coding conventions, typing, ...)

- created more functions and put them in a unique folder, 

- structured the functions folder better (unique script -> 2 folders and 6 scripts with different functionality for more visibility)

- more parametrizaion with YAML file


## Application

- Created CI tests to continuously test the code quality and run the unit tests + to continuously deploy a Docker image of the app to Dockerhub

Deployed, new functionalities, Docker
