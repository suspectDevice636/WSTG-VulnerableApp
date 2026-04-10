#!/usr/bin/env python3
"""
WSTG Vulnerable Application - V2 (Enhanced)
A realistic note-taking application with intentional security vulnerabilities
for security testing and training purposes.

V2 Enhancements:
- Realistic UI design (appears as functional web app)
- Multiple pre-created users for IDOR testing
- Admin user for privilege escalation testing
- Hidden vulnerabilities (not obvious)
- Insecure CSP headers
- CORS misconfiguration
- SQL injection vulnerability
- Hardcoded credentials in comments
- Base64 encoded secrets
- File upload vulnerabilities
- Missing CSRF tokens
- Weak password validation
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import base64
from functools import wraps
from datetime import datetime, timedelta
import sqlite3
import jwt

app = Flask(__name__)

# ===== VULNERABLE CONFIGURATION =====
# Configuration with intentional vulnerabilities
app.config['SECRET_KEY'] = 'super_secret_key_change_me'  # Weak secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions (intentionally too permissive)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'exe', 'sh'}

# ===== JWT CONFIGURATION (VULNERABLE) =====
# VULNERABLE: Weak JWT secret (easy to brute force)
JWT_SECRET = 'jwt_secret_123'
# VULNERABLE: Long token expiration (default 7 days, some tokens never expire)
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

db = SQLAlchemy(app)

# ===== DATABASE MODELS =====
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    notes = db.relationship('Note', backref='author', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_private = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Note {self.title}>'


# ===== VULNERABLE HELPERS =====
# Hardcoded credentials (hidden in comments for developer)
# Admin credentials: admin / AdminPass123!
# Database admin: dbuser / db_password_2024

# Base64 encoded API key (intentionally not obvious)
# echo -n "internal_api_key_secret" | base64
INTERNAL_API_KEY = base64.b64decode(b'aW50ZXJuYWxfYXBpX2tleV9zZWNyZXQ=').decode()

def allowed_file(filename):
    """Check if file extension is allowed (VULNERABLE - too permissive)"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ===== JWT FUNCTIONS (VULNERABLE) =====
def generate_jwt_token(user_id, username, is_admin=False, no_expiry=False):
    """Generate JWT token (VULNERABLE - weak secret, long expiration)"""
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'iat': datetime.utcnow()
    }

    # VULNERABLE: No expiration if no_expiry is True
    if not no_expiry:
        payload['exp'] = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)

    # VULNERABLE: Weak secret key
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token


def verify_jwt_token(token):
    """Verify JWT token (VULNERABLE - doesn't validate all claims)"""
    try:
        # VULNERABLE: Uses weak secret, no signature verification options
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwt_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Check Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        # VULNERABLE: Also check for token in query parameter (bad practice)
        elif 'token' in request.args:
            token = request.args.get('token')

        if not token:
            return jsonify({'error': 'Token required'}), 401

        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Store in request for later use
        request.user_id = payload['user_id']
        request.username = payload['username']
        request.is_admin = payload.get('is_admin', False)

        return f(*args, **kwargs)
    return decorated_function


# ===== RESPONSE HEADERS (VULNERABLE) =====
@app.after_request
def set_security_headers(response):
    """Set security headers (intentionally weak)"""

    # CORS Misconfiguration - Wildcard origin
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    # Insecure CSP - allows inline scripts and unsafe eval
    response.headers['Content-Security-Policy'] = "default-src 'self' * data:; script-src 'self' 'unsafe-inline' 'unsafe-eval' *; style-src 'self' 'unsafe-inline' *; img-src 'self' * data:;"

    # Missing security headers (VULNERABLE)
    # No HSTS
    # No X-Frame-Options
    # No X-Content-Type-Options

    return response


# ===== ROUTES =====
@app.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page (VULNERABLE to weak password validation)"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        # VULNERABLE: No rate limiting, no account lockout
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            return redirect(url_for('dashboard'))

        # VULNERABLE: Information disclosure - tells attacker if username exists
        error = 'Invalid username or password'
        return render_template('login.html', error=error), 401

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register page (VULNERABLE to weak validation)"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')

        # VULNERABLE: Weak password validation (no min length check, no complexity)
        if len(password) < 1:
            return render_template('register.html', error='Password required'), 400

        # VULNERABLE: User enumeration possible
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists'), 400

        if User.query.filter_by(email=email).first():
            return render_template('register.html', error='Email already exists'), 400

        # Create new user (not admin)
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            is_admin=False
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))


