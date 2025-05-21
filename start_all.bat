@echo off
echo ====================================
echo Chatbot AI - Startup Script
echo ====================================
echo.

REM Set terminal colors
color 0B

echo Checking environment...
if not exist "env310" (
    echo Virtual environment not found. Creating environment...
    python -m venv env310
    call env310\Scripts\activate
    python -m pip install --upgrade pip
    echo Please run install_dependencies.bat to install required packages.
    pause
    exit /b 1
) else (
    echo Environment found.
    call env310\Scripts\activate
)

REM Make sure database exists
echo Ensuring database is set up...
call env310\Scripts\python backend\setup_db.py

REM Create test user if needed
echo Setting up test user...
call env310\Scripts\python backend\create_test_user.py

REM Start the backend server
echo Starting backend server on port 8001...
start cmd /k "cd backend && ..\env310\Scripts\activate && ..\env310\Scripts\python app.py"

REM Wait for backend to initialize
echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: npm not found. Please install Node.js.
    echo Press any key to exit...
    pause > nul
    exit /b 1
)

REM Start the frontend
echo Starting frontend...
start cmd /k "cd frontend\chatbotUI && npm install && npm run dev"

echo.
echo ====================================
echo Chatbot AI services started
echo.
echo Backend running at: http://localhost:8001
echo Frontend running at: http://localhost:5173
echo.
echo Default test user:
echo Username: testuser
echo Password: password123
echo.
echo Press any key to shut down all services.
echo ====================================

pause > nul

REM Kill all processes
echo Shutting down services...
taskkill /f /im node.exe > nul 2>&1
taskkill /f /im pythonw.exe > nul 2>&1
taskkill /f /im python.exe > nul 2>&1

echo.
echo All services have been stopped.
echo.
