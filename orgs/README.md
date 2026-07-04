# Organizations Service

Manages organization creation, membership, and roles.

## Features
- Organization management
- Member management
- Role-based access control
- Team management
- Organization settings

## Endpoints
- `POST /orgs` - Create organization
- `GET /orgs/{org_id}` - Get organization
- `POST /orgs/{org_id}/members` - Add member
- `GET /orgs/{org_id}/members` - List members
- `DELETE /orgs/{org_id}/members/{user_id}` - Remove member
