from app.database import execute_query

def get_comments_with_replies(content_type, content_id):
    """Get all comments and replies in a single query to avoid N+1 problem"""
    
    # Single query to get all comments and replies
    all_comments = execute_query('''
        SELECT c.*, u.username,
               CASE 
                   WHEN c.parent_id IS NULL THEN c.id 
                   ELSE c.parent_id 
               END as thread_id
        FROM comments c
        LEFT JOIN users u ON c.user_id = u.id
        WHERE c.content_type = ? AND c.content_id = ?
        ORDER BY thread_id ASC, c.parent_id ASC, c.created_at ASC
    ''', (content_type, content_id), fetch='all')
    
    # Organize comments into threaded structure
    comments_dict = {}
    top_level_comments = []
    
    for comment in all_comments:
        comment_dict = dict(comment)
        comment_dict['replies'] = []
        
        if comment['parent_id'] is None:
            # Top level comment
            comments_dict[comment['id']] = comment_dict
            top_level_comments.append(comment_dict)
        else:
            # Reply - add to parent's replies
            parent_id = comment['parent_id']
            if parent_id in comments_dict:
                comments_dict[parent_id]['replies'].append(comment_dict)
    
    return top_level_comments

def add_comment(user_id, content_type, content_id, comment_text, parent_id=None, country=None):
    """Add a new comment"""
    execute_query('''
        INSERT INTO comments (user_id, content_type, content_id, parent_id, content, country)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, content_type, content_id, parent_id, comment_text, country))

def vote_comment(user_id, comment_id, vote_type):
    """Handle comment voting"""
    # Check existing vote
    existing_vote = execute_query('''
        SELECT vote_type FROM comment_votes 
        WHERE user_id = ? AND comment_id = ?
    ''', (user_id, comment_id), fetch='one')
    
    if existing_vote:
        if existing_vote['vote_type'] == vote_type:
            # Remove vote
            execute_query(
                'DELETE FROM comment_votes WHERE user_id = ? AND comment_id = ?',
                (user_id, comment_id)
            )
        else:
            # Change vote
            execute_query(
                'UPDATE comment_votes SET vote_type = ? WHERE user_id = ? AND comment_id = ?',
                (vote_type, user_id, comment_id)
            )
    else:
        # Add new vote
        execute_query(
            'INSERT INTO comment_votes (user_id, comment_id, vote_type) VALUES (?, ?, ?)',
            (user_id, comment_id, vote_type)
        )
    
    # Get updated counts
    upvotes = execute_query(
        'SELECT COUNT(*) as count FROM comment_votes WHERE comment_id = ? AND vote_type = "up"',
        (comment_id,), fetch='one'
    )['count']
    
    downvotes = execute_query(
        'SELECT COUNT(*) as count FROM comment_votes WHERE comment_id = ? AND vote_type = "down"',
        (comment_id,), fetch='one'
    )['count']
    
    # Update comment counts
    execute_query(
        'UPDATE comments SET upvotes = ?, downvotes = ? WHERE id = ?',
        (upvotes, downvotes, comment_id)
    )
    
    return upvotes, downvotes
