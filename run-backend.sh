#!/bin/bash

# Backend Server Startup Script

echo "🚀 Starting Backend Server..."

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/lib/python*/site-packages/flask" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the Flask server
echo "Starting Flask server on http://localhost:5000..."
python app.py