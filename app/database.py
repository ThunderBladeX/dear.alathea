from flask import g, current_app
import sqlite3
import requests
import json

def get_db():
    """Get database connection for current request"""
    if 'db' not in g:
        config = current_app.config

        try:
            if config.get('IS_PRODUCTION'):
                # Production: Use HTTP client for Turso instead of libsql-client
                g.db = TursoHTTPClient(
                    url=config['TURSO_DATABASE_URL'],
                    auth_token=config['TURSO_AUTH_TOKEN']
                )
            else:
                # Development: Use SQLite
                g.db = sqlite3.connect(config['DATABASE_URL'])
                g.db.row_factory = sqlite3.Row
        except Exception as e:
            current_app.logger.exception(f"Error connecting to database: {e}")
            # Fallback to SQLite if Turso connection fails
            current_app.logger.warning("Falling back to SQLite database")
            g.db = sqlite3.connect('fallback.db')
            g.db.row_factory = sqlite3.Row

    return g.db

class TursoHTTPClient:
    """HTTP client for Turso database"""
    def __init__(self, url, auth_token):
        # Convert libsql URL to HTTP URL
        self.base_url = url.replace('libsql://', 'https://').replace('.turso.io', '.turso.io')
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        self.base_url += 'v2/pipeline'
        
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        })
    
    def execute(self, query, params=None):
        """Execute query via HTTP"""
        try:
            # Format the request
            request_data = {
                "requests": [
                    {
                        "type": "execute",
                        "stmt": {
                            "sql": query
                        }
                    }
                ]
            }
            
            # Add parameters if provided
            if params:
                request_data["requests"][0]["stmt"]["args"] = list(params)
            
            # Make the request
            response = self.session.post(self.base_url, json=request_data, timeout=10)
            response.raise_for_status()
            
            result_data = response.json()
            
            # Return a result object that mimics libsql-client behavior
            return TursoResult(result_data)
            
        except Exception as e:
            current_app.logger.exception(f"Error executing Turso query: {e}")
            raise
    
    def close(self):
        """Close the session"""
        self.session.close()

class TursoResult:
    """Result wrapper for Turso HTTP responses"""
    def __init__(self, result_data):
        self.result_data = result_data
        self._rows = None
    
    @property
    def rows(self):
        """Get rows from the result"""
        if self._rows is None:
            self._rows = []
            
            if (self.result_data and 
                'results' in self.result_data and 
                len(self.result_data['results']) > 0):
                
                result = self.result_data['results'][0]
                if 'response' in result and 'result' in result['response']:
                    result_obj = result['response']['result']
                    
                    if 'rows' in result_obj and 'cols' in result_obj:
                        cols = result_obj['cols']
                        for row_data in result_obj['rows']:
                            row_dict = {}
                            for i, col in enumerate(cols):
                                if i < len(row_data):
                                    row_dict[col] = row_data[i]
                                else:
                                    row_dict[col] = None
                            self._rows.append(row_dict)
        
        return self._rows

def close_db(error):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        try:
            if hasattr(db, 'close'):
                db.close()
        except Exception as e:
            current_app.logger.error(f"Error closing database connection: {e}")

def execute_query(query, params=None, fetch=None):
    """Execute database query with proper connection handling"""
    db = get_db()
    config = current_app.config

    try:
        if config.get('IS_PRODUCTION'):
            # Turso HTTP client
            result = db.execute(query, params)

            if fetch == 'all':
                return result.rows
            elif fetch == 'one':
                rows = result.rows
                return rows[0] if rows else None
            else:
                return result
        else:
            # SQLite
            cursor = db.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetch == 'all':
                return cursor.fetchall()
            elif fetch == 'one':
                return cursor.fetchone()
            else:
                db.commit()
                return cursor
    except Exception as e:
        current_app.logger.exception(f"Error executing query: {e}")
        raise

def init_db(config):
    """Initialize database with tables"""
    tables = [
        '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT FALSE
        )''',
        '''CREATE TABLE IF NOT EXISTS gallery_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            title TEXT NOT NULL,
            caption TEXT,
            tags TEXT,
            width INTEGER,
            height INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS ocs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            base_image TEXT NOT NULL,
            profile_image TEXT,
            description TEXT,
            age TEXT,
            personality TEXT,
            backstory TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS oc_clothing (
            id INTEGER PRIMARY KEY,
            oc_id INTEGER,
            item_name TEXT NOT NULL,
            filename TEXT NOT NULL,
            category TEXT,
            z_index INTEGER DEFAULT 1,
            FOREIGN KEY (oc_id) REFERENCES ocs (id)
        )''',
        '''CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            summary TEXT,
            featured_image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            content_type TEXT NOT NULL,
            content_id INTEGER NOT NULL,
            parent_id INTEGER,
            content TEXT NOT NULL,
            country TEXT,
            upvotes INTEGER DEFAULT 0,
            downvotes INTEGER DEFAULT 0,
            flagged BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (parent_id) REFERENCES comments (id)
        )''',
        '''CREATE TABLE IF NOT EXISTS comment_votes (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            comment_id INTEGER,
            vote_type TEXT CHECK(vote_type IN ('up', 'down')),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (comment_id) REFERENCES comments (id),
            UNIQUE(user_id, comment_id)
        )''',
        '''CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            link TEXT,
            read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )'''
    ]
    
    try:
        # Execute all table creation queries
        for table_sql in tables:
            execute_query(table_sql)
        
        # Create admin user if needed
        from app.auth import create_admin_user
        create_admin_user(config)
        
    except Exception as e:
        current_app.logger.exception(f"Error initializing database: {e}")
        raise
