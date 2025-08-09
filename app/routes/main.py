from flask import Blueprint, render_template, session, current_app
from markupsafe import Markup
from app.database import execute_query
import os

main_bp = Blueprint(
    'main',
    __name__,
    template_folder='../templates',
    static_folder='../static'
)

@main_bp.route('/')
def index():
    try:
        current_app.logger.info("Starting index route")

        gallery_images = []
        blog_posts = []
        ocs = []
        notifications = []
        
        try:
            current_app.logger.info("Fetching gallery images")
            gallery_images = execute_query('''
                SELECT * FROM gallery_images 
                ORDER BY created_at DESC 
                LIMIT 12
            ''', fetch='all') or []
            current_app.logger.info(f"Found {len(gallery_images)} gallery images")
        except Exception as e:
            current_app.logger.exception(f"Error fetching gallery images: {e}")
            gallery_images = []
        
        try:
            current_app.logger.info("Fetching blog posts")
            blog_posts = execute_query('''
                SELECT * FROM blog_posts 
                ORDER BY created_at DESC 
                LIMIT 6
            ''', fetch='all') or []
            current_app.logger.info(f"Found {len(blog_posts)} blog posts")
        except Exception as e:
            current_app.logger.exception(f"Error fetching blog posts: {e}")
            blog_posts = []
        
        try:
            current_app.logger.info("Fetching OCs")
            ocs = execute_query(
                'SELECT * FROM ocs ORDER BY created_at DESC', 
                fetch='all'
            ) or []
            current_app.logger.info(f"Found {len(ocs)} OCs")
        except Exception as e:
            current_app.logger.exception(f"Error fetching OCs: {e}")
            ocs = []
        
        try:
            if 'user_id' in session:
                current_app.logger.info(f"Fetching notifications for user {session['user_id']}")
                notifications = execute_query('''
                    SELECT * FROM notifications 
                    WHERE user_id = ? AND read = FALSE
                    ORDER BY created_at DESC
                ''', (session['user_id'],), fetch='all') or []
                current_app.logger.info(f"Found {len(notifications)} notifications")
        except Exception as e:
            current_app.logger.exception(f"Error fetching notifications: {e}")
            notifications = []
        
        current_app.logger.info("Rendering template")
        return render_template('index.html', 
                             gallery_images=gallery_images,
                             blog_posts=blog_posts,
                             ocs=ocs,
                             notifications=notifications)
    
    except Exception as e:
        current_app.logger.exception(f"Error in index route: {e}")
        return f"<h1>Error</h1><p>Something went wrong: {str(e)}</p><p><a href='/'>Try again</a></p>", 500

@main_bp.route('/commissions')
def commissions():
    try:
        current_app.logger.info("Accessing commissions page")
        return render_template('commissions.html')
    except Exception as e:
        current_app.logger.exception(f"Error in commissions route: {e}")
        return f"<h1>Error</h1><p>Something went wrong: {str(e)}</p><p><a href='/'>Go home</a></p>", 500

@main_bp.route('/notifications')
def notifications_page():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    notifications = execute_query('''
        SELECT * FROM notifications
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', (session['user_id'],), fetch='all') or []

    return render_template('notifications.html', notifications=notifications)

@main_bp.route('/debug-info')
def debug_info():
    blueprint = current_app.blueprints.get('main')

    if not blueprint:
        return "<h1>Error: 'main' blueprint not found!</h1>"

    absolute_static_path = blueprint.static_folder
    blueprint_path = blueprint.root_path
    css_file_path = os.path.join(absolute_static_path, 'style.css')
    file_exists = os.path.exists(css_file_path)

    all_rules = [str(rule) for rule in current_app.url_map.iter_rules()]
    static_rules = [str(rule) for rule in current_app.url_map.iter_rules('static')]
    main_static_rules = [str(rule) for rule in current_app.url_map.iter_rules('main.static')]

    html = f"""
    <h1>Flask Debug Information</h1>
    
    <h2>Blueprint Path Configuration</h2>
    <p>Current Working Directory: <code>{os.getcwd()}</code></p>
    <p>Blueprint's root_path: <code>{blueprint_path}</code></p>
    <p>Blueprint's configured static_folder (relative): <code>{blueprint.static_url_path}</code></p>
    <p><b>Absolute path Flask calculated for static_folder:</b></p>
    <pre><code>{absolute_static_path}</code></pre>
    
    <h2>File Existence Check</h2>
    <p><b>Full path being checked for style.css:</b></p>
    <pre><code>{css_file_path}</code></pre>
    <p><b>Does the file exist at this path?</b> <span style="font-weight: bold; color: {'green' if file_exists else 'red'};">{file_exists}</span></p>

    <h2>URL Routing Rules</h2>
    <h3>'main.static' Rules:</h3>
    <pre>{Markup('<br>').join(main_static_rules) or 'None Found'}</pre>
    <h3>App-level 'static' Rules:</h3>
    <pre>{Markup('<br>').join(static_rules) or 'None Found'}</pre>
    <h3>All Rules:</h3>
    <pre>{Markup('<br>').join(all_rules)}</pre>
    """
    
    return html
