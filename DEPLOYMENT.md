# Production Deployment Guide

This guide covers deploying the Image Moderation API to a production environment with proper security, monitoring, and scalability.

## 🚀 Pre-Deployment Checklist

### **System Requirements**

- **RAM**: Minimum 4GB (8GB+ recommended)
- **CPU**: 2+ cores (4+ cores recommended)
- **Storage**: 20GB+ available space
- **OS**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+

### **Network Requirements**

- **Ports**: 80 (HTTP), 443 (HTTPS), 7000 (API), 3000 (Frontend)
- **Firewall**: Configure according to security requirements
- **SSL/TLS**: Valid SSL certificates for HTTPS

---

## 🔧 Server Setup

### **1. Install Dependencies**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install monitoring tools
sudo apt install htop iotop netstat-nat -y
```

### **2. Create Application User**

```bash
# Create dedicated user for the application
sudo useradd -m -s /bin/bash imgmod
sudo usermod -aG docker imgmod

# Switch to application user
sudo su - imgmod
```

### **3. Setup Directory Structure**

```bash
# Create application directory
mkdir -p /home/imgmod/image-moderation
cd /home/imgmod/image-moderation

# Create required directories
mkdir -p logs backups uploads temp
chmod 755 logs backups
chmod 700 uploads temp
```

---

## 📦 Application Deployment

### **1. Clone Repository**

```bash
# Clone the application
git clone <your-repository-url> .

# Or copy files if using manual deployment
# rsync -av /local/path/ /home/imgmod/image-moderation/
```

### **2. Configure Environment**

```bash
# Copy and configure environment file
cp .env.example .env

# Edit production configuration
nano .env
```

**Production .env Example:**

```bash
# Database
MONGODB_URI=mongodb://localhost:27017/image_moderation
MONGODB_DATABASE=image_moderation

# API Configuration
API_HOST=0.0.0.0
API_PORT=7000
DEBUG=false
ENVIRONMENT=production

# Security
ADMIN_TOKEN=<generate-secure-token>
SECRET_KEY=<generate-secret-key>
JWT_SECRET=<generate-jwt-secret>

# SSL/TLS (if using)
SSL_CERT_PATH=/etc/ssl/certs/imgmod.crt
SSL_KEY_PATH=/etc/ssl/private/imgmod.key

# Monitoring
LOG_LEVEL=INFO
ENABLE_METRICS=true
HEALTH_CHECK_INTERVAL=60

# Resource Limits
MAX_UPLOAD_SIZE=10485760  # 10MB
MAX_CONCURRENT_REQUESTS=50
REQUEST_TIMEOUT=30
```

### **3. Generate Secure Tokens**

```bash
# Generate secure tokens
python3 -c "import secrets; print('ADMIN_TOKEN=' + secrets.token_urlsafe(32))" >> .env
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))" >> .env
```

### **4. Configure Docker Compose for Production**

```bash
# Create production docker-compose file
cp docker-compose.yml docker-compose.prod.yml
```

Edit `docker-compose.prod.yml`:

```yaml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "7000:7000"
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    restart: unless-stopped
    depends_on:
      - mongodb
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: "1.0"
        reservations:
          memory: 1G
          cpus: "0.5"

  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - ./mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro
      - ./backups:/backups
    restart: unless-stopped
    command: mongod --auth
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "0.5"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - REACT_APP_API_URL=http://localhost:7000
    restart: unless-stopped
    depends_on:
      - api
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  mongodb_data:
    driver: local
```

---

## 🛡️ Security Configuration

### **1. Setup SSL/TLS Certificates**

```bash
# Using Let's Encrypt (recommended)
sudo apt install certbot nginx -y

# Generate certificates
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /etc/ssl/certs/imgmod.crt
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /etc/ssl/private/imgmod.key
sudo chown imgmod:imgmod /etc/ssl/certs/imgmod.crt /etc/ssl/private/imgmod.key
```

### **2. Configure Nginx Reverse Proxy**

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/image-moderation
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/ssl/certs/imgmod.crt;
    ssl_certificate_key /etc/ssl/private/imgmod.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # API proxy
    location /api/ {
        proxy_pass http://localhost:7000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Upload limits
        client_max_body_size 10M;
        proxy_read_timeout 30s;
        proxy_connect_timeout 10s;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/image-moderation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **3. Configure Firewall**

```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 7000  # Block direct API access
sudo ufw deny 3000  # Block direct frontend access
sudo ufw deny 27017 # Block direct MongoDB access
```

---

## 🚀 Deployment Process

### **1. Build and Start Services**

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
```

### **2. Initialize Database**

```bash
# Wait for MongoDB to start
sleep 30

# Create initial admin user and tokens
docker-compose -f docker-compose.prod.yml exec api python -c "
from app.auth import create_admin_token
print('Admin token:', create_admin_token())
"
```

### **3. Verify Deployment**

