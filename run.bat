@echo off
cd /d "%~dp0"
echo Starting Commission Reconciliation Dashboard...
echo Open your browser at http://localhost:8501
echo Press Ctrl+C to stop.
echo.
python -m streamlit run app.py
pause
