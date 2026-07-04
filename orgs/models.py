"""
Organization management module for the Organizations Service.
Handles organization creation, membership, roles, teams, and settings.
"""

from datetime import datetime
from typing import Optional, Dict, List
from enum import Enum
import uuid

# In-memory organization database (in production, use a real database)
ORGS = {}

class OrgRole(str, Enum):
    """Organization member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class OrgStatus(str, Enum):
    """Organization account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class OrgMember:
    """Represents an organization member"""
    
    def __init__(self, user_id: str, role: str = OrgRole.MEMBER):
        self.user_id = user_id
        self.role = OrgRole(role) if isinstance(role, str) else role
        self.joined_at = datetime.utcnow()
        self.invited_at = None
        self.invited_by = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat(),
            "invited_at": self.invited_at.isoformat() if self.invited_at else None,
            "invited_by": self.invited_by
        }

class Organization:
    """Represents an organization"""
    
    def __init__(self, name: str, owner_id: str, description: str = None):
        self.org_id = str(uuid.uuid4())
        self.name = name
        self.slug = name.lower().replace(" ", "-")
        self.description = description
        self.owner_id = owner_id
        self.status = OrgStatus.ACTIVE
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.members = {
            owner_id: OrgMember(owner_id, OrgRole.OWNER)
        }
        self.teams = {}  # team_id -> team info
        self.settings = {
            "public": False,
            "allow_external_collaborators": True,
            "require_2fa": False,
            "default_member_role": OrgRole.MEMBER.value
        }
        self.metadata = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "org_id": self.org_id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "owner_id": self.owner_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "member_count": len(self.members),
            "team_count": len(self.teams),
            "settings": self.settings
        }

def create_org(name: str, owner_id: str, description: str = None) -> Dict:
    """
    Create a new organization.
    
    Args:
        name: Organization name
        owner_id: User ID of the owner
        description: Optional organization description
        
    Returns:
        Created organization dictionary
        
    Raises:
        ValueError: If organization with name already exists
    """
    # Check if org already exists
    for org in ORGS.values():
        if org.name.lower() == name.lower():
            raise ValueError(f"Organization '{name}' already exists")
    
    org = Organization(name, owner_id, description)
    ORGS[org.org_id] = org
    
    return org.to_dict()

def get_org(org_id: str) -> Optional[Dict]:
    """
    Get organization by ID.
    
    Args:
        org_id: Organization unique identifier
        
    Returns:
        Organization dictionary if found, None otherwise
    """
    org = ORGS.get(org_id)
    return org.to_dict() if org else None

def get_org_by_slug(slug: str) -> Optional[Dict]:
    """
    Get organization by slug.
    
    Args:
        slug: Organization slug
        
    Returns:
        Organization dictionary if found, None otherwise
    """
    for org in ORGS.values():
        if org.slug == slug:
            return org.to_dict()
    return None

def update_org(org_id: str, **kwargs) -> Optional[Dict]:
    """
    Update organization information.
    
    Args:
        org_id: Organization unique identifier
        **kwargs: Fields to update (name, description, settings, etc.)
        
    Returns:
        Updated organization dictionary if found, None otherwise
    """
    if org_id not in ORGS:
        return None
    
    org = ORGS[org_id]
    org.updated_at = datetime.utcnow()
    
    if "name" in kwargs:
        org.name = kwargs["name"]
        org.slug = kwargs["name"].lower().replace(" ", "-")
    
    if "description" in kwargs:
        org.description = kwargs["description"]
    
    if "settings" in kwargs:
        org.settings.update(kwargs["settings"])
    
    if "metadata" in kwargs:
        org.metadata.update(kwargs["metadata"])
    
    return org.to_dict()

def delete_org(org_id: str) -> bool:
    """
    Delete an organization.
    
    Args:
        org_id: Organization unique identifier
        
    Returns:
        True if successfully deleted, False if org not found
    """
    if org_id in ORGS:
        del ORGS[org_id]
        return True
    return False

def add_member(org_id: str, user_id: str, role: str = OrgRole.MEMBER, invited_by: str = None) -> Optional[Dict]:
    """
    Add a member to an organization.
    
    Args:
        org_id: Organization unique identifier
        user_id: User ID to add
        role: Member role (owner, admin, member, viewer)
        invited_by: User ID of inviter
        
    Returns:
        Updated members list if successful, None otherwise
    """
    if org_id not in ORGS:
        return None
    
    org = ORGS[org_id]
    
    # Check if already a member
    if user_id in org.members:
        return list(org.members.values())
    
    member = OrgMember(user_id, role)
    member.invited_by = invited_by
    member.invited_at = datetime.utcnow()
    
    org.members[user_id] = member
    org.updated_at = datetime.utcnow()
    
    return [m.to_dict() for m in org.members.values()]

