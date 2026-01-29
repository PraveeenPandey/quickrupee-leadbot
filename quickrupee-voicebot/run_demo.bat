@echo off
REM QuickRupee Voice Bot - Demo Launcher (Windows)

echo.
echo 🎙️  QuickRupee Voice Bot - Demo Mode
echo ======================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo.
    echo ⚠️  No .env file found!
    echo.
    echo Please create .env file with your OpenAI API key:
    echo   copy .env.example .env
    echo   notepad .env
    echo.
    echo Then add your OpenAI API key:
    echo   OPENAI_API_KEY=sk-proj-your-key-here
    echo.
    pause
    exit /b 1
)

REM Check if OpenAI API key is set
findstr /C:"OPENAI_API_KEY=sk-" .env >nul
if errorlevel 1 (
    echo.
    echo ⚠️  OpenAI API key not configured!
    echo.
    echo Please edit .env and add your API key:
    echo   notepad .env
    echo.
    echo Change this line:
    echo   OPENAI_API_KEY=your_openai_api_key_here
    echo To:
    echo   OPENAI_API_KEY=sk-proj-your-actual-key
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Setup complete!
echo.
echo 🚀 Starting demo server...
echo.
echo 📱 Open http://localhost:8000 in your browser
echo 🎤 Click 'Start Conversation' and allow microphone access
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the demo server
python demo_server.py
