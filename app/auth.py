from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, current_app
from app.database import execute_query
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        user = execute_query(
            'SELECT is_admin FROM users WHERE id = ?', 
            (session['user_id'],), 
            fetch='one'
        )
        
        if not user or not user['is_admin']:
            flash('Admin access required')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def authenticate_user(username, password):
    """Authenticate user and return user data"""
    user = execute_query(
        'SELECT * FROM users WHERE username = ?', 
        (username,), 
        fetch='one'
    )
    
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def create_user(username, password, ip_address):
    """Create new user account"""
    password_hash = generate_password_hash(password)

    try:
        execute_query('''
            INSERT INTO users (username, password_hash, ip_address)
            VALUES (?, ?, ?)
        ''', (username, password_hash, ip_address))
        return True
    except sqlite3.IntegrityError as e:
        current_app.logger.error(f"Error creating user: {e}")  # Log the error
        return False
    except Exception as e:
        current_app.logger.exception(f"Unexpected error creating user: {e}") #Include traceback
        return False

def create_admin_user(config):
    """Create admin user if doesn't exist"""
    admin_exists = execute_query(
        'SELECT id FROM users WHERE is_admin = TRUE', 
        fetch='one'
    )
    
    if not admin_exists:
        admin_username = config.get('ADMIN_USERNAME', 'admin')
        admin_password = config.get('ADMIN_PASSWORD', 'admin123')
        password_hash = generate_password_hash(admin_password)
        
        execute_query('''
            INSERT INTO users (username, password_hash, is_admin)
            VALUES (?, ?, ?)
        ''', (admin_username, password_hash, True))
        
        print(f"Created admin user: {admin_username}")
        if admin_password == 'admin123':
            print("⚠️  WARNING: Using default admin password! Set ADMIN_PASSWORD environment variable!")
