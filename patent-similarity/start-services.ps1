# PatentAI Services Startup Script
# Starts both backend and frontend services

Write-Host "=====================================" -ForegroundColor Blue
Write-Host "  PatentAI Services Startup" -ForegroundColor Blue
Write-Host "=====================================" -ForegroundColor Blue

# Stop existing processes
Write-Host "`n[1] Stopping existing services..." -ForegroundColor Yellow
taskkill /F /IM python.exe 2>$null
taskkill /F /IM node.exe 2>$null
Start-Sleep -Seconds 2
Write-Host "    ✓ Services stopped" -ForegroundColor Green

# Start Backend
Write-Host "`n[2] Starting Backend Server..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
Start-Process python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning" -WorkingDirectory $backendPath -WindowStyle Hidden
Write-Host "    ✓ Backend starting on http://localhost:8000" -ForegroundColor Green

# Wait for backend
Start-Sleep -Seconds 3

# Test backend
Write-Host "`n[3] Testing Backend Connection..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    $data = $response.Content | ConvertFrom-Json
    Write-Host "    ✓ Backend OK (v$($data.version))" -ForegroundColor Green
} catch {
    Write-Host "    ✗ Backend connection failed" -ForegroundColor Red
}

# Start Frontend
Write-Host "`n[4] Starting Frontend Dev Server..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot ".." "patent-similarity-ui-v2"
Start-Process npm -ArgumentList "run", "dev" -WorkingDirectory $frontendPath -WindowStyle Hidden
Write-Host "    ✓ Frontend starting on http://localhost:3001" -ForegroundColor Green

# Wait for frontend
Start-Sleep -Seconds 5

Write-Host "`n=====================================" -ForegroundColor Blue
Write-Host "  All Services Started!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Blue
Write-Host "`n  Backend API:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Frontend:     http://localhost:3001" -ForegroundColor Cyan
Write-Host "  API Docs:     http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop services" -ForegroundColor Gray

# Keep script running
while ($true) {
    Start-Sleep -Seconds 1
}
