"""
API Key management for service-to-service authentication.
Handles generation, storage, validation, and revocation of API keys.
"""

import uuid
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from enum import Enum

# In-memory API key store (in production, use a database)
API_KEYS_DB = {}

class APIKeyScope(str, Enum):
    """Available scopes for API keys"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    FULL = "full"

class APIKey:
    """Represents an API key with metadata"""
    
    def __init__(self, user_id: str, name: str, scopes: List[str] = None):
        self.key_id = str(uuid.uuid4())
        self.key = self._generate_key()
        self.key_hash = self._hash_key(self.key)
        self.user_id = user_id
        self.name = name
        self.scopes = scopes or ["read"]
        self.created_at = datetime.utcnow()
        self.last_used = None
        self.expires_at = datetime.utcnow() + timedelta(days=365)
        self.active = True
    
    @staticmethod
    def _generate_key() -> str:
        """Generate a random API key"""
        return f"sk_{uuid.uuid4().hex}"
    
    @staticmethod
    def _hash_key(key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "key_id": self.key_id,
            "user_id": self.user_id,
            "name": self.name,
            "scopes": self.scopes,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "expires_at": self.expires_at.isoformat(),
            "active": self.active
        }

def generate_api_key(user_id: str, name: str = "Default Key", scopes: List[str] = None) -> str:
    """
    Generate a new API key for a user.
    
    Args:
        user_id: The user's unique identifier
        name: Friendly name for the key
        scopes: List of scopes (read, write, admin, full)
        
    Returns:
        The generated API key (only shown once)
    """
    if scopes is None:
        scopes = ["read"]
    
    api_key = APIKey(user_id, name, scopes)
    API_KEYS_DB[api_key.key_hash] = api_key
    
    return api_key.key  # Return unhashed key (shown once to user)

def validate_api_key(key: str) -> Optional[str]:
    """
    Validate an API key and return the associated user_id.
    
    Args:
        key: The API key to validate
        
    Returns:
        User ID if valid, None otherwise
    """
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    
    if key_hash not in API_KEYS_DB:
        return None
    
    api_key = API_KEYS_DB[key_hash]
    
    # Check if key is active and not expired
    if not api_key.active or datetime.utcnow() > api_key.expires_at:
        return None
    
    # Update last used timestamp
    api_key.last_used = datetime.utcnow()
    
    return api_key.user_id

def validate_api_key_with_scope(key: str, required_scope: str) -> Optional[str]:
    """
    Validate an API key and check if it has the required scope.
    
    Args:
        key: The API key to validate
        required_scope: Required scope (read, write, admin, full)
        
    Returns:
        User ID if valid and has scope, None otherwise
    """
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    
    if key_hash not in API_KEYS_DB:
        return None
    
    api_key = API_KEYS_DB[key_hash]
    
    # Check if key is active and not expired
    if not api_key.active or datetime.utcnow() > api_key.expires_at:
        return None
    
    # Check scope
    if required_scope not in api_key.scopes and "full" not in api_key.scopes:
        return None
    
    # Update last used timestamp
    api_key.last_used = datetime.utcnow()
    
    return api_key.user_id

def list_api_keys(user_id: str) -> List[Dict]:
    """
    List all API keys for a user.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        List of API key metadata (excluding the actual keys)
    """
    user_keys = [
        key.to_dict() for key in API_KEYS_DB.values()
        if key.user_id == user_id
    ]
    return user_keys

def revoke_api_key(user_id: str, key_id: str) -> bool:
    """
    Revoke an API key.
    
    Args:
        user_id: The user's unique identifier
        key_id: The key ID to revoke
        
    Returns:
        True if successfully revoked, False otherwise
    """
    for key_hash, api_key in API_KEYS_DB.items():
        if api_key.user_id == user_id and api_key.key_id == key_id:
            api_key.active = False
            return True
    return False

def delete_api_key(user_id: str, key_id: str) -> bool:
    """
    Delete an API key permanently.
    
    Args:
        user_id: The user's unique identifier
        key_id: The key ID to delete
        
    Returns:
        True if successfully deleted, False otherwise
    """
    key_hash_to_delete = None
    
    for key_hash, api_key in API_KEYS_DB.items():
        if api_key.user_id == user_id and api_key.key_id == key_id:
            key_hash_to_delete = key_hash
            break
    
    if key_hash_to_delete:
        del API_KEYS_DB[key_hash_to_delete]
        return True
    return False

def refresh_api_key_expiry(user_id: str, key_id: str, days: int = 365) -> bool:
    """
    Extend the expiry date of an API key.
    
    Args:
        user_id: The user's unique identifier
        key_id: The key ID to refresh
        days: Number of days to extend
        
    Returns:
        True if successfully refreshed, False otherwise
    """
    for api_key in API_KEYS_DB.values():
        if api_key.user_id == user_id and api_key.key_id == key_id:
            api_key.expires_at = datetime.utcnow() + timedelta(days=days)
            return True
    return False
