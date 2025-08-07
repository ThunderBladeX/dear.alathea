from flask import current_app
from werkzeug.utils import secure_filename
from app.database import execute_query
import os
import uuid

def handle_file_upload(file, folder):
    """Handle file upload using storage service"""
    return upload_file(file, folder)

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
