"""
Role-Based Authorization & Permission Checks
"""
from typing import List
from fastapi import Depends, HTTPException, status
from app.database.models import User
from app.security.authentication import get_current_user


class RoleChecker:
    """Dependency that ensures the authenticated user possesses one of the allowed roles."""

    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = [r.lower() for r in allowed_roles]

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role.lower() not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Requires one of roles: {', '.join(self.allowed_roles)}. Current role: '{user.role}'."
            )
        return user


# Common role dependencies
require_admin = RoleChecker(["admin"])
require_investigator = RoleChecker(["admin", "investigator"])
require_analyst = RoleChecker(["admin", "investigator", "analyst"])
require_any_authenticated = RoleChecker(["admin", "investigator", "analyst", "client"])
