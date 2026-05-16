"""
User Authentication System for Charm Crush
Handles local user accounts with encrypted credentials and session data
"""
import sqlite3
import hashlib
import secrets
import os
import json
from datetime import datetime
from cryptography.fernet import Fernet
from typing import Optional, Dict, List, Any, Tuple
from queue import Queue
from contextlib import contextmanager


class UserDatabase:
    """SQLite-based user authentication and data encryption database"""
    
    def __init__(self, db_path: str = None, pool_size: int = 5):
        if db_path is None:
            app_data = os.environ.get('APPDATA', os.environ.get('HOME', os.path.expanduser('~')))
            base_dir = os.path.join(app_data, 'CharmCrush')
            self.db_path = os.path.join(base_dir, 'charm_crush.db')
        else:
            self.db_path = db_path
            base_dir = os.path.dirname(self.db_path)
        
        if base_dir:
            os.makedirs(base_dir, exist_ok=True)
        else:
            base_dir = "."
        
        self._connection_pool = Queue(maxsize=pool_size)
        self._init_db()
        self._init_pool()
        
        self.encryption_key = self._get_or_create_encryption_key(base_dir)
        self.fernet = Fernet(self.encryption_key)

    def _init_pool(self):
        """Initialize connection pool"""
        for _ in range(self._connection_pool.maxsize):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._connection_pool.put(conn)

    @contextmanager
    def get_connection(self):
        """Get connection from pool"""
        conn = self._connection_pool.get()
        try:
            yield conn
        finally:
            self._connection_pool.put(conn)

    def close_all(self):
        """Close all pooled connections"""
        while not self._connection_pool.empty():
            conn = self._connection_pool.get()
            conn.close()
    
    def _get_or_create_encryption_key(self, base_dir: str) -> bytes:
        """Get or create encryption key for session data"""
        key_file = os.path.join(base_dir, '.secret_key')
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # On Windows, we should ideally restrict access to this file
            return key
    
    def _init_db(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Session files table (stored encrypted)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                format TEXT NOT NULL,
                content BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                preferences TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Session tags table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id),
                UNIQUE(session_id, tag)
            )
        ''')
        
        conn.commit()
        conn.close()

    # --- ADVANCED AUTH OPS ---
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, created_at, last_login FROM users WHERE is_active = 1')
            return [{'id': r[0], 'username': r[1], 'created_at': r[2], 'last_login': r[3]} for r in cursor.fetchall()]

    def save_user_preferences(self, user_id: int, prefs: Dict) -> bool:
        """Save user preferences"""
        pref_json = json.dumps(prefs)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO user_preferences (user_id, preferences) VALUES (?, ?)', (user_id, pref_json))
            conn.commit()
            return True

    def get_user_preferences(self, user_id: int) -> Dict:
        """Get user preferences"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT preferences FROM user_preferences WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            return json.loads(row[0]) if row else {}
    
    def hash_password(self, password: str) -> Tuple[str, str]:
        """Hash password with salt using PBKDF2"""
        salt = secrets.token_hex(32)
        # Use 100,000 iterations as recommended in the plan
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex() == password_hash
    
    def create_user(self, username: str, password: str) -> Tuple[bool, Optional[int]]:
        """Create a new user account"""
        password_hash, salt = self.hash_password(password)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)',
                (username, password_hash, salt)
            )
            user_id = cursor.lastrowid
            conn.commit()
            return True, user_id
        except sqlite3.IntegrityError:
            return False, None
        finally:
            conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[int]:
        """Authenticate user and return user_id"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, password_hash, salt, is_active FROM users WHERE username = ?',
            (username,)
        )
        result = cursor.fetchone()
        
        if result and result[3] == 1:  # is_active
            user_id, password_hash, salt, _ = result
            if self.verify_password(password, password_hash, salt):
                cursor.execute(
                    'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
                    (user_id,)
                )
                conn.commit()
                conn.close()
                return user_id
        
        conn.close()
        return None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, created_at, last_login FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'created_at': result[2],
                'last_login': result[3]
            }
        return None

    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt binary data using Fernet"""
        return self.fernet.encrypt(data)

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt binary data using Fernet"""
        return self.fernet.decrypt(encrypted_data)
