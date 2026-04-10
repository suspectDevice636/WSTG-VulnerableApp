# WSTG Vulnerable App - Quick Start Guide

## 📦 Two Versions Available

This repository includes **two complete versions** of the WSTG Vulnerable Web Application:

### 🔬 V1 - Lab/Educational Version
- Basic vulnerable web app (shows vulnerabilities openly)
- Good for learning security concepts
- Uses HTTP (port 5000)
- Simpler to understand
- Perfect for beginners

### 🎯 V2 - Realistic Testing Version
- Looks like a real note-taking web app (professional UI)
- **Hidden vulnerabilities** (not obvious at first glance)
- 16+ security flaws (SQL injection, IDOR, JWT, CORS, CSP, etc.)
- Uses HTTPS with self-signed certificates (port 5001)
- Pre-created users for testing
- Great for penetration testing practice

**Choose based on your needs:**
- Learning security? → **V1**
- Realistic testing practice? → **V2**

---

## 🚀 Fastest Way to Start (30 seconds)

### V1 - Quick Start
```bash
cd WSTG-VulnerableApp
docker-compose up
```
Then open: **http://localhost:5000**

### V2 - Quick Start
```bash
cd WSTG-VulnerableApp
docker-compose -f docker-compose-v2.yml up
```
Then open: **https://localhost:5001**
(Browser will warn about certificate - click "Advanced" → "Proceed")

---

## 🔓 Test Credentials

### V1 - Default Users
```
Username: user1
Password: password
```

### V2 - Pre-Created Users
| Username | Password | Role |
|----------|----------|------|
| admin | AdminPass123! | Admin (test privilege escalation) |
| user1 | password123 | Regular user (test IDOR) |
| user2 | password456 | Regular user |
| user3 | password789 | Regular user |
| john | JohnPassword | Regular user |

---

## 📋 Installation Options

### Option A: Docker Compose (Easiest)
```bash
# V1
docker-compose up

# V2
docker-compose -f docker-compose-v2.yml up
```

### Option B: Docker Manual
```bash
# V1
docker build -t wstg-app:v1 .
docker run -p 5000:5000 wstg-app:v1

# V2
docker build -t wstg-app:v2 -f Dockerfile-v2 .
docker run -p 5001:5000 wstg-app:v2
```

### Option C: Local Python

#### V1
```bash
pip install -r requirements.txt
python app.py
# Open: http://localhost:5000
```

#### V2
```bash
pip install -r requirements.txt
./run-v2.sh
# Open: https://localhost:5000
```

---

## 🌐 Key Endpoints

### V1 Endpoints
| URL | What |
|-----|------|
| `/` | Home page with vulnerabilities |
| `/api/user/<id>` | SQL injection |
| `/api/profile/<id>` | IDOR vulnerability |
| `/search` | SQL injection |
| `/admin` | Admin panel (exposed) |

### V2 Endpoints
| URL | What |
|-----|------|
| `/login` | Session-based login |
| `/dashboard` | Note-taking dashboard |
| `/api/notes` | Get all notes (IDOR) |
| `/api/notes/<id>` | Get specific note (IDOR) |
| `/api/auth/token` | JWT token generation |
| `/api/v2/notes` | JWT-protected notes |
| `/api/users` | List all users (info disclosure) |
| `/api/debug` | Debug info (info disclosure) |
| `/upload` | File upload (insecure) |

---

## 🎯 Quick Testing Guide

### V1 - Test SQL Injection
```bash
# Visit:
http://localhost:5000/search?username=admin' OR '1'='1

# Or API:
curl "http://localhost:5000/api/user/1 OR 1=1"
```

### V1 - Test IDOR
```bash
# Visit:
http://localhost:5000/api/profile/1
http://localhost:5000/api/profile/2
http://localhost:5000/api/profile/3
```

### V2 - Test IDOR
```bash
# Login as user1, then access other users' notes:
curl -X GET "https://localhost:5001/api/notes?user_id=2" \
  -H "Cookie: session=..." -k
```

### V2 - Test JWT Weakness
```bash
# Get weak JWT token:
curl -X POST "https://localhost:5001/api/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"password123"}' -k

# Get non-expiring token:
curl -X POST "https://localhost:5001/api/auth/token?no_expiry=true" \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"password123"}' -k

# Use token:
curl -X GET "https://localhost:5001/api/v2/notes" \
  -H "Authorization: Bearer <token>" -k
```

### V2 - Test CORS
```bash
# V2 has wildcard CORS:
curl -X GET "https://localhost:5001/api/sensitive-data" \
  -H "Origin: https://attacker.com" -k
# Response will include: Access-Control-Allow-Origin: *
```

---

## 📁 File Structure

```
WSTG-VulnerableApp/
├── app.py                    ← V1 application
├── app-v2.py                 ← V2 application (note-taking app)
├── templates/
│   ├── base.html            ← V2 base template
│   ├── login.html           ← V2 login
│   ├── dashboard.html       ← V2 notes dashboard
│   ├── admin.html           ← V2 admin panel
│   └── upload.html          ← V2 file upload
├── static/
│   ├── css/style.css        ← V2 professional styling
│   └── js/main.js           ← V2 client-side code
├── Dockerfile               ← V1 container
├── Dockerfile-v2            ← V2 container
├── docker-compose.yml       ← V1 compose
├── docker-compose-v2.yml    ← V2 compose
├── cert.pem & key.pem       ← V2 SSL certificates
├── requirements.txt         ← Python dependencies
├── README.md                ← Main documentation
├── README-V2.md             ← V2 documentation
├── DEPLOYMENT_GUIDE.md      ← Deployment instructions
└── QUICK_START.md           ← This file
```

