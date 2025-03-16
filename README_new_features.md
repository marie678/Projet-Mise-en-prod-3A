# Changes with the 'Mise en production' course

2 garphics 


## Repository organisation / architecture
no dev / fianl_app, no separation between data preprocessing and application, unique read me



## Data externalized

Instead of doing the preprocessing locally on our computers using the data sets downloaded from kaggle and then saving the pre processed dataset in Github, we now do the preprocessing as part of the application code using the original data frames in an s3 folder.

We also directly use parquet files to do load and process the data wich saves time and memory.

Preprocessing code 

## Code

- tested quality of code (imports in order)

- created more functions and put them in a unique folder, 

- structured the functions folder more (unique script -> 2 folders and 6 scripts with different functionality for more visibility)

- more parametrizaion with YAML file


## Application

Deployed, new functionalities, Docker
