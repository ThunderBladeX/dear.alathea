from flask import Blueprint, render_template, session, current_app
from app.database import execute_query

main_bp = Blueprint(
    'main',
    __name__,
      # Go up one level from 'routes' to 'app' then into 'templates' or 'static'
    template_folder='../templates',
    static_folder='../static'
)

@main_bp.route('/')
def index():
    try:
        current_app.logger.info("Starting index route")
        
        # Initialize empty data
        gallery_images = []
        blog_posts = []
        ocs = []
        notifications = []
        
        try:
            # Get recent gallery images
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
            # Get recent blog posts
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
            # Get OCs
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
            # Get notifications for logged in user
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
        # Return a simple error page instead of crashing
        return f"<h1>Error</h1><p>Something went wrong: {str(e)}</p><p><a href='/'>Try again</a></p>", 500

@main_bp.route('/commissions')
def commissions():
    try:
        current_app.logger.info("Accessing commissions page")
        return render_template('commissions.html')
    except Exception as e:
        current_app.logger.exception(f"Error in commissions route: {e}")
        return f"<h1>Error</h1><p>Something went wrong: {str(e)}</p><p><a href='/'>Go home</a></p>", 500
