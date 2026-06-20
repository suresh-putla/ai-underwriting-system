#!/bin/bash

# LOUS Development Startup Script

echo "======================================"
echo "  LOUS - Loan Origination System"
echo "  Starting Development Environment"
echo "======================================"
echo ""

# Check if running from correct directory
if [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    echo "Error: Please run this script from the lous directory"
    exit 1
fi

# Start backend
echo "Starting Backend (FastAPI)..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo "Waiting for backend to start..."
sleep 3

# Start frontend
echo "Starting Frontend (Vite)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "======================================"
echo "  LOUS is now running!"
echo "======================================"
echo ""
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
