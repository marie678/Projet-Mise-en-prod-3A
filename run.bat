@echo off
:: Start Flask backend in the background
start python flask_backend/main_api.py

:: Start Streamlit frontend
start streamlit run app.py

