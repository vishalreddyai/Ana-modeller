#!/bin/bash

# Full-Stack Authentication Website Setup Script

echo "🚀 Setting up Full-Stack Authentication Website..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Setup Backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Backend setup complete!"

# Setup Frontend
echo "📦 Setting up frontend..."
cd ../frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

echo "✅ Frontend setup complete!"

# Go back to root directory
cd ..

echo ""
echo "🎉 Setup complete! Here's how to run the application:"
echo ""
echo "1. Start the backend server:"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   python app.py"
echo ""
echo "2. Start the frontend server (in a new terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Open your browser and visit:"
echo "   http://localhost:3000"
echo ""
echo "📚 For more information, see README.md"
echo ""
echo "Happy coding! 🚀"