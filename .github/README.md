# 🚀 GitHub Actions Workflows

This directory contains comprehensive CI/CD and automation workflows for the **Image Moderation System** with **Nudity and Drugs Detection**.

## 📋 Available Workflows

### 1. 🚀 **Continuous Integration** (`ci.yml`)

**Triggers:** Push to `main`/`develop`, Pull Requests  
**Purpose:** Comprehensive testing and quality assurance

#### 🎯 **What it does:**

- **🐍 Backend Testing**: Python tests with MongoDB
- **⚛️ Frontend Testing**: React/Node.js testing and building
- **🛡️ Security Scanning**: Bandit and Safety checks
- **🐳 Docker Testing**: Build and test containers
- **📊 Code Quality**: Complexity analysis and metrics
- **✅ Integration Summary**: Overall CI status

#### 📊 **Key Features:**

- Parallel job execution for speed
- MongoDB service container for testing
- Code coverage reporting (Codecov integration)
- Linting and formatting checks (Black, Flake8, ESLint)
- Docker build validation

---

### 2. 🐳 **Docker Build & Publish** (`docker-publish.yml`)

**Triggers:** Push to `main`, Tags (`v*`), Pull Requests  
**Purpose:** Build, test, and publish Docker images

#### 🎯 **What it does:**

- **🏗️ Build Testing**: Test Docker builds work correctly
- **📦 GitHub Registry**: Publish to `ghcr.io`
- **🐳 Docker Hub**: Optional publishing to Docker Hub
- **🔍 Security Scanning**: Trivy vulnerability scanning
- **📊 Image Information**: Display published image details

#### 🔧 **Configuration Required:**

```bash
# For Docker Hub publishing (optional)
DOCKERHUB_USERNAME=your-username
DOCKERHUB_TOKEN=your-token
```

---

### 3. 🚀 **Deploy to Environments** (`deploy.yml`)

**Triggers:** Push to `main`/`develop`, Releases  
**Purpose:** Automated deployment to staging/production

#### 🎯 **What it does:**

- **🧪 Staging Deployment**: Auto-deploy `develop` branch
- **🌟 Production Deployment**: Deploy `main` branch
- **🏷️ Release Deployment**: Deploy specific release versions
- **🔄 Rollback Capability**: Emergency rollback on failure
- **📊 Health Checks**: Post-deployment validation

#### 🔧 **Environment Setup:**

Create GitHub Environments:

- `staging`: For development testing
- `production`: For live deployment

---

### 4. 🚀 **Performance Testing** (`performance-test.yml`)

**Triggers:** Push to `main`/`develop`, PRs, Daily at 2 AM UTC  
**Purpose:** Load testing and performance validation

#### 🎯 **What it does:**

- **🚀 Load Testing**: Locust-based concurrent user simulation
- **🎯 AI Performance**: Test nudity/drugs detection speed
- **📊 Performance Analysis**: Response time and reliability metrics
- **📈 Automated Validation**: Fail builds if performance degrades

#### 📊 **Performance Targets:**

- ⏱️ **Average Response Time**: < 5000ms
- 🎯 **Maximum Response Time**: < 10000ms
- ✅ **Success Rate**: > 95%
- 👥 **Concurrent Users**: 10 users tested

---

### 5. 🔒 **Security Scanning** (`security.yml`)

**Triggers:** Push to `main`/`develop`, PRs, Daily at 3 AM UTC  
**Purpose:** Comprehensive security analysis

#### 🎯 **What it does:**

- **🐍 Python Security**: Bandit static analysis, Safety dependency checks
- **🔍 Vulnerability Scanning**: Multiple security tools
- **📋 Security Reports**: Detailed vulnerability reports
- **🚨 Security Alerts**: Fail builds on high-severity issues

#### 🛡️ **Security Tools Used:**

- **Bandit**: Python code security analysis
- **Safety**: Python dependency vulnerability checking
- **GitHub Security**: Automated security advisories

---

## 🔧 Setup Instructions

### 1. **Repository Setup**

```bash
# Clone your repository
git clone <your-repo-url>
cd <your-repo>

# Ensure you have the workflows
ls -la .github/workflows/
```

### 2. **GitHub Secrets Configuration**

Go to **Settings > Secrets and Variables > Actions** and add:

#### 🔐 **Required Secrets:**

```bash
# For Docker Hub (optional)
DOCKERHUB_USERNAME=your-dockerhub-username
DOCKERHUB_TOKEN=your-dockerhub-access-token

# For notifications (optional)
SLACK_WEBHOOK_URL=your-slack-webhook
DISCORD_WEBHOOK_URL=your-discord-webhook
```

### 3. **Environment Protection Rules**

