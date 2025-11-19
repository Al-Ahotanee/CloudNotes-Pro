"""
CloudNotes Pro - Flask Application
Enterprise-grade notes sharing platform
"""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json
from datetime import datetime, timedelta
from functools import wraps
import secrets

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['UPLOAD_FOLDER'] = 'uploaded_files'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'txt', 'ppt', 'pptx', 'zip'}
app.config['DATABASE'] = 'notes_system.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

CORS(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ============================================================================
# DATABASE UTILITIES
# ============================================================================

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT,
            uploader_id INTEGER NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            downloads INTEGER DEFAULT 0,
            tags TEXT,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_size INTEGER,
            rating_sum INTEGER DEFAULT 0,
            rating_count INTEGER DEFAULT 0,
            FOREIGN KEY (uploader_id) REFERENCES users(id)
        )
    """)

    # Download history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS download_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Ratings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            review TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(note_id, user_id),
            FOREIGN KEY (note_id) REFERENCES notes(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()

    # Create demo data if database is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        create_demo_data(conn)

    conn.close()

def create_demo_data(conn):
    """Create demo users and sample notes"""
    cursor = conn.cursor()

    # Demo users
    demo_users = [
        ("admin", "admin123", "admin@university.edu", "admin"),
        ("student1", "pass123", "student1@university.edu", "student"),
        ("professor", "prof123", "professor@university.edu", "teacher")
    ]

    for username, password, email, role in demo_users:
        cursor.execute("""
            INSERT INTO users (username, password, email, role)
            VALUES (?, ?, ?, ?)
        """, (username, generate_password_hash(password), email, role))

    # Sample notes
    sample_notes = [
        {
            "title": "Introduction to Python Programming",
            "category": "Computer Science",
            "subject": "Programming",
            "description": "Comprehensive guide covering Python basics, data structures, OOP, and best practices",
            "uploader_id": 1,
            "tags": json.dumps(["python", "programming", "basics", "oop"]),
            "file_name": "intro_python.pdf"
        },
        {
            "title": "Calculus I - Derivatives and Integrals",
            "category": "Mathematics",
            "subject": "Calculus",
            "description": "Complete notes on differential and integral calculus with solved examples",
            "uploader_id": 2,
            "tags": json.dumps(["calculus", "derivatives", "integrals"]),
            "file_name": "calculus_notes.pdf"
        },
        {
            "title": "Database Management Systems",
            "category": "Computer Science",
            "subject": "Databases",
            "description": "SQL, normalization, transactions, and database design patterns",
            "uploader_id": 1,
            "tags": json.dumps(["database", "sql", "dbms"]),
            "file_name": "dbms_notes.pdf"
        },
        {
            "title": "Organic Chemistry Reactions",
            "category": "Chemistry",
            "subject": "Organic Chemistry",
            "description": "Common organic reactions and mechanisms",
            "uploader_id": 3,
            "tags": json.dumps(["chemistry", "organic", "reactions"]),
            "file_name": "organic_chem.pdf"
        },
        {
            "title": "Data Structures and Algorithms",
            "category": "Computer Science",
            "subject": "DSA",
            "description": "Comprehensive coverage of DSA concepts",
            "uploader_id": 2,
            "tags": json.dumps(["dsa", "algorithms", "programming"]),
            "file_name": "dsa_notes.pdf"
        }
    ]

    for note in sample_notes:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], note["file_name"])
        with open(file_path, "w") as f:
            f.write(f"Sample content for {note['title']}\n")
            f.write("Demo file for CloudNotes Pro\n")

        file_size = os.path.getsize(file_path)

        cursor.execute("""
            INSERT INTO notes (title, category, subject, description, uploader_id,
                             tags, file_path, file_name, file_size)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (note["title"], note["category"], note["subject"], note["description"],
              note["uploader_id"], note["tags"], file_path, note["file_name"], file_size))

    conn.commit()

# ============================================================================
# AUTHENTICATION DECORATORS
# ============================================================================

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ============================================================================
# ROUTES - PAGES
# ============================================================================

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

# ============================================================================
# ROUTES - AUTHENTICATION
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']

            return jsonify({
                'success': True,
                'message': f'Welcome back, {username}!',
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role']
                }
            })

        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()

        if len(username) < 3:
            return jsonify({'success': False, 'error': 'Username must be at least 3 characters'}), 400

        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400

        if not email or '@' not in email:
            return jsonify({'success': False, 'error': 'Valid email required'}), 400

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (username, password, email, role)
                VALUES (?, ?, ?, 'student')
            """, (username, generate_password_hash(password), email))
            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'message': 'Registration successful! Please login.'
            })

        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'error': 'Username already exists'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/status')
def auth_status():
    """Check authentication status"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session['username'],
                'role': session['role']
            }
        })
    return jsonify({'authenticated': False})

# ============================================================================
# ROUTES - NOTES
# ============================================================================

