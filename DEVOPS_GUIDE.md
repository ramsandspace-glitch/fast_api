# DevOps Team Guide - Deploying FastAPI Server

This guide explains how to share and deploy this Docker-based FastAPI application with the DevOps team.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Sharing via Git Repository](#sharing-via-git-repository)
3. [Sharing Docker Images](#sharing-docker-images)
4. [For DevOps Team](#for-devops-team)
5. [Deployment Options](#deployment-options)
6. [Environment Configuration](#environment-configuration)
7. [CI/CD Integration](#cicd-integration)

## Prerequisites

### For You (Developer)

- Git installed and configured
- Docker installed and running
- Docker Hub account (free) OR private registry access
- Basic understanding of Git commands

### For DevOps Team

- Docker and Docker Compose installed
- Kubernetes cluster (if using K8s)
- Access to deployment environments
- Registry access credentials

## Sharing via Git Repository

### Step 1: Prepare Your Repository

Make sure your project is ready for sharing:

**Check your files:**
```
Training/                  # Project root folder
├── server.py              # Main application
├── db_adapter.py          # Database adapter
├── requirements.txt       # Dependencies
├── Dockerfile             # Docker build file
├── docker-compose.yml     # Docker Compose config
├── .dockerignore          # Docker ignore file
├── .gitignore             # Git ignore file
├── README.md              # User documentation
├── DEVOPS_GUIDE.md        # This file
├── SHARING_CHECKLIST.md   # Sharing checklist
└── VE/                    # Virtual environment folder (git ignored)
    ├── Scripts/           # Windows activation scripts
    ├── Lib/               # Python packages
    └── logs/              # Log files
```

### Step 2: Create .gitignore File

Create a `.gitignore` file to exclude unnecessary files:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Virtual Environment
venv/
env/
ENV/
VE/

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment variables (keep template)
.env
.env.local
.env.*.local

# Database files
*.db
*.sqlite
*.sqlite3

# Docker (keep compose file)
.docker/
```

### Step 3: Initialize Git Repository

```bash
# Navigate to project folder
cd Training

# Initialize Git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: FastAPI server with multi-database support"

# Create a new repository on GitHub/GitLab/Bitbucket
# Then add remote and push:

# GitHub example:
git remote add origin https://github.com/yourusername/your-repo-name.git
git branch -M main
git push -u origin main
```

### Step 4: Share Repository Access

**Option A: Public Repository**
- Anyone can access it
- Good for open-source projects

**Option B: Private Repository**
- Add DevOps team members as collaborators:
  - GitHub: Settings → Collaborators → Add people
  - GitLab: Project → Members → Add member
  - Bitbucket: Repository settings → Access management

**Option C: Organization Repository**
- Create organization in GitHub/GitLab
- Add DevOps team to organization
- Give appropriate permissions

## Sharing Docker Images

There are two ways to share Docker images:

### Method 1: Docker Hub (Recommended for Beginners)

**Step 1: Create Docker Hub Account**
- Go to https://hub.docker.com
- Sign up for free account
- Create a repository (e.g., `yourusername/fastapi-server`)

**Step 2: Build and Tag Image**

```bash
# Build the image
docker build -t yourusername/fastapi-server:latest .

# Tag it (if needed)
docker tag fastapi-server yourusername/fastapi-server:latest
```

**Step 3: Push to Docker Hub**

```bash
# Login to Docker Hub
docker login

# Enter your Docker Hub username and password

# Push the image
docker push yourusername/fastapi-server:latest
```

**Step 4: Share with DevOps Team**

Provide them with:
```
Image Name: yourusername/fastapi-server:latest
Pull Command: docker pull yourusername/fastapi-server:latest
```

### Method 2: Private Docker Registry

**Option A: Docker Hub Private Repository**
- Same as above, but make repository private
- Add team members with read access

**Option B: Self-Hosted Registry**
```bash
# DevOps team will set this up
# You'll push to their registry instead:

docker tag fastapi-server registry.company.com/fastapi-server:latest
docker push registry.company.com/fastapi-server:latest
```

**Option C: Cloud Registries**
- AWS ECR (Elastic Container Registry)
- Google Container Registry (GCR)
- Azure Container Registry (ACR)

Ask DevOps team which registry they use.

## For DevOps Team

### Quick Start

**Clone the repository:**
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

**Or pull Docker image:**
```bash
docker pull yourusername/fastapi-server:latest
```

### Build Locally

```bash
# Build from source
docker build -t fastapi-server:latest .

# Or use docker-compose
docker-compose build
```

### Run Locally for Testing

```bash
# Start everything (app + database)
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

### Application Details

**Port:** 8000 (configurable)

**Health Check Endpoint:** `GET /health/db`

**Environment Variables Required:**
- `DB_TYPE` - Database type (mongodb, postgresql, mysql, sqlite)
- Database connection variables (see Configuration section)

**Container Details:**
- Base Image: `python:3.11-slim`
- Working Directory: `/app`
- Logs: Written to `/app/logs/server.log` (mounted volume)

## Deployment Options

### Option 1: Docker Compose (Simple Deployment)

**For:** Development, small production environments

**Deployment Steps:**

1. **Copy files to server:**
   ```bash
   scp -r Training/ user@server:/opt/fastapi-server/
   ```

2. **On server, start services:**
   ```bash
   cd /opt/fastapi-server
   docker-compose up -d
   ```

3. **Check status:**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

**docker-compose.yml** is ready to use with:
- FastAPI application service
- MongoDB database service
- Volume mounts for persistence
- Network configuration

### Option 2: Docker Swarm

**For:** Medium-scale deployments, multiple servers

**Initialize Swarm:**
```bash
docker swarm init
```

**Deploy Stack:**
```bash
docker stack deploy -c docker-compose.yml fastapi-stack
```

**Update Stack:**
```bash
docker service update --image yourusername/fastapi-server:new-version fastapi-stack_api
```

### Option 3: Kubernetes

**For:** Large-scale, production deployments

**Create Kubernetes Manifests:**

Create `k8s/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-server
  template:
    metadata:
      labels:
        app: fastapi-server
    spec:
      containers:
      - name: fastapi
        image: yourusername/fastapi-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: DB_TYPE
          value: "mongodb"
        - name: MONGODB_URI
          value: "mongodb://mongodb-service:27017"
        - name: MONGODB_DB
          value: "dummydatabase"
        livenessProbe:
          httpGet:
            path: /health/db
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/db
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi-server
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deploy:**
```bash
kubectl apply -f k8s/deployment.yaml
```

### Option 4: Cloud Platforms

**AWS ECS:**
- Use ECS Task Definition with Docker image
- Configure environment variables
- Set up RDS or DocumentDB for database

**Google Cloud Run:**
```bash
gcloud run deploy fastapi-server \
  --image gcr.io/project-id/fastapi-server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Azure Container Instances:**
```bash
az container create \
  --resource-group myResourceGroup \
  --name fastapi-server \
  --image yourusername/fastapi-server:latest \
  --dns-name-label fastapi-server \
  --ports 8000
```

## Environment Configuration

### Required Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_TYPE` | Yes | `mongodb` | Database type: mongodb, postgresql, mysql, sqlite |
| `MONGODB_URI` | If MongoDB | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB` | If MongoDB | `dummydatabase` | MongoDB database name |
| `DATABASE_URL` | If SQL | - | SQL database connection URL |

### Environment Files for Different Stages

**Development (.env.dev):**
```
DB_TYPE=mongodb
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=dummydatabase
```

**Staging (.env.staging):**
```
DB_TYPE=postgresql
DATABASE_URL=postgresql://user:pass@staging-db:5432/fastapi_db
```

**Production (.env.prod):**
```
DB_TYPE=postgresql
DATABASE_URL=postgresql://user:pass@prod-db:5432/fastapi_db
```

### Using Environment Files in Docker

```bash
# Docker Compose
docker-compose --env-file .env.prod up -d

# Docker Run
docker run --env-file .env.prod fastapi-server
```

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/docker.yml`:

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build Docker image
      run: docker build -t yourusername/fastapi-server:${{ github.sha }} .
    
    - name: Push Docker image
      run: |
        docker push yourusername/fastapi-server:${{ github.sha }}
        docker tag yourusername/fastapi-server:${{ github.sha }} yourusername/fastapi-server:latest
        docker push yourusername/fastapi-server:latest
```

### GitLab CI Example

Create `.gitlab-ci.yml`:

```yaml
stages:
  - build
  - deploy

build:
  stage: build
  script:
    - docker build -t registry.gitlab.com/yourgroup/fastapi-server:$CI_COMMIT_SHA .
    - docker push registry.gitlab.com/yourgroup/fastapi-server:$CI_COMMIT_SHA

deploy:
  stage: deploy
  script:
    - docker pull registry.gitlab.com/yourgroup/fastapi-server:$CI_COMMIT_SHA
    - docker-compose up -d
  only:
    - main
```

## Information to Provide DevOps Team

### 1. Repository Information

```
Repository URL: https://github.com/yourusername/your-repo-name
Branch: main
Docker Image: yourusername/fastapi-server:latest
```

### 2. Application Specifications

```
- Port: 8000 (HTTP)
- Health Check: GET /health/db
- Logs Location: /app/logs/server.log
- Base Image: python:3.11-slim
- Resource Requirements:
  - Memory: Minimum 256MB, Recommended 512MB
  - CPU: Minimum 0.25 cores, Recommended 0.5 cores
```

### 3. Database Requirements

```
Supported Databases:
- MongoDB (via Motor)
- PostgreSQL (via SQLAlchemy + asyncpg)
- MySQL (via SQLAlchemy + aiomysql)
- SQLite (via SQLAlchemy + aiosqlite)

Database must be accessible from container network.
```

### 4. Networking

```
Container Port: 8000
Host Port: 8000 (configurable)
Protocol: HTTP
Internal Communication:
  - API to Database: Use service name in docker-compose
  - API to external DB: Use host.docker.internal (Docker Desktop)
```

### 5. Volumes Needed

```
- Logs: ./logs:/app/logs (for persistence)
- SQLite data: ./data:/app/data (if using SQLite)
```

## Security Considerations

### For DevOps Team

1. **Secrets Management:**
   - Don't hardcode passwords in docker-compose.yml
   - Use secrets management (Docker secrets, Kubernetes secrets, etc.)
   - Example:
     ```yaml
     environment:
       - DATABASE_URL=${DB_CONNECTION_STRING}
     ```

2. **Image Security:**
   - Scan images for vulnerabilities
   - Use specific tags, not `latest` in production
   - Keep base images updated

3. **Network Security:**
   - Use internal networks in Docker
   - Expose only necessary ports
   - Use reverse proxy (nginx, traefik) for HTTPS

4. **Resource Limits:**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '1'
         memory: 512M
       reservations:
         cpus: '0.25'
         memory: 256M
   ```

## Monitoring and Logging

### Health Checks

The application includes health check endpoint:
- **Endpoint:** `GET /health/db`
- **Response:** 200 if healthy, 503 if database unavailable

### Logging

- Logs written to: `/app/logs/server.log`
- Log format: `datetime|loglevel|module|file|function|line|logmessage`
- Mount logs volume to persist logs

### Recommended Monitoring

- Application logs via mounted volume
- Container health via Docker/K8s health checks
- Database connection monitoring via `/health/db` endpoint
- Resource usage monitoring (CPU, memory)

## Troubleshooting for DevOps

### Container Won't Start

```bash
# Check logs
docker logs fastapi-server

# Check if port is in use
netstat -tuln | grep 8000

# Check Docker status
docker ps -a
```

### Database Connection Issues

```bash
# Test database connectivity from container
docker exec fastapi-server ping mongodb

# Check environment variables
docker exec fastapi-server env | grep DB_

# Verify network
docker network inspect <network-name>
```

### Image Pull Issues

```bash
# Login to registry
docker login

# Pull specific tag
docker pull yourusername/fastapi-server:tag-name

# Verify image
docker images | grep fastapi-server
```

## Update Process

### For Developer

1. **Make code changes**
2. **Commit and push to Git:**
   ```bash
   git add .
   git commit -m "Update: description"
   git push origin main
   ```

3. **Build and push new image:**
   ```bash
   docker build -t yourusername/fastapi-server:v1.0.1 .
   docker push yourusername/fastapi-server:v1.0.1
   ```

### For DevOps Team

1. **Pull new image:**
   ```bash
   docker pull yourusername/fastapi-server:v1.0.1
   ```

2. **Update deployment:**
   ```bash
   # Docker Compose
   docker-compose pull
   docker-compose up -d
   
   # Kubernetes
   kubectl set image deployment/fastapi-server fastapi=yourusername/fastapi-server:v1.0.1
   ```

3. **Verify deployment:**
   ```bash
   curl http://localhost:8000/health/db
   ```

## Support and Contact

**If DevOps team needs help:**
- Check README.md for application details
- Check logs in `/app/logs/server.log`
- Review this DEVOPS_GUIDE.md
- Contact developer for code-related issues

## Quick Reference Commands

```bash
# Build image
docker build -t fastapi-server:latest .

# Run container
docker run -p 8000:8000 -e DB_TYPE=mongodb fastapi-server:latest

# Docker Compose
docker-compose up -d
docker-compose down
docker-compose logs -f

# Check health
curl http://localhost:8000/health/db

# View logs
docker logs fastapi-server
docker-compose logs fastapi-server
```

---

**Last Updated:** [Current Date]
**Maintained By:** [Your Name/Team]
**Repository:** [Your Repository URL]