# ===== JWT ENDPOINTS (VULNERABLE) =====
@app.route('/api/auth/token', methods=['POST'])
def get_jwt_token():
    """Generate JWT token from username/password (VULNERABLE)"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password, data['password']):
        # VULNERABLE: Information disclosure - tells if user exists
        return jsonify({'error': 'Invalid credentials'}), 401

    # VULNERABLE: Token never expires if no_expiry parameter is passed
    no_expiry = request.args.get('no_expiry', 'false').lower() == 'true'

    token = generate_jwt_token(user.id, user.username, user.is_admin, no_expiry)

    return jsonify({
        'token': token,
        'user_id': user.id,
        'username': user.username,
        'is_admin': user.is_admin,
        # VULNERABLE: Exposes secret in response (for testing purposes)
        'secret_hint': 'jwt_secret_*'
    })


@app.route('/api/auth/refresh', methods=['POST'])
def refresh_jwt_token():
    """Refresh JWT token (VULNERABLE - no validation)"""
    token = request.headers.get('Authorization', '').split(' ')[-1]

    if not token:
        return jsonify({'error': 'Token required'}), 401

    # VULNERABLE: No proper validation, just decodes and re-encodes
    payload = verify_jwt_token(token)

    if not payload:
        return jsonify({'error': 'Invalid token'}), 401

    # VULNERABLE: Issues new token without checking anything
    new_token = generate_jwt_token(payload['user_id'], payload['username'], payload.get('is_admin'))

    return jsonify({'token': new_token})


@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    """Verify and decode token (VULNERABLE - exposes claims)"""
    token = request.args.get('token') or request.headers.get('Authorization', '').split(' ')[-1]

    if not token:
        return jsonify({'error': 'Token required'}), 401

    payload = verify_jwt_token(token)

    if not payload:
        return jsonify({'error': 'Invalid token'}), 401

    # VULNERABLE: Returns full payload including claims
    return jsonify({
        'valid': True,
        'payload': payload
    })


@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard (main page after login)"""
    user = User.query.get(session['user_id'])

    # Get only notes owned by the current user
    user_notes = Note.query.filter_by(user_id=session['user_id']).all()

    return render_template('dashboard.html', user=user, notes=user_notes)


@app.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    """API to get notes (VULNERABLE to IDOR)"""
    user_id = request.args.get('user_id', session['user_id'])

    # VULNERABLE: IDOR - No verification that requesting user owns the requested user_id
    notes = Note.query.filter_by(user_id=user_id).all()

    return jsonify({
        'notes': [
            {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'author': User.query.get(note.user_id).username,
                'created_at': note.created_at.isoformat()
            } for note in notes
        ]
    })


@app.route('/api/notes/<int:note_id>', methods=['GET'])
@login_required
def get_note(note_id):
    """Get specific note (VULNERABLE to IDOR)"""
    note = Note.query.get(note_id)

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # VULNERABLE: No ownership check - anyone can view any note
    return jsonify({
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'author': User.query.get(note.user_id).username,
        'user_id': note.user_id,  # VULNERABLE: Exposes user_id
        'is_private': note.is_private,
        'created_at': note.created_at.isoformat()
    })


@app.route('/api/notes', methods=['POST'])
@login_required
def create_note():
    """Create a new note"""
    data = request.get_json()

    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content required'}), 400

    new_note = Note(
        title=data['title'],
        content=data['content'],
        user_id=session['user_id'],
        is_private=data.get('is_private', True)
    )

    db.session.add(new_note)
    db.session.commit()

    return jsonify({
        'id': new_note.id,
        'message': 'Note created successfully'
    }), 201


