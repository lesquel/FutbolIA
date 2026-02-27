# ===========================================
# GoalMind - Setup Script (Windows PowerShell)
# ===========================================
# Run with: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"

$ROOT_DIR = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Cyan }
function Write-Ok { Write-Host "[OK] $args" -ForegroundColor Green }
function Write-Warn { Write-Host "[WARN] $args" -ForegroundColor Yellow }
function Write-Err { Write-Host "[ERROR] $args" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "⚽ GoalMind - Project Setup" -ForegroundColor Cyan
Write-Host "=========================================="
Write-Host ""

# -------------------------------------------
# Check prerequisites
# -------------------------------------------
Write-Info "Checking prerequisites..."

# Python
try {
    $pythonVersion = python --version 2>&1
    Write-Ok "Python $pythonVersion found"
} catch {
    Write-Err "Python 3 is required. Install from https://python.org"
}

# uv
try {
    $uvVersion = uv --version 2>&1
    Write-Ok "uv found ($uvVersion)"
} catch {
    Write-Warn "uv not found. Installing..."
    irm https://astral.sh/uv/install.ps1 | iex
    Write-Ok "uv installed"
}

# Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Ok "Node.js $nodeVersion found"
} catch {
    Write-Warn "Node.js not found. Install from https://nodejs.org"
}

# Bun
try {
    $bunVersion = bun --version 2>&1
    Write-Ok "Bun found ($bunVersion)"
} catch {
    Write-Warn "Bun not found. Installing..."
    irm https://bun.sh/install.ps1 | iex
    Write-Ok "Bun installed"
}

Write-Host ""

# -------------------------------------------
# Backend Setup
# -------------------------------------------
Write-Info "Setting up backend..."
Set-Location "$ROOT_DIR\futbolia-backend"

# Copy .env if it doesn't exist
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Ok "Created .env from .env.example"
    Write-Warn "Edit futbolia-backend\.env to add your API keys"
} else {
    Write-Ok ".env already exists"
}

# Create data directory
New-Item -ItemType Directory -Force -Path "data\chromadb" | Out-Null
Write-Ok "Data directory created"

# Install Python dependencies
Write-Info "Installing Python dependencies..."
uv sync
Write-Ok "Backend dependencies installed"

Write-Host ""

# -------------------------------------------
# Frontend Setup
# -------------------------------------------
Write-Info "Setting up frontend..."
Set-Location "$ROOT_DIR\futbolia-mobile"

# Copy .env if it doesn't exist
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Ok "Created .env from .env.example"
} else {
    Write-Ok ".env already exists"
}

# Install Node.js dependencies
Write-Info "Installing frontend dependencies..."
bun install
Write-Ok "Frontend dependencies installed"

Write-Host ""

# -------------------------------------------
# Summary
# -------------------------------------------
Set-Location $ROOT_DIR
Write-Host "=========================================="
Write-Host "✅ GoalMind setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit futbolia-backend\.env with your API keys"
Write-Host "  2. Start MongoDB (locally or via Docker)"
Write-Host "  3. Run: task dev  (or: make dev)"
Write-Host ""
Write-Host "Useful commands:"
Write-Host "  task dev          - Start backend + frontend"
Write-Host "  task dev-backend  - Start backend only"
Write-Host "  task dev-frontend - Start frontend only"
Write-Host "  task test         - Run all tests"
Write-Host "  task lint         - Check code quality"
Write-Host "  task docker-up    - Start with Docker Compose"
Write-Host "=========================================="
