"""
User management module for the Users Service.
Handles user profiles, settings, preferences, and account management.
"""

from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
import uuid

# In-memory user database (in production, use a real database)
USERS = {}

class UserPlan(str, Enum):
    """Available user subscription plans"""
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class User:
    """Represents a user account"""
    
    def __init__(self, email: str, username: str = None):
        self.user_id = str(uuid.uuid4())
        self.email = email.lower()
        self.username = username or email.split("@")[0]
        self.plan = UserPlan.FREE
        self.status = UserStatus.ACTIVE
        self.org_id = None
        self.role = "member"
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.last_login = None
        self.profile = {
            "first_name": None,
            "last_name": None,
            "avatar_url": None,
            "bio": None,
            "phone": None
        }
        self.preferences = {
            "notifications_enabled": True,
            "email_digest": "weekly",
            "language": "en",
            "timezone": "UTC"
        }
        self.metadata = {}
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary"""
        return {
            "user_id": self.user_id,
            "email": self.email,
            "username": self.username,
            "plan": self.plan.value,
            "status": self.status.value,
            "org_id": self.org_id,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "profile": self.profile,
            "preferences": self.preferences
        }

def create_user(email: str, username: str = None) -> Dict:
    """
    Create a new user account.
    
    Args:
        email: User email address
        username: Optional username (defaults to email prefix)
        
    Returns:
        Created user dictionary
        
    Raises:
        ValueError: If email already exists
    """
    # Check if email already exists
    for user in USERS.values():
        if user.email == email.lower():
            raise ValueError(f"User with email {email} already exists")
    
    user = User(email, username)
    USERS[user.user_id] = user
    
    return user.to_dict()

def get_user(user_id: str) -> Optional[Dict]:
    """
    Get user by user_id.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        User dictionary if found, None otherwise
    """
    user = USERS.get(user_id)
    return user.to_dict() if user else None

def get_user_by_email(email: str) -> Optional[Dict]:
    """
    Get user by email address.
    
    Args:
        email: The user's email address
        
    Returns:
        User dictionary if found, None otherwise
    """
    email_lower = email.lower()
    for user in USERS.values():
        if user.email == email_lower:
            return user.to_dict()
    return None

def update_user(user_id: str, **kwargs) -> Optional[Dict]:
    """
    Update user information.
    
    Args:
        user_id: The user's unique identifier
        **kwargs: Fields to update (username, plan, org_id, profile fields, preferences)
        
    Returns:
        Updated user dictionary if found, None otherwise
    """
    if user_id not in USERS:
        return None
    
    user = USERS[user_id]
    user.updated_at = datetime.utcnow()
    
    # Update basic fields
    if "username" in kwargs:
        user.username = kwargs["username"]
    
    if "plan" in kwargs:
        if isinstance(kwargs["plan"], str):
            user.plan = UserPlan(kwargs["plan"])
        else:
            user.plan = kwargs["plan"]
    
    if "org_id" in kwargs:
        user.org_id = kwargs["org_id"]
    
    if "role" in kwargs:
        user.role = kwargs["role"]
    
    if "status" in kwargs:
        if isinstance(kwargs["status"], str):
            user.status = UserStatus(kwargs["status"])
        else:
            user.status = kwargs["status"]
    
    # Update profile
    if "profile" in kwargs:
        user.profile.update(kwargs["profile"])
    
    # Update preferences
    if "preferences" in kwargs:
        user.preferences.update(kwargs["preferences"])
    
    # Update metadata
    if "metadata" in kwargs:
        user.metadata.update(kwargs["metadata"])
    
    return user.to_dict()

def delete_user(user_id: str) -> bool:
    """
    Delete a user account.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        True if successfully deleted, False if user not found
    """
    if user_id in USERS:
        del USERS[user_id]
        return True
    return False

def deactivate_user(user_id: str) -> Optional[Dict]:
    """
    Deactivate a user account (soft delete).
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        Updated user dictionary if found, None otherwise
    """
    if user_id not in USERS:
        return None
    
    user = USERS[user_id]
    user.status = UserStatus.INACTIVE
    user.updated_at = datetime.utcnow()
    
    return user.to_dict()

def reactivate_user(user_id: str) -> Optional[Dict]:
    """
    Reactivate a deactivated user account.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        Updated user dictionary if found, None otherwise
    """
    if user_id not in USERS:
        return None
    
    user = USERS[user_id]
    user.status = UserStatus.ACTIVE
    user.updated_at = datetime.utcnow()
    
    return user.to_dict()

def upgrade_plan(user_id: str, new_plan: str) -> Optional[Dict]:
    """
    Upgrade user's subscription plan.
    
    Args:
        user_id: The user's unique identifier
        new_plan: New plan type (free, starter, pro, enterprise)
        
    Returns:
        Updated user dictionary if found, None otherwise
    """
    if user_id not in USERS:
        return None
    
    user = USERS[user_id]
    user.plan = UserPlan(new_plan)
    user.updated_at = datetime.utcnow()
    
    return user.to_dict()

def record_login(user_id: str) -> Optional[Dict]:
    """
    Record user login timestamp.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        Updated user dictionary if found, None otherwise
    """
    if user_id not in USERS:
        return None
    
    user = USERS[user_id]
    user.last_login = datetime.utcnow()
    
    return user.to_dict()

def list_users(plan: str = None, status: str = None, org_id: str = None) -> List[Dict]:
    """
    List users with optional filters.
    
    Args:
        plan: Filter by plan (optional)
        status: Filter by status (optional)
        org_id: Filter by organization (optional)
        
    Returns:
        List of user dictionaries matching criteria
    """
    users = []
    
    for user in USERS.values():
        # Apply filters
        if plan and user.plan.value != plan:
            continue
        if status and user.status.value != status:
            continue
        if org_id and user.org_id != org_id:
            continue
        
        users.append(user.to_dict())
    
    return users

def get_org_users(org_id: str) -> List[Dict]:
    """
    Get all users in an organization.
    
    Args:
        org_id: The organization's unique identifier
        
    Returns:
        List of user dictionaries in the organization
    """
    return [user.to_dict() for user in USERS.values() if user.org_id == org_id]

def assign_to_org(user_id: str, org_id: str, role: str = "member") -> Optional[Dict]:
    """
    Assign a user to an organization.
    
    Args:
        user_id: The user's unique identifier
        org_id: The organization's unique identifier
        role: User's role in the organization (member, admin, owner)
        
    Returns:
        Updated user dictionary if found, None otherwise
    """
    if user_id not in USERS:
        return None
    
    user = USERS[user_id]
    user.org_id = org_id
    user.role = role
    user.updated_at = datetime.utcnow()
    
    return user.to_dict()
