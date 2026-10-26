@echo off
title Smart Device Forecast System
echo ===================================================
echo Starting Smart Device Forecast (Backend + Frontend)
echo ===================================================

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    python -m scripts.seed --sample
)

start "Backend Server (FastAPI on Port 8000)" cmd /k "call .venv\Scripts\activate.bat && uvicorn backend.app.main:app --reload --port 8000"

cd frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm.cmd install
)
start "Frontend Server (Vite on Port 5173)" cmd /k "call npm.cmd run dev"

echo.
echo Both servers have been launched in separate windows!
echo Backend:  http://127.0.0.1:8000/api/docs
echo Frontend: http://localhost:5173
echo ===================================================
pause
