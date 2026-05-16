"""
User Authentication System for GitHub Repo Downloader
Handles local user accounts with encrypted credentials
"""
import sqlite3
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from typing import Optional, Dict, Any
import json


class UserDatabase:
    """SQLite-based user authentication database"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            self.db_path = os.path.join(app_data, 'GitHubDownloader', 'users.db')
        else:
            self.db_path = db_path
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self.encryption_key = self._get_or_create_encryption_key()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for credentials"""
        key_file = os.path.join(os.path.dirname(self.db_path), '.enc_key')
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)
            return key
    
    def _init_db(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS github_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                auth_type TEXT NOT NULL,
                access_token TEXT,
                refresh_token TEXT,
                token_expires_at TIMESTAMP,
                github_username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                repo_url TEXT NOT NULL,
                repo_name TEXT,
                local_path TEXT,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_count INTEGER,
                file_size INTEGER,
                status TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> tuple:
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_obj.hex() == password_hash
    
    def create_user(self, username: str, password: str) -> tuple:
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
    
    def save_github_credentials(self, user_id: int, auth_type: str, 
                                access_token: str, github_username: str,
                                refresh_token: str = None, 
                                token_expires_at: datetime = None):
        """Save GitHub credentials for user"""
        fernet = Fernet(self.encryption_key)
        encrypted_token = fernet.encrypt(access_token.encode()).decode()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if credentials exist
        cursor.execute('SELECT id FROM github_credentials WHERE user_id = ?', (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE github_credentials 
                SET auth_type = ?, access_token = ?, refresh_token = ?,
                    token_expires_at = ?, github_username = ?
                WHERE user_id = ?
            ''', (auth_type, encrypted_token, 
                  fernet.encrypt(refresh_token.encode()).decode() if refresh_token else None,
                  token_expires_at, github_username, user_id))
        else:
            cursor.execute('''
                INSERT INTO github_credentials 
                (user_id, auth_type, access_token, refresh_token, token_expires_at, github_username)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, auth_type, encrypted_token, 
                  fernet.encrypt(refresh_token.encode()).decode() if refresh_token else None,
                  token_expires_at, github_username))
        
        conn.commit()
        conn.close()
    
    def get_github_credentials(self, user_id: int) -> Optional[Dict]:
        """Get decrypted GitHub credentials"""
        fernet = Fernet(self.encryption_key)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT auth_type, access_token, refresh_token, token_expires_at, github_username 
            FROM github_credentials WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            auth_type, encrypted_token, encrypted_refresh, token_expires, github_username = result
            
            try:
                access_token = fernet.decrypt(encrypted_token.encode()).decode()
            except:
                access_token = None
            
            refresh_token = None
            if encrypted_refresh:
                try:
                    refresh_token = fernet.decrypt(encrypted_refresh.encode()).decode()
                except:
                    pass
            
            return {
                'auth_type': auth_type,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_expires_at': token_expires,
                'github_username': github_username
            }
        return None
    
    def delete_github_credentials(self, user_id: int):
        """Delete GitHub credentials"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM github_credentials WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
    
    def log_download(self, user_id: int, repo_url: str, repo_name: str,
                     local_path: str, file_count: int, file_size: int, status: str):
        """Log a download to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO download_history 
            (user_id, repo_url, repo_name, local_path, file_count, file_size, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, repo_url, repo_name, local_path, file_count, file_size, status))
        conn.commit()
        conn.close()
    
    def get_download_history(self, user_id: int, limit: int = 100) -> list:
        """Get download history for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM download_history 
            WHERE user_id = ? 
            ORDER BY downloaded_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_user_count(self) -> int:
        """Get total user count"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        count = cursor.fetchone()[0]
        conn.close()
        return count
