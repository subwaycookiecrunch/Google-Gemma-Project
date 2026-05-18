#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  🦠 PARASITE EVOLVED — One-Click Launcher
#  Double-click this file to start the entire demo environment.
# ═══════════════════════════════════════════════════════════════
set -e

# Resolve project root (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ─── Terminal styling ─────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

clear
echo ""
echo -e "${RED}${BOLD}"
echo "  ██████╗  █████╗ ██████╗  █████╗ ███████╗██╗████████╗███████╗"
echo "  ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██╔════╝██║╚══██╔══╝██╔════╝"
echo "  ██████╔╝███████║██████╔╝███████║███████╗██║   ██║   █████╗  "
echo "  ██╔═══╝ ██╔══██║██╔══██╗██╔══██║╚════██║██║   ██║   ██╔══╝  "
echo "  ██║     ██║  ██║██║  ██║██║  ██║███████║██║   ██║   ███████╗"
echo "  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝   ╚══════╝"
echo -e "${GREEN}                    E V O L V E D${NC}"
echo ""
echo -e "${DIM}  Biological-inspired AI security analysis platform${NC}"
echo -e "${DIM}  ─────────────────────────────────────────────────${NC}"
echo ""

# ─── Cleanup handler ──────────────────────────────────────────
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo -e "${YELLOW}🦠 Shutting down PARASITE EVOLVED...${NC}"
    [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null && echo -e "${DIM}  Backend stopped${NC}"
    [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null && echo -e "${DIM}  Frontend stopped${NC}"
    # Kill any remaining processes on our ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    echo -e "${GREEN}✅ Clean shutdown complete.${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# ─── Step 1: Preflight checks ────────────────────────────────
echo -e "${CYAN}[1/7]${NC} Running preflight checks..."

# Check Python
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌ python3 not found. Please install Python 3.9+${NC}"
    echo "   brew install python3"
    read -p "Press Enter to exit..."
    exit 1
fi
PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "  ${DIM}Python ${PYVER}${NC}"

# Check Node
if ! command -v node &>/dev/null; then
    echo -e "${RED}❌ node not found. Please install Node.js 18+${NC}"
    echo "   brew install node"
    read -p "Press Enter to exit..."
    exit 1
fi
NODEVER=$(node -v)
echo -e "  ${DIM}Node ${NODEVER}${NC}"

# Check npm
if ! command -v npm &>/dev/null; then
    echo -e "${RED}❌ npm not found. Please install npm${NC}"
    read -p "Press Enter to exit..."
    exit 1
fi

# Check WeasyPrint system deps (for PDF generation)
if ! python3 -c "import ctypes.util; exit(0 if ctypes.util.find_library('gobject-2.0') else 1)" 2>/dev/null; then
    echo -e "  ${YELLOW}⚠️  libgobject not found — PDF reports will use fallback mode${NC}"
    echo -e "  ${DIM}   To enable real PDFs: brew install pango glib gobject-introspection${NC}"
fi

echo -e "  ${GREEN}✅ All prerequisites met${NC}"

# ─── Step 2: Kill stale processes ─────────────────────────────
echo -e "${CYAN}[2/7]${NC} Cleaning ports 3000 & 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
echo -e "  ${GREEN}✅ Ports cleared${NC}"

# ─── Step 3: Python environment ──────────────────────────────
echo -e "${CYAN}[3/7]${NC} Setting up Python environment..."

if [ ! -d "venv" ]; then
    echo -e "  ${DIM}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate
echo -e "  ${DIM}Installing Python dependencies...${NC}"
pip install -q -r requirements.txt 2>/dev/null
echo -e "  ${GREEN}✅ Python environment ready${NC}"

# ─── Step 4: Node environment ────────────────────────────────
echo -e "${CYAN}[4/7]${NC} Setting up Node environment..."

if [ ! -d "frontend/node_modules" ]; then
    echo -e "  ${DIM}Installing npm dependencies (first run, may take a minute)...${NC}"
    (cd frontend && npm install --silent 2>/dev/null)
fi
echo -e "  ${GREEN}✅ Node environment ready${NC}"

# ─── Step 5: Start backend ───────────────────────────────────
echo -e "${CYAN}[5/7]${NC} Starting FastAPI backend..."

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || true
fi

source venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend health
echo -e "  ${DIM}Waiting for backend to be ready...${NC}"
for i in $(seq 1 20); do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Backend is alive (PID: ${BACKEND_PID})${NC}"
        break
    fi
    if [ $i -eq 20 ]; then
        echo -e "  ${RED}❌ Backend failed to start. Check logs above.${NC}"
        read -p "Press Enter to exit..."
        exit 1
    fi
    sleep 1
done

# ─── Step 6: Pre-warm demo session ───────────────────────────
echo -e "${CYAN}[6/7]${NC} Pre-warming demo session (this runs the full AI pipeline)..."
echo -e "  ${DIM}Infiltrating → Evolving → Revealing → Healing → Artifacts${NC}"

python3 demo.py 2>&1 | while IFS= read -r line; do
    echo -e "  ${DIM}${line}${NC}"
done

if [ -f "frontend/public/demo-session.json" ]; then
    SESSION_ID=$(python3 -c "import json; print(json.load(open('frontend/public/demo-session.json'))['session_id'])")
    echo -e "  ${GREEN}✅ Demo session ready: ${SESSION_ID}${NC}"
else
    echo -e "  ${YELLOW}⚠️  Demo pre-warm may have failed. You can still use manual mode.${NC}"
fi

# ─── Step 7: Start frontend ──────────────────────────────────
echo -e "${CYAN}[7/7]${NC} Building & starting Next.js frontend..."

(cd frontend && npm run dev &)
FRONTEND_PID=$!

# Wait for frontend
echo -e "  ${DIM}Waiting for dev server to start...${NC}"
for i in $(seq 1 30); do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Frontend is alive (PID: ${FRONTEND_PID})${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "  ${YELLOW}⚠️  Frontend may still be starting. Try the URL in a moment.${NC}"
    fi
    sleep 1
done

# ─── Ready ────────────────────────────────────────────────────
echo ""
echo -e "${RED}${BOLD}  ═══════════════════════════════════════════════════${NC}"
echo -e "${RED}${BOLD}  🦠 PARASITE EVOLVED IS READY${NC}"
echo -e "${RED}${BOLD}  ═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}▸ Demo Mode:${NC}     http://localhost:3000/demo"
echo -e "  ${CYAN}▸ Full App:${NC}      http://localhost:3000"
echo -e "  ${DIM}▸ Backend API:${NC}   http://localhost:8000"
echo ""
echo -e "  ${DIM}Keyboard shortcuts in Demo Mode:${NC}"
echo -e "  ${DIM}  [Space/→]  Next slide    [←]  Previous slide${NC}"
echo -e "  ${DIM}  [P]        Toggle personality (Parasitic ↔ Symbiotic)${NC}"
echo -e "  ${DIM}  [F]        Fullscreen    [R]  Reset to slide 1${NC}"
echo -e "  ${DIM}  [Esc]      Exit demo${NC}"
echo ""
echo -e "  ${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Open browser automatically
sleep 1
open "http://localhost:3000/demo" 2>/dev/null || true

# Keep alive — wait for background processes
wait
