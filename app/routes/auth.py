from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.auth import authenticate_user, create_user

auth_bp = Blueprint('auth', __name__)

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
