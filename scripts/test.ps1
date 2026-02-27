# ===========================================
# GoalMind - Test Runner (Windows PowerShell)
# ===========================================
# Run with: .\scripts\test.ps1

$ROOT_DIR = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$exitCode = 0

Write-Host ""
Write-Host "⚽ GoalMind - Test Runner" -ForegroundColor Cyan
Write-Host "=========================================="
Write-Host ""

# -------------------------------------------
# Backend Tests
# -------------------------------------------
Write-Host "[BACKEND] Running Python tests..." -ForegroundColor Cyan
Set-Location "$ROOT_DIR\futbolia-backend"

uv run pytest tests/ -v --tb=short
if ($LASTEXITCODE -eq 0) {
    Write-Host "[BACKEND] ✅ Tests passed" -ForegroundColor Green
} else {
    Write-Host "[BACKEND] ❌ Tests failed" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""

# -------------------------------------------
# Backend Lint
# -------------------------------------------
Write-Host "[BACKEND] Running Ruff lint..." -ForegroundColor Cyan
uv run ruff check .
if ($LASTEXITCODE -eq 0) {
    Write-Host "[BACKEND] ✅ Lint passed" -ForegroundColor Green
} else {
    Write-Host "[BACKEND] ❌ Lint issues found" -ForegroundColor Red
    $exitCode = 1
}

Write-Host "[BACKEND] Checking Ruff format..." -ForegroundColor Cyan
uv run ruff format --check .
if ($LASTEXITCODE -eq 0) {
    Write-Host "[BACKEND] ✅ Format check passed" -ForegroundColor Green
} else {
    Write-Host "[BACKEND] ❌ Format issues found (run: task format)" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""

# -------------------------------------------
# Frontend Lint
# -------------------------------------------
Write-Host "[FRONTEND] Running ESLint..." -ForegroundColor Cyan
Set-Location "$ROOT_DIR\futbolia-mobile"

bun run lint
if ($LASTEXITCODE -eq 0) {
    Write-Host "[FRONTEND] ✅ ESLint passed" -ForegroundColor Green
} else {
    Write-Host "[FRONTEND] ❌ ESLint issues found" -ForegroundColor Red
    $exitCode = 1
}

Write-Host "[FRONTEND] Checking Prettier format..." -ForegroundColor Cyan
bun run format:check
if ($LASTEXITCODE -eq 0) {
    Write-Host "[FRONTEND] ✅ Prettier check passed" -ForegroundColor Green
} else {
    Write-Host "[FRONTEND] ❌ Prettier issues found (run: task format)" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""

# -------------------------------------------
# Frontend TypeCheck
# -------------------------------------------
Write-Host "[FRONTEND] Running TypeScript check..." -ForegroundColor Cyan
bun run typecheck
if ($LASTEXITCODE -eq 0) {
    Write-Host "[FRONTEND] ✅ Type check passed" -ForegroundColor Green
} else {
    Write-Host "[FRONTEND] ❌ Type errors found" -ForegroundColor Red
    $exitCode = 1
}

Write-Host ""
Write-Host "=========================================="
if ($exitCode -eq 0) {
    Write-Host "✅ All checks passed!" -ForegroundColor Green
} else {
    Write-Host "❌ Some checks failed. See above for details." -ForegroundColor Red
}
Write-Host "=========================================="

Set-Location $ROOT_DIR
exit $exitCode
