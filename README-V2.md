# WSTG Vulnerable Application - V2 (Enhanced)

A **realistic** note-taking web application (`SecureNotes`) with **intentional security vulnerabilities** designed for security testing and training.

## 🎯 What is V2?

V2 is an enhanced version of the vulnerable application that:
- ✅ Looks like a real, functional web application
- ✅ Has hidden vulnerabilities (not obvious)
- ✅ Includes pre-created users for testing
- ✅ Features multiple security flaws across different categories
- ✅ Uses HTTPS with self-signed certificates
- ✅ Includes admin functionality with privilege escalation vector

## 🚀 Running V2

### Option 1: Direct Python Execution

```bash
pip install -r requirements.txt
python3 -c "from app_v2 import app, init_db; import ssl; init_db(); context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); context.load_cert_chain('cert.pem', 'key.pem'); app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=context)"
```

Or use the provided script:
```bash
chmod +x run-v2.sh
./run-v2.sh
```

### Option 2: Docker

```bash
docker-compose -f docker-compose-v2.yml up
```

Access the application at: `https://localhost:5001`

## 👥 Test Users

| Username | Password | Role |
|----------|----------|------|
| admin | AdminPass123! | Admin (Privilege Escalation Test) |
| user1 | password123 | Regular User |
| user2 | password456 | Regular User |
| user3 | password789 | Regular User |
| john | JohnPassword | Regular User |

## 🔴 Vulnerabilities in V2 (16 Total)

### 1. **Hardcoded Credentials** 
- **Location**: HTML comments in `/login` page
- **Vulnerability**: Developer left credentials in HTML source code
- **Detection**: View page source, search for comments
- **WSTG Phase**: 2 (Information Gathering)
- **Severity**: CRITICAL

```html
<!-- Test credentials:
     Username: admin
     Password: AdminPass123!
-->
```

### 2. **Base64 Encoded Secrets**
- **Location**: `app-v2.py` line ~85
- **Vulnerability**: API key encoded in base64 (easily decoded)
- **Detection**: Decode: `aW50ZXJuYWxfYXBpX2tleV9zZWNyZXQ=`
- **WSTG Phase**: 2 (Information Gathering)
- **Severity**: HIGH

### 3. **CORS Misconfiguration (V1 + V2)**
- **Endpoint**: All endpoints
- **Vulnerability**: `Access-Control-Allow-Origin: *` with credentials
- **Detection**: Check response headers
- **WSTG Phase**: 4 (Configuration/Deployment Testing)
- **Severity**: HIGH

```bash
curl -i https://localhost:5000/api/sensitive-data
# Response includes: Access-Control-Allow-Origin: *
```

### 4. **Insecure CSP Header (V1 + V2)**
- **Vulnerability**: `unsafe-inline`, `unsafe-eval`, wildcard sources allowed
- **Detection**: Check CSP header, test XSS payloads
- **WSTG Phase**: 4.6 (Content Security Policy Testing)
- **Severity**: HIGH

```
CSP: default-src 'self' * data:; script-src 'self' 'unsafe-inline' 'unsafe-eval' *;
```

### 5. **Insecure Direct Object References (IDOR)**
- **Endpoints**: 
  - `GET /api/notes` (user_id parameter)
  - `GET /api/notes/<id>` (no ownership check)
  - `PUT /api/notes/<id>` (no ownership check)
  - `DELETE /api/notes/<id>` (no ownership check)
- **Vulnerability**: No verification that requesting user owns the resource
- **Detection**: Login as user1, access user2's notes by changing IDs
- **WSTG Phase**: 6 (Authorization Testing)
- **Severity**: CRITICAL
- **Test**:
```bash
# Login as user1, then:
curl -X GET https://localhost:5000/api/notes/3 \
  -H "Cookie: session=..."
# Returns user2's note (should fail!)
```

### 6. **SQL Injection**
- **Endpoint**: `GET /api/search?q=<payload>`
- **Vulnerability**: User input concatenated directly into SQL query
- **Detection**: Test with `' OR '1'='1` or `'; DROP TABLE users;--`
- **WSTG Phase**: 7 (Input Validation Testing)
- **Severity**: CRITICAL
- **Test**:
```bash
curl "https://localhost:5000/api/search?q=' OR '1'='1"
```

### 7. **Privilege Escalation (Weak Admin Check)**
- **Endpoint**: `POST /api/admin/promote/<user_id>`
- **Vulnerability**: Session variable can be manipulated to escalate privileges
- **Detection**: Modify session cookie to set `is_admin=true`
- **WSTG Phase**: 6 (Authorization Testing)
- **Severity**: CRITICAL
- **Test**:
```javascript
// In browser console, modify session
// Then call: fetch('/api/admin/promote/1', {method: 'POST'})
```

### 8. **Missing CSRF Tokens**
- **Endpoints**: All state-changing operations (POST, PUT, DELETE)
- **Vulnerability**: No CSRF token validation
- **Detection**: No `csrf_token` in forms or headers
- **WSTG Phase**: 6 (CSRF Testing)
- **Severity**: HIGH
- **Test**:
```html
<!-- Attacker site can make requests to user's notes -->
<form action="https://securenotes.com/api/notes/1" method="POST">
  <!-- Note will be deleted without user knowledge -->
</form>
```

### 9. **Weak Password Validation**
- **Endpoint**: `POST /register`
- **Vulnerability**: No minimum length, complexity, or pattern requirements
- **Detection**: Register with password "1" or empty string
- **WSTG Phase**: 5 (Authentication Testing)
- **Severity**: MEDIUM

