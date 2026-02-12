@echo off
REM BharatPropChain Setup Script for Windows

echo ========================================
echo BharatPropChain Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [5/5] Creating storage directories...
if not exist "storage\uploads" mkdir storage\uploads
if not exist "storage\encrypted" mkdir storage\encrypted

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Edit .env and add your Algorand account details
echo 3. Get test ALGO from https://bank.testnet.algorand.network/
echo 4. Run: python backend/app.py
echo.
echo For frontend, open frontend/index.html in your browser
echo Or run: python -m http.server 8000 --directory frontend
echo.
pause