@app.route('/api/notes/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    """Update a note (VULNERABLE to IDOR)"""
    note = Note.query.get(note_id)

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # VULNERABLE: No ownership check - anyone can edit any note
    data = request.get_json()

    if 'title' in data:
        note.title = data['title']
    if 'content' in data:
        note.content = data['content']
    if 'is_private' in data:
        note.is_private = data['is_private']

    note.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Note updated successfully'})


@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    """Delete a note (VULNERABLE to IDOR)"""
    note = Note.query.get(note_id)

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # VULNERABLE: No ownership check - anyone can delete any note
    db.session.delete(note)
    db.session.commit()

    return jsonify({'message': 'Note deleted successfully'})


@app.route('/api/search', methods=['GET'])
@login_required
def search_notes():
    """Search notes (VULNERABLE to SQL Injection)"""
    query = request.args.get('q', '')

    # VULNERABLE: SQL Injection via search query
    # This intentionally uses string formatting instead of parameterized queries
    sql_query = f"SELECT * FROM note WHERE title LIKE '%{query}%' OR content LIKE '%{query}%'"

    try:
        result = db.session.execute(sql_query)
        notes = result.fetchall()
        return jsonify({
            'results': [dict(note) for note in notes]
        })
    except Exception as e:
        # VULNERABLE: Information disclosure - reveals database error
        return jsonify({'error': str(e)}), 500


# ===== JWT API ENDPOINTS (VULNERABLE) =====
@app.route('/api/v2/notes', methods=['GET'])
@jwt_required
def get_notes_jwt():
    """Get notes using JWT auth (VULNERABLE to IDOR)"""
    user_id = request.args.get('user_id', request.user_id)

    # VULNERABLE: IDOR - can access any user's notes
    notes = Note.query.filter_by(user_id=user_id).all()

    return jsonify({
        'notes': [
            {
                'id': note.id,
                'title': note.title,
                'content': note.content,
                'user_id': note.user_id,
                'created_at': note.created_at.isoformat()
            } for note in notes
        ]
    })


@app.route('/api/v2/notes/<int:note_id>', methods=['GET'])
@jwt_required
def get_note_jwt(note_id):
    """Get specific note using JWT auth (VULNERABLE to IDOR)"""
    note = Note.query.get(note_id)

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # VULNERABLE: No ownership check
    return jsonify({
        'id': note.id,
        'title': note.title,
        'content': note.content,
        'user_id': note.user_id,
        'created_at': note.created_at.isoformat()
    })


@app.route('/api/v2/notes', methods=['POST'])
@jwt_required
def create_note_jwt():
    """Create note using JWT auth"""
    data = request.get_json()

    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content required'}), 400

    new_note = Note(
        title=data['title'],
        content=data['content'],
        user_id=request.user_id,
        is_private=data.get('is_private', True)
    )

    db.session.add(new_note)
    db.session.commit()

    return jsonify({
        'id': new_note.id,
        'message': 'Note created'
    }), 201


@app.route('/api/v2/notes/<int:note_id>', methods=['PUT'])
@jwt_required
def update_note_jwt(note_id):
    """Update note using JWT auth (VULNERABLE to IDOR)"""
    note = Note.query.get(note_id)

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # VULNERABLE: No ownership check
    data = request.get_json()

    if 'title' in data:
        note.title = data['title']
    if 'content' in data:
        note.content = data['content']

    db.session.commit()

    return jsonify({'message': 'Updated'})


@app.route('/api/v2/notes/<int:note_id>', methods=['DELETE'])
@jwt_required
def delete_note_jwt(note_id):
    """Delete note using JWT auth (VULNERABLE to IDOR)"""
    note = Note.query.get(note_id)

    if not note:
        return jsonify({'error': 'Note not found'}), 404

    # VULNERABLE: No ownership check
    db.session.delete(note)
    db.session.commit()

    return jsonify({'message': 'Deleted'})


@app.route('/api/users', methods=['GET'])
def get_all_users():
    """Get all users (VULNERABLE - exposed endpoint)"""
    users = User.query.all()

    # VULNERABLE: Exposes all user information including admin status
    return jsonify({
        'users': [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat()
            } for user in users
        ]
    })


