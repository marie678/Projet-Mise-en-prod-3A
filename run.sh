#!/bin/bash

# Start Flask backend in the background
nohup python3 flask_backend/main_api.py > flask.log 2>&1 &

# Start Streamlit frontend
streamlit run app.py
