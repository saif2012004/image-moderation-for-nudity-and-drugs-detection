# ===========================================
# Image Moderation API - Windows PowerShell Deployment Script
# ===========================================

param(
    [Parameter(Position=0)]
    [ValidateSet("deploy", "check", "health", "logs", "stop", "start", "restart", "status")]
    [string]$Command = "deploy"
)

# Configuration
$DOCKER_COMPOSE_FILE = "docker-compose.yml"
$LOG_FILE = "./deploy.log"

# Logging functions
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] $Message"
    Write-Host $logMessage -ForegroundColor Green
    Add-Content -Path $LOG_FILE -Value $logMessage
}

function Write-Error-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] ERROR: $Message"
    Write-Host $logMessage -ForegroundColor Red
    Add-Content -Path $LOG_FILE -Value $logMessage
    exit 1
}

function Write-Info-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] INFO: $Message"
    Write-Host $logMessage -ForegroundColor Blue
    Add-Content -Path $LOG_FILE -Value $logMessage
}

# Pre-deployment checks
function Test-Prerequisites {
    Write-Log "Checking prerequisites..."
    
    # Check if Docker is installed and running
    try {
        $dockerVersion = docker --version 2>$null
        if ($dockerVersion) {
            Write-Info-Log "Docker found: $dockerVersion"
        } else {
            Write-Error-Log "Docker is not installed or not in PATH"
        }
    }
    catch {
        Write-Error-Log "Docker is not installed or not in PATH"
    }
    
    try {
        docker info 2>$null | Out-Null
        Write-Info-Log "Docker daemon is running"
    }
    catch {
        Write-Error-Log "Docker daemon is not running"
    }
    
    # Check if Docker Compose is available
    try {
        $composeVersion = docker-compose --version 2>$null
        if ($composeVersion) {
            Write-Info-Log "Docker Compose found: $composeVersion"
        } else {
            Write-Error-Log "Docker Compose is not installed or not in PATH"
        }
    }
    catch {
        Write-Error-Log "Docker Compose is not installed or not in PATH"
    }
    
    # Check if required files exist
    if (-not (Test-Path $DOCKER_COMPOSE_FILE)) {
        Write-Error-Log "docker-compose.yml not found"
    }
    
    if (-not (Test-Path "Dockerfile")) {
        Write-Error-Log "Dockerfile not found"
    }
    
    Write-Log "Prerequisites check completed ✓"
}

# Build and deploy
function Start-Deployment {
    Write-Log "Starting deployment..."
    
    # Stop existing containers gracefully
    Write-Info-Log "Stopping existing containers..."
    docker-compose down --timeout 30
    
    # Build new images
    Write-Info-Log "Building application images..."
    docker-compose build --no-cache
    
    # Start services
    Write-Info-Log "Starting services..."
    docker-compose up -d
    
    Write-Log "Deployment completed ✓"
}

# Health checks
function Test-Health {
    Write-Log "Performing health checks..."
    
    # Wait for services to start
    Write-Info-Log "Waiting for services to start..."
    Start-Sleep -Seconds 30
    
    # Check API
    Write-Info-Log "Checking API health..."
    $retries = 0
    $maxRetries = 10
    $apiHealthy = $false
    
    while ($retries -lt $maxRetries -and -not $apiHealthy) {
        try {
            $response = Invoke-RestMethod -Uri "http://localhost:7000/health" -TimeoutSec 5
            if ($response.status -eq "healthy") {
                Write-Log "API is healthy ✓"
                $apiHealthy = $true
            }
        }
        catch {
            $retries++
            Write-Info-Log "API health check failed (attempt $retries/$maxRetries)"
            Start-Sleep -Seconds 10
        }
    }
    
    if (-not $apiHealthy) {
        Write-Error-Log "API failed to become healthy after $maxRetries attempts"
    }
    
    Write-Log "Health checks completed ✓"
}

# Post-deployment tasks
function Complete-Deployment {
    Write-Log "Running post-deployment tasks..."
    
    # Show container status
    Write-Info-Log "Container status:"
    docker-compose ps
    
    # Display access URLs
    Write-Host ""
    Write-Log "Deployment successful! 🎉"
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Green
    Write-Host "  API:      http://localhost:7000" -ForegroundColor Blue
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Blue
    Write-Host "  API Docs: http://localhost:7000/docs" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Admin Token:" -ForegroundColor Green
    Write-Host "  Bearer BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA" -ForegroundColor Blue
    Write-Host ""
    
    Write-Log "Post-deployment tasks completed ✓"
}

# Print usage
function Show-Usage {
    Write-Host "Usage: .\deploy.ps1 [COMMAND]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Green
    Write-Host "  deploy    - Full deployment (default)" -ForegroundColor Blue
    Write-Host "  check     - Run prerequisite checks only" -ForegroundColor Blue
    Write-Host "  health    - Run health checks only" -ForegroundColor Blue
    Write-Host "  logs      - Show application logs" -ForegroundColor Blue
    Write-Host "  stop      - Stop all services" -ForegroundColor Blue
    Write-Host "  start     - Start all services" -ForegroundColor Blue
    Write-Host "  restart   - Restart all services" -ForegroundColor Blue
    Write-Host "  status    - Show service status" -ForegroundColor Blue
}

# Main execution logic
try {
    switch ($Command) {
        "deploy" {
            Write-Log "Starting full deployment process..."
            Test-Prerequisites
            Start-Deployment
            Test-Health
            Complete-Deployment
        }
        "check" {
            Test-Prerequisites
        }
        "health" {
            Test-Health
        }
        "logs" {
            docker-compose logs -f
        }
        "stop" {
            Write-Log "Stopping all services..."
            docker-compose down
            Write-Log "Services stopped ✓"
        }
        "start" {
            Write-Log "Starting all services..."
            docker-compose up -d
            Write-Log "Services started ✓"
        }
        "restart" {
            Write-Log "Restarting all services..."
            docker-compose restart
            Write-Log "Services restarted ✓"
        }
        "status" {
            docker-compose ps
        }
        default {
            Show-Usage
            exit 1
        }
    }
}
catch {
    Write-Error-Log "Deployment failed: $($_.Exception.Message)"
} 