@app.route('/api/notes/search', methods=['GET'])
def search_notes():
    """Search notes"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', 'All')
        sort_by = request.args.get('sort', 'recent')

        conn = get_db()
        cursor = conn.cursor()

        sql = """
            SELECT n.*, u.username as uploader_name,
                   CASE WHEN n.rating_count > 0
                        THEN CAST(n.rating_sum AS FLOAT) / n.rating_count
                        ELSE 0 END as avg_rating
            FROM notes n
            JOIN users u ON n.uploader_id = u.id
            WHERE 1=1
        """
        params = []

        if query:
            sql += """ AND (
                n.title LIKE ? OR
                n.description LIKE ? OR
                n.subject LIKE ? OR
                n.tags LIKE ?
            )"""
            search_term = f"%{query}%"
            params.extend([search_term] * 4)

        if category != "All":
            sql += " AND n.category = ?"
            params.append(category)

        if sort_by == "recent":
            sql += " ORDER BY n.upload_date DESC"
        elif sort_by == "popular":
            sql += " ORDER BY n.downloads DESC"
        elif sort_by == "rating":
            sql += " ORDER BY avg_rating DESC"

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            results.append({
                'id': row['id'],
                'title': row['title'],
                'category': row['category'],
                'subject': row['subject'],
                'description': row['description'],
                'uploader_name': row['uploader_name'],
                'upload_date': row['upload_date'],
                'downloads': row['downloads'],
                'tags': json.loads(row['tags']),
                'file_name': row['file_name'],
                'file_size': row['file_size'],
                'avg_rating': round(row['avg_rating'], 1)
            })

        return jsonify({'success': True, 'notes': results})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/categories')
def get_categories():
    """Get all categories"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM notes ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return jsonify({'success': True, 'categories': ['All'] + categories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/upload', methods=['POST'])
@login_required
def upload_note():
    """Upload new note"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400

        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        subject = request.form.get('subject', '').strip()
        description = request.form.get('description', '').strip()
        tags = request.form.get('tags', '')

        if not all([title, category, subject]):
            return jsonify({'success': False, 'error': 'Title, category, and subject required'}), 400

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        file.save(file_path)
        file_size = os.path.getsize(file_path)

        tags_list = json.dumps([tag.strip() for tag in tags.split(",") if tag.strip()])

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notes (title, category, subject, description, uploader_id,
                             tags, file_path, file_name, file_size)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, category, subject, description, session['user_id'],
              tags_list, file_path, filename, file_size))
        conn.commit()
        note_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'success': True,
            'message': f'"{title}" uploaded successfully!',
            'note_id': note_id
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/download/<int:note_id>')
@login_required
def download_note(note_id):
    """Download note file"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        note = cursor.fetchone()

        if not note:
            conn.close()
            return jsonify({'success': False, 'error': 'Note not found'}), 404

        cursor.execute("UPDATE notes SET downloads = downloads + 1 WHERE id = ?", (note_id,))
        cursor.execute("""
            INSERT INTO download_history (note_id, user_id) VALUES (?, ?)
        """, (note_id, session['user_id']))
        conn.commit()
        conn.close()

        return send_file(
            note['file_path'],
            as_attachment=True,
            download_name=note['file_name']
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/rate', methods=['POST'])
@login_required
def rate_note():
    """Rate a note"""
    try:
        data = request.get_json()
        note_id = data.get('note_id')
        rating = data.get('rating')
        review = data.get('review', '')

        if not note_id or not rating:
            return jsonify({'success': False, 'error': 'Note ID and rating required'}), 400

        if rating < 1 or rating > 5:
            return jsonify({'success': False, 'error': 'Rating must be between 1 and 5'}), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ratings (note_id, user_id, rating, review)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(note_id, user_id)
            DO UPDATE SET rating = ?, review = ?
        """, (note_id, session['user_id'], rating, review, rating, review))

        cursor.execute("""
            UPDATE notes
            SET rating_sum = (SELECT SUM(rating) FROM ratings WHERE note_id = ?),
                rating_count = (SELECT COUNT(*) FROM ratings WHERE note_id = ?)
            WHERE id = ?
        """, (note_id, note_id, note_id))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Rating submitted successfully!'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/notes/delete/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    """Delete a note"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        note = cursor.fetchone()

        if not note:
            conn.close()
            return jsonify({'success': False, 'error': 'Note not found'}), 404

        if note['uploader_id'] != session['user_id'] and session['role'] != 'admin':
            conn.close()
            return jsonify({'success': False, 'error': 'Permission denied'}), 403

        if os.path.exists(note['file_path']):
            os.remove(note['file_path'])

        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        cursor.execute("DELETE FROM download_history WHERE note_id = ?", (note_id,))
        cursor.execute("DELETE FROM ratings WHERE note_id = ?", (note_id,))

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Note deleted successfully'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ROUTES - USER PROFILE
# ============================================================================

@app.route('/api/user/profile')
@login_required
def get_profile():
    """Get user profile and statistics"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT username, email, created_at, role FROM users WHERE id = ?
        """, (session['user_id'],))
        user = cursor.fetchone()

        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(downloads), 0) as total_downloads
            FROM notes WHERE uploader_id = ?
        """, (session['user_id'],))
        upload_stats = cursor.fetchone()

        cursor.execute("""
            SELECT COUNT(*) FROM download_history WHERE user_id = ?
        """, (session['user_id'],))
        download_count = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            'success': True,
            'profile': {
                'username': user['username'],
                'email': user['email'],
                'member_since': user['created_at'][:10],
                'role': user['role'],
                'total_uploads': upload_stats['count'],
                'total_downloads_of_uploads': upload_stats['total_downloads'],
                'personal_downloads': download_count
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Resource not found'}), 404
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        init_db()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
