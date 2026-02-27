# ===========================================
# GoalMind - Development Server (Windows PowerShell)
# Starts backend + frontend in parallel
# ===========================================
# Run with: .\scripts\dev.ps1
# Options:  .\scripts\dev.ps1 -Backend  (backend only)
#           .\scripts\dev.ps1 -Frontend (frontend only)

param(
    [switch]$Backend,
    [switch]$Frontend
)

$ROOT_DIR = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$jobs = @()

Write-Host ""
Write-Host "⚽ GoalMind - Development Server" -ForegroundColor Cyan
Write-Host "=========================================="
Write-Host ""

try {
    # Start Backend
    if (-not $Frontend) {
        Write-Host "[BACKEND] Starting on http://localhost:8000 ..." -ForegroundColor Green
        $backendJob = Start-Job -ScriptBlock {
            param($dir)
            Set-Location $dir
            uv run python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
        } -ArgumentList "$ROOT_DIR\futbolia-backend"
        $jobs += $backendJob
        Write-Host "[BACKEND] Job ID: $($backendJob.Id)" -ForegroundColor Green
    }

    # Start Frontend
    if (-not $Backend) {
        Write-Host "[FRONTEND] Starting Expo dev server ..." -ForegroundColor Green
        $frontendJob = Start-Job -ScriptBlock {
            param($dir)
            Set-Location $dir
            bun start
        } -ArgumentList "$ROOT_DIR\futbolia-mobile"
        $jobs += $frontendJob
        Write-Host "[FRONTEND] Job ID: $($frontendJob.Id)" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "=========================================="
    Write-Host "✅ Development servers running!" -ForegroundColor Green
    Write-Host "  Backend:  http://localhost:8000"
    Write-Host "  API Docs: http://localhost:8000/docs"
    Write-Host "  Frontend: http://localhost:8081"
    Write-Host ""
    Write-Host "Press Ctrl+C to stop all servers"
    Write-Host "=========================================="

    # Stream output from jobs
    while ($true) {
        foreach ($job in $jobs) {
            $output = Receive-Job -Job $job -ErrorAction SilentlyContinue
            if ($output) { Write-Host $output }
        }
        Start-Sleep -Milliseconds 500
    }
}
finally {
    Write-Host ""
    Write-Host "[INFO] Shutting down..." -ForegroundColor Cyan
    foreach ($job in $jobs) {
        Stop-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] All processes stopped" -ForegroundColor Green
}
