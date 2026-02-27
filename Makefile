# ===========================================
# GoalMind - Makefile
# ===========================================
# Cross-platform task runner for Linux/macOS
# For Windows, use Taskfile.yml with: task <target>

.PHONY: help setup dev dev-backend dev-frontend test lint format clean docker-up docker-down

# Default target
help: ## Show this help message
	@echo ""
	@echo "⚽ GoalMind - Available Commands"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""

# -------------------------------------------
# Setup
# -------------------------------------------
setup: ## Install all dependencies (backend + frontend)
	@bash scripts/setup.sh

# -------------------------------------------
# Development
# -------------------------------------------
dev: ## Start backend + frontend dev servers
	@bash scripts/dev.sh

dev-backend: ## Start backend dev server only
	@bash scripts/dev.sh --backend

dev-frontend: ## Start frontend dev server only
	@bash scripts/dev.sh --frontend

# -------------------------------------------
# Testing & Quality
# -------------------------------------------
test: ## Run all tests and checks
	@bash scripts/test.sh

test-backend: ## Run backend tests only
	@cd futbolia-backend && uv run pytest tests/ -v --tb=short

lint: ## Check code quality (lint + format check)
	@echo "🔍 Checking backend..."
	@cd futbolia-backend && uv run ruff check .
	@cd futbolia-backend && uv run ruff format --check .
	@echo ""
	@echo "🔍 Checking frontend..."
	@cd futbolia-mobile && bun run lint
	@cd futbolia-mobile && bun run format:check
	@echo ""
	@echo "✅ All lint checks passed!"

format: ## Auto-format all code
	@echo "🎨 Formatting backend..."
	@cd futbolia-backend && uv run ruff format .
	@cd futbolia-backend && uv run ruff check --fix .
	@echo ""
	@echo "🎨 Formatting frontend..."
	@cd futbolia-mobile && bun run format
	@cd futbolia-mobile && bun run lint:fix
	@echo ""
	@echo "✅ All code formatted!"

# -------------------------------------------
# Docker
# -------------------------------------------
docker-up: ## Start full stack with Docker Compose
	@docker compose up --build -d
	@echo ""
	@echo "✅ GoalMind is running!"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo "  Frontend: http://localhost:3000"

docker-down: ## Stop Docker Compose services
	@docker compose down

docker-logs: ## Show Docker Compose logs
	@docker compose logs -f

# -------------------------------------------
# Maintenance
# -------------------------------------------
clean: ## Remove build artifacts and caches
	@echo "🧹 Cleaning..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .expo -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name web-build -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Clean complete!"

install-hooks: ## Install pre-commit hooks
	@cd futbolia-backend && uv run pre-commit install
	@echo "✅ Pre-commit hooks installed!"
