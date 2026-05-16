"""
Session Management for Charm Crush
Handles CRUD operations for sessions and their files
"""
import uuid
import os
import sqlite3
import json
import threading
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple


class SessionManager:
    """Manages sessions and associated configuration files for a user"""
    
    def __init__(self, user_db, user_id: int, auto_save_interval: int = 60):
        self.db = user_db
        self.user_id = user_id
        self.auto_save_interval = auto_save_interval
        self.auto_save_enabled = False
        self._auto_save_timer = None
        self._pending_changes = {}
        self._session_locks = {}
        self._lock = threading.Lock()
    
    def create_session(self, name: str, description: str = "") -> Optional[str]:
        """Create a new session and return its ID"""
        session_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO sessions (id, user_id, name, description) VALUES (?, ?, ?, ?)',
                (session_id, self.user_id, name, description)
            )
            conn.commit()
            return session_id
        except Exception as e:
            print(f"Error creating session: {e}")
            return None
        finally:
            conn.close()
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions for the current user"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, name, description, created_at, updated_at FROM sessions WHERE user_id = ? ORDER BY updated_at DESC',
            (self.user_id,)
        )
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0],
                'name': r[1],
                'description': r[2],
                'created_at': r[3],
                'updated_at': r[4]
            }
            for r in results
        ]
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session details including files"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Get session metadata
        cursor.execute(
            'SELECT id, name, description, created_at, updated_at FROM sessions WHERE id = ? AND user_id = ?',
            (session_id, self.user_id)
        )
        session_row = cursor.fetchone()
        
        if not session_row:
            conn.close()
            return None
            
        # Get session files
        cursor.execute(
            'SELECT id, file_path, format, content, updated_at FROM session_files WHERE session_id = ?',
            (session_id,)
        )
        file_rows = cursor.fetchall()
        conn.close()
        
        files = []
        for f in file_rows:
            decrypted_content = None
            if f[3]: # content is BLOB
                try:
                    decrypted_content = self.db.decrypt_data(f[3])
                except Exception as e:
                    print(f"Error decrypting file {f[1]}: {e}")
            
            files.append({
                'id': f[0],
                'file_path': f[1],
                'format': f[2],
                'content': decrypted_content,
                'updated_at': f[4]
            })
            
        return {
            'id': session_row[0],
            'name': session_row[1],
            'description': session_row[2],
            'created_at': session_row[3],
            'updated_at': session_row[4],
            'files': files
        }
    
    def rename_session(self, session_id: str, new_name: str) -> bool:
        """Rename an existing session"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'UPDATE sessions SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND user_id = ?',
                (new_name, session_id, self.user_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error renaming session: {e}")
            return False
        finally:
            conn.close()
            
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its files"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            # First delete files (due to foreign key)
            cursor.execute('DELETE FROM session_files WHERE session_id = ?', (session_id,))
            # Then delete session
            cursor.execute('DELETE FROM sessions WHERE id = ? AND user_id = ?', (session_id, self.user_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
        finally:
            conn.close()

    def add_file_to_session(self, session_id: str, file_path: str, format_type: str, content: bytes) -> bool:
        """Add or update an encrypted file in a session"""
        encrypted_content = self.db.encrypt_data(content)
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if file already exists in session
            cursor.execute(
                'SELECT id FROM session_files WHERE session_id = ? AND file_path = ?',
                (session_id, file_path)
            )
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute(
                    'UPDATE session_files SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                    (encrypted_content, existing[0])
                )
            else:
                cursor.execute(
                    'INSERT INTO session_files (session_id, file_path, format, content) VALUES (?, ?, ?, ?)',
                    (session_id, file_path, format_type, encrypted_content)
                )
            
            # Update session timestamp
            cursor.execute(
                'UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (session_id,)
            )
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding file to session: {e}")
            return False
        finally:
            conn.close()

    def remove_file_from_session(self, file_id: int) -> bool:
        """Remove a file from a session"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM session_files WHERE id = ?', (file_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing file: {e}")
            return False
        finally:
            conn.close()

    def duplicate_session(self, session_id: str) -> Optional[str]:
        """Duplicate a session and all its files"""
        original = self.get_session(session_id)
        if not original:
            return None
            
        new_id = self.create_session(f"{original['name']} (Copy)", original['description'])
        if not new_id:
            return None
            
        for f in original.get('files', []):
            self.add_file_to_session(new_id, f['file_path'], f['format'], f['content'])
            
        return new_id

    def search_sessions(self, query: str) -> List[Dict[str, Any]]:
        """Search sessions by name or description"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        search_query = f"%{query}%"
        cursor.execute(
            '''SELECT id, name, description, created_at, updated_at FROM sessions 
               WHERE user_id = ? AND (name LIKE ? OR description LIKE ?)
               ORDER BY updated_at DESC''',
            (self.user_id, search_query, search_query)
        )
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': r[0],
                'name': r[1],
                'description': r[2],
                'created_at': r[3],
                'updated_at': r[4]
            }
            for r in results
        ]

    def get_available_templates(self) -> List[str]:
        """Get list of available session templates"""
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        if not os.path.exists(templates_dir):
            return []
        return [f.replace('.json', '') for f in os.listdir(templates_dir) if f.endswith('.json')]

    def create_session_from_template(self, template_name: str, name: str, description: str = "") -> Optional[str]:
        """Create a new session from a template file"""
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        template_path = os.path.join(templates_dir, f"{template_name}.json")
        
        if not os.path.exists(template_path):
            return self.create_session(name, description)
        
        session_id = self.import_session(template_path, name)
        if session_id and description:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE sessions SET description = ? WHERE id = ?', (description, session_id))
            conn.commit()
            conn.close()
        return session_id

    def export_session(self, session_id: str, file_path: str) -> bool:
        """Export session to a JSON file"""
        session_data = self.get_session(session_id)
        if not session_data:
            return False
            
        # Convert bytes content to string for JSON serialization
        export_data = session_data.copy()
        for f in export_data.get('files', []):
            if f['content']:
                try:
                    f['content'] = f['content'].decode('utf-8')
                except:
                    f['content'] = str(f['content'])
                    
        try:
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error exporting session: {e}")
            return False

    def import_session(self, file_path: str, new_name: str = None) -> Optional[str]:
        """Import session from a JSON file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            name = new_name or data.get('name', 'Imported Session')
            description = data.get('description', '')
            
            session_id = self.create_session(name, description)
            if not session_id:
                return None
                
            for file_info in data.get('files', []):
                content_str = file_info.get('content', '')
                content_bytes = content_str.encode('utf-8') if isinstance(content_str, str) else b''
                self.add_file_to_session(
                    session_id, 
                    file_info.get('file_path', 'unknown'),
                    file_info.get('format', 'txt'),
                    content_bytes
                )
                
            return session_id
        except Exception as e:
            print(f"Error importing session: {e}")
            return None

    def import_session_safe(self, file_path: str, new_name: str = None) -> Tuple[bool, Optional[str], List[str]]:
        """Import session with detailed error reporting"""
        errors = []
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            name = new_name or data.get('name', 'Imported Session')
            description = data.get('description', '')
            
            session_id = self.create_session(name, description)
            if not session_id:
                return False, None, ["Database error: Failed to create session entry"]
                
            for i, file_info in enumerate(data.get('files', [])):
                try:
                    content_str = file_info.get('content', '')
                    content_bytes = content_str.encode('utf-8') if isinstance(content_str, str) else b''
                    self.add_file_to_session(
                        session_id, 
                        file_info.get('file_path', f'imported_file_{i}'),
                        file_info.get('format', 'txt'),
                        content_bytes
                    )
                except Exception as fe:
                    errors.append(f"Failed to import file {i}: {str(fe)}")
                
            return True, session_id, errors
        except Exception as e:
            return False, None, [f"Critical import error: {str(e)}"]

    # --- ADVANCED ENHANCEMENTS ---

    def validate_session(self, session_id: str) -> Dict:
        """Validate session integrity"""
        session = self.get_session(session_id)
        if not session:
            return {'valid': False, 'error': 'Session not found'}
        
        valid_files = []
        for file_info in session.get('files', []):
            if file_info['content'] is not None:
                valid_files.append(file_info)
        
        return {
            'valid': True,
            'file_count': len(valid_files),
            'invalid_files': len(session.get('files', [])) - len(valid_files)
        }

    def get_session_stats(self) -> Dict:
        """Get comprehensive session statistics"""
        sessions = self.get_all_sessions()
        total_files = 0
        total_size = 0
        
        for session in sessions:
            session_data = self.get_session(session['id'])
            if session_data:
                files = session_data.get('files', [])
                total_files += len(files)
                for f in files:
                    if f.get('content'):
                        total_size += len(f['content'])
        
        def _format_size(size_bytes):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024
            return f"{size_bytes:.1f} TB"

        return {
            'total_sessions': len(sessions),
            'total_files': total_files,
            'total_size_human': _format_size(total_size),
            'average_files_per_session': total_files / len(sessions) if sessions else 0
        }

    def get_user_activity_stats(self, days: int = 30) -> Dict:
        """Get activity stats for the last N days"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT COUNT(*) FROM sessions WHERE user_id = ? AND updated_at > datetime("now", ?)',
            (self.user_id, f'-{days} days')
        )
        recent_count = cursor.fetchone()[0]
        conn.close()
        return {'recent_sessions': recent_count}

    def get_all_tags(self) -> List[str]:
        """Get all unique tags used by this user"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT DISTINCT tag FROM session_tags t
               JOIN sessions s ON t.session_id = s.id
               WHERE s.user_id = ?''',
            (self.user_id,)
        )
        results = [r[0] for r in cursor.fetchall()]
        conn.close()
        return results

    def export_sessions(self, session_ids: List[str], output_dir: str) -> Dict:
        """Bulk export multiple sessions to a directory"""
        results = {'exported': 0, 'failed': 0}
        for sid in session_ids:
            session = self.get_session(sid)
            if session:
                safe_name = session['name'].replace(' ', '_').replace('/', '_')
                file_name = f"{safe_name}_{sid[:8]}.json"
                target_path = os.path.join(output_dir, file_name)
                if self.export_session(sid, target_path):
                    results['exported'] += 1
                else:
                    results['failed'] += 1
            else:
                results['failed'] += 1
        return results

    def delete_sessions(self, session_ids: List[str]) -> Dict:
        """Bulk delete sessions"""
        results = {'deleted': 0, 'failed': 0}
        for sid in session_ids:
            if self.delete_session(sid):
                results['deleted'] += 1
            else:
                results['failed'] += 1
        return results

    def add_session_tag(self, session_id: str, tag: str) -> bool:
        """Add a tag to a session (stored in DB)"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT OR IGNORE INTO session_tags (session_id, tag) VALUES (?, ?)',
                (session_id, tag)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding tag: {e}")
            return False
        finally:
            conn.close()

    def remove_session_tag(self, session_id: str, tag: str) -> bool:
        """Remove a tag from a session"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                'DELETE FROM session_tags WHERE session_id = ? AND tag = ?',
                (session_id, tag)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error removing tag: {e}")
            return False
        finally:
            conn.close()

    def get_sessions_by_tag(self, tag: str) -> List[Dict]:
        """Get all sessions associated with a tag"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT s.id, s.name, s.description, s.created_at, s.updated_at 
               FROM sessions s JOIN session_tags t ON s.id = t.session_id 
               WHERE t.tag = ? AND s.user_id = ?''',
            (tag, self.user_id)
        )
        results = cursor.fetchall()
        conn.close()
        return [
            {'id': r[0], 'name': r[1], 'description': r[2], 'created_at': r[3], 'updated_at': r[4]}
            for r in results
        ]

    def _get_session_lock(self, session_id: str):
        """Get or create a lock for a specific session"""
        with self._lock:
            if session_id not in self._session_locks:
                self._session_locks[session_id] = threading.Lock()
            return self._session_locks[session_id]

    # Auto-save logic
    def enable_auto_save(self, enabled: bool):
        self.auto_save_enabled = enabled
        if enabled:
            if self._auto_save_timer and self._auto_save_timer.is_alive():
                return
            self._start_auto_save_timer()
        else:
            if self._auto_save_timer:
                self._auto_save_timer.cancel()

    def _start_auto_save_timer(self):
        self._auto_save_timer = threading.Timer(self.auto_save_interval, self._auto_save_worker)
        self._auto_save_timer.daemon = True
        self._auto_save_timer.start()

    def _auto_save_worker(self):
        if not self.auto_save_enabled:
            return
        # Save pending changes
        with self._lock:
            changes = self._pending_changes.copy()
            self._pending_changes.clear()
        
        for sid, data in changes.items():
            # In a real app, this would iterate and save files
            pass
            
        self._start_auto_save_timer()

