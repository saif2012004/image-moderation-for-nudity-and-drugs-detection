#!/bin/bash

# ===========================================
# Image Moderation API - Production Deployment Script
# ===========================================

set -e  # Exit on any error

# Configuration
APP_NAME="image-moderation-api"
DOCKER_COMPOSE_FILE="docker-compose.yml"
BACKUP_DIR="./backups"
LOG_FILE="./deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

# Pre-deployment checks
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
    fi
    
    # Check if required files exist
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        error "docker-compose.yml not found"
    fi
    
    if [ ! -f "Dockerfile" ]; then
        error "Dockerfile not found"
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        warning ".env file not found, copying from .env.example"
        if [ -f ".env.example" ]; then
            cp .env.example .env
        else
            error ".env.example file not found"
        fi
    fi
    
    log "Prerequisites check completed ✓"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p "./logs"
    mkdir -p "./uploads"
    mkdir -p "./data"
    
    log "Directories created ✓"
}

# Backup existing data
backup_data() {
    log "Creating backup of existing data..."
    
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
    
    if docker-compose ps | grep -q "Up"; then
        info "Creating database backup..."
        docker-compose exec -T mongodb mongodump --db image_moderation --archive > "$BACKUP_DIR/db_backup_$TIMESTAMP.archive" || warning "Database backup failed"
    fi
    
    # Backup configuration files
    tar -czf "$BACKUP_FILE" \
        --exclude="./backups" \
        --exclude="./logs" \
        --exclude="./uploads" \
        --exclude=".git" \
        --exclude="node_modules" \
        --exclude="__pycache__" \
        . || warning "File backup failed"
    
    log "Backup created: $BACKUP_FILE ✓"
}

# Build and deploy
deploy() {
    log "Starting deployment..."
    
    # Stop existing containers gracefully
    info "Stopping existing containers..."
    docker-compose down --timeout 30
    
    # Remove old images to free space
    info "Cleaning up old Docker images..."
    docker image prune -f || warning "Image cleanup failed"
    
    # Pull latest base images
    info "Pulling latest base images..."
    docker-compose pull mongodb || warning "Failed to pull MongoDB image"
    
    # Build new images
    info "Building application images..."
    docker-compose build --no-cache --pull
    
    # Start services
    info "Starting services..."
    docker-compose up -d
    
    log "Deployment completed ✓"
}

# Health checks
health_check() {
    log "Performing health checks..."
    
    # Wait for services to start
    info "Waiting for services to start..."
    sleep 30
    
    # Check MongoDB
    info "Checking MongoDB health..."
    if docker-compose exec -T mongodb mongosh --eval "db.runCommand('ping')" &> /dev/null; then
        log "MongoDB is healthy ✓"
    else
        error "MongoDB health check failed"
    fi
    
    # Check API
    info "Checking API health..."
    local retries=0
    local max_retries=10
    
    while [ $retries -lt $max_retries ]; do
        if curl -f http://localhost:7000/health &> /dev/null; then
            log "API is healthy ✓"
            break
        else
            retries=$((retries + 1))
            warning "API health check failed (attempt $retries/$max_retries)"
            sleep 10
        fi
    done
    
    if [ $retries -eq $max_retries ]; then
        error "API failed to become healthy after $max_retries attempts"
    fi
    
    # Check Frontend
    info "Checking Frontend health..."
    if curl -f http://localhost:3000 &> /dev/null; then
        log "Frontend is healthy ✓"
    else
        warning "Frontend health check failed"
    fi
    
    log "Health checks completed ✓"
}

# Post-deployment tasks
post_deploy() {
    log "Running post-deployment tasks..."
    
    # Show container status
    info "Container status:"
    docker-compose ps
    
    # Show logs
    info "Recent logs:"
    docker-compose logs --tail=20
    
    # Display access URLs
    echo ""
    log "Deployment successful! 🎉"
    echo ""
    echo -e "${GREEN}Access URLs:${NC}"
    echo -e "  ${BLUE}API:${NC}      http://localhost:7000"
    echo -e "  ${BLUE}Frontend:${NC} http://localhost:3000"
    echo -e "  ${BLUE}API Docs:${NC} http://localhost:7000/docs"
    echo ""
    echo -e "${GREEN}Admin Token:${NC}"
    echo -e "  ${BLUE}Bearer BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA${NC}"
    echo ""
    
    log "Post-deployment tasks completed ✓"
}

# Rollback function
rollback() {
    error_exit() {
        error "Rollback failed! Manual intervention required."
    }
    
    trap error_exit ERR
    
    warning "Rolling back to previous version..."
    
    # Stop current containers
    docker-compose down --timeout 30
    
    # Find latest backup
    LATEST_BACKUP=$(find "$BACKUP_DIR" -name "backup_*.tar.gz" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
    
    if [ -n "$LATEST_BACKUP" ]; then
        info "Restoring from backup: $LATEST_BACKUP"
        tar -xzf "$LATEST_BACKUP" --exclude=".env"
        
        # Restore database if backup exists
        DB_BACKUP=$(find "$BACKUP_DIR" -name "db_backup_*.archive" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)
        if [ -n "$DB_BACKUP" ]; then
            docker-compose up -d mongodb
            sleep 20
            docker-compose exec -T mongodb mongorestore --db image_moderation --archive < "$DB_BACKUP"
        fi
        
        # Start services
        docker-compose up -d
        
        log "Rollback completed ✓"
    else
        error "No backup found for rollback"
    fi
}

# Print usage
usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy    - Full deployment (default)"
    echo "  check     - Run prerequisite checks only"
    echo "  backup    - Create backup only"
    echo "  health    - Run health checks only"
    echo "  rollback  - Rollback to previous version"
    echo "  logs      - Show application logs"
    echo "  stop      - Stop all services"
    echo "  start     - Start all services"
    echo "  restart   - Restart all services"
    echo "  status    - Show service status"
}

# Main deployment flow
main() {
    case "${1:-deploy}" in
        "deploy")
            log "Starting full deployment process..."
            check_prerequisites
            create_directories
            backup_data
            deploy
            health_check
            post_deploy
            ;;
        "check")
            check_prerequisites
            ;;
        "backup")
            backup_data
            ;;
        "health")
            health_check
            ;;
        "rollback")
            rollback
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "stop")
            log "Stopping all services..."
            docker-compose down
            log "Services stopped ✓"
            ;;
        "start")
            log "Starting all services..."
            docker-compose up -d
            log "Services started ✓"
            ;;
        "restart")
            log "Restarting all services..."
            docker-compose restart
            log "Services restarted ✓"
            ;;
        "status")
            docker-compose ps
            ;;
        *)
            usage
            exit 1
            ;;
    esac
}

# Error handling
trap 'error "Deployment failed at line $LINENO"' ERR

# Run main function
main "$@" 