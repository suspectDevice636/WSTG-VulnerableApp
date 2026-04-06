# Complete Deployment Guide - WSTG Vulnerable App (Upgraded)

## 📦 What You Have

A fully upgraded, Docker-ready WSTG Vulnerable Web Application with:

✅ **Professional UI** - Modern templates and responsive design
✅ **Docker Ready** - Complete containerization with docker-compose
✅ **Git Committed** - All changes in version control
✅ **All Vulnerabilities Intact** - Perfect for security testing
✅ **Comprehensive Docs** - QUICK_START, UPGRADE_SUMMARY, DOCKER_DEPLOYMENT guides

## 🚀 Fastest Way to Deploy

### 1. Start Locally (30 seconds)
```bash
cd WSTG-VulnerableApp
docker-compose up
```

Open: http://localhost:5000

### 2. Start with Custom Port
```bash
# In docker-compose.yml, change:
# "5000:5000"  →  "8080:5000"

docker-compose up
```

Open: http://localhost:8080

### 3. Background Mode
```bash
docker-compose up -d
docker-compose logs -f  # View logs
docker-compose down     # Stop later
```

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Docker installed: `docker --version`
- [ ] Docker Compose installed: `docker-compose --version`
- [ ] Git installed: `git --version`
- [ ] Repository cloned or code directory ready
- [ ] Port 5000 available (or configure different port)

### Deployment Steps

#### Option A: Docker Compose (Recommended)
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd WSTG-VulnerableApp
   ```

2. Verify structure:
   ```bash
   ls -la  # Should see: app.py, Dockerfile, docker-compose.yml, templates/, static/
   ```

3. Start the application:
   ```bash
   docker-compose up
   ```

4. Verify it's running:
   ```bash
   curl http://localhost:5000/health
   # Expected response: {"status":"ok"}
   ```

5. Access the application:
   ```
   http://localhost:5000
   ```

6. Stop the application:
   ```bash
   docker-compose down
   ```

#### Option B: Manual Docker Build
1. Build the image:
   ```bash
   docker build -t wstg-vulnerable-app:v1.0 .
   ```

2. Run the container:
   ```bash
   docker run -d \
     --name wstg-app \
     -p 5000:5000 \
     -v $(pwd)/templates:/app/templates \
     -v $(pwd)/static:/app/static \
     -e FLASK_ENV=development \
     wstg-vulnerable-app:v1.0
   ```

3. View logs:
   ```bash
   docker logs -f wstg-app
   ```

4. Stop the container:
   ```bash
   docker stop wstg-app
   docker rm wstg-app
   ```

#### Option C: Deploy to Remote Server
1. Upload to server:
   ```bash
   scp -r . user@server:/path/to/app
   ```

2. On the server:
   ```bash
   cd /path/to/app
   docker-compose up -d
   ```

3. Verify:
   ```bash
   docker-compose ps
   docker-compose logs
   ```

## 🔍 Verification

### Health Check
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{"status":"ok"}
```

### Container Status
```bash
docker-compose ps
```

Expected output:
```
NAME                COMMAND             SERVICE             STATUS
wstg-vulnerable-app  "python app.py"    wstg-vulnerable-app  Up (healthy)
```

### Test Endpoints
```bash
# Home page
curl http://localhost:5000/

# API endpoint (SQL Injection)
curl http://localhost:5000/api/user/1

# Admin panel
curl http://localhost:5000/admin

# Login (requires POST)
curl -X POST http://localhost:5000/login \
  -d "username=admin&password=admin123"
```

## 📁 File Structure

```
WSTG-VulnerableApp/
├── app.py                    # Main Flask application (updated)
├── app_original.py          # Backup of original version
├── app_upgraded.py          # Source of upgrade
├── Dockerfile               # Docker image definition (UPDATED)
├── docker-compose.yml       # Docker Compose config (UPDATED)
├── requirements.txt         # Python dependencies (UPDATED)
│
├── templates/               # NEW - HTML templates
│   ├── base.html           # Base template
│   ├── index.html          # Home page
│   ├── login.html          # Login form
│   ├── dashboard.html      # User dashboard
│   ├── admin.html          # Admin panel
│   └── backup.html         # Backup files
│
├── static/                 # NEW - Static files
│   └── css/
│       └── style.css       # Professional CSS
│
├── data/                   # Data directory
├── public/                 # Public files
│
├── README.md              # Original documentation
├── QUICK_START.md         # NEW - Quick start guide
├── UPGRADE_SUMMARY.md     # NEW - Upgrade details
├── DOCKER_DEPLOYMENT.md   # NEW - Docker documentation
├── DEPLOYMENT_GUIDE.md    # NEW - This file
└── LICENSE                # MIT License
```

## 🔐 Important Security Notes

⚠️ **This application is INTENTIONALLY VULNERABLE**

**Only use for:**
- ✅ Authorized security testing
- ✅ Educational purposes
- ✅ CI/CD pipeline validation
- ✅ Penetration testing tool development

**Never:**
- ❌ Deploy to production
- ❌ Expose to the internet
- ❌ Use with sensitive data
- ❌ Connect to untrusted networks

### Running in Isolated Environment
```bash
# Use Docker network isolation
docker-compose up

# Only accessible from local machine on port 5000
# No external access unless port is explicitly exposed
```

## 🔧 Configuration

### Change Port
Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Host:Container (change 8080 to desired port)
```

Then restart:
```bash
docker-compose restart
```

### Environment Variables
Edit `docker-compose.yml` environment section:
```yaml
environment:
  - FLASK_ENV=production      # Change to production if needed
  - FLASK_DEBUG=0             # Disable debug mode for production
  - PYTHONUNBUFFERED=1        # Keep enabled for logging
