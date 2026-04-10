# Docker Deployment Guide - V1 & V2

## Overview

The WSTG Vulnerable Web Application is fully containerized with two versions:

- **V1**: Original basic vulnerable app (runs on port 5000)
- **V2**: Enhanced realistic app with hidden vulnerabilities (runs on port 5001)

Both are ready for Docker and Docker Compose deployment.

## Prerequisites

- Docker >= 20.10
- Docker Compose >= 1.29
- Git (for cloning)

---

## Quick Start - Docker Compose (Recommended)

### V1 - Original Lab App
```bash
git clone <repo-url>
cd WSTG-VulnerableApp

docker-compose up
# Access: http://localhost:5000
```

### V2 - Realistic Enhanced App
```bash
git clone <repo-url>
cd WSTG-VulnerableApp

docker-compose -f docker-compose-v2.yml up
# Access: https://localhost:5001
# (Browser will warn about self-signed certificate - this is expected)
```

---

## Docker Compose Configuration

### V1 - docker-compose.yml
```yaml
version: '3.8'

services:
  wstg-vulnerable-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: wstg-vulnerable-app-v1
    ports:
      - "5000:5000"
    environment:
      FLASK_ENV: development
      FLASK_DEBUG: 1
    volumes:
      - ./templates:/app/templates
      - ./static:/app/static
      - ./data:/app/data
    restart: unless-stopped
```

### V2 - docker-compose-v2.yml
```yaml
version: '3.8'

services:
  securenotes-v2:
    build:
      context: .
      dockerfile: Dockerfile-v2
    container_name: securenotes-v2
    ports:
      - "5001:5000"
    environment:
      FLASK_ENV: development
      FLASK_DEBUG: 1
    volumes:
      - ./uploads:/app/uploads
      - ./notes.db:/app/notes.db
    restart: unless-stopped
```

---

## Docker Build & Run

### Build V1 Image
```bash
docker build -t wstg-vulnerable-app:v1.0 .
```

### Build V2 Image
```bash
docker build -t wstg-vulnerable-app:v2.0 -f Dockerfile-v2 .
```

### Run V1 Container
```bash
docker run -d \
  --name wstg-app-v1 \
  -p 5000:5000 \
  -e FLASK_ENV=development \
  -e FLASK_DEBUG=1 \
  -v $(pwd)/templates:/app/templates \
  -v $(pwd)/static:/app/static \
  wstg-vulnerable-app:v1.0
```

### Run V2 Container
```bash
docker run -d \
  --name wstg-app-v2 \
  -p 5001:5000 \
  -e FLASK_ENV=development \
  -e FLASK_DEBUG=1 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/notes.db:/app/notes.db \
  wstg-vulnerable-app:v2.0
```

---

## Container Management

### View Logs
```bash
# V1
docker logs -f wstg-app-v1

# V2
docker logs -f wstg-app-v2

# Docker Compose
docker-compose logs -f
docker-compose -f docker-compose-v2.yml logs -f
```

### Stop Containers
```bash
# Using Docker
docker stop wstg-app-v1 wstg-app-v2

# Using Docker Compose
docker-compose down
docker-compose -f docker-compose-v2.yml down
```

### Remove Containers
```bash
docker rm wstg-app-v1 wstg-app-v2
```

### Check Running Containers
```bash
docker ps
docker ps -a  # Show all (including stopped)
```

---

## Dockerfile Details

### V1 - Dockerfile
- Base: Python 3.11-slim
- Runs: `python app.py`
- Port: 5000 (HTTP)
- No SSL

### V2 - Dockerfile-v2
- Base: Python 3.11-slim
- Runs: Python with SSL context
- Port: 5000 (HTTPS internally, exposed as 5001)
- Uses self-signed certificates (cert.pem, key.pem)
- Pre-populates SQLite database with test users

---

## Health Checks

### V1 Health Check
```bash
curl http://localhost:5000/
# Should return HTML home page

curl http://localhost:5000/api/debug
# Returns debug information (VULNERABLE endpoint)
```

### V2 Health Check
```bash
curl -k https://localhost:5001/
# Should return HTML login page
# -k ignores certificate warnings

curl -k https://localhost:5001/api/debug
# Returns debug information (VULNERABLE endpoint)
```

---

## Running Both Versions

### Simultaneously with Docker Compose
```bash
# Terminal 1: V1
docker-compose up

# Terminal 2: V2
docker-compose -f docker-compose-v2.yml up
```

