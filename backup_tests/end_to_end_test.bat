@echo off
echo ====================================
echo Chatbot AI - End-to-End Test
echo ====================================
echo.

REM Set terminal colors
color 0B

echo Starting backend server on port 8001...
start cmd /k "cd backend && ..\env310\Scripts\activate && ..\env310\Scripts\python app.py"

REM Wait for backend to start
timeout /t 5 /nobreak > nul

echo Starting frontend server...
start cmd /k "cd frontend\chatbotUI && npm run dev"

REM Wait for frontend to start
timeout /t 10 /nobreak > nul

echo Running end-to-end tests...
cd backend
..\env310\Scripts\python test_frontend_flow.py

REM Pause to keep window open
pause
