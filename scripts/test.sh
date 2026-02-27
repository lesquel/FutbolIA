#!/usr/bin/env bash
# ===========================================
# GoalMind - Test Runner (Linux/macOS)
# ===========================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}⚽ GoalMind - Test Runner${NC}"
echo "=========================================="
echo ""

EXIT_CODE=0

# -------------------------------------------
# Backend Tests
# -------------------------------------------
echo -e "${BLUE}[BACKEND]${NC} Running Python tests..."
cd "$ROOT_DIR/futbolia-backend"

if uv run pytest tests/ -v --tb=short 2>/dev/null; then
    echo -e "${GREEN}[BACKEND]${NC} ✅ Tests passed"
else
    echo -e "${RED}[BACKEND]${NC} ❌ Tests failed"
    EXIT_CODE=1
fi

echo ""

# -------------------------------------------
# Backend Lint
# -------------------------------------------
echo -e "${BLUE}[BACKEND]${NC} Running Ruff lint..."
if uv run ruff check . 2>/dev/null; then
    echo -e "${GREEN}[BACKEND]${NC} ✅ Lint passed"
else
    echo -e "${RED}[BACKEND]${NC} ❌ Lint issues found"
    EXIT_CODE=1
fi

echo -e "${BLUE}[BACKEND]${NC} Checking Ruff format..."
if uv run ruff format --check . 2>/dev/null; then
    echo -e "${GREEN}[BACKEND]${NC} ✅ Format check passed"
else
    echo -e "${RED}[BACKEND]${NC} ❌ Format issues found (run: make format)"
    EXIT_CODE=1
fi

echo ""

# -------------------------------------------
# Frontend Lint
# -------------------------------------------
echo -e "${BLUE}[FRONTEND]${NC} Running ESLint..."
cd "$ROOT_DIR/futbolia-mobile"

if bun run lint 2>/dev/null; then
    echo -e "${GREEN}[FRONTEND]${NC} ✅ ESLint passed"
else
    echo -e "${RED}[FRONTEND]${NC} ❌ ESLint issues found"
    EXIT_CODE=1
fi

echo -e "${BLUE}[FRONTEND]${NC} Checking Prettier format..."
if bun run format:check 2>/dev/null; then
    echo -e "${GREEN}[FRONTEND]${NC} ✅ Prettier check passed"
else
    echo -e "${RED}[FRONTEND]${NC} ❌ Prettier issues found (run: make format)"
    EXIT_CODE=1
fi

echo ""

# -------------------------------------------
# Frontend TypeCheck
# -------------------------------------------
echo -e "${BLUE}[FRONTEND]${NC} Running TypeScript check..."
if bun run typecheck 2>/dev/null; then
    echo -e "${GREEN}[FRONTEND]${NC} ✅ Type check passed"
else
    echo -e "${RED}[FRONTEND]${NC} ❌ Type errors found"
    EXIT_CODE=1
fi

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
else
    echo -e "${RED}❌ Some checks failed. See above for details.${NC}"
fi
echo "=========================================="

exit $EXIT_CODE
