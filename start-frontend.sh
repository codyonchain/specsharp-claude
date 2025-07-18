#!/bin/bash

echo "Starting SpecSharp Frontend..."

cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start the development server
echo "Starting React development server..."
npm run dev