from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.auth import authenticate_user, create_user
from app.database import execute_query

auth_bp = Blueprint(
    'auth',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            
            # Update IP address
            ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            execute_query(
                'UPDATE users SET ip_address = ? WHERE id = ?', 
                (ip_address, user['id'])
            )
            
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if len(username) < 3 or len(password) < 6:
            flash('Username must be at least 3 characters and password at least 6 characters')
            return render_template('register.html')
        
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        if create_user(username, password, ip_address):
            flash('Registration successful! Please log in.')
            return redirect(url_for('auth.login'))
        else:
            flash('Username already exists')
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))
