# Simple PowerShell Deployment Script for Image Moderation API

param(
    [string]$Command = "check"
)

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor Green
}

function Write-Error-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] ERROR: $Message" -ForegroundColor Red
}

function Write-Info-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] INFO: $Message" -ForegroundColor Blue
}

function Test-Prerequisites {
    Write-Log "Checking prerequisites..."
    
    # Check Docker
    try {
        $dockerOutput = docker --version 2>$null
        if ($dockerOutput) {
            Write-Info-Log "Docker found: $dockerOutput"
        } else {
            Write-Error-Log "Docker is not installed"
            return $false
        }
    }
    catch {
        Write-Error-Log "Docker is not installed"
        return $false
    }
    
    # Check Docker Compose
    try {
        $composeOutput = docker-compose --version 2>$null
        if ($composeOutput) {
            Write-Info-Log "Docker Compose found: $composeOutput"
        } else {
            Write-Error-Log "Docker Compose is not installed"
            return $false
        }
    }
    catch {
        Write-Error-Log "Docker Compose is not installed"
        return $false
    }
    
    # Check required files
    if (-not (Test-Path "docker-compose.yml")) {
        Write-Error-Log "docker-compose.yml not found"
        return $false
    }
    
    if (-not (Test-Path "Dockerfile")) {
        Write-Error-Log "Dockerfile not found"
        return $false
    }
    
    Write-Log "Prerequisites check completed successfully ✓"
    return $true
}

function Start-Services {
    Write-Log "Starting services..."
    docker-compose up -d
    Write-Log "Services started ✓"
}

function Stop-Services {
    Write-Log "Stopping services..."
    docker-compose down
    Write-Log "Services stopped ✓"
}

function Show-Status {
    Write-Log "Container status:"
    docker-compose ps
}

function Show-Logs {
    Write-Log "Showing logs..."
    docker-compose logs
}

function Deploy-All {
    Write-Log "Starting full deployment..."
    
    if (Test-Prerequisites) {
        Write-Log "Building and starting services..."
        docker-compose down --timeout 30
        docker-compose build --no-cache
        docker-compose up -d
        
        Write-Log "Deployment completed! ✓"
        Write-Host ""
        Write-Host "Access URLs:" -ForegroundColor Green
        Write-Host "  API:      http://localhost:7000" -ForegroundColor Blue
        Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Blue
        Write-Host "  API Docs: http://localhost:7000/docs" -ForegroundColor Blue
        Write-Host ""
        Write-Host "Admin Token:" -ForegroundColor Green
        Write-Host "  Bearer BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA" -ForegroundColor Blue
    }
}

# Main execution
switch ($Command) {
    "check" { Test-Prerequisites }
    "deploy" { Deploy-All }
    "start" { Start-Services }
    "stop" { Stop-Services }
    "status" { Show-Status }
    "logs" { Show-Logs }
    default {
        Write-Host "Usage: .\deploy-simple.ps1 [check|deploy|start|stop|status|logs]" -ForegroundColor Yellow
    }
} 