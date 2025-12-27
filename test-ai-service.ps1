# Test AI Comment Service
# This script tests the AI comment service endpoints

Write-Host "Testing AI Comment Service..." -ForegroundColor Green

# Wait for service to be ready
Write-Host "`nWaiting for AI service to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Test health endpoint
Write-Host "`nTesting /health endpoint..." -ForegroundColor Cyan
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get
    Write-Host "Health check successful!" -ForegroundColor Green
    Write-Host ($healthResponse | ConvertTo-Json) -ForegroundColor White
} catch {
    Write-Host "Health check failed: $_" -ForegroundColor Red
}

# Test generate comment endpoint
Write-Host "`nTesting /generate-comment endpoint..." -ForegroundColor Cyan
try {
    $body = @{
        title = "My First Post"
        text = "This is an amazing post about software engineering"
    } | ConvertTo-Json

    $commentResponse = Invoke-RestMethod -Uri "http://localhost:8001/generate-comment" `
        -Method Post `
        -Body $body `
        -ContentType "application/json"
    
    Write-Host "AI Comment generated successfully!" -ForegroundColor Green
    Write-Host ($commentResponse | ConvertTo-Json) -ForegroundColor White
} catch {
    Write-Host "Comment generation failed: $_" -ForegroundColor Red
}

Write-Host "`nTest complete!" -ForegroundColor Green
