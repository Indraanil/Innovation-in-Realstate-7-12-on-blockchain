@echo off
REM BharatPropChain Quick Start Script

echo ========================================
echo   BharatPropChain - Starting...
echo ========================================
echo.

REM Start the backend server
echo [1/2] Starting Backend API Server...
start "BharatPropChain Backend" cmd /k "cd /d %~dp0 && python backend/app.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo [2/2] Opening Frontend in Browser...
start "" "file:///%~dp0frontend/index.html"

echo.
echo ========================================
echo   BharatPropChain is Running!
echo ========================================
echo.
echo Backend API: http://localhost:5000
echo Frontend: Opened in your default browser
echo.
echo Press any key to stop the backend server...
pause >nul

REM This will close the script but the backend window stays open
echo.
echo Note: Close the "BharatPropChain Backend" window to stop the server.
