from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
import json
from datetime import datetime
import requests
from functools import wraps
import uuid

app = Flask(__name__)
app.secret_key = 'cMUHHMCpCiHMjWdbhtkamKIDu'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/uploads/gallery', exist_ok=True)
os.makedirs('static/uploads/ocs', exist_ok=True)
os.makedirs('static/uploads/blog', exist_ok=True)

# Database setup
def init_db():
    conn = sqlite3.connect('site.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Gallery images table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gallery_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            title TEXT NOT NULL,
            caption TEXT,
            tags TEXT,
            width INTEGER,
            height INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # OCs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ocs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            base_image TEXT NOT NULL,
            profile_image TEXT,
            description TEXT,
            age TEXT,
            personality TEXT,
            backstory TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # OC clothing items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS oc_clothing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            oc_id INTEGER,
            item_name TEXT NOT NULL,
            filename TEXT NOT NULL,
            category TEXT,
            z_index INTEGER DEFAULT 1,
            FOREIGN KEY (oc_id) REFERENCES ocs (id)
        )
    ''')
    
    # Blog posts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            summary TEXT,
            featured_image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content_type TEXT NOT NULL,
            content_id INTEGER NOT NULL,
            parent_id INTEGER,
            content TEXT NOT NULL,
            country TEXT,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0,
            flagged BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (parent_id) REFERENCES comments (id)
        )
    ''')
    
    # Comment votes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comment_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            comment_id INTEGER,
            vote_type TEXT CHECK(vote_type IN ('up', 'down')),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (comment_id) REFERENCES comments (id),
            UNIQUE(user_id, comment_id)
        )
    ''')
    
    # Notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            link TEXT,
            read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('site.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user_country(ip_address):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}')
        data = response.json()
        return data.get('country', 'Unknown')
    except:
        return 'Unknown'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        conn = get_db_connection()
        user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        
        if not user or not user['is_admin']:
            flash('Admin access required')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    conn = get_db_connection()
    
    # Get recent gallery images
    gallery_images = conn.execute('''
        SELECT * FROM gallery_images 
        ORDER BY created_at DESC 
        LIMIT 12
    ''').fetchall()
    
    # Get recent blog posts
    blog_posts = conn.execute('''
        SELECT * FROM blog_posts 
        ORDER BY created_at DESC 
        LIMIT 6
    ''').fetchall()
    
    # Get OCs
    ocs = conn.execute('SELECT * FROM ocs ORDER BY created_at DESC').fetchall()
    
    # Get notifications for logged in user
    notifications = []
    if 'user_id' in session:
        notifications = conn.execute('''
            SELECT * FROM notifications 
            WHERE user_id = ? AND read = FALSE
            ORDER BY created_at DESC
        ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                         gallery_images=gallery_images,
                         blog_posts=blog_posts,
                         ocs=ocs,
                         notifications=notifications)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            # Update IP address
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            conn.execute('UPDATE users SET ip_address = ? WHERE id = ?', (ip_address, user['id']))
            conn.commit()
            conn.close()
            
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if len(username) < 3 or len(password) < 6:
            flash('Username must be at least 3 characters and password at least 6 characters')
            return render_template('register.html')
        
        conn = get_db_connection()
        existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
        
        if existing_user:
            flash('Username already exists')
            conn.close()
            return render_template('register.html')
        
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        password_hash = generate_password_hash(password)
        
        conn.execute('''
            INSERT INTO users (username, password_hash, ip_address)
            VALUES (?, ?, ?)
        ''', (username, password_hash, ip_address))
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/gallery')
def gallery():
    conn = get_db_connection()
    images = conn.execute('SELECT * FROM gallery_images ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('gallery.html', images=images)

@app.route('/gallery/<int:image_id>')
def gallery_image(image_id):
    conn = get_db_connection()
    image = conn.execute('SELECT * FROM gallery_images WHERE id = ?', (image_id,)).fetchone()
    
    if not image:
        return redirect(url_for('gallery'))
    
    # Get comments
    comments = conn.execute('''
        SELECT c.*, u.username 
        FROM comments c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.content_type = 'gallery' AND c.content_id = ? AND c.parent_id IS NULL
        ORDER BY c.created_at DESC
    ''', (image_id,)).fetchall()
    
    # Get replies for each comment
    for comment in comments:
        comment['replies'] = conn.execute('''
            SELECT c.*, u.username 
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.parent_id = ?
            ORDER BY c.created_at ASC
        ''', (comment['id'],)).fetchall()
    
    conn.close()
    return render_template('gallery_image.html', image=image, comments=comments)

@app.route('/ocs')
def ocs():
    conn = get_db_connection()
    ocs = conn.execute('SELECT * FROM ocs ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('ocs.html', ocs=ocs)

@app.route('/oc/<int:oc_id>')
def oc_detail(oc_id):
    conn = get_db_connection()
    oc = conn.execute('SELECT * FROM ocs WHERE id = ?', (oc_id,)).fetchone()
    
    if not oc:
        return redirect(url_for('ocs'))
    
    # Get clothing items
    clothing_items = conn.execute('''
        SELECT * FROM oc_clothing 
        WHERE oc_id = ? 
        ORDER BY z_index ASC, category ASC
    ''', (oc_id,)).fetchall()
    
    # Get comments
    comments = conn.execute('''
        SELECT c.*, u.username 
        FROM comments c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.content_type = 'oc' AND c.content_id = ? AND c.parent_id IS NULL
        ORDER BY c.created_at DESC
    ''', (oc_id,)).fetchall()
    
    conn.close()
    return render_template('oc_detail.html', oc=oc, clothing_items=clothing_items, comments=comments)

@app.route('/blog')
def blog():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM blog_posts ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('blog.html', posts=posts)

@app.route('/blog/<int:post_id>')
def blog_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM blog_posts WHERE id = ?', (post_id,)).fetchone()
    
    if not post:
        return redirect(url_for('blog'))
    
    # Get comments
    comments = conn.execute('''
        SELECT c.*, u.username 
        FROM comments c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.content_type = 'blog' AND c.content_id = ? AND c.parent_id IS NULL
        ORDER BY c.created_at DESC
    ''', (post_id,)).fetchall()
    
    conn.close()
    return render_template('blog_post.html', post=post, comments=comments)

@app.route('/commissions')
def commissions():
    return render_template('commissions.html')

@app.route('/notifications')
@login_required
def notifications():
    conn = get_db_connection()
    notifications = conn.execute('''
        SELECT * FROM notifications 
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (session['user_id'],)).fetchall()
    
    # Mark all as read
    conn.execute('UPDATE notifications SET read = TRUE WHERE user_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    
    return render_template('notifications.html', notifications=notifications)

@app.route('/calculate_commission', methods=['POST'])
def calculate_commission():
    data = request.json
    
    base_prices = {
        'bust': 25,
        'half': 40,
        'full': 60
    }
    
    base_price = base_prices.get(data['type'], 25)
    total = base_price
    
    # Apply modifiers
    if data.get('multiple_characters'):
        total *= 1.3
    
    if data.get('nsfw'):
        total *= 1.25
    
    if data.get('rush'):
        total *= 1.5
    
    if data.get('unrendered'):
        total *= 0.5
    
    if data.get('indonesian_discount'):
        total *= 0.625
    
    return jsonify({
        'base_price': base_price,
        'total_price': round(total, 2)
    })

@app.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    content_type = request.form['content_type']
    content_id = request.form['content_id']
    comment_text = request.form['comment']
    parent_id = request.form.get('parent_id')
    
    if not comment_text.strip():
        flash('Comment cannot be empty')
        return redirect(request.referrer)
    
    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
    country = get_user_country(ip_address)
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO comments (user_id, content_type, content_id, parent_id, content, country)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], content_type, content_id, parent_id, comment_text, country))
    conn.commit()
    conn.close()
    
    return redirect(request.referrer)

# Admin routes
@app.route('/admin')
@admin_required
def admin():
    return render_template('admin.html')

@app.route('/admin/upload', methods=['GET', 'POST'])
@admin_required
def admin_upload():
    if request.method == 'POST':
        upload_type = request.form['type']
        
        if upload_type == 'gallery':
            file = request.files['file']
            title = request.form['title']
            caption = request.form.get('caption', '')
            tags = request.form.get('tags', '')
            
            if file and file.filename:
                filename = secure_filename(file.filename)
                filename = f"{uuid.uuid4()}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'gallery', filename))
                
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO gallery_images (filename, title, caption, tags)
                    VALUES (?, ?, ?, ?)
                ''', (filename, title, caption, tags))
                conn.commit()
                conn.close()
                
                flash('Gallery image uploaded successfully!')
        
        elif upload_type == 'blog':
            title = request.form['title']
            content = request.form['content']
            summary = request.form.get('summary', '')
            
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO blog_posts (title, content, summary)
                VALUES (?, ?, ?)
            ''', (title, content, summary))
            conn.commit()
            conn.close()
            
            flash('Blog post created successfully!')
    
    return render_template('admin_upload.html')

@app.route('/vote_comment', methods=['POST'])
@login_required
def vote_comment():
    data = request.json
    comment_id = data['comment_id']
    vote_type = data['vote_type']
    
    conn = get_db_connection()
    
    # Check if user already voted
    existing_vote = conn.execute('''
        SELECT vote_type FROM comment_votes 
        WHERE user_id = ? AND comment_id = ?
    ''', (session['user_id'], comment_id)).fetchone()
    
    if existing_vote:
        if existing_vote['vote_type'] == vote_type:
            # Remove vote
            conn.execute('DELETE FROM comment_votes WHERE user_id = ? AND comment_id = ?', 
                        (session['user_id'], comment_id))
        else:
            # Change vote
            conn.execute('UPDATE comment_votes SET vote_type = ? WHERE user_id = ? AND comment_id = ?',
                        (vote_type, session['user_id'], comment_id))
    else:
        # Add new vote
        conn.execute('INSERT INTO comment_votes (user_id, comment_id, vote_type) VALUES (?, ?, ?)',
                    (session['user_id'], comment_id, vote_type))
    
    # Update comment vote counts
    upvotes = conn.execute('SELECT COUNT(*) as count FROM comment_votes WHERE comment_id = ? AND vote_type = "up"',
                          (comment_id,)).fetchone()['count']
    downvotes = conn.execute('SELECT COUNT(*) as count FROM comment_votes WHERE comment_id = ? AND vote_type = "down"',
                            (comment_id,)).fetchone()['count']
    
    conn.execute('UPDATE comments SET upvotes = ?, downvotes = ? WHERE id = ?',
                (upvotes, downvotes, comment_id))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'upvotes': upvotes,
        'downvotes': downvotes
    })

@app.route('/admin/export')
@admin_required
def admin_export():
    conn = get_db_connection()
    
    # Export all data
    export_data = {
        'gallery_images': [dict(row) for row in conn.execute('SELECT * FROM gallery_images').fetchall()],
        'ocs': [dict(row) for row in conn.execute('SELECT * FROM ocs').fetchall()],
        'oc_clothing': [dict(row) for row in conn.execute('SELECT * FROM oc_clothing').fetchall()],
        'blog_posts': [dict(row) for row in conn.execute('SELECT * FROM blog_posts').fetchall()],
        'comments': [dict(row) for row in conn.execute('SELECT * FROM comments').fetchall()],
        'export_timestamp': datetime.now().isoformat()
    }
    
    conn.close()
    
    return jsonify(export_data)

@app.route('/admin/import', methods=['POST'])
@admin_required
def admin_import():
    try:
        file = request.files['import_file']
        data = json.loads(file.read().decode('utf-8'))
        
        conn = get_db_connection()
        
        # Import data (this is a simplified version - you might want to add validation)
        for table, records in data.items():
            if table == 'export_timestamp':
                continue
                
            for record in records:
                if table == 'gallery_images':
                    conn.execute('''
                        INSERT OR REPLACE INTO gallery_images 
                        (id, filename, title, caption, tags, width, height, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (record['id'], record['filename'], record['title'], 
                         record.get('caption'), record.get('tags'),
                         record.get('width'), record.get('height'), record['created_at']))
                # Add similar blocks for other tables...
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/upload', methods=['GET', 'POST'])
@admin_required
def admin_upload():
    if request.method == 'POST':
        upload_type = request.form['type']
        
        if upload_type == 'gallery':
            file = request.files['file']
            title = request.form['title']
            caption = request.form.get('caption', '')
            tags = request.form.get('tags', '')
            
            if file and file.filename:
                filename = secure_filename(file.filename)
                filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'gallery', filename)
                file.save(filepath)
                
                # Get image dimensions (optional)
                try:
                    from PIL import Image
                    with Image.open(filepath) as img:
                        width, height = img.size
                except:
                    width, height = None, None
                
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO gallery_images (filename, title, caption, tags, width, height)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (filename, title, caption, tags, width, height))
                conn.commit()
                conn.close()
                
                flash('Gallery image uploaded successfully!')
        
        elif upload_type == 'oc':
            name = request.form['name']
            age = request.form.get('age', '')
            personality = request.form.get('personality', '')
            description = request.form.get('description', '')
            backstory = request.form.get('backstory', '')
            
            base_image_filename = None
            profile_image_filename = None
            
            if 'base_image' in request.files and request.files['base_image'].filename:
                base_file = request.files['base_image']
                base_image_filename = f"{uuid.uuid4()}_{secure_filename(base_file.filename)}"
                base_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'ocs', base_image_filename))
            
            if 'profile_image' in request.files and request.files['profile_image'].filename:
                profile_file = request.files['profile_image']
                profile_image_filename = f"{uuid.uuid4()}_{secure_filename(profile_file.filename)}"
                profile_file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'ocs', profile_image_filename))
            
            if base_image_filename:  # Only create OC if base image is provided
                conn = get_db_connection()
                conn.execute('''
                    INSERT INTO ocs (name, base_image, profile_image, description, age, personality, backstory)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, base_image_filename, profile_image_filename, description, age, personality, backstory))
                conn.commit()
                conn.close()
                
                flash('OC created successfully!')
            else:
                flash('Base image is required for OC creation.')
        
        elif upload_type == 'blog':
            title = request.form['title']
            content = request.form['content']
            summary = request.form.get('summary', '')
            
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO blog_posts (title, content, summary)
                VALUES (?, ?, ?)
            ''', (title, content, summary))
            conn.commit()
            conn.close()
            
            flash('Blog post created successfully!')
    
    # Get stats for display
    conn = get_db_connection()
    stats = {
        'gallery_count': conn.execute('SELECT COUNT(*) as count FROM gallery_images').fetchone()['count'],
        'oc_count': conn.execute('SELECT COUNT(*) as count FROM ocs').fetchone()['count'],
        'blog_count': conn.execute('SELECT COUNT(*) as count FROM blog_posts').fetchone()['count'],
        'comment_count': conn.execute('SELECT COUNT(*) as count FROM comments').fetchone()['count']
    }
    conn.close()
    
    return render_template('admin_upload.html', stats=stats)

