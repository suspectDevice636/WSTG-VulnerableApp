#!/usr/bin/env python3
"""
WSTG Vulnerable Web Application - Upgraded UI
==============================================
A deliberately vulnerable Flask app for testing WSTG penetration testing automation.
Contains common OWASP vulnerabilities for educational and authorized testing purposes.

UPGRADED: Professional UI with modern templates and styling

WARNING: This application contains intentional vulnerabilities and should ONLY be used
for authorized security testing and educational purposes.
"""

from flask import Flask, render_template, render_template_string, request, redirect, jsonify
import sqlite3
import os
import logging
from pathlib import Path

app = Flask(__name__)
app.config['DEBUG'] = True  # Intentionally enabled for testing

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = '/tmp/wstg_vulnerable.db'

def init_db():
    """Initialize database with vulnerable schema"""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create users table
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        email TEXT,
        role TEXT
    )''')

    # Insert test data
    c.execute("INSERT INTO users VALUES (1, 'admin', 'admin123', 'admin@example.com', 'admin')")
    c.execute("INSERT INTO users VALUES (2, 'user', 'password123', 'user@example.com', 'user')")
    c.execute("INSERT INTO users VALUES (3, 'guest', 'guest', 'guest@example.com', 'guest')")

    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# ============================================================================
# VULNERABILITY 1: SQL Injection
# ============================================================================
@app.route('/api/user/<user_id>')
def get_user(user_id):
    """SQL Injection vulnerability - direct string concatenation in SQL"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # VULNERABLE: Direct string concatenation (SQL Injection)
        query = f"SELECT * FROM users WHERE id = {user_id}"
        c.execute(query)
        user = c.fetchone()
        conn.close()

        if user:
            return jsonify({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            })
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e), 'query': query}), 500

@app.route('/search')
def search():
    """Search endpoint with SQL injection vulnerability"""
    username = request.args.get('username', '')
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # VULNERABLE: SQL Injection in search
        query = f"SELECT * FROM users WHERE username LIKE '%{username}%'"
        c.execute(query)
        results = c.fetchall()
        conn.close()

        users = [dict(row) for row in results]
        return jsonify({'results': users})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# VULNERABILITY 2: Weak Authentication & IDOR
# ============================================================================
@app.route('/api/profile/<user_id>')
def get_profile(user_id):
    """Insecure Direct Object Reference - no authorization checks"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'password': user['password'],  # EXPOSED!
            'role': user['role']
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Weak authentication - no rate limiting, weak validation"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # VULNERABLE: No rate limiting, weak checks
        if username and password:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = c.fetchone()
            conn.close()

            if user:
                return redirect(f'/dashboard/{user[0]}')
            return "Invalid credentials", 401

    return render_template('login.html')

@app.route('/dashboard/<user_id>')
def dashboard(user_id):
    """IDOR - no authorization checking"""
    return render_template('dashboard.html', user_id=user_id)

# ============================================================================
# VULNERABILITY 3: Missing Security Headers
# ============================================================================
@app.route('/xss')
def xss_test():
    """Reflected XSS vulnerability - no input validation"""
    message = request.args.get('message', 'No message')

    # VULNERABLE: Direct rendering of user input
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>XSS Test</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    </head>
    <body>
        <nav>
            <div class="container">
                <h1>🔐 WSTG Security Lab</h1>
                <div>
                    <a href="/">Home</a>
                    <a href="/login">Login</a>
                    <a href="/admin">Admin</a>
                    <a href="/api/user/1">API</a>
                </div>
            </div>
        </nav>
        <main>
            <div class="container">
                <h1>Message Echo</h1>
                <div class="card">
                    <div class="card-header">
                        <h3>XSS Vulnerability Test</h3>
                    </div>
                    <p>Your message:</p>
                    <p><strong>{message}</strong></p>
                    <hr>
                    <p style="color: var(--text-light); font-size: 0.9rem;">
                        Try: &lt;script&gt;alert('XSS')&lt;/script&gt;
                    </p>
                    <p style="color: var(--text-light); font-size: 0.9rem;">
                        Or: &lt;img src=x onerror=alert(1)&gt;
                    </p>
                </div>
            </div>
        </main>
        <footer>
            <p>&copy; 2024 WSTG Vulnerable Application - For Authorized Security Testing Only</p>
        </footer>
    </body>
    </html>
    '''

