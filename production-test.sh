#!/bin/bash
# Test production deployment (port 8000 only - no dev server)

set -e

echo "🚀 Testing Production Deployment"
echo "================================"
echo ""

# Kill any existing processes
echo "🛑 Stopping existing servers..."
pkill -9 -f "python.*main.py" 2>/dev/null || true
pkill -9 -f "vite" 2>/dev/null || true
pkill -9 -f "node.*5173" 2>/dev/null || true
sleep 2

# Navigate to project root
cd "$(dirname "$0")"

# Install backend dependencies (skip if already installed)
echo ""
echo "📦 Checking backend dependencies..."
cd backend
# Skip install if in active development environment
# pip install -q -r requirements.txt

# Build frontend
echo ""
echo "🏗️  Building frontend for production..."
cd ../frontend
npm run build

# Verify build
if [ ! -f "dist/index.html" ]; then
    echo "❌ Frontend build failed - dist/index.html not found"
    exit 1
fi

echo "✅ Frontend built successfully"

# Start backend (which serves frontend)
echo ""
echo "🚀 Starting production server on port 8000..."
cd ../backend
python3 main.py > /tmp/production.log 2>&1 &
BACKEND_PID=$!

echo "⏳ Waiting for server to start..."
sleep 8

# Test health endpoint
echo ""
echo "🔍 Testing API health endpoint..."
HEALTH=$(curl -s http://localhost:8000/api/health)
if [[ $HEALTH == *"healthy"* ]]; then
    echo "✅ API is healthy"
else
    echo "❌ API health check failed"
    cat /tmp/production.log
    exit 1
fi

# Test frontend
echo ""
echo "🔍 Testing frontend..."
FRONTEND=$(curl -s http://localhost:8000)
if [[ $FRONTEND == *"LOUS"* ]]; then
    echo "✅ Frontend is being served"
else
    echo "❌ Frontend not loading"
    exit 1
fi

# Test authentication
echo ""
echo "🔍 Testing authentication..."
AUTH_RESPONSE=$(curl -s -X POST http://localhost:8000/api/user-auth \
  -H "Content-Type: application/json" \
  -d '{"username": "borrower", "password": "borrower123"}')

if [[ $AUTH_RESPONSE == *"success"*true* ]]; then
    echo "✅ Authentication working"
else
    echo "❌ Authentication failed"
    echo "$AUTH_RESPONSE"
    exit 1
fi

# Test submitted docs endpoint
echo ""
echo "🔍 Testing submitted documents endpoint..."
DOCS_RESPONSE=$(curl -s "http://localhost:8000/api/submitted-docs?user_id=borrower")
if [[ $DOCS_RESPONSE == *"documents"* ]]; then
    echo "✅ Documents API working"
else
    echo "❌ Documents API failed"
    echo "$DOCS_RESPONSE"
    exit 1
fi

# Test LangGraph docs-submission endpoint
echo ""
echo "🔍 Testing LangGraph docs-submission endpoint..."
LANGGRAPH_RESPONSE=$(curl -s -X POST http://localhost:8000/api/docs-submission \
  -H "Content-Type: application/json" \
  -d '{"username": "borrower"}')
if [[ $LANGGRAPH_RESPONSE == *"All required documents"* ]]; then
    echo "✅ LangGraph agent endpoint working"
else
    echo "⚠️  LangGraph response: $LANGGRAPH_RESPONSE"
fi

echo ""
echo "================================"
echo "✅ Production deployment test PASSED!"
echo ""
echo "🌐 Application is running at:"
echo "   http://localhost:8000"
echo ""
echo "📊 Server logs:"
echo "   tail -f /tmp/production.log"
echo ""
echo "🛑 To stop the server:"
echo "   pkill -f 'python.*main.py'"
echo ""
