#!/usr/bin/env bash
# ===========================================
# GoalMind - Setup Script (Linux/macOS)
# ===========================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo ""
echo -e "${BLUE}⚽ GoalMind - Project Setup${NC}"
echo "=========================================="
echo ""

# -------------------------------------------
# Check prerequisites
# -------------------------------------------
info "Checking prerequisites..."

# Python
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    success "Python $PYTHON_VERSION found"
else
    error "Python 3 is required. Install from https://python.org"
fi

# uv
if command -v uv &>/dev/null; then
    success "uv found ($(uv --version 2>&1))"
else
    warn "uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    success "uv installed"
fi

# Node.js
if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version)
    success "Node.js $NODE_VERSION found"
else
    warn "Node.js not found. Install from https://nodejs.org"
fi

# Bun
if command -v bun &>/dev/null; then
    success "Bun found ($(bun --version 2>&1))"
else
    warn "Bun not found. Installing..."
    curl -fsSL https://bun.sh/install | bash
    export PATH="$HOME/.bun/bin:$PATH"
    success "Bun installed"
fi

echo ""

# -------------------------------------------
# Backend Setup
# -------------------------------------------
info "Setting up backend..."
cd "$ROOT_DIR/futbolia-backend"

# Copy .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    success "Created .env from .env.example"
    warn "Edit futbolia-backend/.env to add your API keys"
else
    success ".env already exists"
fi

# Create data directory
mkdir -p data/chromadb
success "Data directory created"

# Install Python dependencies
info "Installing Python dependencies..."
uv sync
success "Backend dependencies installed"

# Install pre-commit hooks
if command -v pre-commit &>/dev/null || uv run pre-commit --version &>/dev/null 2>&1; then
    info "Installing pre-commit hooks..."
    cd "$ROOT_DIR"
    uv run --project futbolia-backend pre-commit install
    success "Pre-commit hooks installed"
fi

echo ""

# -------------------------------------------
# Frontend Setup
# -------------------------------------------
info "Setting up frontend..."
cd "$ROOT_DIR/futbolia-mobile"

# Copy .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    success "Created .env from .env.example"
else
    success ".env already exists"
fi

# Install Node.js dependencies
info "Installing frontend dependencies..."
bun install
success "Frontend dependencies installed"

echo ""

# -------------------------------------------
# Summary
# -------------------------------------------
echo "=========================================="
echo -e "${GREEN}✅ GoalMind setup complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit futbolia-backend/.env with your API keys"
echo "  2. Start MongoDB (locally or via Docker)"
echo "  3. Run: make dev  (or: task dev)"
echo ""
echo "Useful commands:"
echo "  make dev          - Start backend + frontend"
echo "  make dev-backend  - Start backend only"
echo "  make dev-frontend - Start frontend only"
echo "  make test         - Run all tests"
echo "  make lint         - Check code quality"
echo "  make docker-up    - Start with Docker Compose"
echo "=========================================="
