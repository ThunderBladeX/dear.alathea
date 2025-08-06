from flask import Blueprint, render_template, request, redirect, url_for, session
from app.database import execute_query
from app.services.comment_service import get_comments_with_replies

gallery_bp = Blueprint('gallery', __name__, url_prefix='/gallery')

@gallery_bp.route('/')
def index():
    images = execute_query(
        'SELECT * FROM gallery_images ORDER BY created_at DESC', 
        fetch='all'
    )
    return render_template('gallery.html', images=images)

@gallery_bp.route('/<int:image_id>')
def image_detail(image_id):
    image = execute_query(
        'SELECT * FROM gallery_images WHERE id = ?', 
        (image_id,), 
        fetch='one'
    )
    
    if not image:
        return redirect(url_for('gallery.index'))
    
    # Get comments using optimized service
    comments = get_comments_with_replies('gallery', image_id)
    
    return render_template('gallery_image.html', image=image, comments=comments)
