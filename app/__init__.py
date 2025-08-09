from whitenoise import WhiteNoise
from flask import Flask, g, render_template
import os
from config import Config

def create_app():
    app = Flask(__name__)

    print(f"App template folder: {app.template_folder}")
    print(f"App root path: {app.root_path}")
    print(f"Full template path: {os.path.join(app.root_path, app.template_folder)}")

    template_dir = os.path.join(app.root_path, app.template_folder)
    if os.path.exists(template_dir):
        print(f"Files in template directory: {os.listdir(template_dir)}")
    else:
        print(f"Template directory does not exist: {template_dir}")

    app.wsgi_app = WhiteNoise(app.wsgi_app, root='app/static/', prefix='static/')

    app.config.from_object(Config)
    app.config['CACHE_FOLDER'] = '/tmp/cache'

    os.makedirs(app.config['CACHE_FOLDER'], exist_ok=True)
    if not app.config.get('IS_PRODUCTION'):
        try:
            base_static_path = app.static_folder 
            os.makedirs(os.path.join(base_static_path, 'uploads'), exist_ok=True)
            os.makedirs(os.path.join(base_static_path, 'uploads', 'gallery'), exist_ok=True)
            os.makedirs(os.path.join(base_static_path, 'uploads', 'ocs'), exist_ok=True)
            os.makedirs(os.path.join(base_static_path, 'uploads', 'blog'), exist_ok=True)
        except Exception as e:
            app.logger.warning(f"Could not create upload directories: {e}")

    try:
        from app.database import init_db, close_db
        with app.app_context():
            init_db(app.config)
        app.logger.info("Database initialized successfully")
    except Exception as e:
        app.logger.exception(f"Error initializing database: {e}")

    try:
        from app.routes.main import main_bp
        app.register_blueprint(main_bp)
        app.logger.info("Main blueprint registered")

        try:
            from app.routes.auth import auth_bp
            app.register_blueprint(auth_bp)
            app.logger.info("Auth blueprint registered")
        except ImportError as e:
            app.logger.warning(f"Auth blueprint not found: {e}")
        
        try:
            from app.routes.gallery import gallery_bp
            app.register_blueprint(gallery_bp)
            app.logger.info("Gallery blueprint registered")
        except ImportError as e:
            app.logger.warning(f"Gallery blueprint not found: {e}")
        
        try:
            from app.routes.ocs import ocs_bp
            app.register_blueprint(ocs_bp)
            app.logger.info("OCs blueprint registered")
        except ImportError as e:
            app.logger.warning(f"OCs blueprint not found: {e}")
        
        try:
            from app.routes.blog import blog_bp
            app.register_blueprint(blog_bp)
            app.logger.info("Blog blueprint registered")
        except ImportError as e:
            app.logger.warning(f"Blog blueprint not found: {e}")
        
        try:
            from app.routes.admin import admin_bp
            app.register_blueprint(admin_bp)
            app.logger.info("Admin blueprint registered")
        except ImportError as e:
            app.logger.warning(f"Admin blueprint not found: {e}")
        
        try:
            from app.routes.api import api_bp
            app.register_blueprint(api_bp)
            app.logger.info("API blueprint registered")
        except ImportError as e:
            app.logger.warning(f"API blueprint not found: {e}")
            
    except Exception as e:
        app.logger.exception(f"Error registering blueprints: {e}")
        raise

    try:
        from app.database import close_db
        app.teardown_appcontext(close_db)
    except Exception as e:
        app.logger.warning(f"Could not register database teardown: {e}")

    try:
        from app.services.storage_service import optimize_image_url, get_file_url

        @app.template_global()
        def get_optimized_url(stored_path, size='medium', quality=85):
            return optimize_image_url(stored_path, size, quality)

        @app.template_global()
        def get_file_url_global(stored_path):
            return get_file_url(stored_path)
        
        app.logger.info("Storage service template globals registered")
    except ImportError as e:
        app.logger.warning(f"Storage service not available: {e}")

        @app.template_global()
        def get_optimized_url(stored_path, size='medium', quality=85):
            return f"/static/uploads/{stored_path}"

        @app.template_global()
        def get_file_url_global(stored_path):
            return f"/static/uploads/{stored_path}"
        
        app.logger.info("Fallback template globals registered")

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception(f"500 error: {error}")
        try:
            return render_template('error.html', 
                                 error_code=500, 
                                 error_message="Internal server error"), 500
        except Exception as template_error:
            app.logger.exception(f"Error rendering error template: {template_error}")
            return f"<h1>500 Internal Server Error</h1><p>{str(error)}</p>", 500

    @app.errorhandler(404)
    def page_not_found(error):
        app.logger.warning(f"404 error: {error}")
        try:
            return render_template('error.html',
                                 error_code=404,
                                 error_message="Page not found"), 404
        except Exception as template_error:
            app.logger.exception(f"Error rendering 404 template: {template_error}")
            return f"<h1>404 Page Not Found</h1><p>{str(error)}</p>", 404

    app.logger.info("Flask app created successfully")
    return app