# Create admin user on first run
def create_admin_user():
    conn = get_db_connection()
    admin_exists = conn.execute('SELECT id FROM users WHERE is_admin = TRUE').fetchone()
    
    if not admin_exists:
        # Get admin credentials from environment variables
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        password_hash = generate_password_hash(admin_password)
        conn.execute('''
            INSERT INTO users (username, password_hash, is_admin)
            VALUES (?, ?, ?)
        ''', (admin_username, password_hash, True))
        conn.commit()
        
        if admin_password == 'admin123':
            print("⚠️  WARNING: Using default admin password! Set ADMIN_PASSWORD environment variable!")
        print(f"Created admin user: {admin_username}")
    
    conn.close()

# Add clothing item reordering route
@app.route('/admin/reorder_clothing', methods=['POST'])
@admin_required
def reorder_clothing():
    data = request.json
    oc_id = data['oc_id']
    clothing_order = data['clothing_order']  # List of {id, z_index}
    
    conn = get_db_connection()
    for item in clothing_order:
        conn.execute('UPDATE oc_clothing SET z_index = ? WHERE id = ? AND oc_id = ?', 
                    (item['z_index'], item['id'], oc_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# Add image optimization route
@app.route('/api/optimize_image/<path:filename>')
def optimize_image(filename):
    """Serve optimized images with WebP conversion and caching"""
    try:
        # Check if WebP is supported
        accept_header = request.headers.get('Accept', '')
        supports_webp = 'image/webp' in accept_header
        
        # Parse size parameter
        size = request.args.get('size', 'original')
        quality = int(request.args.get('quality', '85'))
        
        # Size presets for performance
        size_presets = {
            'thumb': (150, 150),
            'small': (300, 300),
            'medium': (600, 600),
            'large': (1200, 1200),
            'original': None
        }
        
        target_size = size_presets.get(size)
        
        # Generate cache filename
        base_name = os.path.splitext(filename)[0]
        ext = '.webp' if supports_webp else os.path.splitext(filename)[1]
        cache_name = f"{base_name}_{size}_q{quality}{ext}"
        cache_path = os.path.join('static/cache', cache_name)
        
        # Serve from cache if exists
        if os.path.exists(cache_path):
            return send_file(cache_path)
        
        # Load original image
        original_path = os.path.join('static', filename)
        if not os.path.exists(original_path):
            return '', 404
            
        from PIL import Image, ImageOps
        
        with Image.open(original_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Auto-orient based on EXIF
            img = ImageOps.exif_transpose(img)
            
            # Resize if needed
            if target_size:
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Ensure cache directory exists
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            
            # Save optimized image
            if supports_webp:
                img.save(cache_path, 'WebP', quality=quality, optimize=True)
            else:
                img.save(cache_path, quality=quality, optimize=True)
        
        return send_file(cache_path)
        
    except Exception as e:
        # Fallback to original
        return send_file(os.path.join('static', filename))

# Add database connection pooling and caching
import threading
from contextlib import contextmanager

class DatabasePool:
    def __init__(self, database_path, pool_size=5):
        self.database_path = database_path
        self.pool = []
        self.pool_size = pool_size
        self.lock = threading.Lock()
        
    @contextmanager
    def get_connection(self):
        with self.lock:
            if self.pool:
                conn = self.pool.pop()
            else:
                conn = sqlite3.connect(self.database_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
        
        try:
            yield conn
        finally:
            with self.lock:
                if len(self.pool) < self.pool_size:
                    self.pool.append(conn)
                else:
                    conn.close()

# Initialize connection pool
db_pool = DatabasePool('site.db')

# Replace get_db_connection with pooled version
def get_db_connection():
    return sqlite3.connect('site.db')  # Keep simple for now, use pool in production

# Add performance middleware
@app.before_request
def before_request():
    # Add performance timing
    request.start_time = datetime.now()

@app.after_request
def after_request(response):
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Add caching headers for static content
    if request.endpoint == 'static':
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
    elif request.endpoint in ['optimize_image']:
        response.headers['Cache-Control'] = 'public, max-age=86400'  # 1 day
    
    # Add performance timing header
    if hasattr(request, 'start_time'):
        duration = (datetime.now() - request.start_time).total_seconds()
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
    
    return response

# Add compression support
from flask import gzip

@app.after_request
def compress_response(response):
    accept_encoding = request.headers.get('Accept-Encoding', '')
    
    if ('gzip' in accept_encoding.lower() and 
        response.status_code < 300 and 
        response.content_length and response.content_length > 500 and
        'Content-Encoding' not in response.headers):
        
        response.data = gzip.compress(response.data)
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = len(response.data)
    
    return response

if __name__ == '__main__':
    init_db()
    create_admin_user()
    app.run(debug=True)
