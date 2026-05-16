"""
Session Sharing Manager for Charm Crush
Handles link-based sharing of encrypted sessions
"""
import uuid
import json
import os
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple


class SharePermission(Enum):
    VIEW = "view"
    EDIT = "edit"


class ShareStatus(Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ShareLink:
    def __init__(self, share_id: str, session_id: str, creator_id: int, permission: SharePermission, 
                 password: str = None, expires_at: datetime = None):
        self.share_id = share_id
        self.session_id = session_id
        self.creator_id = creator_id
        self.permission = permission
        self.password = password
        self.password_protected = password is not None
        self.status = ShareStatus.ACTIVE
        self.expires_at = expires_at or (datetime.now() + timedelta(days=7))
        
    def get_share_url(self) -> str:
        return f"charmcrush://share/{self.share_id}"


class SessionSharingManager:
    """Manages creation, validation, and revocation of session share links"""
    
    def __init__(self, storage_dir: str = None):
        if storage_dir:
            self.storage_dir = storage_dir
        else:
            app_data = os.environ.get('APPDATA', os.environ.get('HOME', os.path.expanduser('~')))
            self.storage_dir = os.path.join(app_data, 'CharmCrush', 'shares')
            
        os.makedirs(self.storage_dir, exist_ok=True)
        self.shares = {} # share_id -> ShareLink
        
    def create_share_link(self, session_id: str, creator_id: int, permission: str = 'view', 
                          password: str = None, expires_in_days: int = 7) -> ShareLink:
        share_id = str(uuid.uuid4())
        perm = SharePermission.EDIT if permission == 'edit' else SharePermission.VIEW
        expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        share = ShareLink(share_id, session_id, creator_id, perm, password, expires_at)
        self.shares[share_id] = share
        return share
        
    def get_share_link(self, share_id: str) -> Optional[ShareLink]:
        return self.shares.get(share_id)
        
    def revoke_share_link(self, share_id: str) -> bool:
        if share_id in self.shares:
            self.shares[share_id].status = ShareStatus.REVOKED
            return True
        return False
        
    def validate_access(self, share_id: str, password: str = None) -> Tuple[bool, Optional[ShareLink], Optional[str]]:
        share = self.get_share_link(share_id)
        if not share:
            return False, None, "Share not found"
            
        if share.status != ShareStatus.ACTIVE:
            return False, share, f"Share is {share.status.value}"
            
        if share.expires_at < datetime.now():
            share.status = ShareStatus.EXPIRED
            return False, share, "Share has expired"
            
        if share.password_protected and share.password != password:
            return False, share, "Invalid password"
            
        return True, share, None
        
    def get_statistics(self) -> Dict:
        active = [s for s in self.shares.values() if s.status == ShareStatus.ACTIVE]
        return {
            'total_shares': len(self.shares),
            'active_shares': len(active)
        }
