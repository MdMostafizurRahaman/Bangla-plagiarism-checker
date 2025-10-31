@echo off
echo Starting Bangla Plagiarism Checker...
echo.

echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+ first.
    pause
    exit /b 1
)

echo [2/3] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 18+ first.
    pause
    exit /b 1
)

echo [3/3] Starting servers...
echo.

echo Starting Backend Server...
start "Bangla Plagiarism - Backend" cmd /k "cd /d \"%~dp0backend\" && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "Bangla Plagiarism - Frontend" cmd /k "cd /d \"%~dp0frontend\" && npm run dev"

echo.
echo ===================================
echo   Bangla Plagiarism Checker Started
echo ===================================
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul