from flask import current_app
import requests
import uuid
import os
from werkzeug.utils import secure_filename

def upload_file(file, folder):
    """Upload file to appropriate storage (Vercel Blob or local)"""
    if not file or not file.filename:
        raise ValueError("No file provided")
    
    # Generate secure filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    config = current_app.config
    
    if config.get('USE_BLOB_STORAGE'):
        # Upload to Vercel Blob
        return upload_to_blob(file, folder, unique_filename)
    else:
        # Save locally for development
        return save_locally(file, folder, unique_filename)

def upload_to_blob(file, folder, filename):
    """Upload file to Vercel Blob storage"""
    config = current_app.config
    blob_token = config.get('BLOB_READ_WRITE_TOKEN')
    
    if not blob_token:
        raise ValueError("Blob storage token not configured")
    
    # Vercel Blob API endpoint
    blob_url = f"https://blob.vercel-storage.com/upload"
    
    # Prepare the file data
    file.seek(0)  # Reset file pointer
    files = {
        'file': (filename, file.read(), file.content_type)
    }
    
    headers = {
        'Authorization': f'Bearer {blob_token}',
    }
    
    # Upload to Vercel Blob
    response = requests.post(blob_url, files=files, headers=headers)
    
    if response.status_code != 200:
        raise ValueError(f"Blob upload failed: {response.text}")
    
    data = response.json()
    
    # Return the blob URL
    return data['url']

def save_locally(file, folder, filename):
    """Save file locally for development"""
    filepath = os.path.join('static/uploads', folder, filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    file.save(filepath)
    
    # Return local path
    return f"uploads/{folder}/{filename}"

def get_file_url(stored_path):
    """Get the full URL for a stored file"""
    if stored_path.startswith('https://'):
        # It's already a full Blob URL
        return stored_path
    else:
        # It's a local path, add static prefix
        from flask import url_for
        return url_for('static', filename=stored_path)

def optimize_image_url(stored_path, size='medium', quality=85):
    """Generate optimized image URL"""
    if stored_path.startswith('https://'):
        # Vercel automatically optimizes images from Blob storage
        return f"{stored_path}?w={get_size_width(size)}&q={quality}"
    else:
        # For local development, use our optimization API
        from flask import url_for
        return url_for('api.optimize_image_api', filename=stored_path, size=size, quality=quality)

def get_size_width(size):
    """Get pixel width for size preset"""
    sizes = {
        'thumb': 150,
        'small': 300,
        'medium': 600,
        'large': 1200
    }
    return sizes.get(size, 600)