#### 🧪 **Staging Environment:**

- **Deployment Branch**: `develop`
- **Required Reviewers**: 0 (auto-deploy)
- **Wait Timer**: 0 minutes

#### 🌟 **Production Environment:**

- **Deployment Branch**: `main`
- **Required Reviewers**: 1+ (manual approval)
- **Wait Timer**: 5 minutes (safety delay)

### 4. **Branch Protection Rules**

#### 📋 **For `main` branch:**

- ✅ Require pull request reviews
- ✅ Require status checks to pass before merging
- ✅ Require CI workflow to pass
- ✅ Require up-to-date branches before merging

#### 📋 **For `develop` branch:**

- ✅ Require status checks to pass before merging
- ✅ Require CI workflow to pass

---

## 🎯 Workflow Triggers Summary

| Workflow           | Push `main` | Push `develop` | Pull Request | Schedule   | Release |
| ------------------ | ----------- | -------------- | ------------ | ---------- | ------- |
| **CI**             | ✅          | ✅             | ✅           | ❌         | ❌      |
| **Docker Publish** | ✅          | ❌             | ✅           | ❌         | ✅      |
| **Deploy**         | ✅          | ✅             | ❌           | ❌         | ✅      |
| **Performance**    | ✅          | ✅             | ✅           | ✅ (Daily) | ❌      |
| **Security**       | ✅          | ✅             | ✅           | ✅ (Daily) | ❌      |

---

## 📊 Monitoring and Alerts

### **GitHub Actions Status**

- ✅ **All workflows passing**: System is healthy
- ⚠️ **Performance degraded**: Check performance test results
- 🚨 **Security issues**: Review security scan reports
- ❌ **Build failing**: Check CI workflow logs

### **Performance Monitoring**

Monitor these key metrics in workflow runs:

- 📈 **Response Times**: Track API performance trends
- 🎯 **Success Rates**: Monitor reliability metrics
- 👥 **Concurrent Users**: Validate system under load
- 🔍 **AI Detection Speed**: Monitor nudity/drugs detection performance

### **Security Monitoring**

Regular security checks ensure:

- 🛡️ **No high-severity vulnerabilities**
- 🔐 **Dependencies are up-to-date**
- 🔍 **No secrets in code**
- 📊 **Security best practices followed**

---

## 🚀 Quick Start

### **First-time Setup:**

1. **Fork/Clone** this repository
2. **Configure secrets** in GitHub repository settings
3. **Set up environments** (staging, production)
4. **Configure branch protection** rules
5. **Push to `develop`** to trigger first workflow run

### **Daily Development:**

1. **Create feature branch** from `develop`
2. **Make changes** to your code
3. **Push changes** - CI workflow runs automatically
4. **Create Pull Request** - Full testing suite runs
5. **Merge to `develop`** - Staging deployment happens
6. **Merge to `main`** - Production deployment (with approval)

### **Release Process:**

1. **Create release** from `main` branch
2. **Tag version** (e.g., `v1.0.0`)
3. **Publish release** - Docker images published with version tags
4. **Production deployment** happens automatically

---

## 🆘 Troubleshooting

### **Common Issues:**

#### 🚨 **CI Workflow Failing**

```bash
# Check logs in GitHub Actions tab
# Common fixes:
- Update Python dependencies
- Fix linting errors
- Update Docker base images
```

#### 🐳 **Docker Build Issues**

```bash
# Local testing:
docker build -t test-api .
docker build -t test-frontend ./frontend

# Check Dockerfile syntax and dependencies
```

#### 🔒 **Security Scan Failures**

```bash
# Run locally:
pip install bandit safety
bandit -r app/
safety check

# Fix identified vulnerabilities
```

#### ⚡ **Performance Test Failures**

```bash
# Check if API is responding slowly
# Common causes:
- Database connection issues
- AI model loading problems
- Resource constraints
```

---

## 📈 Continuous Improvement

### **Workflow Optimization:**

- 🔄 **Regular Updates**: Keep action versions updated
- 📊 **Performance Tuning**: Optimize build times
- 🛡️ **Security Enhancement**: Add new security tools
- 📋 **Monitoring**: Add better failure notifications

### **System Scaling:**

- 🚀 **Multi-environment**: Add staging/dev environments
- 🌍 **Multi-region**: Deploy to multiple regions
- 📊 **Advanced Monitoring**: Add APM tools
- 🔄 **Auto-scaling**: Configure horizontal scaling

---

## 📞 Support

For workflow issues:

1. **Check GitHub Actions logs** for detailed error messages
2. **Review this documentation** for configuration steps
3. **Check repository issues** for known problems
4. **Create new issue** with workflow logs attached

**Happy Deploying! 🚀**
