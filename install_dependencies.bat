@echo off
echo ====================================
echo Chatbot AI - Dependencies Installation
echo ====================================
echo.

REM Set terminal colors
color 0B

echo Activating virtual environment...
call env310\Scripts\activate

echo Installing backend dependencies...
pip install -r requirement.txt

echo Verifying installations...
python -c "import groq; import gtts; import speech_recognition; import fastapi; import uvicorn; import sqlalchemy; import dotenv; print('All required packages are installed!')"

echo.
echo ====================================
echo Installation Complete!
echo Your environment is now ready for the delivery.
echo ====================================

pause
