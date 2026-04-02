@echo off
echo ================================================
echo   Social Analytics Backend - Setup Script
echo ================================================

echo.
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo Upgrading pip...
pip install --upgrade pip

echo Installing dependencies (takes ~2 min)...
pip install -r requirements.txt

if not exist ".env" (
    copy .env.example .env
    echo .env created - FILL IN YOUR API KEYS before running!
) else (
    echo .env already exists
)

echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo   Next steps:
echo   1. Open .env and add your API keys
echo   2. Make sure MongoDB is running
echo   3. Run: venv\Scripts\activate
echo   4. Run: python run.py
echo   5. Open: http://localhost:8000/docs
echo.
pause
