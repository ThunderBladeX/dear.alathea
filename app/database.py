from flask import g, current_app
import sqlite3
import asyncio
import threading

def get_db():
    """Get database connection for current request"""
    if 'db' not in g:
        config = current_app.config

        try:
            if config.get('IS_PRODUCTION'):
                # Production: Use libsql for Turso with proper async handling
                import libsql_client
                
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    # If we get here, we're in an async context
                    g.db = libsql_client.create_client(
                        url=config['TURSO_DATABASE_URL'],
                        auth_token=config['TURSO_AUTH_TOKEN']
                    )
                except RuntimeError:
                    # No running event loop, create a sync wrapper
                    g.db = SyncLibSQLWrapper(
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

class SyncLibSQLWrapper:
    """Synchronous wrapper for libsql-client"""
    def __init__(self, url, auth_token):
        self.url = url
        self.auth_token = auth_token
        self._client = None
        self._loop = None
        self._thread = None
        self._setup_async_client()
    
    def _setup_async_client(self):
        """Setup async client in a separate thread"""
        def run_async_loop():
            import libsql_client
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            async def create_client():
                return libsql_client.create_client(
                    url=self.url,
                    auth_token=self.auth_token
                )
            
            self._client = self._loop.run_until_complete(create_client())
            
        self._thread = threading.Thread(target=run_async_loop)
        self._thread.start()
        self._thread.join()
    
    def execute(self, query, params=None):
        """Execute query synchronously"""
        def run_query():
            async def async_execute():
                if params:
                    return await self._client.execute(query, params)
                else:
                    return await self._client.execute(query)
            
            return self._loop.run_until_complete(async_execute())
        
        return run_query()
    
    def close(self):
        """Close the connection"""
        if self._loop and not self._loop.is_closed():
            self._loop.close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

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
            # Turso/libsql
            if params:
                result = db.execute(query, params)
            else:
                result = db.execute(query)

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