@app.route('/api/admin/promote/<int:user_id>', methods=['POST'])
@login_required
def promote_to_admin(user_id):
    """Promote user to admin (VULNERABLE to privilege escalation)"""

    # VULNERABLE: No proper admin check - can be exploited
    # Just checking if user exists, not if current user is REALLY admin
    target_user = User.query.get(user_id)

    if not target_user:
        return jsonify({'error': 'User not found'}), 404

    # VULNERABLE: Easy privilege escalation
    # If session['is_admin'] is True (can be manipulated), user can promote themselves
    if session.get('is_admin'):
        target_user.is_admin = True
        db.session.commit()
        return jsonify({'message': f'{target_user.username} is now admin'})

    return jsonify({'error': 'Admin access required'}), 403


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    """File upload (VULNERABLE)"""
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # VULNERABLE: No file content validation, only extension check
            # VULNERABLE: Predictable filename, no randomization
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'path': f'/uploads/{filename}'  # VULNERABLE: Exposes upload path
            })

        return jsonify({'error': 'File type not allowed'}), 400

    return render_template('upload.html')


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files (VULNERABLE to path traversal)"""
    # VULNERABLE: No path validation - allows path traversal (../)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(filepath) and os.path.isfile(filepath):
        with open(filepath, 'r', errors='ignore') as f:
            return f.read()

    return 'File not found', 404


@app.route('/api/debug')
def debug_info():
    """Debug endpoint (VULNERABLE - information disclosure)"""
    # VULNERABLE: Exposes internal configuration and debugging info
    return jsonify({
        'debug_mode': app.debug,
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'database': app.config['SQLALCHEMY_DATABASE_URI'],
        'secret_key': app.config['SECRET_KEY'],
        'api_key': INTERNAL_API_KEY,  # VULNERABLE: Exposes API key
        'users_count': User.query.count(),
        'notes_count': Note.query.count()
    })


@app.route('/api/sensitive-data')
def sensitive_data():
    """Endpoint exposing sensitive data (from V1)"""
    # VULNERABLE: CORS allows cross-origin access to this endpoint
    return jsonify({
        'stripe_key': 'sk_live_[REDACTED]',
        'database_host': 'localhost',
        'database_user': 'root',
        'api_tokens': [
            'token_abc123def456',
            'token_xyz789uvw012'
        ]
    })


@app.route('/admin')
@admin_required
def admin_panel():
    """Admin panel"""
    users = User.query.all()
    notes = Note.query.all()

    return render_template('admin.html', users=users, notes=notes)


# ===== DATABASE INITIALIZATION =====
def init_db():
    """Initialize database with test users"""
    with app.app_context():
        db.create_all()

        # Check if users already exist
        if User.query.first() is not None:
            return

        # Create pre-made users for IDOR testing
        users_data = [
            {'username': 'admin', 'email': 'admin@securenotes.com', 'password': 'AdminPass123!', 'is_admin': True},
            {'username': 'user1', 'email': 'user1@example.com', 'password': 'password123', 'is_admin': False},
            {'username': 'user2', 'email': 'user2@example.com', 'password': 'password456', 'is_admin': False},
            {'username': 'user3', 'email': 'user3@example.com', 'password': 'password789', 'is_admin': False},
            {'username': 'john', 'email': 'john@example.com', 'password': 'JohnPassword', 'is_admin': False},
        ]

        for user_data in users_data:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=generate_password_hash(user_data['password']),
                is_admin=user_data['is_admin']
            )
            db.session.add(user)

        db.session.commit()

        # Create sample notes for IDOR testing
        admin_user = User.query.filter_by(username='admin').first()
        user1 = User.query.filter_by(username='user1').first()
        user2 = User.query.filter_by(username='user2').first()

        sample_notes = [
            Note(title='Admin Secret Notes', content='This is confidential admin information that should not be accessible to regular users.', user_id=admin_user.id, is_private=True),
            Note(title='User1 Personal Note', content='This is a private note from user1. It should not be visible to other users.', user_id=user1.id, is_private=True),
            Note(title='User2 Shopping List', content='Milk, Eggs, Bread, Cheese - shopping list from user2', user_id=user2.id, is_private=True),
            Note(title='Shared Note', content='This note is shared and visible to all users', user_id=admin_user.id, is_private=False),
        ]

        for note in sample_notes:
            db.session.add(note)

        db.session.commit()


# ===== ERROR HANDLERS =====
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors (VULNERABLE: Verbose error messages)"""
    return jsonify({'error': str(error)}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors (VULNERABLE: Information disclosure)"""
    return jsonify({'error': str(error), 'type': type(error).__name__}), 500


# ===== ENTRY POINT =====
if __name__ == '__main__':
    init_db()
    # VULNERABLE: Debug mode enabled
    app.run(debug=True, host='0.0.0.0', port=5000)
