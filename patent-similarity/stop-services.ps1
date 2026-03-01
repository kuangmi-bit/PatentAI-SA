# PatentAI Services Stop Script
Write-Host "Stopping PatentAI Services..." -ForegroundColor Yellow
taskkill /F /IM python.exe 2>$null
taskkill /F /IM node.exe 2>$null
Write-Host "✓ All services stopped" -ForegroundColor Green