# ============================================================================
# VULNERABILITY 4: Directory Listing & Sensitive Files
# ============================================================================
@app.route('/backup')
def backup_files():
    """Exposed backup files"""
    return render_template('backup.html')

@app.route('/files/<filename>')
def get_file(filename):
    """Serves backup files without restriction"""
    backup_content = {
        'config.bak': 'DATABASE_URL=mysql://admin:password123@localhost/db\nAPI_KEY=sk_test_1234567890abcdef',
        'database.sql.bak': 'INSERT INTO users VALUES (1, "admin", "admin123");',
        'app.config.backup': 'DEBUG=True\nSECRET_KEY=super_secret_key_123\nADMIN_EMAIL=admin@example.com',
        '.env.backup': 'API_KEY=supersecretkey\nDB_PASSWORD=password123\nADMIN_TOKEN=token123'
    }

    if filename in backup_content:
        return backup_content[filename], 200, {'Content-Type': 'text/plain'}
    return 'File not found', 404

# ============================================================================
# VULNERABILITY 5: Unrestricted HTTP Methods
# ============================================================================
@app.route('/resource/<resource_id>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def resource_endpoint(resource_id):
    """Allows unrestricted HTTP methods"""
    if request.method == 'GET':
        return jsonify({'id': resource_id, 'name': 'Resource', 'data': 'value'})
    elif request.method == 'PUT':
        return jsonify({'message': 'Resource updated', 'id': resource_id})
    elif request.method == 'DELETE':
        return jsonify({'message': 'Resource deleted', 'id': resource_id})
    elif request.method == 'PATCH':
        return jsonify({'message': 'Resource patched', 'id': resource_id})

    return jsonify({'error': 'Method not allowed'}), 405

# ============================================================================
# VULNERABILITY 6: Exposed Configuration & Information Disclosure
# ============================================================================
@app.route('/admin')
def admin_panel():
    """Exposed admin panel with debug info"""
    python_version = os.popen("python3 --version 2>&1").read().strip()
    return render_template('admin.html',
                         db_path=DB_PATH,
                         python_version=python_version)

# ============================================================================
# VULNERABILITY 7: robots.txt & sitemap exposure
# ============================================================================
@app.route('/robots.txt')
def robots():
    """Exposed robots.txt with sensitive paths"""
    return '''User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/
Disallow: /backup
Disallow: /dashboard/
Disallow: /.git

# Sensitive paths accidentally exposed
# /admin/users
# /api/v1/users
# /config
# /database.sql
''', 200, {'Content-Type': 'text/plain'}

@app.route('/sitemap.xml')
def sitemap():
    """Exposed sitemap with all endpoints"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>http://localhost/</loc></url>
    <url><loc>http://localhost/login</loc></url>
    <url><loc>http://localhost/admin</loc></url>
    <url><loc>http://localhost/backup</loc></url>
    <url><loc>http://localhost/api/user/1</loc></url>
    <url><loc>http://localhost/api/profile/1</loc></url>
    <url><loc>http://localhost/search</loc></url>
</urlset>
''', 200, {'Content-Type': 'application/xml'}

# ============================================================================
# VULNERABILITY 8: .git directory exposure
# ============================================================================
@app.route('/.git/config')
def git_config():
    """Exposed .git directory"""
    return '''[core]
	repositoryformatversion = 0
	filemode = true
	bare = false
	logallrefupdates = true
[remote "origin"]
	url = https://github.com/suspect-device/vulnerable-app.git
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
	remote = origin
	merge = refs/heads/main
''', 200, {'Content-Type': 'text/plain'}

# ============================================================================
# VULNERABILITY 9: Unvalidated Redirects
# ============================================================================
@app.route('/redirect')
def unvalidated_redirect():
    """Unvalidated redirect vulnerability"""
    url = request.args.get('url', '/')
    return redirect(url)

# ============================================================================
# MAIN ROUTES
# ============================================================================
@app.route('/')
def index():
    """Home page with links to vulnerable endpoints"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
