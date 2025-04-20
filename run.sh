#!/bin/bash

# Start Flask backend in the background
nohup python3 flask_backend/main_api.py > flask.log 2>&1 &

# # Wait a few seconds for Flask to be ready
# echo "Waiting for Flask backend to start..."
# sleep 5

# Start Streamlit frontend
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