### 10. **Information Disclosure**
- **Endpoints**: 
  - `/api/debug` - Exposes all configuration and secrets
  - `/api/users` - Lists all users with admin status
  - Error responses - Verbose SQL/application errors
- **Vulnerability**: Sensitive information exposed
- **Detection**: Access endpoints directly
- **WSTG Phase**: 2 (Information Gathering)
- **Severity**: HIGH

### 11. **Insecure File Upload**
- **Endpoint**: `POST /upload`
- **Vulnerability**: 
  - Extension checking only (can upload .exe, .sh files)
  - No content validation
  - Path traversal possible via `../`
  - Predictable file locations
- **Detection**: Upload malicious file, access via `/uploads/`
- **WSTG Phase**: 6 (Input Validation Testing)
- **Severity**: HIGH

### 12. **User Enumeration**
- **Endpoint**: `POST /register`, `POST /login`
- **Vulnerability**: Different error messages reveal if username exists
- **Detection**: Try registering existing vs new username
- **WSTG Phase**: 5 (Authentication Testing)
- **Severity**: MEDIUM

### 13. **Debug Mode Enabled**
- **Vulnerability**: Flask debug mode enabled in production
- **Detection**: Error pages show stack traces, file paths, variables
- **WSTG Phase**: 4.2 (Debug Functions Testing)
- **Severity**: MEDIUM

### 14. **Self-Signed Certificate (Poor SSL/TLS)**
- **Vulnerability**: Self-signed certificate, no certificate pinning
- **Detection**: Certificate validation warnings
- **WSTG Phase**: 4.7 (SSL/TLS Testing)
- **Severity**: MEDIUM

### 15. **JWT Vulnerabilities** (NEW!)
- **Endpoints**: `/api/auth/token`, `/api/auth/refresh`, `/api/auth/verify`, `/api/v2/notes/*`
- **Vulnerabilities**:
  - Weak secret key: `jwt_secret_123` (easily brute-forceable)
  - Long expiration: 7 days (can be extended to lifetime with `no_expiry=true`)
  - No token revocation/blacklist (tokens can't be invalidated)
  - Token passed via query parameter (should be header only)
  - No signature algorithm validation
  - Debug endpoint exposes token payload and secret hints
  - Refresh endpoint doesn't validate claims
- **Detection**: Decode JWT with `jwt.io`, brute-force secret, test `no_expiry` parameter
- **WSTG Phase**: 5.5 (Token Security Testing)
- **Severity**: CRITICAL
- **Test**:
```bash
# Get token
curl -X POST https://localhost:5000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"password123"}'

# Use token to access notes (IDOR still works)
curl -X GET "https://localhost:5000/api/v2/notes?user_id=2" \
  -H "Authorization: Bearer <token>"

# Get non-expiring token
curl -X POST "https://localhost:5000/api/auth/token?no_expiry=true" \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"password123"}'
```

### 16. **Sensitive Data Exposure**
- **Endpoint**: `GET /api/sensitive-data`
- **Vulnerability**: API keys, credentials, tokens exposed via CORS
- **Detection**: Cross-origin request reveals sensitive data
- **WSTG Phase**: 2 (Information Gathering)
- **Severity**: CRITICAL

## 🧪 Testing with WSTG Automation Script

Run the WSTG automation script against V2:

```bash
./wstg-automation.sh https://localhost:5000 -o ./v2-scan-results
```

Expected detections:
- ✅ CORS headers (wildcard origin)
- ✅ CSP headers (unsafe-inline, unsafe-eval)
- ✅ Directory listing
- ✅ Exposed `.git` directory
- ✅ Missing security headers
- ✅ Directory enumeration (Gobuster)
- ✅ Parameter fuzzing (wfuzz)
- ✅ HTTP methods allowed
- ✅ SSL/TLS certificate issues (self-signed)

## 📋 V2 Feature Comparison

| Feature | V1 | V2 |
|---------|----|----|
| Realistic UI | ❌ | ✅ |
| Multiple Users | ❌ | ✅ |
| Admin User | ❌ | ✅ |
| Privilege Escalation | ❌ | ✅ |
| IDOR Testing | ⚠️ | ✅ |
| Hidden Vulns | ❌ | ✅ |
| HTTPS/SSL | ❌ | ✅ |
| Database (SQLite) | ✅ | ✅ |
| Notes/Content | ⚠️ | ✅ |
| File Upload | ✅ | ✅ |

## 🔧 Docker Notes

- V2 runs on port **5001** (to avoid conflict with V1 on 5000)
- Database file: `notes.db` (persists uploads)
- SSL certificates in container: `/app/cert.pem` and `/app/key.pem`
- Browser will warn about self-signed certificate (expected)

## ⚠️ Legal Notice

This application is for **authorized security testing only**. 
- Only use on systems you own or have explicit permission to test
- Unauthorized access is illegal
- Follow responsible disclosure practices

## 📚 Learning Objectives

After testing V2, you should understand:
- How vulnerabilities hide in realistic applications
- IDOR attacks and authorization bypass
- CORS and CSP security implications
- SQL injection in modern frameworks
- Privilege escalation vectors
- File upload security flaws
- Information disclosure risks
- SSL/TLS certificate issues
- JWT token vulnerabilities and attacks
- Weak secret key brute-forcing
- Token expiration bypass techniques

## 🚀 Next Steps

1. Run V2 locally
2. Test each vulnerability
3. Use WSTG scanner to detect issues
4. Compare findings between V1 and V2
5. Document your discoveries

---

**Version**: 2.0.0  
**Last Updated**: 2024  
**Author**: WSTG Project