```

### Database Persistence
Add to `docker-compose.yml` volumes:
```yaml
volumes:
  - ./data:/tmp              # Persist database between restarts
```

## 📊 Resource Usage

### Container Specs
- **Base Image:** Python 3.9-slim (~150MB)
- **RAM Usage:** ~100-150MB idle
- **CPU:** Minimal under normal load
- **Disk:** ~200MB total (image + container)

### Network
- **Port:** 5000 (HTTP)
- **Protocol:** HTTP (no HTTPS)
- **Health Check:** Every 10 seconds

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs wstg-vulnerable-app

# Look for:
# - Port already in use (change port in docker-compose.yml)
# - File permission issues (check volumes)
# - Python errors in app.py
```

### Port 5000 already in use
```bash
# Option 1: Change port in docker-compose.yml
# Option 2: Kill process using port
lsof -i :5000
kill -9 <PID>

# Option 3: Use different port
sudo lsof -i :5000
sudo kill -9 <PID>
```

### Templates not loading
```bash
# Verify template files exist
docker-compose exec wstg-vulnerable-app ls -la /app/templates

# Check file permissions
ls -la templates/

# Rebuild container
docker-compose build --no-cache
docker-compose up
```

### Health check failing
```bash
# Check manually
docker-compose exec wstg-vulnerable-app curl http://localhost:5000/health

# Check container logs
docker-compose logs --tail=50

# May need to increase start_period in docker-compose.yml
```

## 📈 Scaling & Advanced Deployment

### Multiple Instances (Load Balancing)
```yaml
# docker-compose.yml
services:
  wstg-vulnerable-app:
    deploy:
      replicas: 3
    ports:
      - "5000-5002:5000"
```

### Kubernetes Deployment
```bash
# Convert docker-compose to Kubernetes
kompose convert -f docker-compose.yml

# Deploy to Kubernetes
kubectl apply -f wstg-vulnerable-app-deployment.yaml
```

### Docker Registry Push
```bash
# Tag image
docker tag wstg-vulnerable-app:latest myregistry/wstg-app:v1.0

# Push to registry
docker push myregistry/wstg-app:v1.0

# Pull from registry
docker pull myregistry/wstg-app:v1.0
```

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `QUICK_START.md` | Get up and running quickly (5 min read) |
| `UPGRADE_SUMMARY.md` | Details about the UI upgrade |
| `DOCKER_DEPLOYMENT.md` | Docker-specific documentation |
| `DEPLOYMENT_GUIDE.md` | This comprehensive guide |
| `README.md` | Original project documentation |

## ✅ Post-Deployment Verification

### 1. Service Health
```bash
docker-compose ps  # Should show "healthy"
```

### 2. Application Functionality
```bash
# Test main page
curl http://localhost:5000/ | head -20

# Test API
curl http://localhost:5000/api/user/1

# Test admin panel
curl http://localhost:5000/admin
```

### 3. Container Logs
```bash
docker-compose logs --tail=100
```

### 4. Performance
```bash
docker stats wstg-vulnerable-app
```

## 🔄 Maintenance

### View Logs
```bash
# Current logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# Last N lines
docker-compose logs --tail=50

# Specific service
docker-compose logs wstg-vulnerable-app
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart wstg-vulnerable-app

# Stop and start (forces rebuild)
docker-compose down
docker-compose up
```

### Update Code
```bash
# Update app.py (hot reload)
nano app.py
# Changes reflected immediately due to volume mount

# Update requirements
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Clean Up
```bash
# Remove containers only
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove images too
docker-compose down -v --rmi all

# System-wide cleanup
docker system prune -a
```

## 📞 Support & Issues

### Common Issues

**Issue: "Cannot connect to localhost:5000"**
- Verify: `docker-compose ps` shows container is up
- Check port: `lsof -i :5000`
- Check firewall: May need to open port

**Issue: "Templates not found"**
- Verify: `docker-compose exec wstg-vulnerable-app ls /app/templates`
- Check: Volume mounts in docker-compose.yml
- Rebuild: `docker-compose build --no-cache`

**Issue: "Database not persisting"**
- Add volume: `- ./data:/tmp` to docker-compose.yml
- Restart: `docker-compose restart`

### Getting Help
1. Check logs: `docker-compose logs`
2. Review documentation: DOCKER_DEPLOYMENT.md
3. Verify installation: `docker --version`, `docker-compose --version`
4. Check network: `curl http://localhost:5000/health`

## 🎓 Next Steps

1. **Review Documentation**
   - Read QUICK_START.md for basics
   - Review UPGRADE_SUMMARY.md for changes
   - Check DOCKER_DEPLOYMENT.md for Docker details

2. **Test the Application**
   - Visit http://localhost:5000
   - Try different endpoints
   - Test vulnerabilities

3. **Customize (Optional)**
   - Modify port in docker-compose.yml
   - Add environment variables
   - Integrate into CI/CD pipeline

4. **Version Control**
   - Push changes to your repository
   - Track deployments in git
   - Maintain version history

## 📝 Version Information

- **Application Version:** 2.0 (UI Upgraded)
- **Docker Base Image:** Python 3.9-slim
- **Flask Version:** 2.0.1
- **Jinja2 Version:** 3.0.1
- **Docker Compose Version:** 3.8+
- **Upgrade Date:** April 6, 2026
- **Commit:** fb18793

---

**Your WSTG Vulnerable Application is ready for deployment!** 🚀

For questions, refer to the documentation files or check the git commit history for details about the upgrade.
