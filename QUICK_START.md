# WSTG Vulnerable App - Quick Start Guide

## ✨ What's New

Your vulnerable webapp now has a **professional, modern UI** with:
- 📱 Responsive design that works on all devices
- 🎨 Professional color scheme and typography
- 📊 Better organized vulnerability categories
- 🔐 Clear visual hierarchy and navigation
- ⚡ Smooth transitions and hover effects

**All security vulnerabilities remain intact** - perfect for testing!

## 🚀 Quick Start

### Option 1: Using Docker (Recommended)
```bash
cd WSTG-VulnerableApp
docker-compose up
```

### Option 2: Direct Python
```bash
cd WSTG-VulnerableApp
pip install flask
python3 app.py
```

Then open: **http://localhost:5000**

## 🔓 Test Credentials

```
Admin    → admin / admin123
User     → user / password123
Guest    → guest / guest
```

## 🌐 Key Pages

| URL | Description |
|-----|-------------|
| `/` | Home page with all vulnerabilities listed |
| `/login` | Login page (weak authentication) |
| `/dashboard/<id>` | User dashboard (IDOR vulnerability) |
| `/admin` | Admin panel (exposed without auth) |
| `/backup` | Backup files (information disclosure) |
| `/search` | Search with SQL injection |
| `/api/user/<id>` | API endpoint with SQL injection |
| `/api/profile/<id>` | Profile endpoint (IDOR) |
| `/xss` | XSS vulnerability page |

## 🎯 Testing the Vulnerabilities

### SQL Injection
```
Try: /api/user/1 OR 1=1
Or:  /search?username=admin' OR '1'='1
```

### IDOR (Insecure Direct Object Reference)
```
Try: /api/profile/1, /api/profile/2, /api/profile/3
Or:  /dashboard/1, /dashboard/2, /dashboard/3
```

### XSS
```
Try: /xss?message=<script>alert('XSS')</script>
Or:  /xss?message=<img src=x onerror=alert(1)>
```

### Information Disclosure
```
Visit: /admin - Exposed system info
Visit: /backup - Exposed backup files
Visit: /robots.txt - Exposed paths
Visit: /.git/config - Git directory
```

## 📁 New Files & Structure

```
WSTG-VulnerableApp/
├── templates/           ← HTML templates (NEW)
│   ├── base.html       ← Base template
│   ├── index.html      ← Home page
│   ├── login.html      ← Login form
│   ├── dashboard.html  ← User dashboard
│   ├── admin.html      ← Admin panel
│   └── backup.html     ← Backup files
├── static/
│   └── css/
│       └── style.css   ← Professional styling (NEW)
├── app.py              ← Updated to use templates
├── app_original.py     ← Backup of original version
├── UPGRADE_SUMMARY.md  ← Detailed upgrade info
└── QUICK_START.md      ← This file
```

## 🎨 UI Features

### Professional Styling
- Modern gradient navigation bar
- Clean card-based layouts
- Color-coded severity badges (Critical/High/Medium)
- Responsive grid system
- Professional color palette

### Better Organization
- Vulnerability categories with clear descriptions
- Collapsible file content previews
- Detailed impact analysis
- Quick access links
- Visual warnings and alerts

### Mobile Friendly
- Responsive design adapts to all screen sizes
- Touch-friendly buttons and links
- Optimized for mobile testing

## 🔄 Reverting to Original (if needed)

If you want to go back to the original inline HTML:
```bash
cp app_original.py app.py
rm -rf templates/ static/
```

Then restart the app.

## 📚 More Information

See `UPGRADE_SUMMARY.md` for:
- Detailed changelog
- Technical specifications
- Color palette details
- Component documentation
- Future enhancement ideas

## 💡 Tips

1. **For Penetration Testing**: The UI changes make this app look more realistic for testing
2. **For Education**: Better organized vulnerabilities make it easier to learn
3. **For CI/CD**: Can still validate WSTG automation scripts without modification
4. **For Demos**: Professional appearance is great for security training demos

## ⚠️ Remember

This application contains **intentional vulnerabilities** and should **ONLY** be used for:
- ✅ Authorized security testing
- ✅ Educational purposes
- ✅ CI/CD pipeline testing
- ✅ Penetration testing tool validation

**DO NOT** deploy to production or public networks!

---

**Enjoy your upgraded vulnerable app!** 🎉
