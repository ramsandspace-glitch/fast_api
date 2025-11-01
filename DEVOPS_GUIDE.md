# DevOps Team Guide - Deploying FastAPI Server

## Prerequisites

- Docker and Docker Compose installed
- Kubernetes cluster (if using K8s)
- Access to deployment environments
- Registry access credentials

### Quick Start

**pull Docker image:**

```bash
Image Name: rammurthy018/fast_api:latest
Pull Command: docker pull rammurthy018/fast_api:latest
```

### Build Locally

```bash
# Build from source
docker build -t fast_api:latest .

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
