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
COPY requirements.lock.txt .

# installation des dépendances
RUN pip install -r requirements.lock.txt

COPY . /app

# Instead of copying the script create it directly to avoid errors
RUN echo '#!/bin/bash\n\n# Start Flask backend in the background\npython3 flask_backend/main_api.py > flask.log 2>&1 &\n\n# Wait for Flask to start\necho "Waiting for Flask backend to start..."\nsleep 5\n\n# Start Streamlit frontend\nstreamlit run app.py --server.port=8501 --server.address=0.0.0.0' > /app/run.sh && \
    chmod +x /app/run.sh


EXPOSE 8501
EXPOSE 5000
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["/app/run.sh"]