def remove_member(org_id: str, user_id: str) -> bool:
    """
    Remove a member from an organization.
    
    Args:
        org_id: Organization unique identifier
        user_id: User ID to remove
        
    Returns:
        True if successfully removed, False otherwise
    """
    if org_id not in ORGS:
        return False
    
    org = ORGS[org_id]
    
    # Can't remove owner
    if user_id == org.owner_id:
        return False
    
    if user_id in org.members:
        del org.members[user_id]
        org.updated_at = datetime.utcnow()
        return True
    
    return False

def update_member_role(org_id: str, user_id: str, new_role: str) -> Optional[Dict]:
    """
    Update a member's role in the organization.
    
    Args:
        org_id: Organization unique identifier
        user_id: User ID
        new_role: New role (owner, admin, member, viewer)
        
    Returns:
        Updated member info if successful, None otherwise
    """
    if org_id not in ORGS:
        return None
    
    org = ORGS[org_id]
    
    if user_id not in org.members:
        return None
    
    org.members[user_id].role = OrgRole(new_role) if isinstance(new_role, str) else new_role
    org.updated_at = datetime.utcnow()
    
    return org.members[user_id].to_dict()

def get_org_members(org_id: str) -> Optional[List[Dict]]:
    """
    Get all members of an organization.
    
    Args:
        org_id: Organization unique identifier
        
    Returns:
        List of member dictionaries if org found, None otherwise
    """
    if org_id not in ORGS:
        return None
    
    org = ORGS[org_id]
    return [member.to_dict() for member in org.members.values()]

def get_user_orgs(user_id: str) -> List[Dict]:
    """
    Get all organizations for a user.
    
    Args:
        user_id: User unique identifier
        
    Returns:
        List of organization dictionaries
    """
    user_orgs = []
    for org in ORGS.values():
        if user_id in org.members:
            org_dict = org.to_dict()
            org_dict["member_role"] = org.members[user_id].role.value
            user_orgs.append(org_dict)
    return user_orgs

def create_team(org_id: str, name: str, description: str = None) -> Optional[Dict]:
    """
    Create a team within an organization.
    
    Args:
        org_id: Organization unique identifier
        name: Team name
        description: Optional team description
        
    Returns:
        Created team dictionary if successful, None otherwise
    """
    if org_id not in ORGS:
        return None
    
    org = ORGS[org_id]
    team_id = str(uuid.uuid4())
    
    team = {
        "team_id": team_id,
        "name": name,
        "description": description,
        "created_at": datetime.utcnow().isoformat(),
        "members": []
    }
    
    org.teams[team_id] = team
    org.updated_at = datetime.utcnow()
    
    return team

def add_team_member(org_id: str, team_id: str, user_id: str) -> bool:
    """
    Add a member to a team.
    
    Args:
        org_id: Organization unique identifier
        team_id: Team unique identifier
        user_id: User ID to add
        
    Returns:
        True if successfully added, False otherwise
    """
    if org_id not in ORGS or team_id not in ORGS[org_id].teams:
        return False
    
    org = ORGS[org_id]
    team = org.teams[team_id]
    
    if user_id not in team["members"]:
        team["members"].append(user_id)
        org.updated_at = datetime.utcnow()
        return True
    
    return False

def remove_team_member(org_id: str, team_id: str, user_id: str) -> bool:
    """
    Remove a member from a team.
    
    Args:
        org_id: Organization unique identifier
        team_id: Team unique identifier
        user_id: User ID to remove
        
    Returns:
        True if successfully removed, False otherwise
    """
    if org_id not in ORGS or team_id not in ORGS[org_id].teams:
        return False
    
    org = ORGS[org_id]
    team = org.teams[team_id]
    
    if user_id in team["members"]:
        team["members"].remove(user_id)
        org.updated_at = datetime.utcnow()
        return True
    
    return False

def get_org_teams(org_id: str) -> Optional[List[Dict]]:
    """
    Get all teams in an organization.
    
    Args:
        org_id: Organization unique identifier
        
    Returns:
        List of team dictionaries if org found, None otherwise
    """
    if org_id not in ORGS:
        return None
    
    return list(ORGS[org_id].teams.values())
