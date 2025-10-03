#!/bin/bash

# Frontend Server Startup Script

echo "🚀 Starting Frontend Server..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the Next.js development server
echo "Starting Next.js development server on http://localhost:3000..."
npm run dev