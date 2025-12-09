# Quick Start Script for Business Opportunities Finder
# Run this script to set up and start the application

Write-Host "🚀 Business Opportunities Finder - Setup Script" -ForegroundColor Cyan
Write-Host "=" * 60

# Check if Docker is running
Write-Host "`n📦 Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker is running" -ForegroundColor Green

# Check if .env exists
Write-Host "`n🔑 Checking environment configuration..." -ForegroundColor Yellow
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Please edit .env and add your API keys:" -ForegroundColor Red
    Write-Host "   - GEMINI_API_KEY (REQUIRED)" -ForegroundColor Red
    Write-Host "   - Reddit/ProductHunt (Optional)" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Press Enter after updating .env, or type 'exit' to quit"
    if ($continue -eq 'exit') {
        exit 0
    }
}
else {
    Write-Host "✅ .env file exists" -ForegroundColor Green
}

# Build and start containers
Write-Host "`n🏗️  Building and starting containers..." -ForegroundColor Yellow
docker-compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start containers" -ForegroundColor Red
    exit 1
}

# Wait for backend to be ready
Write-Host "`n⏳ Waiting for backend to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check health
Write-Host "`n🏥 Checking application health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Write-Host "✅ Application is healthy" -ForegroundColor Green
}
catch {
    Write-Host "⚠️  Health check failed, but containers may still be starting..." -ForegroundColor Yellow
}

# Show status
Write-Host "`n📊 Container Status:" -ForegroundColor Yellow
docker-compose ps

Write-Host "`n" + "=" * 60
Write-Host "✨ Setup Complete!" -ForegroundColor Green
Write-Host "=" * 60

Write-Host "`n📍 Access the application:"
Write-Host "   Dashboard: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan

Write-Host "`n📝 Useful commands:"
Write-Host "   View logs:          docker-compose logs -f" -ForegroundColor Gray
Write-Host "   Stop:               docker-compose down" -ForegroundColor Gray
Write-Host "   Restart:            docker-compose restart" -ForegroundColor Gray
Write-Host "   Run discovery now:  docker-compose exec backend python -m app.scheduler.daily_job" -ForegroundColor Gray

Write-Host "`n💡 Next steps:"
Write-Host "   1. Open http://localhost:8000 in your browser"
Write-Host "   2. Run a manual discovery to populate data"
Write-Host "   3. The scheduler will run automatically at 7:00 AM daily"
Write-Host ""
Write-Host "Happy opportunity hunting! 🎯" -ForegroundColor Green
