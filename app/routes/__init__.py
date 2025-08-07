from flask import Flask, g
import os
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['CACHE_FOLDER'] = '/tmp/cache'
    
    # Ensure directory exist
    os.makedirs(app.config['CACHE_FOLDER'], exist_ok=True)

    # Only create local directories in development
    if not app.config.get('IS_PRODUCTION'):
        os.makedirs('static/uploads', exist_ok=True)
        os.makedirs('static/uploads/gallery', exist_ok=True)
        os.makedirs('static/uploads/ocs', exist_ok=True)
        os.makedirs('static/uploads/blog', exist_ok=True)
    
    # Initialize database
    from app.database import init_db
    init_db(app.config)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.gallery import gallery_bp
    from app.routes.ocs import ocs_bp
    from app.routes.blog import blog_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(gallery_bp)
    app.register_blueprint(ocs_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    
    # Register request handlers
    from app.database import get_db, close_db
    app.teardown_appcontext(close_db)
    
    # Register error handlers
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception(error)
        return render_template('error.html', 
                             error_code=500, 
                             error_message="Internal server error"), 500

    @app.errorhandler(404)
    def page_not_found(error):
        app.logger.warning(f"Page not found: {error}")
        return render_template('error.html',
                             error_code=404,
                             error_message="Page not found"), 404

    return app
