# app/Dockerfile

# image docker de base
FROM python:3.11-slim

# définition du répertoire de travail
WORKDIR /app/Streamlit_app

# maj environnement linux
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    # git \
    && rm -rf /var/lib/apt/lists/*
# RUN git clone https://github.com/nguibe/Projet-Infra-3A.git .

# copie des fichiers nécessaires sur l'image
COPY requirements.lock.txt /app/Streamlit_app/requirements.lock.txt

# installation des dépendances
RUN pip install -r requirements.lock.txt

COPY . /app

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["streamlit", "run", "Welcome_page.py", "--server.port=8501", "--server.address=0.0.0.0"]