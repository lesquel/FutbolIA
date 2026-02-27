#!/usr/bin/env bash
# ===========================================
# GoalMind - Development Server (Linux/macOS)
# Starts backend + frontend in parallel
# ===========================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Trap to kill background processes on exit
cleanup() {
    echo ""
    echo -e "${BLUE}[INFO]${NC} Shutting down..."
    kill 0 2>/dev/null
    wait 2>/dev/null
    echo -e "${GREEN}[OK]${NC} All processes stopped"
}
trap cleanup EXIT INT TERM

echo ""
echo -e "${BLUE}⚽ GoalMind - Development Server${NC}"
echo "=========================================="
echo ""

# Parse arguments
BACKEND_ONLY=false
FRONTEND_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --backend) BACKEND_ONLY=true; shift ;;
        --frontend) FRONTEND_ONLY=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Start Backend
if [ "$FRONTEND_ONLY" = false ]; then
    echo -e "${GREEN}[BACKEND]${NC} Starting on http://localhost:8000 ..."
    cd "$ROOT_DIR/futbolia-backend"
    uv run python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo -e "${GREEN}[BACKEND]${NC} PID: $BACKEND_PID"
fi

# Start Frontend
if [ "$BACKEND_ONLY" = false ]; then
    echo -e "${GREEN}[FRONTEND]${NC} Starting Expo dev server ..."
    cd "$ROOT_DIR/futbolia-mobile"
    bun start &
    FRONTEND_PID=$!
    echo -e "${GREEN}[FRONTEND]${NC} PID: $FRONTEND_PID"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Development servers running!${NC}"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:8081"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "=========================================="

# Wait for background processes
wait
