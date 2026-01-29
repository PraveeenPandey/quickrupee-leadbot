#!/bin/bash

# QuickRupee Voice Bot - Demo Launcher
# Automatically sets up and runs the demo

echo "🎙️  QuickRupee Voice Bot - Demo Mode"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo ""
    echo "Please create .env file with your OpenAI API key:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    echo "Then add your OpenAI API key:"
    echo "  OPENAI_API_KEY=sk-proj-your-key-here"
    echo ""
    exit 1
fi

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo ""
    echo "⚠️  OpenAI API key not configured!"
    echo ""
    echo "Please edit .env and add your API key:"
    echo "  nano .env"
    echo ""
    echo "Change this line:"
    echo "  OPENAI_API_KEY=your_openai_api_key_here"
    echo "To:"
    echo "  OPENAI_API_KEY=sk-proj-your-actual-key"
    echo ""
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting demo server..."
echo ""
echo "📱 Open http://localhost:8000 in your browser"
echo "🎤 Click 'Start Conversation' and allow microphone access"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the demo server
python demo_server.py
