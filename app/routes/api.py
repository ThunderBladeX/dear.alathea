from flask import Blueprint, request, jsonify, session, send_file
from app.auth import login_required, admin_required
from app.database import execute_query
from app.services.comment_service import add_comment, vote_comment
from app.services.image_service import optimize_image
import os

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/add_comment', methods=['POST'])
@login_required
def add_comment_api():
    content_type = request.form['content_type']
    content_id = request.form['content_id']
    comment_text = request.form['comment']
    parent_id = request.form.get('parent_id')
    
    if not comment_text.strip():
        return jsonify({'success': False, 'message': 'Comment cannot be empty'})
    
    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
    country = get_user_country(ip_address)
    
    add_comment(session['user_id'], content_type, content_id, comment_text, parent_id, country)
    
    return jsonify({'success': True})

@api_bp.route('/vote_comment', methods=['POST'])
@login_required
def vote_comment_api():
    data = request.json
    comment_id = data['comment_id']
    vote_type = data['vote_type']
    
    upvotes, downvotes = vote_comment(session['user_id'], comment_id, vote_type)
    
    return jsonify({
        'success': True,
        'upvotes': upvotes,
        'downvotes': downvotes
    })

@api_bp.route('/calculate_commission', methods=['POST'])
def calculate_commission():
    data = request.json
    
    base_prices = {
        'bust': 25,
        'half': 40,
        'full': 60
    }
    
    base_price = base_prices.get(data['type'], 25)
    total = base_price
    
    # Apply modifiers
    if data.get('multiple_characters'):
        total *= 1.3
    if data.get('nsfw'):
        total *= 1.25
    if data.get('rush'):
        total *= 1.5
    if data.get('unrendered'):
        total *= 0.5
    if data.get('indonesian_discount'):
        total *= 0.625
    
    return jsonify({
        'base_price': base_price,
        'total_price': round(total, 2)
    })

@api_bp.route('/optimize_image/<path:filename>')
def optimize_image_api(filename):
    """Serve optimized images"""
    return optimize_image(filename, request.args)

@api_bp.route('/reorder_clothing', methods=['POST'])
@admin_required
def reorder_clothing():
    data = request.json
    oc_id = data['oc_id']
    clothing_order = data['clothing_order']
    
    for item in clothing_order:
        execute_query(
            'UPDATE oc_clothing SET z_index = ? WHERE id = ? AND oc_id = ?',
            (item['z_index'], item['id'], oc_id)
        )
    
    return jsonify({'success': True})

def get_user_country(ip_address):
    """Get user country from IP (simplified)"""
    try:
        import requests
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=2)
        data = response.json()
        return data.get('country', 'Unknown')
    except:
        return 'Unknown'
