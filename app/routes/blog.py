from flask import Blueprint, render_template, redirect, url_for
from app.database import execute_query
from app.services.comment_service import get_comments_with_replies

blog_bp = Blueprint(
    'blog',
    __name__,
    template_folder='../templates',
    static_folder='../static',
    url_prefix='/blog'
)

@blog_bp.route('/')
def index():
    posts = execute_query('SELECT * FROM blog_posts ORDER BY created_at DESC', fetch='all')
    return render_template('blog.html', posts=posts)

@blog_bp.route('/<int:post_id>')
def post_detail(post_id):
    post = execute_query('SELECT * FROM blog_posts WHERE id = ?', (post_id,), fetch='one')
    
    if not post:
        return redirect(url_for('blog.index'))
    
    comments = get_comments_with_replies('blog', post_id)
    return render_template('blog_post.html', post=post, comments=comments)
