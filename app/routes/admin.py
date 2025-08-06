from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from app.auth import admin_required
from app.database import execute_query
from app.services.admin_service import handle_file_upload, get_admin_stats
import os
import uuid

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/upload', methods=['GET', 'POST'])
@admin_required
def upload():
    if request.method == 'POST':
        upload_type = request.form['type']
        
        try:
            if upload_type == 'gallery':
                handle_gallery_upload(request)
                flash('Gallery image uploaded successfully!')
            elif upload_type == 'oc':
                handle_oc_upload(request)
                flash('Character created successfully!')
            elif upload_type == 'blog':
                handle_blog_upload(request)
                flash('Blog post created successfully!')
            elif upload_type == 'clothing':
                handle_clothing_upload(request)
                flash('Clothing item added successfully!')
        except Exception as e:
            flash(f'Upload failed: {str(e)}')
    
    stats = get_admin_stats()
    return render_template('admin_upload.html', stats=stats)

def handle_gallery_upload(request):
    """Handle gallery image upload"""
    file = request.files['file']
    title = request.form['title']
    caption = request.form.get('caption', '')
    tags = request.form.get('tags', '')
    
    if not file or not file.filename:
        raise ValueError("No file provided")
    
    filename = handle_file_upload(file, 'gallery')
    
    # Get image dimensions
    width, height = get_image_dimensions(
        os.path.join(current_app.config['UPLOAD_FOLDER'], 'gallery', filename)
    )
    
    execute_query('''
        INSERT INTO gallery_images (filename, title, caption, tags, width, height)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (filename, title, caption, tags, width, height))

def handle_oc_upload(request):
    """Handle OC creation"""
    name = request.form['name']
    age = request.form.get('age', '')
    personality = request.form.get('personality', '')
    description = request.form.get('description', '')
    backstory = request.form.get('backstory', '')
    
    base_image_filename = None
    profile_image_filename = None
    
    if 'base_image' in request.files and request.files['base_image'].filename:
        base_image_filename = handle_file_upload(request.files['base_image'], 'ocs')
    
    if 'profile_image' in request.files and request.files['profile_image'].filename:
        profile_image_filename = handle_file_upload(request.files['profile_image'], 'ocs')
    
    if not base_image_filename:
        raise ValueError("Base image is required")
    
    execute_query('''
        INSERT INTO ocs (name, base_image, profile_image, description, age, personality, backstory)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, base_image_filename, profile_image_filename, description, age, personality, backstory))

def handle_blog_upload(request):
    """Handle blog post creation"""
    title = request.form['title']
    content = request.form['content']
    summary = request.form.get('summary', '')
    
    featured_image_filename = None
    if 'featured_image' in request.files and request.files['featured_image'].filename:
        featured_image_filename = handle_file_upload(request.files['featured_image'], 'blog')
    
    execute_query('''
        INSERT INTO blog_posts (title, content, summary, featured_image)
        VALUES (?, ?, ?, ?)
    ''', (title, content, summary, featured_image_filename))

def handle_clothing_upload(request):
    """Handle clothing item upload"""
    oc_id = request.form['oc_id']
    item_name = request.form['item_name']
    category = request.form['category']
    z_index = request.form.get('z_index', 1)
    
    if 'clothing_file' not in request.files:
        raise ValueError("No clothing file provided")
    
    filename = handle_file_upload(request.files['clothing_file'], 'ocs')
    
    execute_query('''
        INSERT INTO oc_clothing (oc_id, item_name, filename, category, z_index)
        VALUES (?, ?, ?, ?, ?)
    ''', (oc_id, item_name, filename, category, z_index))

def get_image_dimensions(filepath):
    """Get image dimensions using PIL"""
    try:
        from PIL import Image
        with Image.open(filepath) as img:
            return img.size
    except:
        return None, None