---

## 🔐 Security Features (Intentional Vulnerabilities)

### V1 Vulnerabilities
- SQL Injection
- IDOR (Insecure Direct Object References)
- Weak Authentication
- Missing Security Headers
- Information Disclosure
- XSS Vulnerabilities
- CORS Misconfiguration
- Insecure CSP

### V2 Vulnerabilities (16 Total)
- Hardcoded Credentials (in HTML comments)
- Base64 Encoded Secrets
- SQL Injection
- IDOR (Insecure Direct Object References)
- Privilege Escalation (admin promotion)
- Weak Password Validation
- Missing CSRF Tokens
- Information Disclosure Endpoints
- Insecure File Upload
- User Enumeration
- **JWT Vulnerabilities** (NEW!)
  - Weak secret key
  - Long expiration (7 days)
  - No token revocation
  - Debug endpoint
  - Token passed via query param
- CORS Misconfiguration
- Insecure CSP
- Self-Signed SSL Certificate
- Sensitive Data Exposure

---

## 🧪 Testing with WSTG Scanner

Run the automated scanner against your instance:

```bash
# Test V1
./wstg-automation.sh http://localhost:5000 -o ./v1-results

# Test V2
./wstg-automation.sh https://localhost:5001 -o ./v2-results -k
```

Then review the scan results in:
- `./v1-results/SCAN-SUMMARY.txt`
- `./v2-results/SCAN-SUMMARY.txt`

---

## 🚀 Run Both Versions Simultaneously

```bash
# Terminal 1: V1
docker-compose up

# Terminal 2: V2 (in same directory)
docker-compose -f docker-compose-v2.yml up
```

Then access:
- V1: http://localhost:5000
- V2: https://localhost:5001

---

## 🔧 Common Tasks

### Stop the Application
```bash
# Foreground (Ctrl+C)
# Or background:
docker-compose down
docker-compose -f docker-compose-v2.yml down
```

### View Logs
```bash
docker-compose logs -f
docker-compose -f docker-compose-v2.yml logs -f
```

### Change Port
Edit `docker-compose.yml` or `docker-compose-v2.yml`:
```yaml
ports:
  - "8080:5000"  # Change 5000 to desired port
```

### Reset Database (V2)
```bash
docker-compose -f docker-compose-v2.yml down -v
docker-compose -f docker-compose-v2.yml up
```

---

## 📚 Documentation

| Document | What It Covers |
|----------|---|
| README.md | Main documentation, V1 details, all 12+ vulnerabilities |
| README-V2.md | V2 specific info, 16 vulnerabilities, test cases |
| DEPLOYMENT_GUIDE.md | How to deploy V1 and V2 |
| DOCKER_DEPLOYMENT.md | Docker and Docker Compose details |
| QUICK_START.md | This file - getting started quickly |

---

## 💡 Tips for Success

1. **Start with V1** if you're new to security testing
2. **Compare V1 vs V2** to see how vulnerabilities can be hidden
3. **Use the WSTG scanner** to automatically detect issues
4. **Read the vulnerability docs** to understand each flaw
5. **Test manually** to practice hands-on security skills
6. **Try both** authenticated and unauthenticated access

---

## ❓ Troubleshooting

### Port Already in Use
```bash
# Find what's using the port
lsof -i :5000

# Kill it or use different port
```

### SSL Certificate Warning (V2)
- This is **expected** for self-signed certificates
- Click "Advanced" → "Proceed" in your browser
- This is intentional for testing SSL/TLS vulnerabilities

### Can't Access Application
```bash
# Check if container is running
docker ps

# View logs for errors
docker logs <container-name>
```

### Database Issues (V2)
```bash
# Reset everything
docker-compose -f docker-compose-v2.yml down -v
docker-compose -f docker-compose-v2.yml up
```

---

## ⚠️ Important Notes

- ✅ This app has **intentional vulnerabilities** for testing
- ✅ Only run in **isolated/local environments**
- ✅ Never expose to **public networks**
- ✅ For **authorized testing only**
- ✅ All vulnerabilities are **intentional** for learning

---

## 🎓 Learning Path

1. **Day 1**: Deploy V1, understand basic vulnerabilities
2. **Day 2**: Deploy V2, spot the hidden flaws
3. **Day 3**: Run WSTG scanner on both
4. **Day 4**: Manual testing of V2 endpoints
5. **Day 5**: JWT attacks, privilege escalation
6. **Day 6**: IDOR testing across both versions
7. **Day 7**: Write your own tests and exploits

---

**Ready? Pick your version and start testing!**

- V1: `docker-compose up` → http://localhost:5000
- V2: `docker-compose -f docker-compose-v2.yml up` → https://localhost:5001

---

**Version**: 2.0.0  
**Last Updated**: 2024
