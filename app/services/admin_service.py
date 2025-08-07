from flask import current_app
from werkzeug.utils import secure_filename
from app.database import execute_query
import os
import uuid

def handle_file_upload(file, folder):
    """Handle file upload with secure naming"""
    if not file or not file.filename:
        raise ValueError("No file provided")

    filename = secure_filename(file.filename)
    filename = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(filepath, exist_ok=True) # Ensure folder exists
    filepath = os.path.join(filepath, filename)


    file.save(filepath)
    return filename

def get_admin_stats():
    """Get statistics for admin dashboard"""
    stats = {}

    try:
        stats['gallery_count'] = execute_query(
            'SELECT COUNT(*) as count FROM gallery_images',
            fetch='one'
        )['count']

        stats['oc_count'] = execute_query(
            'SELECT COUNT(*) as count FROM ocs',
            fetch='one'
        )['count']

        stats['blog_count'] = execute_query(
            'SELECT COUNT(*) as count FROM blog_posts',
            fetch='one'
        )['count']

        stats['comment_count'] = execute_query(
            'SELECT COUNT(*) as count FROM comments',
            fetch='one'
        )['count']
    except Exception as e:
        current_app.logger.exception(f"Error getting admin stats: {e}")
        return None

    return stats
