#!/usr/bin/env pwsh
# Quick start script for SQLite backend

Write-Host "Starting Test Tool Platform with SQLite..." -ForegroundColor Green

# Activate virtual environment
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    & .\venv\Scripts\Activate.ps1
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Copy SQLite config if .env doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from SQLite template..." -ForegroundColor Yellow
    Copy-Item ".env.sqlite" ".env"
}

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
alembic upgrade head

# Start server
Write-Host "`nStarting server at http://localhost:8000" -ForegroundColor Green
Write-Host "API docs at http://localhost:8000/api/docs" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop`n" -ForegroundColor Cyan
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
