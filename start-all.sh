#!/bin/bash

echo "Starting SpecSharp Application..."
echo "================================="

# Function to check if a port is in use
check_port() {
    lsof -i:$1 > /dev/null 2>&1
}

# Kill any existing processes
echo "Cleaning up existing processes..."
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 2

# Start backend
echo "Starting Backend on port 8001..."
cd /Users/codymarchant/specsharp/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
for i in {1..10}; do
    if curl -s http://localhost:8001/ > /dev/null; then
        echo "✓ Backend is running!"
        break
    fi
    sleep 1
done

# Start frontend
echo "Starting Frontend on port 3000..."
cd /Users/codymarchant/specsharp/frontend
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 5

echo ""
echo "SpecSharp is running!"
echo "===================="
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8001"
echo "API Docs: http://localhost:8001/docs"
echo ""
echo "Process IDs:"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop all services, run: pkill -f 'uvicorn|vite'"
echo ""
echo "Logs:"
echo "Backend: /Users/codymarchant/specsharp/backend/backend.log"
echo "Frontend: /Users/codymarchant/specsharp/frontend/frontend.log"