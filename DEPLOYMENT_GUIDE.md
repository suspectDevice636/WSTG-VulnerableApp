# Complete Deployment Guide - WSTG Vulnerable App (V1 & V2)

## 📦 What You Have

A fully upgraded WSTG Vulnerable Web Application with two versions:

### V1 - Original Lab Application
✅ Basic vulnerable web app (shows vulnerabilities openly)
✅ Good for learning security concepts
✅ Runs on port 5000
✅ Docker ready

### V2 - Realistic Enhanced Application  
✅ Looks like a real note-taking web app (professional UI)
✅ Hidden vulnerabilities (not obvious)
✅ 16+ security flaws including JWT vulnerabilities
✅ Pre-created users for testing (IDOR, privilege escalation)
✅ HTTPS with self-signed certificates
✅ Runs on port 5001 (Docker) or 5000 (direct)
✅ Fully documented vulnerability guide

---

## 🚀 Quick Start - Choose Your Version

### V1 (Basic Lab)
```bash
cd WSTG-VulnerableApp
docker-compose up
# Access: http://localhost:5000
```

### V2 (Realistic)
```bash
cd WSTG-VulnerableApp
docker-compose -f docker-compose-v2.yml up
# Access: https://localhost:5001
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Docker installed: `docker --version`
- [ ] Docker Compose installed: `docker-compose --version`
- [ ] Git installed: `git --version`
- [ ] Repository cloned
- [ ] Port 5000 available (for V1) or 5001 (for V2)

---

## V1 Deployment

### Option A: Docker Compose (Recommended)
```bash
cd WSTG-VulnerableApp
docker-compose up
```
- Access: http://localhost:5000
- Runs in foreground with logs visible
- Press Ctrl+C to stop

### Option B: Background Mode
```bash
docker-compose up -d
docker-compose logs -f  # View logs
docker-compose down     # Stop later
```

### Option C: Manual Docker Build
```bash
docker build -t wstg-vulnerable-app:v1 .
docker run -d \
  --name wstg-app-v1 \
  -p 5000:5000 \
  -e FLASK_ENV=development \
  wstg-vulnerable-app:v1
```

### Option D: Local Python
```bash
pip install -r requirements.txt
python app.py
```
- Access: http://localhost:5000

---

## V2 Deployment

### Option A: Docker Compose (Recommended)
```bash
cd WSTG-VulnerableApp
docker-compose -f docker-compose-v2.yml up
```
- Access: https://localhost:5001
- Browser will warn about self-signed certificate (expected)
- Click "Advanced" → "Proceed"

### Option B: Background Mode
```bash
docker-compose -f docker-compose-v2.yml up -d
docker-compose -f docker-compose-v2.yml logs -f
docker-compose -f docker-compose-v2.yml down
```

### Option C: Manual Docker Build
```bash
docker build -t wstg-vulnerable-app:v2 -f Dockerfile-v2 .
docker run -d \
  --name wstg-app-v2 \
  -p 5001:5000 \
  -e FLASK_ENV=development \
  wstg-vulnerable-app:v2
```

### Option D: Local Python with SSL
```bash
pip install -r requirements.txt
./run-v2.sh
```
- Access: https://localhost:5000
- Self-signed certificate warning is expected

---

## 🔐 V2 Test Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | AdminPass123! | Admin (test privilege escalation) |
| user1 | password123 | Regular user |
| user2 | password456 | Regular user |
| user3 | password789 | Regular user |
| john | JohnPassword | Regular user |

---

## 📡 Running Both Versions Simultaneously

Run both V1 and V2 at the same time on different ports:

```bash
# Terminal 1: V1 on port 5000
docker-compose up

# Terminal 2: V2 on port 5001
docker-compose -f docker-compose-v2.yml up
```

Then access:
- V1: http://localhost:5000
- V2: https://localhost:5001

---

## 🧪 Verification

### V1 Health Check
```bash
curl http://localhost:5000/
# Should return HTML home page
```

### V2 Health Check
```bash
curl -k https://localhost:5001/
# Should return HTML home page
# -k ignores certificate warnings
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find what's using port 5000
lsof -i :5000

# Use different port
docker run -p 8080:5000 wstg-vulnerable-app
```

### Certificate Warning on V2
- Expected for self-signed certificates
- Click "Advanced" or "Proceed anyway"
- This is intentional for testing

### Container Won't Start
```bash
docker logs container_name
docker-compose logs
```

### Permission Denied
```bash
sudo docker-compose up
# Or add user to docker group:
sudo usermod -aG docker $USER
```

---

## 🔧 Custom Configuration

### Change V1 Port
Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Change 5000 to desired port
```

### Change V2 Port
Edit `docker-compose-v2.yml`:
```yaml
ports:
  - "8443:5000"  # Change 5001 to desired port
```

---

## 📚 Documentation

- **V1 Details**: See main README.md
- **V2 Details**: See README-V2.md
- **Docker Details**: See DOCKER_DEPLOYMENT.md
- **Quick Start**: See QUICK_START.md

---

## ✅ Security Notes

- ⚠️ V2 uses self-signed certificates (intentional for testing)
- ⚠️ Both versions have intentional vulnerabilities for testing
- ✅ Only run in isolated/local environments
- ✅ Never expose to public networks
- ✅ For authorized testing only

---

## 🚀 Next Steps After Deployment

1. **V1**: View vulnerabilities openly, understand the concepts
2. **V2**: Test hidden vulnerabilities, find security flaws
3. **Run WSTG Scanner**: `./wstg-automation.sh https://localhost:5000`
4. **Document Findings**: Compare V1 vs V2 vulnerability detection

---

**Version**: 2.0.0  
**Last Updated**: 2024
