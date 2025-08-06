from flask import Blueprint, render_template, session
from app.database import execute_query

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get recent gallery images
    gallery_images = execute_query('''
        SELECT * FROM gallery_images 
        ORDER BY created_at DESC 
        LIMIT 12
    ''', fetch='all')
    
    # Get recent blog posts
    blog_posts = execute_query('''
        SELECT * FROM blog_posts 
        ORDER BY created_at DESC 
        LIMIT 6
    ''', fetch='all')
    
    # Get OCs
    ocs = execute_query(
        'SELECT * FROM ocs ORDER BY created_at DESC', 
        fetch='all'
    )
    
    # Get notifications for logged in user
    notifications = []
    if 'user_id' in session:
        notifications = execute_query('''
            SELECT * FROM notifications 
            WHERE user_id = ? AND read = FALSE
            ORDER BY created_at DESC
        ''', (session['user_id'],), fetch='all')
    
    return render_template('index.html', 
                         gallery_images=gallery_images,
                         blog_posts=blog_posts,
                         ocs=ocs,
                         notifications=notifications)

@main_bp.route('/commissions')
def commissions():
    return render_template('commissions.html')
