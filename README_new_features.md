# Changes with the 'Mise en production' course


Original project structure             |  Current project structure
:-------------------------:|:-------------------------:
 ![](https://github.com/user-attachments/assets/2c4d1c0c-2302-4329-b107-0ab745f07161) | ![](https://github.com/user-attachments/assets/174222c2-6639-492a-a75b-780b495a7946)

 Original repository architecture             |  Current repository architecture
:-------------------------:|:-------------------------:
 ![](https://github.com/user-attachments/assets/2b1a1195-0d0f-4f5d-82a8-c6ecc084dfcd) | ![](https://github.com/user-attachments/assets/50680326-2f31-46aa-98da-269cc9ed12e0)





## Repository organisation / architecture
The new repository architecture was simplified: 

- Insted of giving acces to older versions of the app via a "dev" folder in the repository, we used tags which allow us to retrace our steps and at the same time make the application architecture visible in root.

- There are no longer a separation between data, preprocessing and application folders. This also enables better visibility and faster understanding of the project.

- A unique README now summurises all the application functionnalities and characteristics.


## Data externalisation 

Instead of doing the preprocessing locally on our computers, using the data sets downloaded from kaggle, and then saving the pre processed dataset in Github, we now do the preprocessing as part of the application code using the original data frames in an s3 folder.

We also directly use parquet files to do load and process the data wich saves time and memory. Indeed, 

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

- More functions were created and put in a unique structured folder. Rather than having them in a unique script we created 2 folders and 6 scripts with different functionality for more visibility.

- Load/create the preprocessed dataset when the app is opened for the first time.

- External parametrizaion with YAML file: the dataframes related parameters (columns to keep or format, file names) and s3 connexion parameters were externalized.


## Application

- Created CI tests to continuously test the code quality and run the unit tests + to continuously deploy a Docker image of the app to Dockerhub
- Deployed manually via kubernetes
- Then created a CD pipeline to deploy automatically via ArgoCD