### Access Both
- V1: http://localhost:5000
- V2: https://localhost:5001

### Monitor Both
```bash
# New terminal
docker ps
docker logs -f wstg-app-v1
docker logs -f wstg-app-v2
```

---

## Port Management

### Change V1 Port (e.g., to 8080)
Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"
```

Then:
```bash
docker-compose up
# Access: http://localhost:8080
```

### Change V2 Port (e.g., to 8443)
Edit `docker-compose-v2.yml`:
```yaml
ports:
  - "8443:5000"
```

Then:
```bash
docker-compose -f docker-compose-v2.yml up
# Access: https://localhost:8443
```

---

## Network Configuration

### Create Custom Network
```bash
docker network create wstg-network
```

### Run Containers on Network
```bash
docker run -d \
  --name wstg-app-v1 \
  --network wstg-network \
  -p 5000:5000 \
  wstg-vulnerable-app:v1.0

docker run -d \
  --name wstg-app-v2 \
  --network wstg-network \
  -p 5001:5000 \
  wstg-vulnerable-app:v2.0
```

---

## Volume Management

### V1 Volumes
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, images
- `data/` - Application data

### V2 Volumes
- `uploads/` - User uploaded files
- `notes.db` - SQLite database

### Inspect Volumes
```bash
docker volume ls
docker volume inspect <volume-name>
```

---

## Environment Variables

### V1
```
FLASK_ENV=development  # Development mode
FLASK_DEBUG=1          # Debug mode enabled
```

### V2
```
FLASK_ENV=development  # Development mode
FLASK_DEBUG=1          # Debug mode enabled
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :5000
lsof -i :5001

# Kill process
kill -9 <PID>

# Or use different port in docker-compose.yml
```

### Container Won't Start
```bash
# Check logs
docker logs <container_name>
docker-compose logs

# Check Dockerfile syntax
docker build --no-cache .
```

### Certificate Warning on V2
- Expected for self-signed certificates
- Click "Advanced" or "Proceed" in browser
- This is intentional for testing SSL/TLS vulnerabilities

### Database Issues in V2
```bash
# Reset V2 database
docker volume rm <volume_name>
docker-compose -f docker-compose-v2.yml up
```

### Out of Memory
```bash
# Limit container memory
docker run -m 512m -d ...

# Or in docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M
```

---

## Docker Compose Commands Reference

```bash
# Start services
docker-compose up              # Foreground
docker-compose up -d           # Background

# Stop services
docker-compose down            # Stop and remove
docker-compose stop            # Just stop

# View logs
docker-compose logs -f         # Follow logs
docker-compose logs app-name   # Specific service

# Rebuild images
docker-compose build
docker-compose build --no-cache

# Execute command in container
docker-compose exec service-name bash

# View running services
docker-compose ps
```

---

## Production Considerations

⚠️ **These applications contain intentional vulnerabilities and should NEVER be deployed to production.**

For testing/development only:
- Use in isolated environments
- Don't expose to public networks
- Use self-signed certificates only for testing
- Enable debug mode only in development
- Regularly update Docker images

---

## Security Notes for Docker

### Image Security
```bash
# Scan image for vulnerabilities
docker scan wstg-vulnerable-app:v1.0

# Use minimal base images
FROM python:3.11-slim
```

### Container Security
```bash
# Don't run as root
USER appuser

# Use read-only filesystem (where possible)
--read-only

# Drop unnecessary capabilities
--cap-drop=ALL
```

### Network Security
```bash
# Use custom network instead of default bridge
docker network create app-network

# Expose only necessary ports
-p 5000:5000
```

---

## Docker Compose Best Practices

✅ Use version pinning for images
✅ Define resource limits
✅ Use named volumes for persistence
✅ Document environment variables
✅ Use docker-compose.override.yml for local changes
✅ Keep docker-compose.yml in version control

---

## Next Steps

1. Deploy V1: `docker-compose up`
2. Deploy V2: `docker-compose -f docker-compose-v2.yml up`
3. Run WSTG Scanner: `./wstg-automation.sh https://localhost:5000`
4. Test vulnerabilities using WSTG methodology
5. Compare V1 vs V2 detection

---

**Version**: 2.0.0  
**Last Updated**: 2024  
**Documentation for**: WSTG Vulnerable App V1 & V2
