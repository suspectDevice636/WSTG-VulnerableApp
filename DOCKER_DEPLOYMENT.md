# Docker Deployment Guide

## Overview

The WSTG Vulnerable Web Application has been fully containerized and is ready for deployment using Docker and Docker Compose.

## Prerequisites

- Docker >= 20.10
- Docker Compose >= 1.29
- Git (for cloning the repository)

## Quick Start with Docker Compose (Recommended)

### 1. Clone the Repository
```bash
git clone <repository-url> WSTG-VulnerableApp
cd WSTG-VulnerableApp
```

### 2. Start the Application
```bash
docker-compose up
```

The application will be available at: **http://localhost:5000**

### 3. Stop the Application
```bash
docker-compose down
```

## Docker Build & Run

### Build Docker Image
```bash
docker build -t wstg-vulnerable-app:latest .
```

### Run Docker Container
```bash
docker run -d \
  --name wstg-vulnerable-app \
  -p 5000:5000 \
  -v $(pwd)/templates:/app/templates \
  -v $(pwd)/static:/app/static \
  -e FLASK_ENV=development \
  -e FLASK_DEBUG=1 \
  wstg-vulnerable-app:latest
```

### Access the Application
```bash
# View container logs
docker logs -f wstg-vulnerable-app

# Check health
curl http://localhost:5000/health

# Visit in browser
open http://localhost:5000
```

### Stop Docker Container
```bash
docker stop wstg-vulnerable-app
docker rm wstg-vulnerable-app
```

## Docker Compose Services

### Configuration

**File:** `docker-compose.yml`

```yaml
services:
  wstg-vulnerable-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: wstg-vulnerable-app
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
      - PYTHONUNBUFFERED=1
    volumes:
      - ./app.py:/app/app.py
      - ./templates:/app/templates
      - ./static:/app/static
      - /tmp:/tmp
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 5s
```

### Volume Mounting

| Host Path | Container Path | Purpose |
|-----------|-----------------|---------|
| `./app.py` | `/app/app.py` | Flask application (hot reload) |
| `./templates` | `/app/templates` | HTML templates |
| `./static` | `/app/static` | CSS, JavaScript, static files |
| `/tmp` | `/tmp` | Database storage |

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `FLASK_ENV` | `development` | Development environment |
| `FLASK_DEBUG` | `1` | Enable debug mode |
| `PYTHONUNBUFFERED` | `1` | Unbuffered Python output |

## Health Checks

The container includes a health check that monitors the `/health` endpoint:

```bash
# Check container health
docker-compose ps
```

Expected output:
```
wstg-vulnerable-app   Up (healthy)
```

## Deployment Architecture

### Container Contents

```
docker://wstg-vulnerable-app
├── Python 3.9 (slim)
├── Flask 2.0.1
├── Werkzeug 2.0.1
├── /app/
│   ├── app.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── admin.html
│   │   └── backup.html
│   └── static/
│       └── css/
│           └── style.css
└── /tmp/ (database storage)
```

### Port Mapping

- **Host Port:** 5000
- **Container Port:** 5000
- **Protocol:** HTTP

## Persistent Data

The database is stored in `/tmp` which is a volume shared between host and container. The database is recreated on application startup, so it's not persistent across container restarts by default.

To make the database persistent, modify `docker-compose.yml`:

```yaml
volumes:
  - ./app.py:/app/app.py
  - ./templates:/app/templates
  - ./static:/app/static
  - ./data:/tmp  # Add this line to persist database
```

## Common Docker Commands

### View Logs
```bash
# Follow logs
docker-compose logs -f

# View specific container logs
docker logs -f wstg-vulnerable-app
```

### Access Container Shell
```bash
docker-compose exec wstg-vulnerable-app bash
```

### Rebuild Image
```bash
docker-compose build --no-cache
```

### View Container Info
```bash
docker-compose ps
docker-compose images
```

### Remove Everything
```bash
docker-compose down -v
```

## Production Deployment Considerations

⚠️ **WARNING:** This application is intentionally vulnerable and should ONLY be used for:
- Authorized security testing
- Educational purposes
- CI/CD pipeline testing

### For Production-like Environments

1. **Use a Reverse Proxy** (nginx, Apache)
   - Add rate limiting
   - Handle SSL/TLS
   - Implement security headers

2. **Update Environment Variables**
   ```bash
   FLASK_ENV=production
   FLASK_DEBUG=0
   ```

3. **Add Authentication** (if not testing authentication vulnerabilities)
   - Implement proper login
   - Use session management
   - Add rate limiting

4. **Secure Data Storage**
   - Use external database (PostgreSQL, MySQL)
   - Implement proper backup strategy
   - Use encrypted storage

5. **Monitoring & Logging**
   - Set up container monitoring
   - Implement centralized logging
   - Add metrics collection

## Testing in Docker

### Run Health Check
```bash
curl http://localhost:5000/health
```

### Test Endpoints
```bash
# SQL Injection endpoint
curl http://localhost:5000/api/user/1

# Login
curl -X POST http://localhost:5000/login \
  -d "username=admin&password=admin123"

# Admin panel
curl http://localhost:5000/admin

# Backup files
curl http://localhost:5000/backup
```

## Troubleshooting

### Container won't start
```bash
docker-compose logs
# Check for port conflicts: lsof -i :5000
```

### Templates not loading
```bash
# Verify volume mounts
docker inspect wstg-vulnerable-app

# Check file permissions
ls -la templates/ static/
```

### Database issues
```bash
# Check /tmp directory
docker-compose exec wstg-vulnerable-app ls -la /tmp/

# Reinitialize database
docker-compose restart
```

### Port already in use
```bash
# Change port in docker-compose.yml
# From: "5000:5000"
# To:   "8080:5000"
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Docker Build & Test
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: docker/setup-buildx-action@v1
      - uses: docker/build-push-action@v2
        with:
          context: .
          push: false
          tags: wstg-vulnerable-app:latest
```

### GitLab CI Example
```yaml
docker-build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t wstg-vulnerable-app:latest .
    - docker-compose up -d
    - docker-compose exec -T wstg-vulnerable-app curl http://localhost:5000/health
```

## Image Size Optimization

Current image size: ~150MB (Python 3.9 slim + Flask + deps)

To further optimize:
1. Use Python 3.9 alpine instead of slim (~100MB)
2. Remove dev dependencies
3. Use multi-stage build

## Security Notes

🔐 **This application is intentionally vulnerable:**
- SQL injection enabled
- Authentication bypasses included
- Debug mode enabled
- Sensitive files exposed

**DO NOT** deploy to production or internet-facing servers without:
- Isolated network (VPN, private subnet)
- Firewall rules
- Access controls
- Monitoring

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review `README.md` and `QUICK_START.md`
3. Check Docker installation: `docker --version`, `docker-compose --version`

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Python Docker Image](https://hub.docker.com/_/python)
