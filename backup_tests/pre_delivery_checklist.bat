@echo off
echo ====================================
echo Chatbot AI - Pre-Delivery Checklist
echo ====================================
echo.

REM Set terminal colors
color 0B

echo Activating virtual environment...
call env310\Scripts\activate

echo [1/7] Checking system message implementation...
python backend\check_system_messages.py

echo [2/7] Testing Text-To-Speech functionality...
python backend\test_tts.py

echo [3/7] Testing Groq API integration...
python backend\test_groq_api.py

echo [4/7] Running final conversation test...
python backend\test_chat_final.py

echo [5/7] Testing delivery requirements...
python backend\delivery_check.py

echo [6/7] Starting backend server (for 10 seconds to check startup)...
start /b cmd /c "cd backend && ..\env310\Scripts\python app.py"
timeout /t 10 /nobreak > nul
taskkill /f /im python.exe > nul 2>&1

echo [7/7] Final database check...
python backend\inspect_db.py

echo.
echo ====================================
echo Checklist Complete!
echo If all tests passed, your project is ready for delivery.
echo ====================================

pause