```bash
# Run health checks
python scripts/health-check.py

# Test API endpoints
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" https://yourdomain.com/api/health

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 📊 Monitoring & Maintenance

### **1. Setup Log Rotation**

```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/image-moderation
```

```
/home/imgmod/image-moderation/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 imgmod imgmod
    postrotate
        docker-compose -f /home/imgmod/image-moderation/docker-compose.prod.yml restart api
    endscript
}
```

### **2. Setup Automated Backups**

```bash
# Create backup cron job
crontab -e
```

```cron
# Daily database backup at 2 AM
0 2 * * * cd /home/imgmod/image-moderation && python scripts/backup.py create

# Weekly backup cleanup
0 3 * * 0 cd /home/imgmod/image-moderation && python scripts/backup.py cleanup

# Daily health check
*/15 * * * * cd /home/imgmod/image-moderation && python scripts/health-check.py --json > /tmp/health-check.json
```

### **3. Setup Monitoring Alerts**

```bash
# Install monitoring tools
sudo apt install prometheus-node-exporter -y

# Create monitoring script
nano scripts/monitor.sh
```

```bash
#!/bin/bash
# Simple monitoring script

HEALTH_URL="https://yourdomain.com/api/health"
ADMIN_TOKEN="YOUR_ADMIN_TOKEN"

# Check API health
if ! curl -s -H "Authorization: Bearer $ADMIN_TOKEN" $HEALTH_URL | grep -q "healthy"; then
    echo "API health check failed" | mail -s "Image Moderation API Alert" admin@yourdomain.com
fi

# Check disk space
DISK_USAGE=$(df /home/imgmod/image-moderation | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage is ${DISK_USAGE}%" | mail -s "Disk Space Alert" admin@yourdomain.com
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ $MEMORY_USAGE -gt 85 ]; then
    echo "Memory usage is ${MEMORY_USAGE}%" | mail -s "Memory Usage Alert" admin@yourdomain.com
fi
```

---

## 🔄 Updates & Maintenance

### **1. Application Updates**

```bash
# Create update script
nano scripts/update.sh
```

```bash
#!/bin/bash
set -e

echo "🔄 Starting application update..."

# Backup database
python scripts/backup.py create

# Pull latest code
git pull origin main

# Rebuild and restart services
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
sleep 30
python scripts/health-check.py

echo "✅ Update completed successfully!"
```

### **2. Security Updates**

```bash
# Regular security updates
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Clean up old images
docker system prune -f
```

---

## 🆘 Troubleshooting

### **Common Issues**

1. **High Memory Usage**

   ```bash
   # Check container stats
   docker stats

   # Increase memory limits in docker-compose.yml
   # Restart services
   ```

2. **Slow AI Processing**

   ```bash
   # Monitor performance
   python scripts/performance-monitor.py

   # Consider scaling or optimizing models
   ```

3. **Database Connection Issues**

   ```bash
   # Check MongoDB logs
   docker-compose -f docker-compose.prod.yml logs mongodb

   # Verify network connectivity
   docker-compose -f docker-compose.prod.yml exec api ping mongodb
   ```

4. **SSL Certificate Renewal**
   ```bash
   # Renew Let's Encrypt certificates
   sudo certbot renew
   sudo systemctl reload nginx
   ```

### **Emergency Procedures**

1. **Service Restart**

   ```bash
   docker-compose -f docker-compose.prod.yml restart
   ```

2. **Rollback**

   ```bash
   # Restore from backup
   python scripts/backup.py restore backups/db_backup_YYYYMMDD_HHMMSS.archive

   # Revert to previous version
   git checkout <previous-commit>
   docker-compose -f docker-compose.prod.yml build
   docker-compose -f docker-compose.prod.yml up -d
   ```

---

## 📈 Performance Optimization

### **1. Resource Scaling**

- **Horizontal Scaling**: Use Docker Swarm or Kubernetes
- **Vertical Scaling**: Increase CPU/memory in docker-compose.yml
- **Database Scaling**: Consider MongoDB replica sets

### **2. Caching Strategy**

- **Redis**: Add Redis for API response caching
- **CDN**: Use CloudFlare or AWS CloudFront
- **Image Optimization**: Implement image compression

### **3. Load Balancing**

```nginx
upstream api_backend {
    server localhost:7000;
    server localhost:7001;  # Additional instances
    server localhost:7002;
}
```

---

## ✅ Production Checklist

- [ ] SSL certificates configured
- [ ] Firewall rules applied
- [ ] Database authentication enabled
- [ ] Admin tokens generated and secured
- [ ] Backups configured and tested
- [ ] Monitoring and alerting setup
- [ ] Log rotation configured
- [ ] Health checks working
- [ ] Performance baselines established
- [ ] Emergency procedures documented
- [ ] Security configuration reviewed
- [ ] Load testing completed

---

**🎉 Your Image Moderation API is now production-ready!**

For support or questions, refer to the main README.md or contact your system administrator.
