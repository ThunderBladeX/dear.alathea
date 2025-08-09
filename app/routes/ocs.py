from flask import Blueprint, render_template, redirect, url_for
from app.database import execute_query
from app.services.comment_service import get_comments_with_replies

ocs_bp = Blueprint(
    'ocs',
    __name__,
    template_folder='../templates',
    static_folder='../static',
    url_prefix='/ocs'
)

@ocs_bp.route('/')
def index():
    ocs = execute_query('SELECT * FROM ocs ORDER BY created_at DESC', fetch='all')
    return render_template('ocs.html', ocs=ocs)

@ocs_bp.route('/<int:oc_id>')
def detail(oc_id):
    oc = execute_query('SELECT * FROM ocs WHERE id = ?', (oc_id,), fetch='one')
    
    if not oc:
        return redirect(url_for('ocs.index'))
    
    # Get clothing items
    clothing_items = execute_query('''
        SELECT * FROM oc_clothing 
        WHERE oc_id = ? 
        ORDER BY z_index ASC, category ASC
    ''', (oc_id,), fetch='all')
    
    # Get comments
    comments = get_comments_with_replies('oc', oc_id)
    
    return render_template('oc_detail.html', oc=oc, clothing_items=clothing_items, comments=comments)
