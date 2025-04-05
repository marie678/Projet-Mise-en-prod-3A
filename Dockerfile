# app/Dockerfile

# image docker de base
FROM python:3.11-slim

# définition du répertoire de travail
WORKDIR /app

# maj environnement linux
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    # git \
    && rm -rf /var/lib/apt/lists/*
# RUN git clone https://github.com/marie678/Projet-Mise-en-prod-3A.git .

# copie des fichiers nécessaires sur l'image
COPY uv_requirements.txt .

# installation des dépendances
RUN pip install -r uv_requirements.txt

COPY . /app

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]