# Test Runner Script for SWEG Project
# This script runs tests in the Docker environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SWEG Project - Test Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
$dockerRunning = docker info 2>$null
if (-not $?) {
    Write-Host "Error: Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Check if services are up
Write-Host "Checking Docker services..." -ForegroundColor Yellow
$beStatus = docker compose ps backend --format json 2>$null | ConvertFrom-Json
if (-not $beStatus -or $beStatus.State -ne "running") {
    Write-Host "Starting Docker services..." -ForegroundColor Yellow
    docker compose up -d
    Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
} else {
    Write-Host "Services are already running." -ForegroundColor Green
}

Write-Host ""
Write-Host "Running tests..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Run tests in Docker
docker compose exec backend python -m pytest domains/posts/tests/ -v --tb=short

$testResult = $LASTEXITCODE

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($testResult -eq 0) {
    Write-Host "All tests passed!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed. See output above." -ForegroundColor Red
}

Write-Host ""
Write-Host "To run specific tests:" -ForegroundColor Yellow
Write-Host "  docker compose exec backend python -m pytest domains/posts/tests/test_models.py -v" -ForegroundColor Gray
Write-Host ""
Write-Host "To run with coverage:" -ForegroundColor Yellow
Write-Host "  docker compose exec backend python -m pytest domains/posts/tests/ --cov=domains" -ForegroundColor Gray
Write-Host ""

exit $testResult
