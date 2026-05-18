#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "🦠 PARASITE EVOLVED — Starting demo environment..."

# Kill anything on ports 8000 and 3000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Trap to kill children on Ctrl+C
cleanup() {
    echo ""
    echo "🦠 Shutting down PARASITE EVOLVED..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start backend from project root (uvicorn needs backend.main:app)
cd "$SCRIPT_DIR"
source backend/venv/bin/activate 2>/dev/null || true
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend ready
echo "⏳ Waiting for backend..."
for i in $(seq 1 15); do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    fi
    sleep 1
done

# Pre-warm demo session
cd "$SCRIPT_DIR"
python3 demo.py
echo "✅ Demo session pre-warmed"

# Start frontend
cd "$SCRIPT_DIR/frontend"
npm run build 2>/dev/null && npm run start &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

sleep 5

echo ""
echo "🦠 PARASITE EVOLVED IS READY"
echo "════════════════════════════"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "Demo:     http://localhost:3000/demo"
echo "════════════════════════════"
echo "Press Ctrl+C to stop all services"

# Keep alive
wait
