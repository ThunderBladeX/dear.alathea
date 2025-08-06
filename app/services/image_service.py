from flask import send_file, current_app
import os

def optimize_image(filename, args):
    """Handle image optimization and serving"""
    try:
        from PIL import Image, ImageOps
        import requests
        
        # Check WebP support
        accept_header = request.headers.get('Accept', '')
        supports_webp = 'image/webp' in accept_header
        
        # Parse parameters
        size = args.get('size', 'original')
        quality = int(args.get('quality', '85'))
        
        # Size presets
        size_presets = {
            'thumb': (150, 150),
            'small': (300, 300),
            'medium': (600, 600),
            'large': (1200, 1200),
            'original': None
        }
        
        target_size = size_presets.get(size)
        
        # Generate cache filename
        base_name = os.path.splitext(filename)[0]
        ext = '.webp' if supports_webp else os.path.splitext(filename)[1]
        cache_name = f"{base_name}_{size}_q{quality}{ext}"
        cache_path = os.path.join(current_app.config['CACHE_FOLDER'], cache_name)
        
        # Serve from cache if exists
        if os.path.exists(cache_path):
            return send_file(cache_path)
        
        # Load original image
        original_path = os.path.join('static', filename)
        if not os.path.exists(original_path):
            return '', 404
        
        with Image.open(original_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Auto-orient based on EXIF
            img = ImageOps.exif_transpose(img)
            
            # Resize if needed
            if target_size:
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Ensure cache directory exists
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            
            # Save optimized image
            if supports_webp:
                img.save(cache_path, 'WebP', quality=quality, optimize=True)
            else:
                img.save(cache_path, quality=quality, optimize=True)
        
        return send_file(cache_path)
        
    except Exception as e:
        # Fallback to original
        return send_file(os.path.join('static', filename))
